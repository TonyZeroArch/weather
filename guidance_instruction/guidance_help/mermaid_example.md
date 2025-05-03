# Mermaid Examples

## Architecture (Layered)

```mermaid
graph TD;
    A[Start: Set Up Project] --> B[Initialize Git & Virtual Environment]
    B --> C[Install Dependencies]
    C --> D[Create Project Folder Structure]

    D --> E[Set Up Flask Application]
    E --> F[Define Database Models]
    F --> G[Create API Routes - Blueprints]
    G --> H[Develop Frontend - Templates/Static]
    H --> I[Implement Business Logic]

    I --> J[Write Unit Tests - Pytest]
    J --> K[Write API Tests - Postman]
    K --> L[Write UI Tests - Selenium/Playwright]

    L --> M[Run Application Locally]
    M --> N[Version Control with GitHub]
    N --> O[Branching Strategy & PR Reviews]

    O --> P[Refactor - Debug Code]
    P --> Q[Final Testing & QA]
    Q --> R[Project Ready for Deployment - Optional]
```

## Architecture

```mermaid
sequenceDiagram
    participant Developer
    participant GitHub
    participant FlaskApp
    participant Database
    participant Testing

    Developer->>GitHub: Initialize Git & Create Repo
    Developer->>FlaskApp: Set Up Virtual Environment
    FlaskApp->>FlaskApp: Install Dependencies (Flask, SQLAlchemy, Pytest)

    Developer->>FlaskApp: Create Project Folder Structure
    Developer->>FlaskApp: Set Up Flask Application (app/__init__.py)
    Developer->>Database: Define Models (SQLAlchemy)

    Developer->>FlaskApp: Create API Routes (Blueprints)
    Developer->>FlaskApp: Develop Frontend
```

## User Journey

Here is a **User Story** for a Flask web application following the **Layered (n-Tier) Architecture** that can be demonstrated using a **Mermaid User Journey Diagram**.

---

### **User Story: User Registration & Login**

#### **Title:** User can register and log into the Flask web application.

#### **Actors:** New User, System (Flask App)

#### **Description:**

As a **new user**,  
I want to **create an account and log in**,  
So that I can **access personalized content**.

#### **Acceptance Criteria:**

✅ User can access the **registration page**.  
✅ User can **submit a valid email and password** for account creation.  
✅ System **validates input and stores user data** in the database.  
✅ User receives a **success message** and can log in.  
✅ Upon logging in, the system **authenticates and redirects** the user to the dashboard.

---

### **Mermaid User Journey Diagram**

```mermaid
journey
    title User Registration & Login Journey
    section Visit Website
      User lands on homepage: 3: User
      User navigates to Sign Up page: 3: User
    section Registration Process
      User enters email & password: 4: User
      User submits form: 4: User
      System validates input: 3: System
      System stores user data in DB: 4: System
      System shows success message: 5: System
    section Login Process
      User navigates to Login page: 3: User
      User enters credentials: 4: User
      System authenticates user: 4: System
      System redirects to dashboard: 5: System
```

---

### **How to Demo This User Story**

1. **Homepage & Navigation:** Show how the user reaches the registration page.
2. **Registration Form:** Demonstrate how the user enters their details and submits the form.
3. **Validation & Storage:** Simulate how the system checks input and stores data.
4. **Login Flow:** Show the user logging in with their credentials and accessing the dashboard.
5. **Redirect & Authentication:** Highlight how the system verifies login details and grants access.

---
