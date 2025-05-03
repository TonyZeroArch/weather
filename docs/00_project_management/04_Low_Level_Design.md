# Low-Level Design Document

### 📑 Low-Level Design Index

1. **Introduction**

   - Scope of low-level design
   - How it supports the high-level architecture

2. **Flask Application Structure**

   - Application factory pattern
   - Blueprint registration
   - App config loading

3. **Routing and View Logic**

   - Route definitions and HTTP methods
   - Request handling flow
   - Error handling at route level

4. **Service Layer Design**

   - Weather Service
   - Location Service
   - Unit Conversion Service
   - Repository Layer

5. **Database Design Details**

   - SQLAlchemy models with fields, types, and relationships
   - Caching expiration rules
   - Migration strategy

6. **Template and Static File Structure**

   - Template file structure (base.html, components)
   - Static resource layout (CSS, JS)
   - Rendering flow with Jinja2

7. **Frontend Interaction Logic**

   - JavaScript for dynamic elements
   - Fetching data via APIs
   - Handling form submissions and loading states

8. **Configuration and Environment**

   - `config.py` structure for DEV, TEST, PROD

   - Environment variable usage

9. **Testing Hooks and Coverage**

   9.1 **Test Locations and Dependencies**

   - Directory structure for all test types
   - Required testing packages

     9.2 **Unit Testing**

   - Structure and examples
   - Mocking services and external APIs

     9.3 **Integration Testing**

   - Testing module interactions (DB, Cache, Services)

     9.4 **System Testing**

   - End-to-End Testing (Selenium, Playwright)
   - Performance Testing (Locust)
   - Security Testing (Bandit)

     9.5 **Acceptance Testing**

   - Robot Framework scenarios and structure

     9.6 **Test Coverage Metrics**

   - Coverage commands and thresholds

     9.7 **CI/CD Integration**

   - Test automation in GitHub Actions

10. **Error Messages and Logging**
    10.1 **Centralized Error Format**
    10.2 **Logging Strategy and Format**
    10.3 **Log File Output (Production Environment)**

11. **Session and Unit Preference Handling**
    11.1 **How Unit Choices Persist During Session**
    11.2 **Data Passed Between Pages**
    11.3 **Best Practices for Unit Handling**

12. **Security Considerations**
    12.1 **Input Validation**  
    12.2 **Protection Against Injection/XSS**  
    12.3 **Secure Config Secrets**

---

## 1. Introduction

### 1.1 Purpose of the Low-Level Design

The Low-Level Design (LLD) document translates the high-level architecture of the Real-Time Weather Dashboard Web Application into detailed technical specifications. It outlines the internal module logic, data handling processes, route definitions, database schema, service responsibilities, and testing touchpoints, serving as a blueprint for developers to implement and maintain the system.

This document ensures:

- Each component’s logic is clearly defined and traceable.
- All external API integrations are handled consistently.
- Frontend-backend interaction is seamless.
- The system is testable, scalable, and ready for deployment.

---

### 1.2 Scope

The LLD focuses on the following functional and technical components:

- Flask app initialization and structure
- RESTful route handling and request logic
- Modular service design (weather, location, units, repository)
- Database and caching schema with SQLAlchemy and Redis
- Jinja2 templates and static file mapping
- JavaScript-driven frontend behavior
- Test strategies and automation hooks
- Config/environment separation
- Error handling and security practices

This design is tailored for a Flask web application using Jinja2 templates and deployed on AWS EC2, with optional React frontend extensibility.

---

### 1.3 Audience

This document is intended for:

- Developers building the backend and frontend components
- QA engineers writing tests and automation
- DevOps and deployment engineers configuring infrastructure
- Future maintainers and contributors to the codebase

---

## 2. Flask Application Structure

### 2.1 Technical Architecture Diagram

```mermaid
graph TD
    A[Browser/Frontend] -->|HTTP Requests with JSON| B[Flask Server/Routes]

    %% Location flow
    B -->|Get Location Data| D[Location API]
    D -->|Query| E[Nominatim External API]
    E -->|Return Coordinates| D

    %% Weather flow
    B -->|Get Weather Data| F[Weather API]
    F -->|Check Cache| K[Redis Cache]
    F -->|Query if needed| G[Open-Meteo External API]
    G -->|Return Weather Data| F
    F -->|Store/Retrieve| I[Weather Repository API]

    %% Units and DB
    B -->|Convert Units| H[Units Conversion API]
    I -->|Store/Retrieve| J[MySQL Database]

    %% Response flow
    B -->|Return HTML| A
```

