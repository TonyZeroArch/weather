# Environment Setup Document

### 📑 Environment Setup Index

## 1. Introduction

- Purpose of environment setup
- Relation to project phase and development process

## 2. Development Environment Setup

- Required tools and versions (Python, Flask, MySQL, Redis, etc.)
- Virtual environment and dependency installation
- Local `.env` configuration file
- Folder structure and startup scripts

## 3. Testing Environment Setup

- Test database and cache setup
- Environment isolation strategy
- Installing test libraries (pytest, robot, selenium, etc.)
- Example testing `.env` and configuration

## 4. Production Environment Setup

- AWS EC2 instance configuration
- RDS MySQL setup and networking
- Redis deployment (local or ElastiCache)
- Domain setup with Route 53
- SSL certificate via AWS ACM

## 5. CI/CD Pipeline Setup

- GitHub Actions pipeline for test + deployment
- Secrets and environment variable management
- Docker build and deployment flow
- Health check and rollback strategy

## 6. Environment Switching and Best Practices

- Config class usage (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`)
- Managing `.env` files securely
- Switching between local/test/prod environments

## 7. Appendix

- Reference `.env` templates
- Docker Compose example (optional)
- Troubleshooting common setup issues

# 1. Introduction

## Purpose of Environment Setup

The environment setup phase ensures all team members and automated systems can build, run, test, and deploy the Real-Time Weather Dashboard consistently across local, testing, and production environments. By establishing standardized tools, configurations, and environments, we prevent "it works on my machine" issues and enable reliable collaboration, testing, and deployment.

This document provides a step-by-step guide to configure each environment (development, testing, production), automate CI/CD pipelines, and manage environment-specific settings like secrets and variables.

## Relation to Project Phase and Development Process

This setup corresponds to **Phase 4 – Environment Setup** in the overall project development process. It is built upon the previously completed phases:

- **Requirement & Feature Analysis** – Ensured all functional and non-functional requirements were captured.
- **High-Level Design** – Defined system architecture, tech stack, and modular breakdown.
- **Low-Level Design** – Provided detailed technical specs including app structure, services, and config management.

With those foundations in place, this phase now prepares the runtime environments and deployment infrastructure to support upcoming implementation, testing, and deployment stages. It also ensures that development and test environments mimic production conditions closely, supporting robust testing and continuous integration.

---

# 2. Development Environment Setup

## Required Tools and Versions

To ensure a consistent development experience across all team members’ systems, install the following tools:

| Tool       | Recommended Version | Notes                                      |
| ---------- | ------------------- | ------------------------------------------ |
| Python     | 3.10+               | Required for Flask and testing libraries   |
| pip        | 22.0+               | Comes with Python                          |
| MySQL      | 8.0+                | Local development database (or use Docker) |
| Redis      | 6.0+                | Used for caching weather data              |
| Git        | Latest              | Version control                            |
| Docker     | Latest              | Containerized environment (MySQL, Redis)   |
| Virtualenv | Latest              | Python environment isolation               |

---

## Virtual Environment and Dependency Installation

Use `virtualenv` or `venv` to isolate Python dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Local `.env` Configuration File

Create a `.env` file in the root of the project with the following variables:

```ini
# .env (Development)
SECRET_KEY=dev-secret-key
DEV_DATABASE_URL=mysql+pymysql://dev_user:dev_pass@localhost/weather_db
REDIS_URL=redis://localhost:6379/0
```

Make sure to add `.env` to `.gitignore` to avoid leaking secrets:

```
# .gitignore
.env
```

You can use `python-dotenv` to load these variables automatically during local runs:

```bash
pip install python-dotenv
```

Then update `run.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Docker Setup for MySQL and Redis (Optional)

If you prefer not to install MySQL and Redis locally, use Docker Compose:

Create a `docker-compose.yml` file in the project root:

```yaml
version: "3.8"
services:
  mysql:
    image: mysql:8.0
    container_name: weather_mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: weather_db
      MYSQL_USER: dev_user
      MYSQL_PASSWORD: dev_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:6.0
    container_name: weather_redis
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

To start services:

```bash
docker-compose up -d
```

---

## Folder Structure and Startup Scripts

Ensure your local folder structure follows the layout defined in the design documents:

```
weather-dashboard/
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── templates/
│   ├── static/
│   ├── utils/
│   └── config.py
├── tests/
├── run.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

To start the Flask development server:

```bash
# Activate environment if not already
source venv/bin/activate

# Start the dev server
flask --app run.py run --debug
```

The server will run at `http://localhost:5000`.

> MySQL and Redis must be running locally or via Docker for full functionality.

---

# 3. Testing Environment Setup

## Test Database and Cache Setup

To perform meaningful integration and system testing, use a real MySQL database and a Redis cache. These environments should mimic production as closely as possible while remaining isolated from actual user data.

### MySQL Test Database

The team will use a shared MySQL test database hosted at:

```
3.95.207.214:3306
```

Update your `.env.test` configuration as follows:

```ini
TEST_DATABASE_URL=mysql+pymysql://test_user:test_pass@3.95.207.214:3306/weather_test_db
```

> Replace `test_user`, `test_pass`, and `weather_test_db` with your assigned credentials.

---

### Redis Test Instance

To test caching behavior using Redis, you can either:

#### Option 1: Run Redis locally

```bash
docker run --name test_redis -p 6379:6379 -d redis:6.0
```

This command starts Redis on the default port 6379.

#### Option 2: Use an existing Redis instance

If using a remote Redis instance (e.g., AWS ElastiCache), update the host in your `.env.test` file:

```ini
REDIS_URL=redis://your_redis_host:6379/0
```

---

### Verifying Redis Setup

You can test Redis connectivity and commands via `redis-cli`:

```bash
docker exec -it test_redis redis-cli
```

Basic test:

```bash
set test_key "Hello"
get test_key
```

Expected result:

```
"Hello"
```

Python test example using `redis` package:

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
assert r.ping() is True
```

---

## Environment Isolation Strategy

The application uses `TestingConfig` in `app/config.py` to isolate runtime behavior:

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    API_TIMEOUT = 1
```

To activate this configuration:

```bash
export FLASK_ENV=testing
export TEST_DATABASE_URL=mysql+pymysql://...
export REDIS_URL=redis://localhost:6379/0
```

---

## Installing Test Libraries

Install the required packages for all test types:

```bash
pip install pytest pytest-mock coverage fakeredis
pip install selenium playwright robotframework requests
pip install locust bandit
```

Install Playwright browser binaries:

```bash
playwright install
```

---

## Example Testing `.env` Configuration

Create a `.env.test` file at the project root:

```ini
# .env.test
SECRET_KEY=test-key
TEST_DATABASE_URL=mysql+pymysql://test_user:test_pass@3.95.207.214:3306/weather_test_db
REDIS_URL=redis://localhost:6379/0
```

---

## Running Tests

### Unit Tests

```bash
pytest tests/unit/
```

### Coverage

```bash
pytest --cov=app tests/
coverage report -m
```

### Robot Framework

```bash
robot tests/robot/
```

This setup ensures realistic test coverage using real MySQL and Redis services in a controlled environment.

---

# 4. Production Environment Setup

## AWS EC2 Instance Configuration

Provision an EC2 instance to host the Flask application and Redis. Use a lightweight Amazon Linux 2 or Ubuntu AMI.

### Setup Steps

1. **Launch EC2 Instance**

   - Instance type: `t2.micro` (for testing) or `t3.small+` (production)
   - Enable inbound ports: `22`, `80`, `443`, `5000` (Flask), `6379` (Redis, if needed)

2. **Install Required Software**

   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx git docker.io redis-server
   sudo pip3 install flask gunicorn pymysql python-dotenv
   ```

3. **Clone your repository**

   ```bash
   git clone https://github.com/your-org/weather-dashboard.git
   cd weather-dashboard
   ```

4. **Set environment variables**

   - Store them in `.env` or inject via EC2 System Manager

5. **Run Flask in production**
   ```bash
   flask --app run.py run --host=0.0.0.0
   # Or with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "run:create_app()"
   ```

---

## RDS MySQL Setup and Networking

Use Amazon RDS to host the production MySQL database.

### Setup Steps

1. **Create an RDS MySQL instance**

   - Instance type: `db.t3.micro+`
   - Set DB name: `weather_db`, user/pass of your choice

2. **Configure Networking**

   - Attach to the same VPC as your EC2 instance
   - Allow inbound traffic from EC2’s security group on port `3306`

3. **Store credentials securely**
   - Inject DB URL as an environment variable:
     ```bash
     export DATABASE_URL=mysql+pymysql://user:pass@your-rds-endpoint/weather_db
     ```

---

## Redis Deployment (Local or ElastiCache)

### Option 1: Local Redis on EC2

```bash
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

Set in `.env`:

```ini
REDIS_URL=redis://localhost:6379/0
```

### Option 2: AWS ElastiCache Redis

1. **Create a Redis cluster**

   - Set name, node type, subnet group

2. **VPC Access**

   - Place it in the same VPC and subnet as EC2

3. **Configure Security Group**

   - Allow access from EC2’s security group on port `6379`

4. **Set Redis URL** in `.env`:

```ini
REDIS_URL=redis://your-cache-host:6379/0
```

---

## Domain Setup with Route 53

To map your domain (e.g., `weather.yourdomain.com`) to your EC2 instance:

1. **Buy or import a domain** in Route 53

2. **Create a hosted zone** and configure DNS

3. **Add an A Record**

   - Alias or static IP of your EC2 instance

4. **Test with:**

```bash
ping weather.yourdomain.com
```

---

## SSL Certificate via AWS ACM

Use AWS Certificate Manager to issue an SSL certificate and enable HTTPS.

### Setup Steps

1. **Request a public certificate**

   - Domain name: `weather.yourdomain.com`
   - Validation method: DNS

2. **Attach to Load Balancer or CloudFront**
   - If using EC2 directly, install cert via Certbot on Nginx:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d weather.yourdomain.com
```

3. **Verify HTTPS is working:**
   ```bash
   curl https://weather.yourdomain.com
   ```

Your application is now securely deployed on AWS and accessible via a custom domain.
