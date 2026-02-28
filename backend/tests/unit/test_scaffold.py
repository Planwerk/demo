"""Verify project scaffold: package imports and structure."""

import importlib


def test_app_package_importable() -> None:
    mod = importlib.import_module("app")
    assert mod is not None


def test_sub_packages_importable() -> None:
    for pkg in ("app.models", "app.schemas", "app.api", "app.api.routes", "app.services"):
        mod = importlib.import_module(pkg)
        assert mod is not None