---

### 2.2 Application Factory Pattern

The app uses the **factory pattern** for initialization, enabling environment-based configuration and test isolation.

#### File: `app/__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
from .routes import main as main_blueprint

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)

    app.register_blueprint(main_blueprint)

    return app
```

---

### 2.3 Folder Structure Overview

```
app/
├── __init__.py              # Application factory
├── routes/                  # Route definitions (Blueprints)
├── controllers/             # View logic (calls services, returns responses)
├── services/                # Internal APIs (weather, location, unit conversion)
├── models/                  # SQLAlchemy models for MySQL
├── templates/               # Jinja2 HTML templates
├── static/                  # Static assets (CSS, JS, images)
├── utils/                   # Helper functions
└── config.py                # Configuration for environments
```

---

### 2.4 Blueprint Registration

Routes are modularized using Flask Blueprints.

#### File: `app/routes/__init__.py`

```python
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views  # Load route handlers
```

In `create_app()`, the blueprint is registered as:

```python
app.register_blueprint(main_blueprint)
```

---

### 2.5 Configuration Management

All runtime and environment-specific settings are managed via `config.py` and `.env` variables. These are essential for running the Flask server locally and in production on AWS.

#### File: `app/config.py`

```python
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@mysql_host/weather_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    API_TIMEOUT = 5
```

> 🔒 Note: MySQL will be hosted on a **separate machine**, possibly on AWS RDS. Ensure `mysql_host` points to that machine’s private IP or endpoint.

---

### 2.6 App Entrypoint

The `run.py` file is used to start the development server.

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

For production (e.g., with Gunicorn on AWS EC2):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 3. Routing and View Logic

---

### 3.1 Route Definitions and HTTP Methods

| Route                   | Method    | Description                    | Template        |
| ----------------------- | --------- | ------------------------------ | --------------- |
| `/`                     | GET       | Home page with current weather | `home.html`     |
| `/forecast/<city>`      | GET       | 7-day forecast view            | `forecast.html` |
| `/hourly/<city>/<date>` | GET       | Hourly forecast for today      | `hourly.html`   |
| `/settings`             | GET, POST | Unit preference form           | `settings.html` |
| `/error`                | GET       | Error fallback page            | `error.html`    |
| `/api/weather`          | GET       | Returns JSON of weather data   | –               |
| `/api/location`         | GET       | Returns JSON coordinates       | –               |

---

### 3.2 Request Handling Flow

Each route is implemented in the `main` Blueprint under `app/routes/views.py`. Here's how each page handles its logic:

#### `/` – Home Page

```python
@main.route('/')
def home():
    # Renders home.html UI with static structure
    return render_template('home.html')
```

#### `/forecast/<city>`

```python
@main.route('/forecast/<city>')
def forecast(city):
    try:
        forecast_data = weather_service.get_7_day_forecast(city)
        return render_template('forecast.html', city=city, forecast=forecast_data)
    except Exception as e:
        current_app.logger.error(f"Forecast error: {e}")
        return redirect(url_for('main.error'))
```

#### `/hourly/<city>`

```python
@main.route('/hourly/<city>/<date>')
def hourly(city,date = None):
    if date is None:
        date = "today"

    try:
        date = datetime.now().strftime('%Y-%m-%d')
        hourly_data = weather_service.get_hourly_forecast(city, date)
        return render_template('hourly.html', city=city, date=date, hourly_data=hourly_data)
    except Exception as e:
        current_app.logger.error(f"Hourly error: {e}")
        return redirect(url_for('main.error'))
```

#### `/settings`

```python
@main.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['temp_unit'] = request.form.get('temp_unit')
        session['wind_unit'] = request.form.get('wind_unit')
        session['precip_unit'] = request.form.get('precip_unit')
        return redirect(url_for('main.settings'))

    return render_template('settings.html')
```

#### `/error`

```python
@main.route('/error')
def error():
    return render_template('error.html')
