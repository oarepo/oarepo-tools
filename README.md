# oarepo-tools

Developer tooling for OARepo packages. It provides the `make-translations` command, which keeps
Python/Jinja (gettext) and JavaScript (i18next) translations of a package in one set of `.po`
catalogues.

## Requirements

- Python 3.14 (oarepo-tools 1.x). Use oarepo-tools 0.2.x for older Python versions.
- Node.js and npm, unless you run with `--without-ui`.

## Installation

In OARepo libraries and repositories nothing needs to be installed: oarepo-cli depends on
oarepo-tools, and `./run.sh translations` runs `make-translations` in the project root
(extra arguments are passed through, e.g. `./run.sh translations --without-ui`).

To use the command on its own, add `oarepo-tools` to your development dependencies, e.g. in
`pyproject.toml`:

```toml
[project.optional-dependencies]
dev = ["oarepo-tools"]
```

## Usage

```bash
make-translations [CONFIG_PATH] [--without-ui]
```

`CONFIG_PATH` is the directory containing the configuration (or the configuration file itself);
it defaults to the current directory. All paths in the configuration are relative to that
directory.

1. Run `make-translations`. It extracts the messages from your sources and creates or updates
   a `messages.po` catalogue for every language in `babel_output_translations`.
2. Translate the catalogues, e.g. with [Poedit](https://poedit.net/) or in a text editor.
3. Run `make-translations` again. It compiles the catalogues to `.mo` files for Python and to
   i18next JSON files for JavaScript.

Use `--without-ui` for packages without JavaScript sources: the i18next steps are skipped and
Node.js is not needed.

## Configuration

The configuration is read from the `[oarepo.i18n]` section of `setup.cfg`. If that file or
section is missing, the `i18n` section of `oarepo.yaml` is used instead.

`oarepo.yaml`:

```yaml
i18n:
  languages:
    - cs
    - en
  babel_source_paths:
    - my_package/
  babel_output_translations: my_package/translations
  # only needed with JavaScript sources (i.e. without --without-ui)
  i18next_source_paths:
    - my_package/ui/theme/assets/semantic-ui/js
  i18next_output_translations: my_package/ui/theme/assets/semantic-ui/translations/my_package
```

`setup.cfg` (legacy) uses the same keys. Write list values one item per line, starting on the
line after the key; a value on the same line as the key is read as a single string.

```ini
[oarepo.i18n]
languages =
    cs
    en
babel_source_paths =
    my_package/
babel_output_translations = my_package/translations
```

| Key | Required | Description |
|---|---|---|
| `languages` | yes | Language codes to manage. |
| `babel_source_paths` | yes | Directories scanned for gettext messages: `*.py` files, `*.html` and `*.jinja` (JinjaX) templates. |
| `babel_output_translations` | yes | Directory where the gettext catalogues (`<lang>/LC_MESSAGES/messages.po`/`.mo`) are generated. |
| `babel_input_translations` | no | Extra gettext catalogue directories (`<lang>/LC_MESSAGES/*.po`) merged into the output, e.g. translations generated for models. |
| `i18next_source_paths` | without `--without-ui` | Directories scanned for i18next messages: `i18next.t(...)` calls and `<Trans>` components in `*.js`/`*.jsx` files. |
| `i18next_output_translations` | without `--without-ui` | Directory where the i18next entrypoint and JSON catalogues are generated. |
| `i18next_input_translations` | no | Extra i18next catalogue directories (`<lang>/translations.json`) merged into the output. |

In Python, mark messages with `_`, `gettext`, `lazy_gettext` and the other standard gettext
functions. In JavaScript, import the generated i18next instance and use `i18next.t("...")` or
`<Trans>`.

## Integrating the output

- Register the package for Invenio translations in `pyproject.toml`; the entry point names the
  package that contains the `translations` directory:

  ```toml
  [project.entry-points."invenio_i18n.translations"]
  my_package = "my_package"
  ```

- Ship the generated `.po`/`.mo` files with the package (hatchling includes them by default
  unless they are gitignored).
- `i18next_output_translations` contains `i18next.js`, which exports a configured `i18next`
  instance, and `messages/<lang>/LC_MESSAGES/translations.json`. Add a webpack alias for this
  directory in your theme bundle, e.g. `"@translations/my_package": "translations/my_package"`,
  and import it with `import { i18next } from "@translations/my_package/i18next";`.

## Side effects

- `babel.ini` in the configuration directory is overwritten with the bundled version on every
  run; customize extraction through the configuration keys instead of editing it.
- `i18next.js` and `messages/index.js` in `i18next_output_translations` are regenerated on every
  run.
- Untranslated messages are left out of the i18next JSON files, so i18next falls back to the key
  (the English text).
- Unless `--without-ui` is used, every run calls `npm install` inside the installed
  `oarepo_tools` package to fetch `i18next-scanner` and `i18next-conv`, so that directory must be
  writable.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
