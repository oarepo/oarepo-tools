#!/usr/bin/env bash

TRANS_ROOT=${1:-.}

i18next-conv -l en -s "${TRANS_ROOT}/extracted-messages.json" -p  -t "${TRANS_ROOT}/messages.pot" -b "${TRANS_ROOT}/extracted-messages.json" 
