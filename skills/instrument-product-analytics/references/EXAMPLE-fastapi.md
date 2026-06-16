# PostHog fastapi Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/fastapi

---

## README.md

# PostHog FastAPI Example

A FastAPI application demonstrating PostHog integration for analytics, feature flags, and error tracking.

## Features

- User registration and authentication with cookie-based sessions
- SQLite database persistence with SQLAlchemy
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

5. Open http://localhost:5002 and either:
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

Manual capture for specific critical operations** (`app/routers/api.py`).

```python
try:
    # Critical operation that might fail
    result = process_payment()
except Exception as e:
    # Manually capture this specific exception
    with new_context():
        identify_context(current_user.email)
        event_id = posthog.capture_exception(e)

    return JSONResponse({
        "error": "Operation failed",
        "error_id": event_id,
        "message": f"Error captured in PostHog. Reference ID: {event_id}"
    }, status_code=500)
```

The `/api/test-error` endpoint demonstrates manual exception capture. Use `?capture=true` to capture in PostHog, or `?capture=false` to skip tracking.

## Project Structure

```
basics/fastapi/
├── app/
│   ├── __init__.py              # Package marker
│   ├── config.py                # Pydantic Settings configuration
│   ├── database.py              # SQLAlchemy setup
│   ├── dependencies.py          # FastAPI dependency injection
│   ├── main.py                  # Application factory and lifespan
│   ├── models.py                # User model (SQLAlchemy)
│   ├── routers/
│   │   ├── __init__.py          # Routers package
│   │   ├── main.py              # Page routes (HTML)
│   │   └── api.py               # API endpoints (JSON)
│   └── templates/               # Jinja2 templates
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py                       # Entry point (uvicorn)
```

---

## .env.example

```example
POSTHOG_PROJECT_TOKEN=<ph_project_token>
POSTHOG_HOST=https://us.i.posthog.com
SECRET_KEY=your-secret-key-here
DEBUG=True
POSTHOG_DISABLED=False

```

---

## app/__init__.py

```py
"""FastAPI PostHog example application."""

```

---

## app/config.py

```py
"""FastAPI application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True

    # Database (SQLite like Flask example)
    database_url: str = "sqlite:///./db.sqlite3"

    # PostHog
    posthog_project_token: str = "<ph_project_token>"
    posthog_host: str = "https://us.i.posthog.com"
    posthog_disabled: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

```

---

## app/database.py

```py
"""Database configuration with SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

```

---

## app/dependencies.py

```py
"""Authentication dependencies for FastAPI."""

from typing import Annotated, Optional

from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

settings = get_settings()
serializer = URLSafeSerializer(settings.secret_key)


def get_session_user_id(session_token: Annotated[Optional[str], Cookie()] = None) -> Optional[int]:
    """Extract user ID from session cookie."""
    if not session_token:
        return None
    try:
        data = serializer.loads(session_token)
        return data.get("user_id")
    except BadSignature:
        return None


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[Optional[int], Depends(get_session_user_id)],
) -> Optional[User]:
    """Get the current authenticated user, or None if not authenticated."""
    if user_id is None:
        return None
    return User.get_by_id(db, user_id)


def require_auth(
    current_user: Annotated[Optional[User], Depends(get_current_user)],
) -> User:
    """Require authentication - raises 401 if not authenticated."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user


def create_session_token(user_id: int) -> str:
    """Create a signed session token for the user."""
    return serializer.dumps({"user_id": user_id})


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[Optional[User], Depends(get_current_user)]
RequiredUser = Annotated[User, Depends(require_auth)]
DbSession = Annotated[Session, Depends(get_db)]

```

---

## app/main.py

```py
"""FastAPI application with PostHog integration."""

from contextlib import asynccontextmanager
from pathlib import Path

import posthog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.middleware import PostHogMiddleware
from app.models import User
from app.routers import api, main

settings = get_settings()

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events for startup/shutdown."""
    # Startup: Initialize PostHog
    if not settings.posthog_disabled:
        posthog.api_key = settings.posthog_project_token
        posthog.host = settings.posthog_host
        posthog.debug = settings.debug

    # Initialize database and seed default user
    init_db()
    db = SessionLocal()
    try:
        if not User.get_by_email(db, "admin@example.com"):
            User.create_user(
                db,
                email="admin@example.com",
                password="admin",
                is_staff=True,
            )
    finally:
        db.close()

    yield

    # Shutdown: Flush PostHog events
    if not settings.posthog_disabled:
        posthog.flush()


app = FastAPI(
    title="PostHog FastAPI Example",
    description="Example application demonstrating PostHog integration with FastAPI",
    lifespan=lifespan,
)

app.add_middleware(PostHogMiddleware)

# Include routers
app.include_router(main.router)
app.include_router(api.router, prefix="/api")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Not found"}, status_code=404)
    return templates.TemplateResponse(
        request, "errors/404.html", status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Internal server error"}, status_code=500)
    return templates.TemplateResponse(
        request, "errors/500.html", status_code=500
    )

```

