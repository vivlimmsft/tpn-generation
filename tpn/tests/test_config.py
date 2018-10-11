import copy

import pytest

from .. import config


PROJECT_DATA = {
    "Arch": {
        "name": "Arch",
        "version": "1.0.3",
        "license": "Some license.\n\nHopefully it's a nice one.",
        "url": "https://someplace.com/on/the/internet",
        "purpose": "npm",
    },
    "Python programming language": {
        "name": "Python programming language",
        "version": "3.6.5",
        "license": "The PSF license.\n\nIt\nis\nvery\nlong!",
        "url": "https://python.org",
        "purpose": "explicit",
    },
}


@pytest.fixture
def example_data():
    return copy.deepcopy(PROJECT_DATA)


@pytest.fixture
def example_config():
    return {"project": [copy.deepcopy(details) for details in PROJECT_DATA.values()]}


def test_get_projects(example_config):
    result = config.get_projects(example_config)
    assert result == PROJECT_DATA


def test_get_projects_key_check(example_config):
    del example_config["project"][0]["url"]
    with pytest.raises(KeyError):
        config.get_projects(example_config)


def test_get_explicit_entries(example_data):
    explicit_entries = config.get_explicit_entries(example_data)
    assert explicit_entries == {
        "Python programming language": PROJECT_DATA["Python programming language"]
    }
    assert "Python programming language" not in example_data


def test_sort_relevant(example_data):
    expected = {"Arch": example_data["Arch"]}
    npm_data = {"Arch": {"version": "1.0.3"}}
    relevant, stale = config.sort("npm", example_data, npm_data)
    assert not stale
    assert "Arch" not in npm_data
    assert len(example_data) == 1
    assert relevant == expected


def test_sort_version_stale(example_data):
    npm_data = {"Arch": {"version": "2.0.0"}}
    relevant, stale = config.sort("npm", example_data, npm_data)
    assert not relevant
    assert "Arch" in stale
    assert stale["Arch"]["version"] == "1.0.3"
    assert "Arch" in npm_data
    assert npm_data["Arch"]["version"] == "2.0.0"


def test_sort_project_stale(example_data):
    npm_data = {"Arch2": {"version": "2.0.0"}}
    relevant, stale = config.sort("npm", example_data, npm_data)
    assert not relevant
    assert "Arch" in stale
    assert stale["Arch"]["version"] == "1.0.3"
    assert "Arch2" in npm_data


def test_sort_no_longer_relevant(example_data):
    relevant, stale = config.sort("npm", example_data, {})
    assert not relevant
    assert "Arch" in stale