```

---

#### `/api/weather`

```python
@main.route('/api/weather')
def api_weather():
    city = request.args.get('city')
    try:
        data = weather_service.get_combined_weather(city)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### `/api/location`

```python
@main.route('/api/location')
def api_location():
    name = request.args.get('name')
    try:
        coords = location_service.geocode(name)
        return jsonify(coords)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### 3.3 Error Handling at Route Level

Each route wraps logic in a try-except block to:

- Log the error for debugging
- Gracefully redirect to the `/error` UI or return HTTP 500 JSON response

```python
try:
    # route-specific logic
except Exception as e:
    current_app.logger.error(f"Route error: {str(e)}")
    return redirect(url_for('main.error')) or return jsonify({'error': str(e)}), 500
```

The error fallback page (`error.html`) provides a friendly message and links back to home.

---

## 4. Service Layer Design

The service layer is responsible for abstracting all external API calls, internal data transformations, and database access logic. This section defines how each service works and how it's structured for modularity, caching, and testability.

---

### 4.1 Weather Service

#### External API Interaction

- The weather service fetches weather data (current, forecast, hourly) from **Open-Meteo API** using HTTP GET requests with query parameters based on coordinates.
- JSON responses are parsed and mapped into Python dictionaries for internal use.

**Example:**

```python
def fetch_weather(coords):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&hourly=temperature_2m"
    response = requests.get(url, timeout=5)
    return response.json()
```

#### Caching Logic

- Before making API calls, the service checks **Redis** for existing weather data for the same location and time range.
- Cached keys follow the pattern: `weather:<lat>:<lon>:<type>`.
- TTL:
  - Current: 5 min
  - Hourly: 15 min
  - Forecast: 1 hour

```python
def get_weather(coords, type="current"):
    key = f"weather:{coords['lat']}:{coords['lon']}:{type}"
    cached = redis.get(key)
    if cached:
        return json.loads(cached)
    else:
        data = fetch_weather(coords)
        redis.setex(key, 300, json.dumps(data))  # TTL = 5 min
        return data
```

---

### 4.2 Location Service

#### Nominatim Integration

- Converts city names or zip codes into latitude and longitude using **Nominatim OpenStreetMap API**.
- Uses `GET /search?q={name}&format=json`.

```python
def geocode(name):
    url = f"https://nominatim.openstreetmap.org/search?q={name}&format=json"
    response = requests.get(url, headers={"User-Agent": "weather-app"})
    data = response.json()
    return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
```

#### Input Normalization

- Strips extra whitespace, converts to lowercase, and handles common user input issues like `"newyork" → "New York"`.

```python
def normalize_input(name):
    return ' '.join(name.strip().title().split())
```

---

### 4.3 Unit Conversion Service

#### Mapping Units and Logic

- Converts:
  - Celsius ↔ Fahrenheit
  - km/h ↔ mph
  - mm ↔ inches

**Example:**

```python
def convert_temperature(value, to_unit):
    return (value * 9/5 + 32) if to_unit == "F" else (value - 32) * 5/9
```

- Mappings are centralized to ensure consistent application across views and APIs.

---

### 4.4 Repository Layer

#### MySQL Access Pattern via SQLAlchemy

- SQLAlchemy is used for all DB access and object-relational mapping (ORM).
- Models are defined in `app/models/`.
- Used to store:
  - Weather cache history
  - User session/unit preferences

**Example Model:**

```python
class WeatherRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(128))
    data_type = db.Column(db.String(32))  # e.g., 'current', 'forecast'
    json_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Query Pattern:**

```python
def get_cached_forecast(city):
    return WeatherRecord.query.filter_by(city=city, data_type='forecast').order_by(WeatherRecord.created_at.desc()).first()
```

---s

All services are designed to be:

- **Modular** (separated into files under `app/services/`)
- **Testable** (mockable in unit tests)
- **Reusable** (can be used by both views and APIs)

---

## 5. Database Design Details

This section describes the SQLAlchemy models, caching expiration rules, and database migration strategy for the Real-Time Weather Dashboard application.

---

### 5.1 SQLAlchemy Models

#### WeatherRecord

Stores cached weather data for each city and data type (e.g., current, forecast, hourly).Place the models in:

```
weather-dashboard/
└── app/
    └── models/
        └── models.py
```