---

## app/middleware.py

```py
"""PostHog middleware for automatic context and user identification.

Uses pure ASGI middleware instead of BaseHTTPMiddleware for better performance/best practices.
"""

from http.cookies import SimpleCookie
from typing import Callable, Optional

from posthog import identify_context, new_context, tag

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import serializer
from app.models import User


class PostHogMiddleware:
    """Pure ASGI middleware that wraps each request in a PostHog context.

    If the user is authenticated, identifies them in the context so routes
    can just call capture() without needing to set up context each time.

    Uses pure ASGI interface for better performance than BaseHTTPMiddleware.
    """

    def __init__(self, app):
        self.app = app
        self.settings = get_settings()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or self.settings.posthog_disabled:
            await self.app(scope, receive, send)
            return

        user = self._get_user_from_scope(scope)

        with new_context():
            if user:
                identify_context(user.email)
                tag("email", user.email)
                tag("is_staff", user.is_staff)

            await self.app(scope, receive, send)

    def _get_user_from_scope(self, scope) -> Optional[User]:
        """Extract authenticated user from session cookie in ASGI scope."""
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode("utf-8")

        if not cookie_header:
            return None

        cookies = SimpleCookie()
        cookies.load(cookie_header)

        session_cookie = cookies.get("session_token")
        if not session_cookie:
            return None

        session_token = session_cookie.value

        try:
            data = serializer.loads(session_token)
            user_id = data.get("user_id")
        except Exception:
            return None

        if not user_id:
            return None

        db = SessionLocal()
        try:
            return User.get_by_id(db, user_id)
        finally:
            db.close()

```

---

## app/models.py

```py
"""User model with SQLite persistence (similar to Flask example)."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Base


class User(Base):
    """User model with SQLite persistence."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Verify the password against the hash."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(
        cls, db: Session, email: str, password: str, is_staff: bool = False
    ) -> "User":
        """Create and save a new user."""
        user = cls(email=email, is_staff=is_staff)
        # nosemgrep: python.django.security.audit.unvalidated-password.unvalidated-password
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_by_id(cls, db: Session, user_id: int) -> Optional["User"]:
        """Get user by ID."""
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def get_by_email(cls, db: Session, email: str) -> Optional["User"]:
        """Get user by email."""
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str) -> Optional["User"]:
        """Authenticate user with email and password."""
        user = cls.get_by_email(db, email)
        if user and user.check_password(password):
            return user
        return None

    def record_login(self, db: Session) -> bool:
        """Record a login and return whether this is the user's first login."""
        is_first_login = self.login_count == 0
        self.login_count += 1
        db.commit()
        return is_first_login

    def update_profile(self, db: Session, name: Optional[str] = None) -> list:
        """Update user profile and return list of changed fields."""
        changed_fields = []
        if name is not None and name != self.name:
            self.name = name
            changed_fields.append("name")
        if changed_fields:
            db.commit()
        return changed_fields

    def __repr__(self) -> str:
        return f"<User {self.email}>"

```

---

## app/routers/__init__.py

```py
"""FastAPI routers package."""

```

---

## app/routers/api.py

