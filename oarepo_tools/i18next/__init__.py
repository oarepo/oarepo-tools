import os
import shutil
import inspect
from pathlib import Path
from subprocess import check_call

import click

npm_proj_cwd = os.path.dirname(inspect.getfile(inspect.currentframe()))
npm_proj_env = dict(os.environ)


def extract_i18next_messages(base_dir: Path, i18n_configuration, translations_dir):
    npm_proj_env["LANGUAGES"] = ",".join(i18n_configuration["languages"] or ["en"])

    source_path_patterns = [
        os.path.join(base_dir / source_path, "**/*.{js,jsx,ts,tsx}")
        for source_path in i18n_configuration["i18next_source_paths"]
    ]

    output_path = base_dir / translations_dir

    # Make sure NPM project is installed & up-to-date
    click.secho("Installing / updating React-i18next dependencies", fg="green")
    check_call(
        ["npm", "install"],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    # Extract JS translations strings
    click.secho(
        f"Extracting i18next  messages from sources matching {source_path_patterns} -> {output_path}",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "extract_messages",
            "--",
            "--output",
            output_path,
            *source_path_patterns,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )

    # Extract JS translations strings
    click.secho(
        f"Compiling i18next translations to PO files in: {output_path}",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "compile_languages",
            "--",
            output_path,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )


def ensure_i18next_entrypoint(i18next_translations_dir: Path):
    # check if i18next.js exists and if it does not, create it
    i18next_entrypoint = i18next_translations_dir / "i18next.js"

    if not i18next_entrypoint.exists():
        shutil.copy(Path(__file__).parent / "i18next.js", i18next_entrypoint)
        click.secho(f"Created i18next.js in {i18next_entrypoint}", fg="green")


def compile_i18next_translations(
    translations_dir, i18n_configuration, output_translations_dir
):
    npm_proj_env["LANGUAGES"] = ",".join(i18n_configuration["languages"] or ["en"])

    click.secho(f"Compiling i18next messages in {translations_dir}", fg="green")
    check_call(
        [
            "npm",
            "run",
            "compile_catalog",
            "--",
            translations_dir,
            output_translations_dir,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )
