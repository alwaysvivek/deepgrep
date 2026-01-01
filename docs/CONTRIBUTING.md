# 🤝 Contributing to DeepGrep

Thank you for your interest in contributing to DeepGrep! This guide will help you get started.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal or political attacks
- Publishing others' private information
- Any conduct that could reasonably be considered inappropriate

---

## Getting Started

### Ways to Contribute

1. **Report Bugs**: Found a bug? Open an issue with details
2. **Suggest Features**: Have an idea? Share it in discussions
3. **Fix Issues**: Check out issues labeled `good first issue`
4. **Improve Documentation**: Help make docs clearer
5. **Write Tests**: Increase test coverage
6. **Review PRs**: Provide feedback on pull requests

### First Time Contributors

Look for issues labeled:
- `good first issue`: Easy tasks for beginners
- `help wanted`: We need community help
- `documentation`: Documentation improvements

---

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- PostgreSQL (optional, for database features)
- Redis (optional, for caching)

### Installation

1. **Fork and clone the repository**

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/deepgrep.git
cd deepgrep

# Add upstream remote
git remote add upstream https://github.com/alwaysvivek/deepgrep.git
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Set up pre-commit hooks**

```bash
pre-commit install
```

5. **Run tests to verify setup**

```bash
pytest tests/ -v
```

---

## How to Contribute

### Reporting Bugs

**Before submitting:**
1. Check if the bug is already reported
2. Verify it's not fixed in the latest version
3. Collect relevant information

**Bug report should include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or screenshots
- Code snippets (if applicable)

**Template:**

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- DeepGrep version: [e.g., 2.0.0]

**Additional context**
Any other relevant information.
```

### Suggesting Features

**Before suggesting:**
1. Check if it's already suggested
2. Consider if it aligns with project goals
3. Think about implementation

**Feature request should include:**
- Clear, descriptive title
- Problem it solves
- Proposed solution
- Alternative solutions considered
- Example use cases

### Working on Issues

1. **Comment on the issue** to express interest
2. **Wait for assignment** or approval
3. **Create a branch** for your work

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

4. **Make your changes** following coding standards
5. **Write tests** for new functionality
6. **Update documentation** if needed
7. **Commit your changes** with clear messages

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### Submitting a PR

1. **Push your branch**

```bash
git push origin feature/your-feature-name
```

2. **Open a pull request** on GitHub

3. **Fill out the PR template**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## Testing
Describe testing performed.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

4. **Address review feedback** promptly

5. **Keep PR focused** - one feature/fix per PR

### Review Process

- Maintainers will review within 48 hours
- Address feedback constructively
- Be patient - reviews take time
- CI/CD must pass before merging

---

## Coding Standards

### Python Style

Follow **PEP 8** with these additions:

```python
# Good
def calculate_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Similarity score between -1 and 1
    """
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
```

### Code Formatting

Use **Black** for formatting:

```bash
black deepgrep tests
```

### Import Sorting

Use **isort**:

```bash
isort deepgrep tests
```

### Type Hints

Use type hints for better code clarity:

```python
from typing import List, Dict, Optional

def search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    pass
```

### Docstrings

Use **Google-style** docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description.
    
    Longer description with more details about the function's
    purpose and behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When input is invalid
    """
    pass
```

---

## Testing Guidelines

### Writing Tests

```python
import pytest
from deepgrep.ml import EmbeddingEngine


class TestEmbeddingEngine:
    """Test embedding engine functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for tests."""
        return EmbeddingEngine("all-MiniLM-L6-v2")
    
    def test_encode_single_text(self, engine):
        """Test encoding a single text."""
        embedding = engine.encode("hello world")
        assert embedding.shape == (1, 384)
    
    def test_encode_multiple_texts(self, engine):
        """Test encoding multiple texts."""
        embeddings = engine.encode(["hello", "world"])
        assert embeddings.shape == (2, 384)
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ml.py -v

# Run with coverage
pytest tests/ -v --cov=deepgrep --cov-report=html

# Run specific test
pytest tests/test_ml.py::TestEmbeddingEngine::test_encode_single_text -v
```

### Test Coverage

Aim for **>80% coverage** for new code:

```bash
pytest tests/ --cov=deepgrep --cov-report=term-missing
```

---

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Include examples in docstrings when helpful
- Keep docstrings up to date with code changes

### User Documentation

Located in `docs/`:
- **README.md**: Project overview
- **TUTORIAL.md**: Step-by-step guide
- **ARCHITECTURE.md**: System design
- **API.md**: API reference

### Updating Documentation

When adding features:
1. Update relevant documentation files
2. Add examples to tutorials
3. Update API reference if needed
4. Add to changelog

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions

### Getting Help

- Check [documentation](docs/)
- Search [existing issues](https://github.com/alwaysvivek/deepgrep/issues)
- Ask in [discussions](https://github.com/alwaysvivek/deepgrep/discussions)

---

## Recognition

Contributors are recognized:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- GitHub contributor badge

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

Feel free to ask questions:
- Open an issue with the `question` label
- Start a discussion on GitHub
- Contact maintainers directly

---

**Thank you for contributing to DeepGrep!** 🎉

Every contribution, no matter how small, helps make DeepGrep better for everyone.
