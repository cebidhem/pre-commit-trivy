"""Tests for the Trivy pre-commit hook."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from pre_commit_hooks.trivy_scan import (
    check_trivy_installed,
    main,
    parse_arguments,
    run_trivy_scan,
)


class TestTrivyInstallation:
    """Tests for Trivy installation checks."""

    def test_trivy_installed(self, mock_trivy_installed):
        """Test that check_trivy_installed returns True when Trivy is installed."""
        assert check_trivy_installed() is True

    def test_trivy_not_installed(self, mock_trivy_not_installed):
        """Test that check_trivy_installed returns False when Trivy is not installed."""
        assert check_trivy_installed() is False


class TestArgumentParsing:
    """Tests for command-line argument parsing."""

    def test_parse_arguments_defaults(self):
        """Test parsing with default arguments."""
        args = parse_arguments([])
        assert args.severity == "HIGH,CRITICAL"
        assert args.format == "table"
        assert args.exit_code == 1
        assert args.scanners == "vuln"
        assert args.skip_db_update is False
        assert args.ignore_unfixed is False
        assert args.config is None
        assert args.timeout is None
        assert args.trivyignore is None
        assert args.trivy_args == []

    def test_parse_arguments_custom_severity(self):
        """Test parsing with custom severity."""
        args = parse_arguments(["--severity", "LOW,MEDIUM"])
        assert args.severity == "LOW,MEDIUM"

    def test_parse_arguments_custom_format(self):
        """Test parsing with custom format."""
        args = parse_arguments(["--format", "json"])
        assert args.format == "json"

    def test_parse_arguments_custom_exit_code(self):
        """Test parsing with custom exit code."""
        args = parse_arguments(["--exit-code", "2"])
        assert args.exit_code == 2

    def test_parse_arguments_skip_db_update(self):
        """Test parsing with skip-db-update flag."""
        args = parse_arguments(["--skip-db-update"])
        assert args.skip_db_update is True

    def test_parse_arguments_custom_scanners(self):
        """Test parsing with custom scanners."""
        args = parse_arguments(["--scanners", "vuln,misconfig,secret"])
        assert args.scanners == "vuln,misconfig,secret"

    def test_parse_arguments_with_config(self):
        """Test parsing with custom config file."""
        args = parse_arguments(["--config", "/path/to/trivy.yaml"])
        assert args.config == "/path/to/trivy.yaml"

    def test_parse_arguments_with_timeout(self):
        """Test parsing with timeout."""
        args = parse_arguments(["--timeout", "5m0s"])
        assert args.timeout == "5m0s"

    def test_parse_arguments_ignore_unfixed(self):
        """Test parsing with ignore-unfixed flag."""
        args = parse_arguments(["--ignore-unfixed"])
        assert args.ignore_unfixed is True

    def test_parse_arguments_with_trivyignore(self):
        """Test parsing with trivyignore file."""
        args = parse_arguments(["--trivyignore", ".trivyignore"])
        assert args.trivyignore == ".trivyignore"

    def test_parse_arguments_with_additional_args(self):
        """Test parsing with additional Trivy arguments."""
        args = parse_arguments(["--", "--debug", "--quiet"])
        assert args.trivy_args == ["--debug", "--quiet"]


class TestTrivyScan:
    """Tests for Trivy scan execution."""

    def test_run_trivy_scan_success(self, mock_subprocess_success):
        """Test successful Trivy scan with no vulnerabilities."""
        args = parse_arguments([])
        exit_code = run_trivy_scan(args)
        assert exit_code == 0

    def test_run_trivy_scan_vulnerabilities_found(self, mock_subprocess_vulnerabilities_found):
        """Test Trivy scan with vulnerabilities found."""
        args = parse_arguments([])
        exit_code = run_trivy_scan(args)
        assert exit_code == 1

    def test_run_trivy_scan_with_severity(self, monkeypatch):
        """Test Trivy scan with custom severity."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        args = parse_arguments(["--severity", "MEDIUM,HIGH,CRITICAL"])
        run_trivy_scan(args)

        # Verify that subprocess.run was called with the correct severity
        call_args = mock_run.call_args[0][0]
        assert "--severity" in call_args
        severity_index = call_args.index("--severity")
        assert call_args[severity_index + 1] == "MEDIUM,HIGH,CRITICAL"

    def test_run_trivy_scan_with_format(self, monkeypatch):
        """Test Trivy scan with custom output format."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        args = parse_arguments(["--format", "json"])
        run_trivy_scan(args)

        # Verify that subprocess.run was called with the correct format
        call_args = mock_run.call_args[0][0]
        assert "--format" in call_args
        format_index = call_args.index("--format")
        assert call_args[format_index + 1] == "json"

    def test_run_trivy_scan_with_config_file(self, monkeypatch):
        """Test Trivy scan with custom config file."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        args = parse_arguments(["--config", "trivy.yaml"])
        run_trivy_scan(args)

        # Verify that subprocess.run was called with the correct config
        call_args = mock_run.call_args[0][0]
        assert "--config" in call_args
        config_index = call_args.index("--config")
        assert call_args[config_index + 1] == "trivy.yaml"

    def test_run_trivy_scan_with_skip_db_update(self, monkeypatch):
        """Test Trivy scan with skip-db-update flag."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        args = parse_arguments(["--skip-db-update"])
        run_trivy_scan(args)

        # Verify that subprocess.run was called with skip-db-update
        call_args = mock_run.call_args[0][0]
        assert "--skip-db-update" in call_args

    def test_run_trivy_scan_with_scanners(self, monkeypatch):
        """Test Trivy scan with custom scanners."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        args = parse_arguments(["--scanners", "vuln,misconfig"])
        run_trivy_scan(args)

        # Verify that subprocess.run was called with the correct scanners
        call_args = mock_run.call_args[0][0]
        assert "--scanners" in call_args
        scanners_index = call_args.index("--scanners")
        assert call_args[scanners_index + 1] == "vuln,misconfig"

    def test_run_trivy_scan_subprocess_error(self, mock_subprocess_error):
        """Test Trivy scan with subprocess error."""
        args = parse_arguments([])
        exit_code = run_trivy_scan(args)
        assert exit_code == 2


