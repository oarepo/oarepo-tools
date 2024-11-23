from pathlib import Path

from oarepo_tools.module_config import PythonPackage


def test_python_package_toml():
    toml_root = Path(__file__).parent / "data" / "mock_toml_package"
    package = PythonPackage(toml_root)
    assert package.top_level_modules == ['mock_toml']

def test_python_package_cfg():
    cfg_root = Path(__file__).parent / "data" / "mock_setupcfg_package"
    package = PythonPackage(cfg_root)
    assert package.top_level_modules == ['mock_setupcfg']