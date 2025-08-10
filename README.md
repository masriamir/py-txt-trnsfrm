# 📡 Retro Text Transformer 📡

A Flask web application for creative text transformations inspired by early 90s internet culture. Transform your text with various fun effects like alternate case, l33t speak, rainbow HTML, and more! Now featuring an accessible pastel color theme system and comprehensive testing infrastructure.

## 🌟 Features

### 🎨 Color Theme System
- **Five Beautiful Pastel Themes**: Pastel Sunset, Mint Fresh, Lavender Dreams, Peach Vibes, Ocean Breeze
- **Theme Picker**: Interactive floating theme selector with visual previews
- **Accessibility-First Design**: WCAG compliant color contrasts and keyboard navigation
- **Persistent Preferences**: Remembers your theme choice across sessions
- **Motion-Sensitive**: Respects user's reduced motion preferences

### Text Transformations
- **Alternate Case**: AlTeRnAtE cAsE while maintaining sentence structure
- **Rainbow HTML**: Generate colorful HTML text
- **L33t Speak**: Convert to h4ck3r sp34k
- **Backwards Text**: Reverse the entire text
- **Upside Down**: Flip text using Unicode characters
- **Stutter Effect**: Add st-st-stuttering effect
- **Zalgo Text**: Light corruption effect with diacritical marks
- **Morse Code**: Convert to dot-dash notation
- **Binary**: Transform to 1s and 0s
- **ROT13**: Classic Caesar cipher
- **SpongeBob Case**: rAnDoM cApItAlIzAtIoN
- **Wave Text**: ~Create~ wave ~effects~
- **Shizzle Speak**: Authentic izzle transformation with sophisticated rules
  - Vowel replacement: "money" → "monizzle"
  - Plural handling: "snitches" → "snitchizzles"
  - Punctuation preservation: "hello!" → "hellizzle!"

### 🧪 Testing & Quality Assurance
- **Comprehensive Test Suite**: Unit, integration, API, and security tests
- **Property-Based Testing**: Automated edge case discovery with Hypothesis
- **Parallel Test Execution**: Fast test runs with pytest-xdist
- **Coverage Reporting**: HTML, XML, and terminal coverage reports (80% minimum)
- **Security Analysis**: Bandit code scanning and Safety dependency vulnerability checks
- **Organized Test Data**: Centralized test data management with faker and pytest-datadir
- **Test Markers**: Organized test categorization (unit, integration, api, smoke, slow, security)

### 🔒 Security Features
- **Automated Security Scanning**: Modern safety scan integration with timeout handling
- **Code Security Analysis**: Bandit static analysis with organized reporting
- **Dependency Vulnerability Scanning**: Safety CLI integration for known vulnerabilities
- **Comprehensive Security Reports**: JSON, HTML, and text formats in organized structure

### Technical Features
- **Python 3.13** with modern async support
- **Flask** web framework with modular structure
- **Bootstrap 5** responsive UI with 90s-inspired accessible design
- **uv** for fast Python package management with organized dependency groups
- **Docker** containerization with multi-stage builds
- **Heroku** ready for cloud deployment
- **Type hints** throughout the codebase
- **Production-ready** with Gunicorn and optional Nginx
- **Modern Testing Stack**: pytest 8.4.1+ with comprehensive plugin ecosystem

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- uv (recommended) or pip
- Docker and Docker Compose (for containerized deployment)
- Heroku CLI (for Heroku deployment)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/masriamir/py-txt-trnsfrm.git
cd py-txt-trnsfrm
```

2. **Install dependencies using uv (recommended)**
```bash
# Install runtime dependencies
uv sync

# Install all development dependencies
uv sync --group dev --group test --group security

# Or install specific groups
uv sync --group dev          # Development tools (black, ruff, mypy)
uv sync --group test         # Testing framework (pytest, coverage, etc.)
uv sync --group security     # Security analysis tools (bandit, safety)
```

3. **Alternative: Install with pip**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

4. **Run the application**
```bash
# Development server
uv run flask --app app run --debug

# Or with Python
python app.py
```

5. **Open in browser**
Navigate to `http://localhost:5000`

## 🧪 Testing & Quality

### Running Tests
```bash
# Run all tests with coverage
uv run pytest

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests
uv run pytest -m api           # API endpoint tests
uv run pytest -m smoke         # Critical functionality tests
uv run pytest -m "not slow"    # Skip long-running tests

# Run tests with specific output
uv run pytest --tb=short       # Short traceback format
uv run pytest -v               # Verbose output
uv run pytest --lf             # Run only failed tests from last run
```

### Security Analysis
```bash
# Run comprehensive security analysis
./run_security_analysis.sh

# Check specific security aspects
uv run bandit -r app/          # Code security analysis
uv run safety scan             # Dependency vulnerability scan
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy app/
```

### Reports
All reports are organized in the `reports/` directory:
- `reports/coverage/html/` - HTML coverage reports
- `reports/coverage/coverage.xml` - XML coverage for CI/CD
- `reports/security/` - Security analysis reports (JSON, HTML, text)

