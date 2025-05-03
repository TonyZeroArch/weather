# High-Level Design Document

## Real-Time Weather Dashboard Web Application

---

## 1. System Overview

The Real-Time Weather Dashboard is a responsive, browser-based application that provides users with real-time weather data based on their input (city name, zip code, or coordinates). It supports both current weather and forecasts, powered by integration with Open-Meteo and Nominatim APIs. It emphasizes reliability, user experience, maintainability, and testability for educational and real-world applications.

---

## 2. Technology Stack

- **Frontend**: HTML, CSS, JavaScript (React optional), Jinja2 (via Flask)
- **Backend**: Python 3, Flask framework
- **Database**: MySQL (via SQLAlchemy ORM)
- **Caching**: Redis
- **External APIs**:
  - [Open-Meteo](https://open-meteo.com/) for weather data
  - [Nominatim](https://nominatim.org/) for geocoding
- **Deployment**: AWS (EC2, RDS, Route 53, GitHub Actions)
- **Testing Tools**: Pytest, Postman, Selenium, Playwright, Robot Framework

---

## 3. System Architecture Overview

The application is built using a distributed, scalable, and data-centered design with well-defined module separation:

- **Frontend** handles user interaction and renders data.
- **Flask Backend** receives user inputs, communicates with internal services, handles caching and API calls, and prepares data for rendering.
- **Database Layer** stores cached weather data and location history.
- **Caching Layer (Redis)** reduces external API calls by storing recent data.
- **CI/CD & Deployment Layer** ensures automatic testing and deployment to AWS.

---

## 4. RESTful API Design

The application follows RESTful design principles:

- **Resources** are accessed via consistent URIs (e.g., `/api/weather`, `/api/location`)
- **HTTP Methods**:
  - `GET` for fetching weather/location
  - `POST` for new search sessions
- **Responses**: JSON structured responses with HTTP status codes (200, 400, 404, 500)
- **Error Handling**: Standardized error schema with message and code

---

## 5. Modular Design and Component Responsibilities

### Internal Services

- **Weather Service**: Handles Open-Meteo API calls and caching logic
- **Location Service**: Handles Nominatim geocoding and input validation
- **Units Service**: Handles measurement conversion based on user preference
- **Repository Service**: Handles DB operations for weather/location data

### UI Components

- Home/search bar
- Current weather display
- 7-day forecast view
- Hourly detail view
- Settings for units

---

## 6. GitHub Project Folder Structure

```
weather-dashboard/
│
├── app/                           # Main Flask app package
│   ├── __init__.py                # App factory
│   ├── routes/                    # Route definitions (Blueprints)
│   ├── controllers/               # Request logic
│   ├── services/                  # Weather, location, units
│   ├── models/                    # SQLAlchemy models
│   ├── utils/                     # Helpers and shared logic
│   ├── templates/                 # Jinja2 templates
│   │   └── base.html
│   ├── static/                    # Static files (CSS, JS)
│   │   ├── css/
│   │   └── js/
│   └── config.py                  # Config class
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── robot/
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── migrations/
│
├── cache/
│   └── redis_config.py
│
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── TEST_PLAN.md
│
├── run.py                         # Entrypoint
├── requirements.txt
├── .env
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 7. Database and Caching Layer

### Database (MySQL)

- Tables for:
  - Cached weather data (location, data, timestamp)
  - User preferences (unit settings)
- ORM: SQLAlchemy
- Migrations: Alembic or raw SQL scripts

### Caching (Redis)

- Keyed by location + data type (current, hourly, forecast)
- TTL:
  - Current weather: 5 min
  - Hourly: 15 min
  - Forecast: 1 hour

---

## 8. Routing and REST API Endpoints

### Backend Routes

- `/weather` → renders dashboard view
- `/weather/hourly/<day>` → renders hourly view for selected day
- `/settings` → units settings view
- `/api/weather` → JSON endpoint for current/forecast data
- `/api/location` → JSON endpoint for geocoding

---

## 9. Frontend Integration and Template Rendering

- Flask renders all views using Jinja2 (`templates/`)
- Static resources (CSS/JS/icons) served via `/static/`
- JavaScript handles interactivity like loading states and user preferences

---

## 10. Security, Logging, and Error Handling

- **Validation**: All user input validated on server side
- **Error Pages**: 404 and 500 templates
- **Logging**: Flask logger + `logging` module for server events
- **Fallbacks**: Use expired cached data if APIs fail

---

## 11. Scalability, Maintainability & Best Practices

- Modular services and testable code
- Follows MVC and SOLID principles
- Configurable environment (DEV/PROD separation)
- Easily deployable with CI/CD
- Coverage target: 70-80%

---

## 12. AWS Deployment Strategy

### AWS Resources

- **EC2**: Flask + Redis Docker container
- **RDS (MySQL)**: Remote database service
- **Route 53**: Custom domain
- **ACM**: SSL certificate for HTTPS

### CI/CD Flow (GitHub Actions)

1. Push to `main` triggers test pipeline
2. On success, Docker image is built and pushed
3. Deployed to EC2 using SSH or AWS CLI
4. Health check and service logs reviewed

---
