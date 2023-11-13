import os
import inspect
from subprocess import check_call

import click


def make_i18next_messages(i18n_configuration):
    npm_proj_cwd = os.path.dirname(inspect.getfile(inspect.currentframe()))
    npm_proj_env = dict(os.environ)
    npm_proj_env["LANGUAGES"] = ",".join(i18n_configuration["languages"] or ["en"])

    sources_root = os.getcwd()
    source_path_patterns = [
        os.path.join(sources_root, source_path, "**/*.{js,jsx}")
        for source_path in i18n_configuration["i18next_source_paths"]
    ]

    output_path = os.path.join(
        sources_root,
        next(iter(i18n_configuration["i18next_output_translations"]), None),
    )

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
        f"Compiling language catalog from i18next translations",
        fg="green",
    )
    check_call(
        [
            "npm",
            "run",
            "postextract_messages",
            "--",
            # sources_root,
            output_path,
        ],
        env=npm_proj_env,
        cwd=npm_proj_cwd,
    )
