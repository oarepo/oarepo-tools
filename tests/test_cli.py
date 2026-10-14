# SPDX-FileCopyrightText: 2024-2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from oarepo_tools.make_translations import main


def test_cli_with_oarepo_yaml():
    config_file = Path(__file__).parent
    result = CliRunner().invoke(main, [str(config_file)])
    assert result.exit_code == 0, result.output


def test_cli_with_setup_cfg():
    config_file = Path(__file__).parent
    result = CliRunner().invoke(main, [str(config_file)])
    assert result.exit_code == 0, result.output


def test_cli_with_config_autodetect():
    stored_cwd = Path.cwd()
    os.chdir(Path(__file__).parent)
    try:
        result = CliRunner().invoke(main, [])
        assert result.exit_code == 0, result.output
    finally:
        os.chdir(stored_cwd)


def test_cli_with_empty_setupcfg():
    base_dir = Path(__file__).parent
    empty_config_file = base_dir / "empty_setup.cfg"
    real_config_file = base_dir / "setup.cfg"
    backup_config_file = base_dir / "setup.cfg.bak"

    real_config_file.rename(base_dir / backup_config_file)
    empty_config_file.rename(real_config_file)

    try:
        result = CliRunner().invoke(main, [])
        assert result.exit_code == 0, result.output
    finally:
        real_config_file.rename(empty_config_file)
        backup_config_file.rename(real_config_file)
