# PostHog flask Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/flask

---

## README.md

# PostHog Flask Example

A Flask application demonstrating PostHog integration for analytics, feature flags, and error tracking.

## Features

- User registration and authentication with Flask-Login
- SQLite database persistence with Flask-SQLAlchemy
- User identification and property tracking
- Custom event tracking
- Feature flags with payload support
- Error tracking with manual exception capture

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your PostHog project key
   ```

4. Run the application:
   ```bash
   python run.py
   ```

5. Open http://localhost:5001 and either:
   - Login with default credentials: `admin@example.com` / `admin`
   - Or click "Sign up here" to create a new account

## PostHog Integration Points

### User Registration
New users are identified and tracked on signup using the context-based API:
```python
with new_context():
    identify_context(user.email)
    tag('email', user.email)
    tag('is_staff', user.is_staff)
    capture('user_signed_up', properties={'signup_method': 'form'})
```

### User Identification
Users are identified on login with their properties:
```python
with new_context():
    identify_context(user.email)
    tag('email', user.email)
    tag('is_staff', user.is_staff)
    capture('user_logged_in', properties={'login_method': 'password'})
```

### Event Tracking
Custom events are captured throughout the app:
```python
with new_context():
    identify_context(current_user.email)
    capture('burrito_considered', properties={'total_considerations': count})
```

### Feature Flags
The dashboard demonstrates feature flag checking:
```python
show_new_feature = posthog.feature_enabled(
    'new-dashboard-feature',
    current_user.email,
    person_properties={'email': current_user.email, 'is_staff': current_user.is_staff}
)
feature_config = posthog.get_feature_flag_payload('new-dashboard-feature', current_user.email)
```

### Error Tracking

The example demonstrates two approaches to error tracking:

Manual capture for specific critical operations** (`app/api/routes.py`).

```python
try:
    # Critical operation that might fail
    result = process_payment()
except Exception as e:
    # Manually capture this specific exception
    with new_context():
        identify_context(current_user.email)
        event_id = posthog.capture_exception(e)

    return jsonify({
        "error": "Operation failed",
        "error_id": event_id,
        "message": f"Error captured in PostHog. Reference ID: {event_id}"
    }), 500
```

The `/api/test-error` endpoint demonstrates manual exception capture. Use `?capture=true` to capture in PostHog, or `?capture=false` to skip tracking.

## Project Structure

```
basics/flask/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Extension instances
│   ├── models.py                # User model (SQLAlchemy)
│   ├── main/
│   │   ├── __init__.py          # Main blueprint
│   │   └── routes.py            # View functions
│   ├── templates/               # HTML templates
│   └── api/
│       ├── __init__.py          # API blueprint
│       └── routes.py            # API endpoints
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py                       # Entry point
```

---

## .env.example

```example
POSTHOG_PROJECT_TOKEN=<ph_project_token>
POSTHOG_HOST=https://us.i.posthog.com
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
POSTHOG_DISABLED=False

```

---

## app/__init__.py

```py
"""Flask application factory."""

import posthog
from flask import Flask, g, jsonify, render_template, request
from flask_login import current_user
from posthog import identify_context, new_context
from werkzeug.exceptions import HTTPException

from app.config import config
from app.extensions import db, login_manager


def create_app(config_name="default"):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Initialize PostHog
    if not app.config["POSTHOG_DISABLED"]:
        posthog.api_key = app.config["POSTHOG_PROJECT_TOKEN"]
        posthog.host = app.config["POSTHOG_HOST"]
        posthog.debug = app.config["DEBUG"]

    # Import models after db is initialized
    from app.models import User

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Simple error handlers - no automatic PostHog capture
    # Capture exceptions manually only where it makes sense (e.g., test endpoints)
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Not found"}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Internal server error"}), 500
        return render_template('errors/500.html'), 500

    # Register blueprints
    from app.api import api_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Create database tables and seed default admin user
    with app.app_context():
        db.create_all()
        if not User.get_by_email("admin@example.com"):
            User.create_user(
                email="admin@example.com",
                password="admin",
                is_staff=True,
            )

    return app

```

---

## app/api/__init__.py

```py
"""API blueprint registration."""

from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api import routes  # noqa: E402, F401

```

---

## app/api/routes.py

```py
"""API endpoints demonstrating PostHog integration patterns."""

import posthog
from flask import jsonify, request, session
from flask_login import current_user, login_required
from posthog import capture, identify_context, new_context

from app.api import api_bp