```python
class WeatherRecord(db.Model):
    __tablename__ = 'weather_records'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    data_type = db.Column(db.String(32), nullable=False)  # 'current', 'forecast', 'hourly'
    json_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### UserPreference

Stores temporary unit preference settings for a user session.

```python
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), unique=True, nullable=False)
    temp_unit = db.Column(db.String(8), default='C')  # 'C' or 'F'
    wind_unit = db.Column(db.String(8), default='km/h')  # 'km/h', 'm/s', or 'mph'
    precip_unit = db.Column(db.String(8), default='mm')  # 'mm' or 'inches'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 5.2 Caching Expiration Rules

```
weather-dashboard/
└── app/
    └── utils/
        └── constants.py
```

Caching is managed by Redis with time-based expiration for different weather data types:

| Data Type      | Expiration Time (TTL) |
| -------------- | --------------------- |
| Current        | 5 minutes             |
| Hourly         | 15 minutes            |
| 7-Day Forecast | 1 hour                |

This ensures TTLs like 300s (current), 900s (hourly), and 3600s (forecast) are consistent across the application.
These values are aligned with `WeatherService` caching logic and should be defined as constants for reuse.

---

### 5.3 Database Migration Strategy

We will use Alembic for managing schema changes.

```
weather-dashboard/
└── database/
    └── migrations/
```

#### Initial Setup

```bash
pip install alembic
alembic init migrations
```

#### Configuration Steps

- Edit `alembic.ini` to point to the SQLAlchemy database URI.
- Update `env.py` to import `db` and the models.

#### Creating a Migration

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

Migrations will be stored under the `database/migrations/` folder and applied during development or deployment.

---

## 6. Template and Static File Structure

This section outlines the organization and rendering flow of HTML templates and static resources used in the Real-Time Weather Dashboard application.

---

### 6.1 Template File Structure

All HTML templates are rendered using **Jinja2**, Flask’s default templating engine. Templates are organized for reuse and modularity.

#### Folder Path:

```
weather-dashboard/
└── app/
    └── templates/
        ├── base.html            # Base layout with common header/footer
        ├── home.html            # Location input form
        ├── forecast.html        # 7-day forecast page
        ├── hourly.html          # Hourly forecast detail view
        └── settings.html        # Unit preference form
```

#### Template Inheritance:

Jinja2 uses `{% extends %}` and `{% block %}` for layout inheritance. All view templates extend `base.html`.

Example:

```html
<!-- forecast.html -->
{% extends "base.html" %} {% block content %}
<h2>7-Day Forecast for {{ city }}</h2>
<!-- Forecast data rendering -->
{% endblock %}
```

---

### 6.2 Static Resource Layout

Static resources like stylesheets, scripts, and images are served from Flask’s `/static/` route.

#### Folder Path:

```
weather-dashboard/
└── app/
    └── static/
        ├── css/
        │   └── styles.css       # Main stylesheet
        ├── js/
        │   └── main.js          # UI interactions and API calls
        └── images/              # Weather icons and background assets
```

These files are referenced in templates as:

```html
<link
  rel="stylesheet"
  href="{{ url_for('static', filename='css/styles.css') }}"
/>
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

---

### 6.3 Rendering Flow with Jinja2

The Flask controller logic passes data to Jinja2 templates via `render_template`.

Example flow:

```python
@main.route('/forecast/<city>')
def forecast(city):
    forecast_data = weather_service.get_7_day_forecast(city)
    return render_template('forecast.html', city=city, forecast=forecast_data)
```

- Flask injects `forecast_data` into `forecast.html`
- Jinja2 syntax like `{{ forecast.day }}` or `{% for day in forecast %}` dynamically renders HTML content

---

## 7. Frontend Interaction Logic

This section describes the JavaScript logic that supports interactive behaviors in the Real-Time Weather Dashboard application. It includes dynamic elements, API data fetching, and user feedback mechanisms such as loading states.

---

### 7.1 JavaScript for Dynamic Elements

The application uses plain JavaScript for DOM manipulation and user interactions. Key behaviors include:

- Updating the forecast and hourly views without full page reloads
- Toggling UI components (e.g., forecast day selectors, unit settings)
- Showing or hiding loading spinners

#### File Location:

```
weather-dashboard/
└── app/
    └── static/
        └── js/
            └── main.js
