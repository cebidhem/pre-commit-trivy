# pre-commit-trivy

[![CI - Tests and Linting](https://github.com/cebidhem/pre-commit-trivy/actions/workflows/ci.yml/badge.svg)](https://github.com/cebidhem/pre-commit-trivy/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pre-commit hook that integrates [Trivy](https://trivy.dev/) security scanning to detect vulnerabilities in your codebase before commits are finalized. This hook helps you catch security issues early in the development process.

## Features

- 🔒 **Security First**: Automatically scan for vulnerabilities before every commit
- 🎯 **Configurable**: Customize severity levels, scanners, and output formats
- ⚡ **Fast**: Skip database updates for faster repeated scans
- 🔧 **Flexible**: Pass-through support for all Trivy options
- 🧪 **Well-Tested**: Comprehensive test suite with >90% coverage
- 🐍 **Modern Python**: Built with Python 3.9+ using best practices

## Prerequisites

- **Python 3.9 or higher**
- **Trivy**: Must be installed separately

### Installing Trivy

Choose your preferred installation method:

**macOS (Homebrew)**:
```bash
brew install trivy
```

**Linux (apt)**:
```bash
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

**Binary Download**:
See [Trivy Installation Guide](https://aquasecurity.github.io/trivy/latest/getting-started/installation/)

## Installation

### As a pre-commit hook

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Add this to your `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/cebidhem/pre-commit-trivy
    rev: v0.1.0  # Use the latest version
    hooks:
      - id: trivy-scan
        # Optional: customize arguments
        args: ['--severity', 'HIGH,CRITICAL', '--skip-db-update']
```

3. Install the hook:
```bash
pre-commit install
```

### As a standalone tool

```bash
pip install pre-commit-trivy
```

## Usage

### Basic Usage

Once installed as a pre-commit hook, it will automatically run on every commit:

```bash
git commit -m "Your commit message"
```

### Standalone Usage

You can also run the scanner directly:

```bash
trivy-scan
```

### Configuration Options

The hook supports extensive configuration through command-line arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--severity` | `HIGH,CRITICAL` | Comma-separated list of severities to check (UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL) |
| `--format` | `table` | Output format (table, json, sarif, template, cyclonedx, spdx, github) |
| `--exit-code` | `1` | Exit code when vulnerabilities are found |
| `--scanners` | `vuln` | Comma-separated list of scanners (vuln, misconfig, secret, license) |
| `--config` | - | Path to custom trivy.yaml configuration file |
| `--skip-db-update` | `false` | Skip Trivy database update (faster for repeated scans) |
| `--timeout` | - | Timeout for the scan (e.g., 5m0s) |
| `--ignore-unfixed` | `false` | Ignore unfixed vulnerabilities |
| `--trivyignore` | - | Path to .trivyignore file |
| `--dependency-tree` | `false` | Show dependency tree with vulnerabilities |

### Examples

**Check only CRITICAL vulnerabilities:**
```yaml
- id: trivy-scan
  args: ['--severity', 'CRITICAL']
```

**Output as JSON:**
```yaml
- id: trivy-scan
  args: ['--format', 'json']
```

**Use multiple scanners:**
```yaml
- id: trivy-scan
  args: ['--scanners', 'vuln,secret,misconfig']
```

**Skip database update for faster scans:**
```yaml
- id: trivy-scan
  args: ['--skip-db-update']
```

**Use custom Trivy configuration:**
```yaml
- id: trivy-scan
  args: ['--config', 'trivy.yaml']
```

**Ignore specific vulnerabilities:**
```yaml
- id: trivy-scan
  args: ['--trivyignore', '.trivyignore']
```

**Show dependency tree:**
```yaml
- id: trivy-scan
  args: ['--dependency-tree']
```

**Comprehensive configuration:**
```yaml
- id: trivy-scan
  args:
    - '--severity'
    - 'MEDIUM,HIGH,CRITICAL'
    - '--scanners'
    - 'vuln,secret'
    - '--format'
    - 'table'
    - '--ignore-unfixed'
    - '--skip-db-update'
```

## Advanced Configuration

### Using trivy.yaml

For complex configurations, create a `trivy.yaml` file (see `trivy.yaml.example`):

```yaml
severity:
  - HIGH
  - CRITICAL

scan:
  scanners:
    - vuln
    - secret

timeout: 5m0s
ignore-unfixed: false
```

Then use it:
```yaml
- id: trivy-scan
  args: ['--config', 'trivy.yaml']
```

### Ignoring Vulnerabilities

Create a `.trivyignore` file (see `.trivyignore.example`):

```
# Ignore this CVE because we use this library in a sandboxed environment
CVE-2023-12345

# False positive - this vulnerability doesn't affect our usage
CVE-2023-67890
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/cebidhem/pre-commit-trivy.git
cd pre-commit-trivy
```

2. Install dependencies using uv:
```bash
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Testing

Run tests with coverage:
```bash
pytest tests/ --cov=pre_commit_hooks --cov-report=term-missing -v
```

### Linting

Format code with black:
```bash
black pre_commit_hooks tests
```

Check code quality with pylint:
```bash
pylint pre_commit_hooks
```

### Running all checks

```bash
# Format check
black --check pre_commit_hooks tests

# Linting
pylint pre_commit_hooks

# Tests with coverage
pytest tests/ --cov=pre_commit_hooks --cov-report=term-missing -v
```

## How It Works

1. **Installation Check**: Verifies that Trivy is installed on your system
2. **Configuration**: Parses command-line arguments and configuration files
3. **Scanning**: Runs `trivy fs` scan on your project directory
4. **Reporting**: Displays vulnerabilities in the specified format
5. **Exit Code**: Returns appropriate exit code (0 = success, 1 = vulnerabilities found, 2 = error)

If vulnerabilities are found matching your severity criteria, the commit will be blocked, allowing you to review and address the issues before committing.

## Exit Codes

- `0`: No vulnerabilities found (or below severity threshold)
- `1`: Vulnerabilities found matching severity criteria
- `2`: Execution error (e.g., Trivy not installed, configuration error)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Maintain test coverage above 90%
- Update documentation as needed
- Use conventional commits for commit messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Trivy](https://trivy.dev/) - The comprehensive security scanner
- [pre-commit](https://pre-commit.com/) - A framework for managing git hooks

## Support

If you encounter any issues or have questions:

1. Check the [Trivy documentation](https://aquasecurity.github.io/trivy/)
2. Review existing [GitHub issues](https://github.com/cebidhem/pre-commit-trivy/issues)
3. Open a new issue with details about your problem

## Roadmap

- [ ] Add support for container image scanning
- [ ] Implement caching for faster repeated scans
- [ ] Add configuration templates for common use cases
- [ ] Integration with CI/CD platforms
- [ ] Enhanced reporting with HTML output
