#!/bin/bash

set -e

BASE_DIR="$(dirname "$0")/.."
VENV_DIR="$BASE_DIR/.venv"

deactivate || true

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR"/bin/pip install -U setuptools pip
  "$VENV_DIR"/bin/pip install -e "${BASE_DIR}[dev]"
fi

source "$VENV_DIR"/bin/activate

if [ ! -f "ruff.toml" ]; then
  cat <<EOF > "ruff.toml"
[lint]
extend-select = [
    "UP",   # pyupgrade
    "D",    # pydocstyle
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "I",    # isort
    "TCH",  # type checking
    "ANN",  # annotations
    "DOC",  # docstrings
]

ignore = [
    "ANN101",  # Missing type annotation for self in method
    "ANN102",  # Missing type annotation for cls in classmethod
    "ANN204",  # Missing return type annotation in __init__ method
    "UP007",   # Imho a: Optional[int] = None is more readable than a: (int | None) = None for kwargs

    "D203",    # 1 blank line required before class docstring (we use D211)
    "D213",    # Multi-line docstring summary should start at the second line - we use D212 (starting on the same line)
    "D404",    # First word of the docstring should not be This
]

[flake8-annotations]
mypy-init-return = true
EOF
fi

if [ ! -f mypy.ini ] ; then

  cat <<EOF > mypy.ini
[mypy]
disable_error_code = ["import-untyped", "import-not-found"]
EOF
fi

python_files=$(
  ( git status --short| grep '^?' | cut -d\  -f2- && git ls-files ) | egrep ".*[.]py" | sort -u
)

python_files_without_tests=$(
  ( git status --short| grep '^?' | cut -d\  -f2- && git ls-files ) | egrep ".*[.]py" | egrep -v "^tests/" | sort -u
)
top_level_package=$(echo $python_files_without_tests | tr ' ' '\n' | grep '/' | cut -d/ -f1 | sort -u)

# python must not be in directories containing ' ', so no quotes here or inside the variable
ruff format -- $python_files
ruff check --fix $python_files_without_tests
python -m licenseheaders -t .copyright.tmpl -cy -f $python_files#

mypy --enable-incomplete-feature=NewGenericSyntax $top_level_package
