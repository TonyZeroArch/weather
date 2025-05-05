# Lab: UI testing using Playwright 

## Objective

This lab demonstrates how to use **Playwright** to test the UI of a web application (Flask-based in this case). 

----------

## Tools Used

-   **Framework:** Playwright
    
-   **Language:** Python
    
-   **Test Runner:** Pytest
    
-   **Browser Support:** Chromium, Firefox, WebKit
    
-   **Application Under Test:** Flask-based weather app (hosted at `http://127.0.0.1:5000/`)
    

----------

## Lab Setup

### 1. Install Dependencies

```bash
pip install pytest playwright
playwright install

```

### 2. `requirements.txt`

```
pip install requirements.txt

```

----------

## Test Scenarios

### Test Case 1: Open Home Page

```python
page.goto("http://127.0.0.1:5000/")

```

### Test Case 2: Navigate to Settings

```python
page.get_by_role("link", name="Settings").click()

```

### Test Case 3: Update Settings

```python
page.get_by_label("Temperature Unit").select_option("F")
page.get_by_label("Wind Speed Unit").select_option("mph")
page.get_by_label("Precipitation Unit").select_option("in")
page.get_by_role("button", name="Save Settings").click()

```

### Test Case 4: Use Search Function (ZIP and City)

```python
page.get_by_role("textbox", name="Enter a city name, zip code").fill("27587")
page.get_by_role("button", name="Search").click()

page.get_by_role("textbox", name="Enter a city name, zip code").fill("raleigh, nc")
page.get_by_role("button", name="Search").click()

```

----------

## Test Implementation

### test_ui_playwright.py

```python
from playwright.sync_api import sync_playwright
import pytest

# playwright_ui_test.py

@pytest.fixture(scope="session")
def browser_context():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    yield page
    browser.close()
    playwright.stop()

@pytest.mark.order(1)
def test_open_website(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")

@pytest.mark.order(2)
def test_click_settings(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("link", name="Settings").click()

@pytest.mark.order(3)
def test_click_hourly(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("link", name="Hourly").click()

@pytest.mark.order(4)
def test_click_forecast(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("link", name="Forecast").click()

@pytest.mark.order(5)
def test_search_zipcode(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("textbox", name="Enter a city name, zip code").click()
    page.get_by_role("textbox", name="Enter a city name, zip code").fill("27587")
    page.get_by_role("button", name="Search").click()

@pytest.mark.order(6)
def test_search_city(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("textbox", name="Enter a city name, zip code").click()
    page.get_by_role("textbox", name="Enter a city name, zip code").fill("raleigh, nc")
    page.get_by_role("button", name="Search").click()

@pytest.mark.order(7)
def test_update_settings(browser_context):
    page = browser_context
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("link", name="Settings").click()
    page.get_by_label("Temperature Unit").select_option("F")
    page.get_by_label("Wind Speed Unit").select_option("mph")
    page.get_by_label("Precipitation Unit").select_option("in")
    page.get_by_role("button", name="Save Settings").click()

if __name__ == "__main__":
    pytest.main(["-v", "playwright_ui_test.py"])

```
----------