```

Example:

```javascript
// Toggle unit settings panel
document.getElementById("unit-toggle").addEventListener("click", function () {
  document.getElementById("unit-panel").classList.toggle("hidden");
});
```

---

### 7.2 Fetching Data via APIs

AJAX requests are used to retrieve weather and location data from the Flask backend. Internally, these requests are handled by:

- `weather_api.py` for weather data
- `loc_api.py` for location geocoding

These service files are located in:

```
weather-dashboard/
└── app/
    └── services/
        ├── weather_api.py
        └── loc_api.py
```

Frontend requests target routes like `/api/weather` or `/api/location`.

Example:

```javascript
async function fetchWeather(city) {
  const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
  if (!response.ok) throw new Error("Weather API failed");
  return await response.json();
}
```

This enables:

- Displaying real-time updates
- Avoiding full page reloads
- Error handling in the UI layer

---

### 7.3 Handling Form Submissions and Loading States

The location input form and unit preference form both rely on JavaScript to submit data and display loading indicators.

#### File Location:

```
weather-dashboard/
└── app/
    └── static/
        └── js/
            └── main.js
```

Example for location search:

```javascript
document.getElementById("search-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = document.getElementById("city-input").value;

  document.getElementById("loading").classList.remove("hidden");

  try {
    const data = await fetchWeather(city);
    updateWeatherUI(data); // Dynamically inject weather into DOM
  } catch (error) {
    alert("Failed to load weather data. Try again.");
  } finally {
    document.getElementById("loading").classList.add("hidden");
  }
});
```

Features:

- Prevents default form submission
- Shows a spinner while waiting for a response
- Gracefully handles API or network failures

---

## 8. Configuration and Environment

This section outlines how the application separates configuration for development, testing, and production environments using Flask's `config.py` file and environment variables.

---

### 8.1 `config.py` Structure for DEV, TEST, PROD

The application uses a `Config` base class and environment-specific subclasses to isolate runtime settings.

#### File Location:

```
weather-dashboard/
└── app/
    └── config.py
```

#### Example Implementation:

```python
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    API_TIMEOUT = 5

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "mysql+pymysql://dev_user:dev_pass@localhost/dev_db")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    API_TIMEOUT = 1

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:pass@prod-db/weather_db")
```

#### Usage in `create_app()`:

```python
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    ...
    return app
```

---

### 8.2 Environment Variable Usage

Environment variables are loaded from a `.env` file or system-level settings and injected into Flask at runtime using `os.getenv()`.

#### Common `.env` keys:

```
SECRET_KEY=supersecretkey
DEV_DATABASE_URL=mysql+pymysql://dev_user:dev_pass@localhost/dev_db
TEST_DATABASE_URL=sqlite:///test.db
DATABASE_URL=mysql+pymysql://user:pass@prod-db/weather_db
REDIS_URL=redis://localhost:6379/0
```

To load these variables during local development, use the `python-dotenv` package or manually source the file:

```bash
pip install python-dotenv
```

Example usage:

```python
from dotenv import load_dotenv
load_dotenv()
```

This keeps sensitive data out of source code and ensures consistent deployment configurations across environments.

---

## 9. Testing Hooks and Coverage

This section describes the complete testing strategy for the Real-Time Weather Dashboard project, covering unit, integration, system (including E2E, performance, security), and acceptance testing. It includes tools, code structure, mocking, coverage metrics, and CI/CD automation.

---

### 9.1 Test Locations and Dependencies

Tests are organized by scope and purpose in the `tests/` directory:

```
weather-dashboard/
└── tests/
    ├── unit/               # Unit tests for isolated functions and services
    ├── integration/        # Service + DB + caching interactions
    ├── system/             # End-to-end, performance, and security tests
    └── robot/              # Human-readable acceptance test scenarios
```

#### Required Packages:

```bash
pip install pytest pytest-mock coverage fakeredis
pip install selenium playwright robotframework requests
pip install locust bandit
```

---

### 9.2 Unit Testing

Unit tests validate service logic in isolation and use mocking to simulate dependencies.

#### Example:

```python
def test_unit_conversion():
    from app.services.unit_service import convert_temperature
    assert convert_temperature(0, "F") == 32
