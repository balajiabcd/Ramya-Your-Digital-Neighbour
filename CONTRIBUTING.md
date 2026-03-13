# Contributing to Ramya Bot

Thank you for your interest in contributing to Ramya Bot!

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/ramya-bot.git
   cd ramya-bot
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for all public functions
- Keep functions small and focused (max ~50 lines)

## Testing

Run tests before submitting a pull request:
```bash
pytest tests/ -v
```

Run linting:
```bash
flake8 src app.py
```

## Pull Request Process

1. Ensure all tests pass and linting is clean
2. Update documentation if needed
3. Describe your changes in the PR description
4. Request review from maintainers

## Security

- Never commit secrets or API keys
- Follow security best practices outlined in the project
- Report security vulnerabilities privately

## Questions?

Open an issue for questions about contributing.
