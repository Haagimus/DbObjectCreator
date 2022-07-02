import toml
from pathlib import Path
import mysql
import DbObjectCreator as dbo

def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""

    path = Path(__file__).resolve().parents[0] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    package_init_version = dbo.__init__('version')
    
    assert package_init_version == pyproject_version

print(test_versions_are_in_sync())

import pkg_resources

pkg_resources.get_distrobution('dbobjectcreator').version
