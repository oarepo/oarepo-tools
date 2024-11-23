#!/usr/bin/env bash
##
## Copyright (C) 2024 CESNET z.s.p.o.
##
## oarepo-tools is free software; you can redistribute it and/or
## modify it under the terms of the MIT License; see LICENSE file for more
## details.
##

i18next-conv -l en -s "${1}" -p  -t "${2}" -b "${1}" 
