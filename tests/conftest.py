"""Pytest configuration and fixtures for pre-commit-trivy tests."""

import subprocess
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_trivy_installed(monkeypatch):
    """Mock Trivy as installed."""

    def mock_which(cmd):
        if cmd == "trivy":
            return "/usr/local/bin/trivy"
        return None

    monkeypatch.setattr("shutil.which", mock_which)


@pytest.fixture
def mock_trivy_not_installed(monkeypatch):
    """Mock Trivy as not installed."""

    def mock_which(cmd):
        return None

    monkeypatch.setattr("shutil.which", mock_which)


@pytest.fixture
def mock_subprocess_success(monkeypatch):
    """Mock successful subprocess run."""

    def mock_run(*args, **kwargs) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def mock_subprocess_vulnerabilities_found(monkeypatch):
    """Mock subprocess run with vulnerabilities found."""

    def mock_run(*args, **kwargs) -> MagicMock:
        result = MagicMock()
        result.returncode = 1
        result.stdout = "Vulnerabilities found"
        result.stderr = ""
        return result

    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def mock_subprocess_error(monkeypatch):
    """Mock subprocess run with error."""

    def mock_run(*args, **kwargs):
        raise subprocess.SubprocessError("Mock error")

    monkeypatch.setattr("subprocess.run", mock_run)