```py
"""API endpoints demonstrating PostHog integration patterns."""

from typing import Annotated

import posthog
from fastapi import APIRouter, Cookie, Form, Query
from fastapi.responses import JSONResponse
from posthog import capture

from app.dependencies import RequiredUser

router = APIRouter()

MAX_BURRITO_COUNT = 10000


@router.post("/burrito/consider")
async def consider_burrito(
    current_user: RequiredUser,
    burrito_count: Annotated[int, Cookie()] = 0,
):
    """Track burrito consideration event."""
    safe_count = max(0, min(burrito_count, MAX_BURRITO_COUNT))
    new_count = safe_count + 1

    capture("burrito_considered", properties={"total_considerations": new_count})

    response = JSONResponse({"success": True, "count": new_count})
    response.set_cookie(
        key="burrito_count",
        value=str(new_count),
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/test-error")
async def test_error(
    current_user: RequiredUser,
    capture_param: Annotated[str, Query(alias="capture")] = "true",
):
    """Test endpoint demonstrating manual exception capture in PostHog."""
    should_capture = capture_param.lower() == "true"

    try:
        raise Exception("Test exception from critical operation")
    except Exception as e:
        if should_capture:
            event_id = posthog.capture_exception(e)
            return JSONResponse(
                {
                    "error": "Operation failed",
                    "error_id": event_id,
                    "message": f"Error captured in PostHog. Reference ID: {event_id}",
                },
                status_code=500,
            )
        else:
            return JSONResponse({"error": "Operation failed"}, status_code=500)


@router.post("/trigger-error")
async def trigger_error(
    current_user: RequiredUser,
    error_type: Annotated[str, Form()] = "generic",
):
    """Trigger different error types for testing error tracking."""
    error_messages = {
        "value": "Invalid value provided",
        "key": "Missing required key",
        "generic": "Generic test error",
    }

    safe_error_type = error_type if error_type in error_messages else "generic"
    error_message = error_messages[safe_error_type]

    try:
        if safe_error_type == "value":
            raise ValueError(error_message)
        elif safe_error_type == "key":
            raise KeyError("missing_key")
        else:
            raise Exception(error_message)
    except Exception as e:
        posthog.capture_exception(e)
        capture(
            "error_triggered",
            properties={"error_type": safe_error_type, "error_message": error_message},
        )

        return JSONResponse(
            {
                "success": True,
                "message": "Error captured in PostHog",
                "error": error_message,
            }
        )


@router.post("/reports/activity")
async def generate_activity_report(
    current_user: RequiredUser,
    report_type: Annotated[str, Form()] = "summary",
):
    """Generate user activity report."""
    valid_report_types = {"summary", "detailed", "export"}
    safe_report_type = report_type if report_type in valid_report_types else "summary"

    report_data = {
        "user": current_user.email,
        "name": current_user.name,
        "date_joined": current_user.date_joined.isoformat(),
        "login_count": current_user.login_count,
        "is_staff": current_user.is_staff,
    }

    if safe_report_type == "detailed":
        report_data["account_age_days"] = (
            __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            - current_user.date_joined
        ).days

    row_count = len(report_data)

    capture(
        "report_generated",
        properties={
            "report_type": safe_report_type,
            "row_count": row_count,
            "username": current_user.email,
        },
    )

    return JSONResponse(
        {
            "success": True,
            "report_type": safe_report_type,
            "row_count": row_count,
            "data": report_data,
        }
    )

```

---

## app/routers/main.py

```py
"""Main routes demonstrating PostHog integration patterns."""

from pathlib import Path
from typing import Annotated

import posthog
from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from posthog import capture

from app.dependencies import (
    CurrentUser,
    DbSession,
    RequiredUser,
    create_session_token,
)
from app.models import User

router = APIRouter()

# Setup templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: CurrentUser, db: DbSession):
    """Home/login page."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse(
        request, "home.html", {"current_user": current_user}
    )


@router.post("/", response_class=HTMLResponse)
async def login(
    request: Request,
    db: DbSession,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    """Handle login form submission."""
    user = User.authenticate(db, email, password)

    if user:
        is_new_user = user.record_login(db)
        posthog.identify(user.email, {"email": user.email, "is_staff": user.is_staff})
        posthog.capture(
            user.email,
            "user_logged_in",
            properties={
                "username": user.email,
                "is_new_user": is_new_user,
            },
        )

        # Create session and redirect
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="session_token",
            value=create_session_token(user.id),
            httponly=True,
            samesite="lax",
        )
        return response

    # Login failed
    return templates.TemplateResponse(
        request,
        "home.html",
        {"current_user": None, "error": "Invalid email or password"},
    )


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, current_user: CurrentUser):
    """User registration page."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse(
        request, "signup.html", {"current_user": current_user}
    )


@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    db: DbSession,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirm: Annotated[str, Form()],
):
    """Handle signup form submission."""
    error = None

    if not email or not password:
        error = "Email and password are required"
    elif password != password_confirm:
        error = "Passwords do not match"
    elif User.get_by_email(db, email):
        error = "Email already registered"

    if error:
        return templates.TemplateResponse(
            request, "signup.html", {"current_user": None, "error": error}
        )

    # Create new user
    user = User.create_user(db, email=email, password=password, is_staff=False)

    posthog.identify(user.email, {"email": user.email, "is_staff": user.is_staff})
    posthog.capture(
        user.email,
        "user_signed_up",
        properties={
            "username": user.email,
            "signup_method": "form",
        },
    )

    # Create session and redirect
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="session_token",
        value=create_session_token(user.id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout(current_user: RequiredUser):
    """Logout and capture event."""
    capture("user_logged_out")

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: RequiredUser,
):
    """Dashboard with feature flag demonstration."""
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

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "current_user": current_user,
            "show_new_feature": show_new_feature,
            "feature_config": feature_config,
        },
    )


@router.get("/burrito", response_class=HTMLResponse)
async def burrito(
    request: Request,
    current_user: RequiredUser,
    burrito_count: Annotated[int, Cookie()] = 0,
):
    """Burrito consideration tracker page."""
    return templates.TemplateResponse(
        request,
        "burrito.html",
        {"current_user": current_user, "burrito_count": burrito_count},
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: RequiredUser):
    """User profile page."""
    capture("profile_viewed")

    return templates.TemplateResponse(
        request, "profile.html", {"current_user": current_user}
    )


@router.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    db: DbSession,
    current_user: RequiredUser,
    name: Annotated[str, Form()],
):
    """Handle profile update."""
    fields_changed = current_user.update_profile(db, name=name)

    if fields_changed:
        capture(
            "profile_updated",
            properties={
                "username": current_user.email,
                "fields_changed": fields_changed,
            },
        )

    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "current_user": current_user,
            "success": "Profile updated" if fields_changed else None,
        },
    )

```