```

#### Mocking External APIs:

```python
def test_weather_api_mocked(mocker):
    mock_resp = {"temp": 75}
    mocker.patch("app.services.weather_api.fetch_weather", return_value=mock_resp)

    from app.services import weather_service
    data = weather_service.get_weather_data("Raleigh")
    assert data["temp"] == 75
```

---

### 9.3 Integration Testing

These tests evaluate how modules interact (e.g., DB + Cache + WeatherService).

```python
def test_forecast_repository_fetch():
    from app.services.repository import get_cached_forecast
    result = get_cached_forecast("New York")
    assert result is not None
```

- Tools: `pytest`, `requests`, `fakeredis`, `Flask test client`

---

### 9.4 System Testing (Non-Functional and E2E)

System testing verifies that the application behaves correctly in realistic, full-stack scenarios.

---

#### End-to-End Testing (UI Automation)

UI flows are tested in real browsers or headless environments.

**Selenium Example:**

```python
from selenium import webdriver

def test_home_page_loads():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000")
    assert "Weather Dashboard" in driver.title
    driver.quit()
```

**Playwright Example:**

```python
from playwright.sync_api import sync_playwright

def test_forecast_title():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5000")
        assert page.title() == "Weather Dashboard"
        browser.close()
```

---

#### Performance Testing (Locust)

```python
# locustfile.py
from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def load_home(self):
        self.client.get("/")
```

Run with:

```bash
locust -f locustfile.py --host=http://localhost:5000
```

---

#### Security Testing (Bandit)

```bash
bandit -r app/
```

Scans for common security issues in Python source code.

---

### 9.5 Acceptance Testing

Acceptance tests simulate user journeys using Robot Framework’s keyword syntax.

**Robot Test File:**

```
tests/robot/weather_dashboard.robot
```

**Example:**

```robot
*** Test Cases ***
User Can View Forecast
    Open Browser    http://localhost:5000    Chrome
    Input Text      id:city-input    Raleigh
    Click Button    id:search-button
    Page Should Contain    7-Day Forecast
```

**Run Command:**

```bash
robot tests/robot/
```

Use this for client-facing or documentation-based validation scenarios.

---

### 9.6 Test Coverage Metrics

Target: **70–80% code coverage**, reported via `pytest-cov`.

```bash
pytest --cov=app tests/
coverage report -m
coverage html
```

Key coverage targets:

- Services
- Routes
- Repositories

---

### 9.7 CI/CD Integration

All test levels are wired into GitHub Actions:

- Unit & integration tests: on every push/PR
- System (E2E + performance/security): pre-deploy pipeline
- Acceptance tests: final validation in release stage
- Coverage thresholds enforced with `coverage report`

---

## 10. Error Messages and Logging

This section outlines the design and implementation of error handling and logging in the Real-Time Weather Dashboard application. It ensures that users receive helpful feedback while developers have sufficient context for debugging and monitoring.

---

### 10.1 Centralized Error Format

All application-level errors are captured using a unified format to ensure consistency across JSON APIs and HTML views.

#### JSON Error Response Format (for API endpoints):

```json
{
  "error": {
    "code": 500,
    "message": "Internal server error. Please try again later."
  }
}
```

#### HTML Error Page (for web interface):

- Renders `error.html` template with error details
- Provides link back to the homepage or retry option

#### Implementation:

```python
from flask import jsonify

def api_error_response(message, code=500):
    return jsonify({"error": {"code": code, "message": message}}), code
```

This function is used in `/api/weather` or `/api/location` for structured failure messages.

---

### 10.2 Logging Strategy and Format

Logging is implemented using Python’s built-in `logging` module and integrated into Flask’s app context.

#### Setup in `__init__.py`:

```python
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    ...
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    return app
```

#### Usage Examples:

```python
import logging
logger = logging.getLogger(__name__)

try:
    data = weather_service.get_weather_data(city)
except Exception as e:
    logger.error(f"Failed to fetch weather: {e}")
    return api_error_response("Weather service unavailable", 503)