@api_bp.route("/burrito/consider", methods=["POST"])
@login_required
def consider_burrito():
    """Track burrito consideration event."""
    # Increment session counter
    burrito_count = session.get("burrito_count", 0) + 1
    session["burrito_count"] = burrito_count

    # PostHog: Capture custom event
    with new_context():
        identify_context(current_user.email)
        capture("burrito_considered", properties={"total_considerations": burrito_count})

    return jsonify({"success": True, "count": burrito_count})


@api_bp.route("/test-error", methods=["POST"])
@login_required
def test_error():
    """Test endpoint demonstrating manual exception capture in PostHog.

    Shows how to intentionally capture specific errors in PostHog.
    Use this pattern for critical operations where you want error tracking.

    Query params:
    - capture: "true" to capture the exception in PostHog, "false" to just raise it
    """
    should_capture = request.args.get("capture", "true").lower() == "true"

    try:
        # Simulate a critical operation failure
        raise Exception("Test exception from critical operation")
    except Exception as e:
        if should_capture:
            # Manually capture this specific exception in PostHog
            with new_context():
                identify_context(current_user.email)
                event_id = posthog.capture_exception(e)

            return jsonify({
                "error": "Operation failed",
                "error_id": event_id,
                "message": f"Error captured in PostHog. Reference ID: {event_id}"
            }), 500
        else:
            # Just return error without PostHog capture
            return jsonify({"error": str(e)}), 500



```

---

## app/config.py

```py
"""Flask application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

    # Database configuration (SQLite like Django example)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PostHog configuration
    POSTHOG_PROJECT_TOKEN = os.environ.get("POSTHOG_PROJECT_TOKEN", "<ph_project_token>")
    POSTHOG_HOST = os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com")
    POSTHOG_DISABLED = os.environ.get("POSTHOG_DISABLED", "False").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

```

---

## app/extensions.py

```py
"""Flask extensions initialized without binding to app."""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "main.home"
login_manager.login_message = "Please log in to access this page."

```

---

## app/main/__init__.py

```py
"""Main blueprint registration."""

from flask import Blueprint

main_bp = Blueprint("main", __name__, template_folder="../templates")

from app.main import routes  # noqa: E402, F401

```

---

## app/main/routes.py

```py
"""Core view functions demonstrating PostHog integration patterns."""

import posthog
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from posthog import capture, identify_context, new_context, tag

from app.main import main_bp
from app.models import User


@main_bp.route("/", methods=["GET", "POST"])
def home():
    """Home/login page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.authenticate(email, password)
        if user:
            login_user(user)

            # PostHog: Identify user and capture login event
            with new_context():
                identify_context(user.email)

                # Set person properties (PII goes in tag, not capture)
                tag("email", user.email)
                tag("is_staff", user.is_staff)
                tag("date_joined", user.date_joined.isoformat())

                capture("user_logged_in", properties={"login_method": "password"})

            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("home.html")


