import os
from pathlib import Path

from oarepo_tools.make_translations import main


def test_cli_with_oarepo_yaml(app, db, cache, extra_entry_points, cli_runner):
    config_file = Path(__file__).parent
    try:
        cli_runner(main([str(config_file)]))
    except SystemExit as se:
        assert se.code == 0


def test_cli_with_setup_cfg(app, db, cache, extra_entry_points, cli_runner):
    config_file = Path(__file__).parent
    try:
        cli_runner(main([str(config_file)]))
    except SystemExit as se:
        assert se.code == 0


def test_cli_with_config_autodetect(app, db, cache, extra_entry_points, cli_runner):
    stored_cwd = os.getcwd()
    os.chdir(Path(__file__).parent)
    try:
        cli_runner(main([]))
    except SystemExit as se:
        assert se.code == 0
    finally:
        os.chdir(stored_cwd)


def test_cli_with_empty_setupcfg(app, db, cache, extra_entry_points, cli_runner):
    base_dir = Path(__file__).parent
    empty_config_file = base_dir / "empty_setup.cfg"
    real_config_file = base_dir / "setup.cfg"
    backup_config_file = base_dir / "setup.cfg.bak"

    real_config_file.rename(base_dir / backup_config_file)
    empty_config_file.rename(real_config_file)

    try:
        cli_runner(main([]))
    except SystemExit as se:
        assert se.code == 0
    finally:
        real_config_file.rename(empty_config_file)
        backup_config_file.rename(real_config_file)