```

#### Logging Levels:

- `DEBUG`: Local development detail
- `INFO`: Startup, shutdown, successful fetches
- `WARNING`: Retry attempts, deprecations
- `ERROR`: API or DB failures
- `CRITICAL`: System crash events

---

### 10.3 Log File Output (Optional for Production)

For production deployment, logs may be written to a rotating file handler:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("logs/app.log", maxBytes=100000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

These logs are useful for long-term diagnostics and AWS integration.

---

## 11. Session and Unit Preference Handling

This section describes how the Real-Time Weather Dashboard application handles user unit preferences across different views using Flask session management. It ensures that temperature, wind speed, and precipitation units persist while users navigate between pages.

---

### 11.1 How Unit Choices Persist During Session

Flask’s built-in `session` object is used to store unit preferences per user session.

#### Supported Units:

- **Temperature**: Celsius (`C`) or Fahrenheit (`F`)
- **Wind Speed**: km/h, m/s, or mph
- **Precipitation**: mm or inches

#### Example – Saving Preferences:

```python
from flask import session, request

@main.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['temp_unit'] = request.form.get('temp_unit', 'C')
        session['wind_unit'] = request.form.get('wind_unit', 'km/h')
        session['precip_unit'] = request.form.get('precip_unit', 'mm')
        return redirect(url_for('main.settings'))
    return render_template('settings.html')
```

#### Session Lifetime:

- Flask sessions persist until the browser is closed or the cookie expires.
- Use `app.config['PERMANENT_SESSION_LIFETIME']` to customize duration if needed.

---

### 11.2 Data Passed Between Pages

The user’s unit preferences are retrieved on each page load and passed into Jinja2 templates for display and formatting.

#### Accessing Preferences:

```python
@main.route('/forecast/<city>')
def forecast(city):
    units = {
        "temp": session.get("temp_unit", "C"),
        "wind": session.get("wind_unit", "km/h"),
        "precip": session.get("precip_unit", "mm")
    }
    forecast_data = weather_service.get_7_day_forecast(city, units)
    return render_template("forecast.html", forecast=forecast_data, units=units)
```

#### Template Example:

```html
<p>Temperature: {{ forecast.temp }} °{{ units.temp }}</p>
```

---

### 11.3 Best Practices for Unit Handling

- Always use session defaults to prevent errors on first visit
- Apply unit conversion centrally in the service layer, not templates
- Provide a clear UI for users to adjust units on the `/settings` page
- Reflect active unit preferences visually for user clarity

---

## 12. Security Considerations

This section covers critical security practices implemented in the Real-Time Weather Dashboard, including input validation, protection against injection and cross-site scripting (XSS), and secure management of secret configuration data.

---

### 12.1 Input Validation

All user inputs are validated at the backend to prevent malformed or malicious data from reaching the application logic or external services.

#### Location Input Example:

```python
@main.route('/forecast/<city>')
def forecast(city):
    if not city.isalpha():
        return redirect(url_for('main.error'))
    ...
```

- Validate city names, zip codes, and coordinates using regex or built-in checks
- Use fallbacks or redirect invalid input to error pages
- Sanitize `request.form` and `request.args` data

---

### 12.2 Protection Against Injection and XSS

The application is protected against common injection attacks and cross-site scripting (XSS):

#### SQL Injection Prevention:

- SQLAlchemy ORM is used to safely query the database

```python
record = WeatherRecord.query.filter_by(city=city).first()
```

#### XSS Prevention:

- Jinja2 auto-escapes HTML output by default

```html
<!-- Safe rendering -->
<p>{{ city }}</p>
```

- Never output raw HTML unless intentionally handled and sanitized
- Avoid inline JavaScript or user-injected scripts

#### Optional: Add CSP Headers

- Consider setting a Content Security Policy (CSP) via Flask middleware

---

### 12.3 Secure Config Secrets

Environment variables are used to store sensitive configuration values like API keys and database credentials.

#### Example `.env` file (project root):

```
SECRET_KEY=my-very-secret-key
DATABASE_URL=mysql+pymysql://weather_user:securePass@localhost/weather_db
REDIS_URL=redis://localhost:6379/0
```

✅ Place this file in the root of the project:

```
weather-dashboard/
├── run.py
├── .env     👈
```

✅ Add `.env` to `.gitignore` to avoid leaking secrets:

```
# .gitignore
.env
```

#### Loading with `python-dotenv`:

1. Install it:

```bash
pip install python-dotenv
```

2. Modify `run.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

3. In `config.py`, read with:

```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

In production, environment variables should be injected via:

- Docker secrets
- AWS Systems Manager (SSM)
- GitHub Actions "Secrets"

---
