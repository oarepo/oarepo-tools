#!/usr/bin/env bash

TRANS_ROOT=${1:-.}

IFS=',' read -ra LNGS <<<"$LANGUAGES"
echo "$1"
for lng in "${LNGS[@]}"; do
    i18next-conv -l "${lng}" -s "${TRANS_ROOT}/messages/cs/LC_MESSAGES/translations.json" -t "${TRANS_ROOT}/messages/${lng}/LC_MESSAGES/messages.po"
done