@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # Validation
        if not email or not password:
            flash("Email and password are required", "error")
        elif password != password_confirm:
            flash("Passwords do not match", "error")
        elif User.get_by_email(email):
            flash("Email already registered", "error")
        else:
            # Create new user
            user = User.create_user(
                email=email,
                password=password,
                is_staff=False,
            )

            # PostHog: Identify new user and capture signup event
            with new_context():
                identify_context(user.email)

                tag("email", user.email)
                tag("is_staff", user.is_staff)
                tag("date_joined", user.date_joined.isoformat())

                capture("user_signed_up", properties={"signup_method": "form"})

            # Log the user in
            login_user(user)
            flash("Account created successfully!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("signup.html")


@main_bp.route("/logout")
@login_required
def logout():
    """Logout and capture event."""
    # PostHog: Capture logout event before session ends
    with new_context():
        identify_context(current_user.email)
        capture("user_logged_out")

    logout_user()
    return redirect(url_for("main.home"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard with feature flag demonstration."""
    # PostHog: Capture dashboard view
    with new_context():
        identify_context(current_user.email)
        capture("dashboard_viewed", properties={"is_staff": current_user.is_staff})

    # Check feature flag
    show_new_feature = posthog.feature_enabled(
        "new-dashboard-feature",
        current_user.email,
        person_properties={
            "email": current_user.email,
            "is_staff": current_user.is_staff,
        },
    )

    # Get feature flag payload
    feature_config = posthog.get_feature_flag_payload(
        "new-dashboard-feature", current_user.email
    )

    return render_template(
        "dashboard.html",
        show_new_feature=show_new_feature,
        feature_config=feature_config,
    )


@main_bp.route("/burrito")
@login_required
def burrito():
    """Burrito consideration tracker page."""
    burrito_count = session.get("burrito_count", 0)
    return render_template("burrito.html", burrito_count=burrito_count)


@main_bp.route("/profile")
@login_required
def profile():
    """User profile page."""
    # PostHog: Capture profile view
    with new_context():
        identify_context(current_user.email)
        capture("profile_viewed")

    return render_template("profile.html")

```

---

## app/models.py

```py
"""User model with SQLite persistence (similar to Django's auth.User)."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """User model with SQLite persistence."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the hash."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(cls, email, password, is_staff=False):
        """Create and save a new user."""
        user = cls(email=email, is_staff=is_staff)
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID."""
        return cls.query.get(int(user_id))

    @classmethod
    def get_by_email(cls, email):
        """Get user by email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user with email and password."""
        user = cls.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    def __repr__(self):
        return f"<User {self.email}>"

```

---

## app/templates/base.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PostHog Flask Example{% endblock %}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        nav {
            background: #1d4ed8;
            padding: 15px 20px;
            margin-bottom: 30px;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin-right: 20px;
        }
        nav a:hover {
            text-decoration: underline;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            margin-bottom: 15px;
            color: #1d4ed8;
        }
        button, .btn {
            background: #1d4ed8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            display: inline-block;
            text-decoration: none;
        }
        button:hover, .btn:hover {
            background: #1e40af;
        }
        button.danger {
            background: #dc2626;
        }
        button.danger:hover {
            background: #b91c1c;
        }
        input {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .messages {
            margin-bottom: 20px;
        }
        .message {
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .message.error {
            background: #fee2e2;
            color: #dc2626;
        }
        .message.success {
            background: #d1fae5;
            color: #059669;
        }
        .feature-flag {
            background: #fef3c7;
            border: 2px dashed #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
        }
        .count {
            font-size: 48px;
            font-weight: bold;
            color: #1d4ed8;
            text-align: center;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8fafc;
            font-weight: 600;
        }
    </style>
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav>
        <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
        <a href="{{ url_for('main.burrito') }}">Burrito</a>
        <a href="{{ url_for('main.profile') }}">Profile</a>
        <a href="{{ url_for('main.logout') }}" style="float: right;">Logout ({{ current_user.email }})</a>
    </nav>
    {% endif %}

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
            <div class="messages">
                {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    {% block scripts %}{% endblock %}
</body>
</html>

```

---

## app/templates/burrito.html

```html
{% extends "base.html" %}

{% block title %}Burrito - PostHog Flask Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Burrito Consideration Tracker</h1>
    <p>This page demonstrates custom event tracking with PostHog.</p>

    <div class="count" id="burrito-count">{{ burrito_count }}</div>
    <p style="text-align: center; color: #666;">Times you've considered a burrito</p>

    <div style="text-align: center; margin-top: 20px;">
        <button onclick="considerBurrito()">Consider a Burrito</button>
    </div>
</div>

<div class="card">
    <h3>Code Example</h3>
    <pre>
# API endpoint captures the event
with new_context():
    identify_context(current_user.email)
    capture('burrito_considered', properties={
        'total_considerations': burrito_count
    })</pre>
</div>
{% endblock %}

{% block scripts %}
<script>
async function considerBurrito() {
    try {
        const response = await fetch('/api/burrito/consider', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            document.getElementById('burrito-count').textContent = data.count;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
</script>
{% endblock %}

```

---

## app/templates/dashboard.html

```html
{% extends "base.html" %}

{% block title %}Dashboard - PostHog Flask Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Dashboard</h1>
    <p>Welcome back, {{ current_user.username }}!</p>
</div>

<div class="card">
    <h2>Feature Flags</h2>

    {% if show_new_feature %}
    <div class="feature-flag">
        <strong>New Feature Enabled!</strong>
        <p>You're seeing this because the <code>new-dashboard-feature</code> flag is enabled for you.</p>
        {% if feature_config %}
        <p><strong>Feature Configuration:</strong></p>
        <pre>{{ feature_config | tojson(indent=2) }}</pre>
        {% endif %}
    </div>
    {% else %}
    <p>The <code>new-dashboard-feature</code> flag is not enabled for your account.</p>
    {% endif %}

    <h3 style="margin-top: 20px;">Code Example</h3>
    <pre>
# Check if feature flag is enabled
show_new_feature = posthog.feature_enabled(
    'new-dashboard-feature',
    user_id,
    person_properties={
        'email': current_user.email,
        'is_staff': current_user.is_staff
    }
)

# Get feature flag payload
feature_config = posthog.get_feature_flag_payload(
    'new-dashboard-feature',
    user_id
)</pre>
</div>
{% endblock %}

```

---

## app/templates/errors/404.html

```html
{% extends "base.html" %}

{% block title %}404 - Page Not Found{% endblock %}

{% block content %}
<div class="card" style="text-align: center; padding: 60px 20px;">
    <h1 style="font-size: 72px; color: #dc2626; margin-bottom: 10px;">404</h1>
    <h2 style="color: #333; margin-bottom: 20px;">Page Not Found</h2>
    <p style="font-size: 18px; color: #666; margin-bottom: 30px;">
        The page you're looking for doesn't exist or has been moved.
    </p>

    {% if error_id %}
    <div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin: 30px 0;">
        <p style="color: #92400e; margin-bottom: 5px; font-weight: 600;">Error Reference ID:</p>
        <code style="background: #fff; padding: 5px 10px; border-radius: 4px; font-family: monospace; color: #1e40af;">{{ error_id }}</code>
        <p style="color: #92400e; margin-top: 10px; font-size: 14px;">
            Share this ID with support if you need assistance.
        </p>
    </div>
    {% endif %}

    <div style="margin-top: 40px;">
        <a href="{{ url_for('main.home') }}" class="btn" style="margin-right: 10px;">Go to Home</a>
        {% if current_user.is_authenticated %}
        <a href="{{ url_for('main.dashboard') }}" class="btn">Go to Dashboard</a>
        {% endif %}
    </div>
</div>
{% endblock %}

```

---

## app/templates/errors/500.html

```html
{% extends "base.html" %}

{% block title %}500 - Internal Server Error{% endblock %}

{% block content %}
<div class="card" style="text-align: center; padding: 60px 20px;">
    <h1 style="font-size: 72px; color: #dc2626; margin-bottom: 10px;">500</h1>
    <h2 style="color: #333; margin-bottom: 20px;">Internal Server Error</h2>
    <p style="font-size: 18px; color: #666; margin-bottom: 30px;">
        Something went wrong on our end. We've been notified and are looking into it.
    </p>

    {% if error_id %}
    <div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin: 30px 0;">
        <p style="color: #92400e; margin-bottom: 5px; font-weight: 600;">Error Reference ID:</p>
        <code style="background: #fff; padding: 5px 10px; border-radius: 4px; font-family: monospace; color: #1e40af;">{{ error_id }}</code>
        <p style="color: #92400e; margin-top: 10px; font-size: 14px;">
            Share this ID with support if you need assistance. This error has been logged in PostHog.
        </p>
    </div>
    {% endif %}

    {% if error and config.DEBUG %}
    <div style="background: #fee2e2; border: 1px solid #dc2626; border-radius: 8px; padding: 15px; margin: 30px 0; text-align: left;">
        <p style="color: #7f1d1d; margin-bottom: 5px; font-weight: 600;">Debug Information:</p>
        <code style="background: #fff; padding: 10px; border-radius: 4px; font-family: monospace; color: #dc2626; display: block; overflow-x: auto;">{{ error }}</code>
    </div>
    {% endif %}

    <div style="margin-top: 40px;">
        <a href="{{ url_for('main.home') }}" class="btn" style="margin-right: 10px;">Go to Home</a>
        {% if current_user.is_authenticated %}
        <a href="{{ url_for('main.dashboard') }}" class="btn">Go to Dashboard</a>
        {% endif %}
    </div>
</div>
{% endblock %}

```

---

## app/templates/home.html

```html
{% extends "base.html" %}

{% block title %}Login - PostHog Flask Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Welcome to PostHog Flask Example</h1>
    <p>This example demonstrates how to integrate PostHog with a Flask application.</p>

    <form method="POST">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" required>

        <button type="submit">Login</button>
    </form>

    <p style="margin-top: 16px; font-size: 14px; color: #666;">
        Don't have an account? <a href="{{ url_for('main.signup') }}">Sign up here</a>
    </p>
    <p style="font-size: 14px; color: #666;">
        <strong>Tip:</strong> Default credentials are admin@example.com/admin
    </p>
</div>

<div class="card">
    <h2>Features Demonstrated</h2>
    <ul style="margin-left: 20px; color: #666;">
        <li>User registration and identification</li>
        <li>Event tracking</li>
        <li>Feature flags</li>
        <li>Error tracking</li>
        <li>Group analytics</li>
    </ul>
</div>
{% endblock %}

```

---

## app/templates/profile.html

```html
{% extends "base.html" %}

{% block title %}Profile - PostHog Flask Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Your Profile</h1>
    <p>This page demonstrates error tracking with PostHog.</p>

    <table>
        <tr>
            <th>Email</th>
            <td>{{ current_user.email }}</td>
        </tr>
        <tr>
            <th>Date Joined</th>
            <td>{{ current_user.date_joined.strftime('%Y-%m-%d %H:%M') }}</td>
        </tr>
        <tr>
            <th>Staff Status</th>
            <td>{{ 'Yes' if current_user.is_staff else 'No' }}</td>
        </tr>
    </table>
</div>

<div class="card">
    <h2>Error Tracking Demo</h2>
    <p>Click a button to trigger an error and see it captured in PostHog:</p>

    <div style="margin: 20px 0;">
        <button class="danger" onclick="triggerError('value')">
            Trigger ValueError
        </button>
        <button class="danger" onclick="triggerError('key')">
            Trigger KeyError
        </button>
        <button class="danger" onclick="triggerError('generic')">
            Trigger Generic Error
        </button>
    </div>

    <div id="error-result" style="display: none;" class="message"></div>
</div>

<div class="card">
    <h3>Code Example</h3>
    <pre>
try:
    raise ValueError('Invalid value provided')
except Exception as e:
    # Capture exception and event with user context
    with new_context():
        identify_context(current_user.email)
        posthog.capture_exception(e)
        capture('error_triggered', properties={
            'error_type': 'value',
            'error_message': str(e)
        })</pre>
</div>
{% endblock %}

{% block scripts %}
<script>
async function triggerError(errorType) {
    const resultDiv = document.getElementById('error-result');
    try {
        const formData = new FormData();
        formData.append('error_type', errorType);

        const response = await fetch('/api/trigger-error', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        resultDiv.style.display = 'block';
        resultDiv.className = 'message ' + (data.success ? 'success' : 'error');
        resultDiv.textContent = data.message + ': ' + data.error;
    } catch (error) {
        console.error('Error:', error);
        resultDiv.style.display = 'block';
        resultDiv.className = 'message error';
        resultDiv.textContent = 'Request failed: ' + error.message;
    }
}
</script>
{% endblock %}

```

---

## app/templates/signup.html

```html
{% extends "base.html" %}

{% block title %}Sign Up - PostHog Flask Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Create an Account</h1>
    <p>Sign up to explore the PostHog Flask integration example.</p>

    <form method="POST">
        <label for="email">Email *</label>
        <input type="email" id="email" name="email" required>

        <label for="password">Password *</label>
        <input type="password" id="password" name="password" required>

        <label for="password_confirm">Confirm Password *</label>
        <input type="password" id="password_confirm" name="password_confirm" required>

        <button type="submit">Sign Up</button>
    </form>

    <p style="margin-top: 16px; font-size: 14px; color: #666;">
        Already have an account? <a href="{{ url_for('main.home') }}">Login here</a>
    </p>
</div>

<div class="card">
    <h2>PostHog Integration</h2>
    <p>When you sign up, the following PostHog events are captured:</p>
    <ul style="margin-left: 20px; color: #666;">
        <li><code>identify_context()</code> - Associates your email with the context</li>
        <li><code>tag()</code> - Sets person properties (email, etc.)</li>
        <li><code>user_signed_up</code> event - Tracks the signup action</li>
    </ul>

    <h3 style="margin-top: 20px;">Code Example</h3>
    <pre>
# After creating the user
with new_context():
    identify_context(user.email)

    tag('email', user.email)
    tag('is_staff', user.is_staff)
    tag('date_joined', user.date_joined.isoformat())

    capture('user_signed_up', properties={'signup_method': 'form'})</pre>
</div>
{% endblock %}

```

---

## requirements.txt

```txt
Flask>=3.1.0
Flask-Login>=0.6.3
Flask-SQLAlchemy>=3.1.0
python-dotenv>=1.0.0
posthog>=3.0.0
Werkzeug>=3.0.0

```

---

## run.py

```py
"""Development server entry point."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=5001)

```

---

