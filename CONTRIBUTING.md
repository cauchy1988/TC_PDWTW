# Contributing to TC_PDWTW

Thank you for your interest in contributing to TC_PDWTW! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

- Use the [GitHub Issues](https://github.com/cauchy1988/TC_PDWTW/issues) page
- Provide a clear description of the problem
- Include steps to reproduce the issue
- Attach relevant code snippets or error messages

### Suggesting Enhancements

- Use the [GitHub Discussions](https://github.com/cauchy1988/TC_PDWTW/discussions) page
- Describe the enhancement and its benefits
- Provide examples of how it would work

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure all tests pass**: `python -m pytest`
6. **Commit your changes**: `git commit -m "Add: description of changes"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Create a Pull Request**

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Testing

- Write unit tests for new functionality
- Ensure existing tests continue to pass
- Aim for high test coverage
- Use descriptive test names

### Documentation

- Update relevant documentation when adding features
- Include examples in docstrings
- Update README.md if adding new major features

## 🏗️ Project Structure

```
TC_PDWTW/
├── src/           # Core implementation
├── tests/         # Test suite
├── examples/      # Usage examples
├── docs/          # Documentation
└── papers/        # Research papers
```

## 🚀 Getting Started

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/TC_PDWTW.git
cd TC_PDWTW

# Add upstream remote
git remote add upstream https://github.com/cauchy1988/TC_PDWTW.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_lns_framework.py
```

## 📝 Commit Message Format

Use clear, descriptive commit messages:

- **Add**: New features
- **Fix**: Bug fixes
- **Update**: Documentation or minor changes
- **Refactor**: Code restructuring
- **Test**: Adding or updating tests

## 🔍 Code Review Process

1. All contributions require review
2. Maintainers will review your PR
3. Address any feedback or requested changes
4. Once approved, your PR will be merged

## 📞 Questions?

If you have questions about contributing:

- Open a [GitHub Discussion](https://github.com/cauchy1988/TC_PDWTW/discussions)
- Contact the maintainer: [cauchy1988](https://github.com/cauchy1988)

## 🙏 Thank You

Your contributions help make TC_PDWTW better for the entire optimization research community!

