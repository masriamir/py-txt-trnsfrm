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
- **Heroku** ready for cloud deployment
- **Type hints** throughout the codebase
- **Comprehensive testing** setup with pytest
- **Production-ready** with Gunicorn and optional Nginx

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

2. **Set up virtual environment with uv**
```bash
# Install uv if you haven't already
pip install uv

# Sync dependencies (creates venv automatically)
uv sync
```

3. **Activate virtual environment**
```bash
# On Windows PowerShell
.venv\Scripts\Activate.ps1

# On Windows Command Prompt
.venv\Scripts\activate.bat

# On macOS/Linux
source .venv/bin/activate
```

4. **Run the application**
```bash
# Using the main script
uv run app.py

# Or using Flask development server
uv run flask run

# The app will be available at http://localhost:5000
```

## ☁️ Heroku Deployment

### Quick Deploy

1. **Install Heroku CLI**
    - Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**
```bash
heroku login
```

3. **Deploy using the provided script**
```bash
# Make script executable (macOS/Linux)
chmod +x deploy.sh
./deploy.sh

# Or run commands manually (see Manual Deploy section)
```

### Manual Heroku Deployment

1. **Initialize git repository** (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create Heroku app**
```bash
# Create with auto-generated name
heroku create

# Or create with specific name
heroku create your-app-name
```

3. **Set environment variables**
```bash
heroku config:set FLASK_CONFIG=production
heroku config:set SECRET_KEY="$(openssl rand -base64 32)"

# On Windows PowerShell, generate SECRET_KEY separately:
# $secret = [Convert]::ToBase64String([System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes(32))
# heroku config:set SECRET_KEY="$secret"
```

4. **Deploy**
```bash
git push heroku main
```

5. **Open your app**
```bash
heroku open
```

6. **View logs**
```bash
heroku logs --tail
```

### Heroku Configuration

The app includes several Heroku-specific configurations:

- **Procfile**: Defines how to run the app with Gunicorn
- **.python-version**: Specifies Python 3.13 for uv package manager
- **heroku_config.py**: Heroku-optimized settings
- **Automatic SSL**: Forces HTTPS in production
- **Proxy handling**: Properly handles Heroku's load balancer
- **Logging**: Configured for Heroku's log aggregation

**Note**: This project uses `uv` as the package manager, so Heroku requires a `.python-version` file instead of `runtime.txt`.

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
py-txt-trnsfrm/
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
├── heroku_config.py            # Heroku-specific configuration
├── Procfile                    # Heroku process definition
├── .python-version             # Python version for Heroku (uv)
├── deploy.sh                   # Deployment script
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── nginx.conf                  # Nginx configuration
└── README.md                   # This file
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_transformers.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code with Black
uv run black .

# Lint with flake8
uv run flake8 app tests

# Type checking with mypy
uv run mypy app

# Run all quality checks
uv run black . && uv run flake8 app tests && uv run mypy app && uv run pytest
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_CONFIG` | Configuration mode | `development` | No |
| `SECRET_KEY` | Flask secret key | Auto-generated | Yes (Production) |
| `FLASK_DEBUG` | Enable debug mode | `False` | No |
| `PORT` | Port to run on | `5000` | No |
| `DYNO` | Heroku dyno indicator | N/A | Auto (Heroku) |

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

## 🐛 Debugging

### Local Debugging
```bash
export FLASK_DEBUG=True  # macOS/Linux
$env:FLASK_DEBUG="True"  # Windows PowerShell
uv run app.py
```

### Heroku Debugging
```bash
# View application logs
heroku logs --tail

# Run commands on Heroku
heroku run python -c "from app import create_app; print('App created successfully')"

# Access Heroku bash
heroku run bash
```

## 📊 Performance & Monitoring

### Heroku Monitoring
- Use `heroku logs --tail` for real-time logs
- Monitor dyno usage with `heroku ps`
- Scale dynos with `heroku ps:scale web=2`

### Performance Tips
- Static files cached with CDN headers
- Gunicorn uses multiple workers
- Gzip compression enabled
- Database connection pooling ready

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes and add tests**
4. **Ensure all tests pass**: `uv run pytest`
5. **Format code**: `uv run black .`
6. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Use descriptive commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Amir Masri

## 🎨 Inspiration

This project draws inspiration from early 1990s internet culture, particularly text transformation utilities that were popular on BBSs and early web communities. The aesthetic and functionality pay homage to tools like "methodist toolz" and similar utilities from that era.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/masriamir/py-txt-trnsfrm/issues) page
2. Create a new issue with detailed information
3. For Heroku-specific issues, include `heroku logs --tail` output
4. Provide your environment details (Python version, OS, etc.)

## 🚀 Live Demo

Visit the live application: [https://py-txt-trnsfrm.herokuapp.com](https://py-txt-trnsfrm.herokuapp.com)

## 🌐 Deployment Status

- ✅ Local Development
- ✅ Docker Support
- ✅ Heroku Ready (with uv support)
- ⏳ AWS/GCP Support (Coming Soon)
- ⏳ Kubernetes Manifests (Coming Soon)

---

**Built with ❤️ and nostalgia for the early days of the internet**

**Deploy to Heroku with one click:** [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/masriamir/py-txt-trnsfrm)
