// This file is used purely for translation keys extraction
import React from 'react'
import { i18next } from "@translations/mock_module/i18next";
import { Trans } from "react-i18next";


export const AComponent = () =>
    <div>
        <h1>{i18next.t('jsstring1')}</h1>
        <Trans>jsstring2</Trans>
    </div>