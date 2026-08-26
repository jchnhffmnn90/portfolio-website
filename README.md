# Portfolio Website

A modern, dynamic portfolio website built with Python and Django. It automatically synchronizes public repositories from GitHub and presents them in a clean project showcase.

## Features

- **GitHub Integration**: Automatically fetches and synchronizes public GitHub repositories.
- **Projects Showcase**: Displays projects with metadata (stars, forks, topics, primary language, repository and demo URLs).
- **Admin Management**: Easily manage, feature, or hide individual projects via the Django Admin interface.
- **Modern Architecture**: Clean separation of apps (`pages`, `projects`), typed services, and modular templates.
- **Testing & Quality Assurance**: Pytest test suite with `pytest-django` and code linting/formatting with `ruff`.

## Tech Stack

- **Backend**: Python 3.12+, Django 5.x
- **Database**: SQLite (default / development)
- **Styling**: Modern responsive CSS
- **Testing & Tooling**: `pytest`, `pytest-django`, `ruff`

## Getting Started

### Prerequisites

- Python 3.12 or newer
- `pip` and `virtualenv`

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:jchnhffmnn90/portfolio-website.git
   cd portfolio-website
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   *Update `.env` with your GitHub username and optional personal access token for higher API rate limits.*

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Development & Testing

### Running Tests

Execute the test suite using `pytest`:
```bash
pytest
```

### Linting & Formatting

Check code quality with `ruff`:
```bash
ruff check .
```

## Project Structure

```text
├── config/              # Django project settings and root routing
├── pages/               # Static and landing pages (Home, About, etc.)
├── projects/            # Project showcase, models, and GitHub sync service
│   ├── migrations/      # Database migrations
│   ├── services/        # GitHub API client and integration logic
│   ├── models.py        # Project model
│   ├── admin.py         # Django admin configuration
│   └── tests.py         # Unit and integration tests
├── static/              # Static assets (CSS, JS, images)
├── templates/           # Shared HTML templates
├── manage.py            # Django CLI management script
├── pytest.ini           # Pytest configuration
├── pyproject.toml       # Ruff and tooling configuration
└── requirements.txt     # Python dependencies
```

## License

This project is licensed under the MIT License.
