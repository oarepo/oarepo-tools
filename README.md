# oarepo-tools

## Installation

Add `oarepo-tools` to 'dev' dependencies section of your setup.cfg (or similar)

## Usage

### `make-translations`

To have unified translations across your javascript (+react) and python sources, add the following
keys to your `setup.cfg`:

```ini


[oarepo.i18n]
# List of paths to scan for babel messages - python files and jinja templates are scanned
babel_source_paths =
    oarepo_oaipmh_harvester/oai_harvester
    oarepo_oaipmh_harvester/oai_run
    oarepo_oaipmh_harvester/oai_record
    oarepo_oaipmh_harvester/oai_batch
    oarepo_oaipmh_harvester/ui

# extra message catalogues - if you use oarepo-model-builder to generate models, add the generated
# translations directories here
babel_input_translations =
    oarepo_oaipmh_harvester/oai_harvester/translations
    oarepo_oaipmh_harvester/oai_run/translations
    oarepo_oaipmh_harvester/oai_record/translations
    oarepo_oaipmh_harvester/oai_batch/translations

# List of paths to scan for i18next messages - javascript and jsx files are scanned
i18next_source_paths =
    oarepo_oaipmh_harvester/ui/oai_harvester/theme/assets/semantic-ui/js
    oarepo_oaipmh_harvester/ui/oai_run/theme/assets/semantic-ui/js
    oarepo_oaipmh_harvester/ui/oai_batch/theme/assets/semantic-ui/js
    oarepo_oaipmh_harvester/ui/oai_record/theme/assets/semantic-ui/js

# this is the location where python translations are generated.
babel_output_translations =
    oarepo_oaipmh_harvester/translations

# Do not forget to add this directory to your package data and `invenio_i18n.translations` entry point
# - without the 'translations' suffix
invenio_i18n.translations =
    oarepo_oaipmh_harvester = oarepo_oaipmh_harvester

# this is the location where javascript translations are generated. Add this directory to webpack
# aliases
i18next_output_translations =
    oarepo_oaipmh_harvester/ui/theme/assets/semantic-ui/translations


```