---

## app/templates/base.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PostHog FastAPI Example{% endblock %}</title>
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
    {% if current_user %}
    <nav>
        <a href="/dashboard">Dashboard</a>
        <a href="/burrito">Burrito</a>
        <a href="/profile">Profile</a>
        <a href="/logout" style="float: right;">Logout ({{ current_user.email }})</a>
    </nav>
    {% endif %}

    <div class="container">
        {% if error %}
        <div class="messages">
            <div class="message error">{{ error }}</div>
        </div>
        {% endif %}
        {% if success %}
        <div class="messages">
            <div class="message success">{{ success }}</div>
        </div>
        {% endif %}

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

{% block title %}Burrito - PostHog FastAPI Example{% endblock %}

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

{% block title %}Dashboard - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Dashboard</h1>
    <p>Welcome back, {{ current_user.email }}!</p>
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

{% block title %}Page Not Found - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/" class="btn">Go Home</a>
</div>
{% endblock %}

```

---

## app/templates/errors/500.html

```html
{% extends "base.html" %}

{% block title %}Server Error - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong on our end. Please try again later.</p>
    <a href="/" class="btn">Go Home</a>
</div>
{% endblock %}

```

---

## app/templates/home.html

```html
{% extends "base.html" %}

{% block title %}Login - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Welcome to PostHog FastAPI Example</h1>
    <p>This example demonstrates how to integrate PostHog with a FastAPI application.</p>

    <form method="POST">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>

        <label for="password">Password</label>
        <input type="password" id="password" name="password" required>

        <button type="submit">Login</button>
    </form>

    <p style="margin-top: 16px; font-size: 14px; color: #666;">
        Don't have an account? <a href="/signup">Sign up here</a>
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

{% block title %}Profile - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Your Profile</h1>
    <p>This page demonstrates profile updates and report generation with PostHog.</p>

    {% if success %}
    <div class="message success">{{ success }}</div>
    {% endif %}

    <form method="POST" action="/profile">
        <table>
            <tr>
                <th>Email</th>
                <td>{{ current_user.email }}</td>
            </tr>
            <tr>
                <th>Name</th>
                <td>
                    <input type="text" name="name" value="{{ current_user.name or '' }}" placeholder="Enter your name">
                </td>
            </tr>
            <tr>
                <th>Date Joined</th>
                <td>{{ current_user.date_joined.strftime('%Y-%m-%d %H:%M') }}</td>
            </tr>
            <tr>
                <th>Login Count</th>
                <td>{{ current_user.login_count }}</td>
            </tr>
            <tr>
                <th>Staff Status</th>
                <td>{{ 'Yes' if current_user.is_staff else 'No' }}</td>
            </tr>
        </table>
        <button type="submit">Update Profile</button>
    </form>
</div>

<div class="card">
    <h2>Activity Reports</h2>
    <p>Generate a report of your account activity:</p>

    <div style="margin: 20px 0;">
        <button onclick="generateReport('summary')">Summary Report</button>
        <button onclick="generateReport('detailed')">Detailed Report</button>
    </div>

    <div id="report-result" style="display: none;" class="message"></div>
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

async function generateReport(reportType) {
    const resultDiv = document.getElementById('report-result');
    try {
        const formData = new FormData();
        formData.append('report_type', reportType);

        const response = await fetch('/api/reports/activity', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        resultDiv.style.display = 'block';
        resultDiv.className = 'message success';
        resultDiv.innerHTML = '<strong>' + data.report_type + ' report generated</strong> (' + data.row_count + ' rows)<br><pre>' + JSON.stringify(data.data, null, 2) + '</pre>';
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

{% block title %}Sign Up - PostHog FastAPI Example{% endblock %}

{% block content %}
<div class="card">
    <h1>Create an Account</h1>
    <p>Sign up to explore the PostHog FastAPI integration example.</p>

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
        Already have an account? <a href="/">Login here</a>
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
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
posthog>=3.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
jinja2>=3.0.0
python-multipart>=0.0.9
werkzeug>=3.0.0
itsdangerous>=2.0.0

```

---

## run.py

```py
"""Development server entry point."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5002, reload=True)

```

---

