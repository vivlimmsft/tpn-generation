import asyncio
import io
import json
import pathlib
import tarfile

import aiohttp


def _projects(package_data):
    """Retrieve the list of projects from the package data.

    'package_data' is assumed to be from a 'package-lock.json' file. All
    dev-related dependencies are ignored.

    """
    packages = {}
    for name, details in package_data["dependencies"].items():
        if details.get("dev", False):
            continue
        packages[name] = {
            "name": name,
            "version": details["version"],
            "url": details["resolved"],
        }
    return packages


# XXX Make async.
def projects_from_data(raw_data):
    """Create the requested projects from the data string provided."""
    json_data = json.loads(raw_data)
    return _projects(json_data)


def _top_level_package_filenames(tarball_paths):
    """Transform the iterable of npm tarball paths to the top-level files contained within the package."""
    paths = []
    for path in tarball_paths:
        parts = pathlib.PurePath(path).parts
        if parts[0] == "package" and len(parts) == 2:
            paths.append(parts[1])
    return frozenset(paths)


# While ``name.lower().startswith("license")`` would works in all of the cases
# below, it is better to err on the side of being conservative and be explicit
# rather than just assume that there won't be an e.g. LICENCE_PLATES or LICENSEE
# file which isn't an actual license.
LICENSE_FILENAMES = frozenset(
    x.lower()
    for x in (
        "license",
        "license.md",
        "license.mkd",
        "license.txt",
        "LICENSE-MIT",
        "LICENSE-MIT.txt",
    )
)


def _find_license(filenames):
    """Find the file name for the license file."""
    for filename in filenames:
        if filename.lower() in LICENSE_FILENAMES:
            return filename
    else:
        raise ValueError(f"no license file found in {sorted(filenames)}")


async def _fetch_license(session, tarball_url):
    """Download and extract the license file."""
    try:
        async with session.get(tarball_url) as response:
            content = await response.read()
        try:
            with tarfile.open(mode="r:gz", fileobj=io.BytesIO(content)) as tarball:
                filenames = _top_level_package_filenames(tarball.getnames())
                license_filename = _find_license(filenames)
                with tarball.extractfile(f"package/{license_filename}") as file:
                    return file.read().decode("utf-8")
        except tarfile.ReadError:
            content_string = content.decode("utf-8")
            print(f"Tried to download gzip at {tarball_url}, got this instead: {content_string}")
    except Exception as exc:
        return exc


async def fill_in_licenses(requested_projects):
    """Add the missing licenses to requested_projects.

    Any failures in the searching for licenses are returned.

    """
    failures = {}
    names = list(requested_projects.keys())
    urls = (requested_projects[name]["url"] for name in names)
    async with aiohttp.ClientSession() as session:
        tasks = (_fetch_license(session, url) for url in urls)
        for name, license_or_exc in zip(names, await asyncio.gather(*tasks)):
            details = requested_projects[name]
            license_or_exc = await _fetch_license(session, details["url"])
            if isinstance(license_or_exc, Exception):
                details["error"] = license_or_exc
                failures[name] = details
            else:
                details["license"] = license_or_exc
    return failures
