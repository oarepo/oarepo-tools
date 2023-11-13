// This file is part of React-Invenio-Deposit
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-app-rdm is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

const { readFileSync, writeFileSync } = require("fs");
const { gettextToI18next } = require("i18next-conv");
const TRANSLATIONS_BASE_PATH = process.argv[2] || './';
const PACKAGE_JSON_BASE_PATH = process.argv[3] || './';
const languages = process.env.LANGUAGES.split(',') || ['en'];

// it accepts the same options as the cli.
// https://github.com/i18next/i18next-gettext-converter#options
const options = {
    /* you options here */
};

function save (target) {
    return (result) => {
        writeFileSync(target, result);
    };
}

for (const lang of languages) {
    gettextToI18next(
        lang,
        readFileSync(`${TRANSLATIONS_BASE_PATH}/${lang}/LC_MESSAGES/messages.po`),
        options
    ).then(save(`${PACKAGE_JSON_BASE_PATH}/messages/${lang}/LC_MESSAGES/translations.json`));
}