class TestMainFunction:
    """Tests for the main function."""

    def test_main_trivy_not_installed(self, mock_trivy_not_installed, capsys):
        """Test main function when Trivy is not installed."""
        exit_code = main([])
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Trivy is not installed" in captured.err
        assert "https://trivy.dev/" in captured.err

    def test_main_no_vulnerabilities(self, mock_trivy_installed, mock_subprocess_success, capsys):
        """Test main function with no vulnerabilities found."""
        exit_code = main([])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "No vulnerabilities found" in captured.out

    def test_main_vulnerabilities_found(
        self, mock_trivy_installed, mock_subprocess_vulnerabilities_found, capsys
    ):
        """Test main function with vulnerabilities found."""
        exit_code = main([])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Vulnerabilities found" in captured.err

    def test_main_with_custom_arguments(self, mock_trivy_installed, monkeypatch, capsys):
        """Test main function with custom arguments."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        exit_code = main(["--severity", "LOW", "--format", "json", "--skip-db-update"])
        assert exit_code == 0

        # Verify command was constructed correctly
        call_args = mock_run.call_args[0][0]
        assert "trivy" in call_args
        assert "fs" in call_args
        assert "--severity" in call_args
        assert "LOW" in call_args
        assert "--format" in call_args
        assert "json" in call_args
        assert "--skip-db-update" in call_args

    def test_main_integration(self, mock_trivy_installed, monkeypatch):
        """End-to-end integration test of main function."""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        monkeypatch.setattr("subprocess.run", mock_run)

        # Test with various argument combinations
        exit_code = main(
            [
                "--severity",
                "HIGH,CRITICAL",
                "--format",
                "table",
                "--scanners",
                "vuln,secret",
                "--skip-db-update",
                "--ignore-unfixed",
            ]
        )

        assert exit_code == 0
        assert mock_run.called

        # Verify the command structure
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "trivy"
        assert call_args[1] == "fs"
        assert "." in call_args  # scan path
