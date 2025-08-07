# 📡 Text Transformer Web 📡

A Flask web application for creative text transformations inspired by early 90s internet culture. Transform your text with various fun effects like alternate case, l33t speak, rainbow HTML, and more!

## 🌟 Features

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

### Technical Features
- **Python 3.13** with modern async support
- **Flask** web framework with modular structure
- **Bootstrap 5** responsive UI with retro 90s styling
- **uv** for fast Python package management
- **Docker** containerization with multi-stage builds
- **Type hints** throughout the codebase
- **Comprehensive testing** setup with pytest
- **Production-ready** with Gunicorn and optional Nginx

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- uv (recommended) or pip
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/masriamir/text-transformer-web.git
cd text-transformer-web
```

2. **Set up virtual environment with uv**
```bash
# Install uv if you haven't already
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
# Install main dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

4. **Set environment variables**
```bash
# Create .env file (optional)
echo "FLASK_DEBUG=True" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env
```

5. **Run the application**
```bash
# Using Flask development server
python app.py

# Or using the module
python -m flask run

# The app will be available at http://localhost:5000
```

### Docker Development

1. **Build and run with Docker Compose**
```bash
# Development mode
docker-compose up --build

# Production mode with Nginx
docker-compose --profile production up --build
```

2. **Access the application**
- Development: http://localhost:5000
- Production: http://localhost:80

## 🛠️ Development

### Project Structure
```
text-transformer-web/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── main/                    # Main blueprint
│   │   ├── __init__.py
│   │   └── routes.py            # URL routes
│   ├── static/                  # Static files
│   │   ├── css/style.css        # Retro 90s styling
│   │   └── js/app.js            # Frontend JavaScript
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   └── index.html           # Main page
│   └── utils/                   # Utility modules
│       └── text_transformers.py # Text transformation logic
├── tests/                       # Test suite
├── app.py                       # Application entry point
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── nginx.conf                  # Nginx configuration
└── README.md                   # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_transformers.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black .

# Lint with flake8
flake8 app tests

# Type checking with mypy
mypy app

# Run all quality checks
black . && flake8 app tests && mypy app && pytest
```

### Adding New Transformations

1. **Add transformation method** to `app/utils/text_transformers.py`:
```python
def my_transformation(self, text: str) -> str:
    """Description of what this transformation does."""
    # Your transformation logic here
    return transformed_text
```

2. **Register in the transformations dictionary**:
```python
self.transformations['my_transformation'] = self.my_transformation
```

3. **Add button to template** in `app/templates/index.html`:
```html
<button class="btn btn-outline-primary transform-btn" data-transform="my_transformation">
    🎯 My Transformation
</button>
```

4. **Update JavaScript mapping** in `app/static/js/app.js`:
```javascript
// Add to getTransformationName and getButtonText functions
'my_transformation': 'My Transformation',
'my_transformation': '🎯 My Transformation',
```

## 🐳 Production Deployment

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_CONFIG` | Configuration mode | `development` |
| `SECRET_KEY` | Flask secret key | Generated |
| `FLASK_DEBUG` | Enable debug mode | `False` |
| `PORT` | Port to run on | `5000` |

### Docker Production Deployment

1. **Set production environment variables**:
```bash
export SECRET_KEY="your-very-secure-secret-key-here"
export FLASK_CONFIG="production"
```

2. **Deploy with Docker Compose**:
```bash
# With Nginx reverse proxy
docker-compose --profile production up -d

# Simple single container
docker-compose up -d web
```

3. **View logs**:
```bash
docker-compose logs -f
```

### Manual Production Setup

1. **Install production dependencies**:
```bash
uv pip install -e . --no-dev
```

2. **Set environment variables**:
```bash
export FLASK_CONFIG=production
export SECRET_KEY="your-secret-key"
```

3. **Run with Gunicorn**:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## 🧪 Testing

### Test Structure
- `tests/test_app.py` - Application and route tests
- `tests/test_transformers.py` - Text transformation logic tests
- `tests/conftest.py` - Pytest fixtures and configuration

### Running Specific Tests

```bash
# Test transformations only
pytest tests/test_transformers.py::TestTextTransformer

# Test specific transformation
pytest tests/test_transformers.py::TestTextTransformer::test_alternate_case

# Test with specific markers
pytest -m "not slow"
```

## 🐛 Debugging

### Debug Mode
```bash
export FLASK_DEBUG=True
python app.py
```

### Using Python Debugger
```python
import pdb; pdb.set_trace()  # Add breakpoint anywhere in code
```

### Docker Debugging
```bash
# Run container with bash
docker-compose run web bash

# View container logs
docker-compose logs web

# Execute commands in running container
docker-compose exec web python -c "from app import create_app; print(create_app())"
```

## 📊 Performance

### Optimization Tips
- Static files are served with long cache headers
- Gunicorn uses multiple workers for better concurrency
- Docker images use multi-stage builds for smaller size
- CSS/JS minification in production (configure as needed)

### Monitoring
```bash
# Check application health
curl http://localhost:5000/

# Docker health check
docker-compose ps
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes and add tests**
4. **Ensure all tests pass**: `pytest`
5. **Format code**: `black .`
6. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Use descriptive commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎨 Inspiration

This project draws inspiration from early 1990s internet culture, particularly text transformation utilities that were popular on BBSs and early web communities. The aesthetic and functionality pay homage to tools like "methodist toolz" and similar utilities from that era.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/masriamir/text-transformer-web/issues) page
2. Create a new issue with detailed information
3. Include steps to reproduce any bugs
4. Provide your environment details (Python version, OS, etc.)

## 🚀 Future Enhancements

- [ ] Save/load text transformations
- [ ] User accounts and favorites
- [ ] More transformation options
- [ ] Batch processing
- [ ] API endpoints
- [ ] Mobile app version
- [ ] Plugin system for custom transformations

---

**Built with ❤️ and nostalgia for the early days of the internet**