## 📁 Dependency Organization

Dependencies are logically organized into groups:

### Essential Runtime Dependencies
```toml
dependencies = [
    "flask>=3.0.0",
    "gunicorn>=21.2.0", 
    "werkzeug>=3.1.3",
]
```

### Development Tools (`--group dev`)
```toml
dev = [
    "black>=23.0.0",    # Code formatting
    "ruff>=0.1.0",      # Linting and code analysis
    "mypy>=1.5.0",      # Type checking
]
```

### Testing Framework (`--group test`)
```toml
test = [
    "pytest>=8.4.1",              # Testing framework
    "pytest-flask>=1.3.0",        # Flask testing utilities
    "pytest-cov>=6.2.1",          # Coverage reporting
    "pytest-mock>=3.14.1",        # Mocking support
    "pytest-timeout>=2.4.0",      # Timeout handling
    "pytest-xdist>=3.8.0",        # Parallel execution
    "coverage>=7.3.0",            # Coverage analysis
    "faker>=37.5.3",              # Test data generation
    "hypothesis>=6.137.1",        # Property-based testing
    "pytest-datadir>=1.8.0",      # Test data management
    "pytest-httpserver>=1.1.3",   # HTTP server mocking
    "responses>=0.25.8",          # HTTP response mocking
]
```

### Security Analysis (`--group security`)
```toml
security = [
    "bandit>=1.8.6",    # Code security analysis
    "safety>=3.6.0",    # Dependency vulnerability scanning
]
```

## 🎨 Theme System

The application features a comprehensive color theme system:

### Available Themes
- **Pastel Sunset** (default): Warm peachy-pink gradients
- **Mint Fresh**: Cool mint green tones  
- **Lavender Dreams**: Soft purple/violet hues
- **Peach Vibes**: Coral and peach colors
- **Ocean Breeze**: Light blue gradients

### Theme Features
- **Visual Theme Picker**: Click the 🎨 button in the top-right corner
- **Persistent Selection**: Your theme choice is saved and remembered
- **Accessibility**: All themes meet WCAG contrast requirements
- **Keyboard Navigation**: Full keyboard accessibility support
- **Responsive Design**: Adapts to mobile and tablet screens

### Accessibility Features
- High contrast text on all themes
- Support for `prefers-contrast: high` media query
- Respect for `prefers-reduced-motion` settings
- Focus indicators for all interactive elements
- Screen reader friendly with proper ARIA labels

## 🐳 Docker Deployment

### Development with Docker Compose
```bash
# Start development environment
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Docker Build
```bash
# Build production image
docker build -t py-txt-trnsfrm:latest .

# Run production container
docker run -p 5000:5000 py-txt-trnsfrm:latest
```

## ☁️ Heroku Deployment

### Quick Deploy
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/masriamir/py-txt-trnsfrm)

### Manual Deployment
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main

# Open in browser
heroku open
```

## 📊 Project Structure
```
py-txt-trnsfrm/
├── app/                      # Flask application
│   ├── main/                 # Main blueprint
│   ├── static/               # Static assets (CSS, JS)
│   ├── templates/            # Jinja2 templates
│   └── utils/                # Utility modules
├── tests/                    # Comprehensive test suite
│   ├── data/                 # Test data management
│   ├── test_*.py             # Test modules
│   └── security_utils.py     # Security testing utilities
├── reports/                  # Generated reports
│   ├── coverage/             # Coverage reports
│   └── security/             # Security analysis reports
├── pyproject.toml            # Project configuration
├── pytest.ini                # Pytest configuration
├── run_security_analysis.sh  # Security analysis script
└── README.md                 # This file
```

## 🛠️ Development Configuration

### pytest Configuration
- **Minimum Version**: pytest 8.0+
- **Parallel Testing**: Automatic CPU core detection
- **Coverage**: 80% minimum threshold
- **Test Organization**: Comprehensive marker system
- **Report Generation**: HTML, XML, and terminal formats

### Code Quality Standards
- **Black**: Code formatting with 88-character line length
- **Ruff**: Fast Python linter with comprehensive rule set
- **MyPy**: Static type checking for Python 3.13
- **Bandit**: Security-focused static analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`uv sync --group dev --group test --group security`)
4. Make your changes
5. Run tests (`uv run pytest`)
6. Run security analysis (`./run_security_analysis.sh`)
7. Format code (`uv run black .` and `uv run ruff format .`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### Current Features ✅
- ✅ 14 text transformation algorithms
- ✅ Responsive Bootstrap 5 UI
- ✅ Accessible pastel theme system
- ✅ Comprehensive testing infrastructure
- ✅ Security analysis automation
- ✅ Docker containerization
- ✅ Heroku deployment ready

### Planned Features 🚧
- 🚧 Additional text transformations
- 🚧 User preferences persistence
- 🚧 Batch text processing
- 🚧 API rate limiting
- 🚧 Text history/favorites
- 🚧 Export functionality (PDF, etc.)

---

<div align="center">
Made with ❤️ and inspired by the golden age of the internet 🌐
</div>
