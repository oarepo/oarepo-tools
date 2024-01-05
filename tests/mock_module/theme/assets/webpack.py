from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={},
            dependencies={},
            devDependencies={},
            aliases={
                "@translations/mock_module": "./translations/mock_module",
            },
        )
    },
)
