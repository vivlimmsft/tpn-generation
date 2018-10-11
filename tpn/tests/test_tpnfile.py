import copy

import pytest

from .. import tpnfile


PROJECT_DATA = {
    "Arch": {
        "name": "Arch",
        "version": "1.0.3",
        "license": "Some license.\n\nHopefully it's a nice one.",
        "url": "https://someplace.com/on/the/internet",
    },
    "Python programming language": {
        "name": "Python programming language",
        "version": "3.6.5",
        "license": "The PSF license.\n\nIt\nis\nvery\nlong!",
        "url": "https://python.org",
    },
}

EXAMPLE = """A header!

With legal stuff!


1. Arch 1.0.3 (https://someplace.com/on/the/internet)
2. Python programming language 3.6.5 (https://python.org)


%% Arch 1.0.3 NOTICES AND INFORMATION BEGIN HERE (https://someplace.com/on/the/internet)
=========================================
Some license.

Hopefully it's a nice one.
=========================================
END OF Arch NOTICES AND INFORMATION

%% Python programming language 3.6.5 NOTICES AND INFORMATION BEGIN HERE (https://python.org)
=========================================
The PSF license.

It
is
very
long!
=========================================
END OF Python programming language NOTICES AND INFORMATION
"""


def test_parse_tpn():
    licenses = tpnfile.parse_tpn(EXAMPLE)
    assert "Arch" in licenses
    assert licenses["Arch"] == PROJECT_DATA["Arch"]
    assert "Python programming language" in licenses
    assert (
        licenses["Python programming language"]
        == PROJECT_DATA["Python programming language"]
    )


def test_sort():
    cached_data = copy.deepcopy(PROJECT_DATA)
    requested_data = copy.deepcopy(PROJECT_DATA)
    for details in requested_data.values():
        del details["license"]
    cached_data["Python programming language"]["version"] = "1.5.2"
    projects = tpnfile.sort(cached_data, requested_data)
    assert not cached_data
    assert len(requested_data) == 1
    assert "Python programming language" in requested_data
    assert requested_data["Python programming language"]["version"] == "3.6.5"
    assert len(projects) == 1
    assert "Arch" in projects
    assert "license" in projects["Arch"]
    assert projects["Arch"]["license"] == PROJECT_DATA["Arch"]["license"]


def test_generate_tpn():
    settings = {"metadata": {"header": "A header!\n\nWith legal stuff!"}}

    assert tpnfile.generate_tpn(settings, PROJECT_DATA) == EXAMPLE
