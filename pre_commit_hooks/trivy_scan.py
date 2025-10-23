"""Pre-commit hook for running Trivy security scans."""

import argparse
import shutil
import subprocess
import sys
from typing import Optional, Sequence


def check_trivy_installed() -> bool:
    """
    Check if Trivy is installed and available in PATH.

    Returns:
        bool: True if Trivy is installed, False otherwise.
    """
    return shutil.which("trivy") is not None


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the Trivy scanner.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:] if None).

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run Trivy security scanner as a pre-commit hook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--severity",
        type=str,
        default="HIGH,CRITICAL",
        help="Comma-separated list of severities to check (default: HIGH,CRITICAL)",
    )

    parser.add_argument(
        "--format",
        type=str,
        default="table",
        choices=["table", "json", "sarif", "template", "cyclonedx", "spdx", "github"],
        help="Output format (default: table)",
    )

    parser.add_argument(
        "--exit-code",
        type=int,
        default=1,
        help="Exit code when vulnerabilities are found (default: 1)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom trivy.yaml configuration file",
    )

    parser.add_argument(
        "--skip-db-update",
        action="store_true",
        help="Skip Trivy database update (faster for repeated scans)",
    )

    parser.add_argument(
        "--scanners",
        type=str,
        default="vuln",
        help="Comma-separated list of scanners to use (default: vuln). "
        "Options: vuln,misconfig,secret,license",
    )

    parser.add_argument(
        "--timeout",
        type=str,
        help="Timeout for the scan (e.g., 5m0s)",
    )

    parser.add_argument(
        "--ignore-unfixed",
        action="store_true",
        help="Ignore unfixed vulnerabilities",
    )

    parser.add_argument(
        "--trivyignore",
        type=str,
        help="Path to .trivyignore file",
    )

    parser.add_argument(
        "trivy_args",
        nargs="*",
        help="Additional arguments to pass to Trivy",
    )

    return parser.parse_args(argv)


def run_trivy_scan(args: argparse.Namespace, scan_path: str = ".") -> int:
    """
    Execute Trivy scan with the provided arguments.

    Args:
        args: Parsed command-line arguments.
        scan_path: Path to scan (default: current directory).

    Returns:
        int: Exit code from Trivy scan (0 for success, non-zero for failures/vulnerabilities).
    """
    # Build the Trivy command
    cmd = ["trivy", "fs"]

    # Add severity filter
    cmd.extend(["--severity", args.severity])

    # Add output format
    cmd.extend(["--format", args.format])

    # Add exit code
    cmd.extend(["--exit-code", str(args.exit_code)])

    # Add scanners
    cmd.extend(["--scanners", args.scanners])

    # Add optional flags
    if args.config:
        cmd.extend(["--config", args.config])

    if args.skip_db_update:
        cmd.append("--skip-db-update")

    if args.timeout:
        cmd.extend(["--timeout", args.timeout])

    if args.ignore_unfixed:
        cmd.append("--ignore-unfixed")

    if args.trivyignore:
        cmd.extend(["--ignorefile", args.trivyignore])

    # Add any additional arguments
    if args.trivy_args:
        cmd.extend(args.trivy_args)

    # Add the scan path
    cmd.append(scan_path)

    # Execute the scan
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=False)
        return result.returncode
    except subprocess.SubprocessError as e:
        print(f"Error running Trivy: {e}", file=sys.stderr)
        return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the Trivy pre-commit hook.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:] if None).

    Returns:
        int: Exit code (0 for success, 1 for vulnerabilities found, 2 for execution errors).
    """
    # Check if Trivy is installed
    if not check_trivy_installed():
        print(
            "Error: Trivy is not installed or not available in PATH.\n"
            "Please install Trivy from: https://trivy.dev/\n"
            "Installation methods:\n"
            "  - macOS: brew install trivy\n"
            "  - Linux (apt): sudo apt-get install trivy\n"
            "  - Binary: https://github.com/aquasecurity/trivy/releases",
            file=sys.stderr,
        )
        return 2

    # Parse arguments
    args = parse_arguments(argv)

    # Run the scan
    print("Running Trivy security scan...")
    exit_code = run_trivy_scan(args)

    if exit_code == 0:
        print("✓ No vulnerabilities found!")
    elif exit_code == 1:
        print("✗ Vulnerabilities found! Please review the output above.", file=sys.stderr)
    else:
        print("✗ Trivy scan failed with an error.", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
