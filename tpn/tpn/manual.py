import pathlib
import re


TPN_SECTION_TEMPLATE = "%% {name} {version} NOTICES AND INFORMATION BEGIN HERE ({url})\n=========================================\n{license}\n=========================================\nEND OF {name} NOTICES AND INFORMATION"
TPN_SECTION_RE = re.compile(
    r"%% (?P<name>.+?) (?P<version>\S+) NOTICES AND INFORMATION BEGIN HERE \((?P<url>http.+?)\)\n=========================================\n(?P<license>.+?)=========================================\nEND OF (?P=name) NOTICES AND INFORMATION",
    re.DOTALL,
)


def parse_tpn(text):
    """Break the TPN text up into individual project details."""
    licenses = {}
    for match in TPN_SECTION_RE.finditer(text):
        details = match.groupdict()
        name = details.pop("name")
        licenses[name] = details
    return licenses


def generate_tpn(config, projects):
    """Create the TPN text."""
    parts = [config["metadata"]["header"]]
    project_names = sorted(projects.keys())
    toc = []
    index_padding = len(f"{len(project_names)}.")
    for index, name in enumerate(project_names, 1):
        index_format = f"{index}.".ljust(index_padding)
        toc.append(
            f"{index_format} {name} {projects[name]['version']} ({projects[name]['url']})"
        )
    parts.append("\n".join(toc))
    licenses = []
    for name, details in projects.items():
        licenses.append(TPN_SECTION_TEMPLATE.format(name=name, **details))
    parts.append("\n\n".join(licenses))
    return "\n\n\n".join(parts) + "\n"
