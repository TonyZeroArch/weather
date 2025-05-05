# UI Testing Educational Lab
## Introduction
### UI Testing
UI testing, or user interface testing, is an important aspect of application testing. As the name implies, this type of testing tests the aspects of the program that the user interacts with. It makes sure that different elements are able to be viewed, interacted with, and look and behave correctly. UI testing is usually considered a type of black-box testing because it is usually done without the need to know the underlying code. It focuses on the behavior of the program.

### Lab Overview
The purpose of the lab is to help you to understand the basics of web-based UI testing. We will be using Selenium to go over basic UI testing strategies through interacting with our weather forecast website. Selenium is used to interact with a web browser's user interface, similar to how a user would, in order to test if the UI is looks and behaves correctly.

### Prerequisites
In order to complete this lab, you will need at least a basic familiarity with:
- Python
- Html
- CSS (Optional but helpful)
- Git and Github

You will also need your IDE of choice. This lab will be using VSCodium. This lab will be using Linux, but it can be completed on any platform if you know the equivalent commands.

### Setup Instructions
Here are the steps you should take before we get started:
1. Install WebDriver
   - WebDriver is a browser specific program that allows Selenium to connect to and control your browser. If using Chrome or Chromium you can use [ChromeDriver](https://developer.chrome.com/docs/chromedriver). Though you can easily find instructions for most, if not all, browsers.
2. Clone the Github repository
   - Open your terminal and change directory to wherever you want to put the repository.
   - Type: ```git clone https://github.com/sp25-csc256-0001/group-project-t6.git``` or your system's equivalent command.
3. Enter the program's virtual environment and install the requirements:
    - Change directory to the new repository.
    - Type: ```source venv/bin/activate``` to enter the VENV.
    - Type: ```pip install -r requirements.txt``` to allow pip to install the requirements needed for the program to run.
4. Start the Flask server
    - You may want to open a second terminal or terminal tab to run the server in the background. It will run and take up the terminal for the rest of the lab. If you do, simply change directory to your repository in the new terminal and run ```source venv/bin/activate``` again to set it up.
    - Type: ```python3 run.py```. Pay attention to the ip the program says it's running on. It should look like:
    ```
    INFO ==----== WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    ```
  
  The server is now running. You can access it on the computer this is running on by going to the ip and port you found. Most likely, though, you can just go to http://localhost:5000.

## Testing

### Testing Fundamentals: Part One
To use Selenium, you should go ahead and import these packages:
```
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```

To begin testing your browser you need to create a WebDriver object to control your browser. For Chrome, this is:
> driver = webdriver.Chrome()

In order to test an element you must select it. Some of the attributes you can select an element with are:
1. ID
2. LINK_TEXT
3. NAME
4. TAG_NAME
5. CLASS_NAME
6. CSS_SELECTOR

#### ID
If an element has an ID attribute you can select an element with it.
> element = driver.find_element(By.ID, "elementId")

This is usually the most reliable way to find an element if the element has an ID. Here's an example from our project:
```python
current_temp = driver.find_element(By.ID, "current_temp")
```
This finds the element that displays the current temperature.

#### LINK_TEXT
If you need to find a link (an `<a>` tag) by its text content, you can use LINK_TEXT:
```python
settings_link = driver.find_element(By.LINK_TEXT, "Settings")
```
This finds a link with the text "Settings".

#### CLASS_NAME
If an element has a class, you can select it using its class name:
```python
hourly_forecast = driver.find_element(By.CLASS_NAME, "hourly-forecast")
```
This finds an element with the class "hourly-forecast".

#### CSS_SELECTOR
For more complex selections, you can use CSS selectors:
```python
hour_card = driver.find_element(By.CSS_SELECTOR, ".hour0 .temp0")
```
This would find an element with class "temp0" that is a child of an element with class "hour0".

### Waiting for Elements
Web applications often load content dynamically, so you may need to wait for elements to appear before interacting with them. Selenium provides two types of waits:

#### Implicit Wait
An implicit wait tells WebDriver to poll the DOM for a certain amount of time when trying to find elements that aren't immediately available:
```python
driver.implicitly_wait(10)  # Wait up to 10 seconds
```

#### Explicit Wait
An explicit wait is more precise. It allows you to wait for a specific condition to occur:
```python
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "city_state"))
)
```
This waits up to 10 seconds for an element with ID "city_state" to be present in the DOM.

### Exercise 1: Basic Page Load Test
Let's start with a basic test that loads the homepage and verifies that the default weather location is displayed correctly.

Create a new file called `test_basic.py` with the following content:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_default_location():
    # Set up the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # Navigate to the homepage
        driver.get("http://localhost:5000")
        
        # Find the location header
        location_header = driver.find_element(By.ID, "city_state")
        
        # Verify the default location is displayed
        assert location_header.text == "Cary, NC"
        
    finally:
        # Clean up by closing the browser
        driver.quit()
```

Run this test using pytest:
```
pytest test_basic.py
```

If the test passes, it means you've successfully verified that the homepage loads with the default location "Cary, NC".

### Testing Fundamentals: Part Two - Testing User Interactions
In this section, we'll learn how to simulate user interactions with the UI.

#### Clicking Elements
To click on an element (like a button or link):
```python
element.click()
```

#### Typing Text
To enter text into an input field:
```python
element.send_keys("text to type")
```

#### Clearing Text
To clear an input field:
```python
element.clear()
```

#### Getting Text and Attributes
To get the text content of an element:
```python
text = element.text
```

To get the value of an attribute:
```python
attribute_value = element.get_attribute("attribute_name")
```

### Exercise 2: Testing the Weather Search
Now let's create a test that simulates a user searching for weather information.

Create a new file called `test_search.py` with the following content:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_search_weather():
    # Set up the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # Navigate to the homepage
        driver.get("http://localhost:5000")
        
        # Find the search input and button
        location_input = driver.find_element(By.ID, "locationInput")
        search_button = driver.find_element(By.ID, "searchButton")
        
        # Enter a location and click search
        location_input.send_keys("Raleigh, NC")
        search_button.click()
        
        # Wait for the weather data to load
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "city_state"), "Raleigh, NC")
        )
        
        # Verify the displayed weather data
        city_state = driver.find_element(By.ID, "city_state").text
        assert "Raleigh, NC" in city_state
        
        # Verify that temperature is displayed
        current_temp = driver.find_element(By.ID, "current_temp")
        assert current_temp.is_displayed()
        
    finally:
        # Clean up
        driver.quit()
```

Run this test:
```
pytest test_search.py
```

This test simulates a user typing "Raleigh, NC" in the search box, clicking the search button, and verifies that the correct location's weather data is displayed.

### Testing Fundamentals: Part Three - Advanced UI Testing

#### Testing Regular Expressions
Sometimes you need to verify that an element's text matches a specific pattern instead of an exact string. You can use regular expressions for this:

```python
import re

# Check if the temperature follows the pattern of a number followed by °F or °C
temperature_text = current_temp.text
pattern = r"^-?\d+(°F|°C)$"
assert bool(re.match(pattern, temperature_text))
```

#### Testing Navigation Between Pages
To test navigation between pages:

1. Click on a link or button that triggers navigation
2. Wait for the new page to load
3. Verify that the URL or page content indicates the correct page loaded



### Exercise 3: Testing Navigation and Settings
Let's create a test that verifies navigation between pages works correctly.

Create a new file called `test_navigation.py` with the following content:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_navigation():
    # Set up the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # Navigate to the homepage
        driver.get("http://localhost:5000")
        
        # Find and click the Settings link
        settings_link = driver.find_element(By.LINK_TEXT, "Settings")
        settings_link.click()
        
        # Wait for the settings page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/settings")
        )
        
        # Verify that we're on the settings page
        assert "/settings" in driver.current_url
        
        # Check if the temperature unit dropdown is present
        temp_unit_dropdown = driver.find_element(By.ID, "temp-unit")
        assert temp_unit_dropdown.is_displayed()
        
        # Now navigate to the forecast page
        forecast_link = driver.find_element(By.LINK_TEXT, "Forecast")
        forecast_link.click()
        
        # Wait for the forecast page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/forecast")
        )
        
        # Verify that we're on the forecast page
        assert "/forecast" in driver.current_url
        
    finally:
        # Clean up
        driver.quit()
```

Run this test:
```
pytest test_navigation.py
```

This test verifies that you can navigate from the homepage to the settings page, then to the forecast page, and that each page loads correctly with its expected elements.

### Exercise 4: Complete Test Suite with Fixtures

Pytest fixtures allow you to set up and tear down resources that are needed for your tests in a clean, reusable way. Let's create a test suite that uses fixtures to avoid duplicating code.

Create a new file called `test_suite.py` with the following content:

```python
import pytest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def browser():
    """Pytest fixture for webdriver setup and teardown."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://localhost:5000")
    yield driver
    driver.quit()

class TestHomePage:
    def test_default_location(self, browser):
        """Tests that the default location is displayed correctly."""
        location_header = browser.find_element(By.ID, "city_state")
        assert location_header.text == "Cary, NC"
    
    def test_current_temp(self, browser):
        """Tests if the current temperature is formatted correctly."""
        current_temp = browser.find_element(By.ID, "current_temp")
        pattern = r"^-?\d+(°F|°C)$"
        assert bool(re.match(pattern, current_temp.text))
    
    def test_search_weather(self, browser):
        """Tests the search functionality."""
        location_input = browser.find_element(By.ID, "locationInput")
        search_button = browser.find_element(By.ID, "searchButton")
        
        # Enter a location and click search
        location_input.send_keys("Raleigh, NC")
        search_button.click()
        
        # Wait for the weather data to load
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.ID, "city_state"), "Raleigh, NC")
        )
        
        # Verify the displayed weather data
        city_state = browser.find_element(By.ID, "city_state").text
        assert "Raleigh, NC" in city_state

class TestNavigation:
    def test_navigation_to_settings(self, browser):
        """Tests navigation from home to settings page."""
        settings_link = browser.find_element(By.LINK_TEXT, "Settings")
        settings_link.click()
        
        WebDriverWait(browser, 10).until(
            EC.url_contains("/settings")
        )
        
        assert "/settings" in browser.current_url
```

Run this test suite:
```
pytest test_suite.py
```

This test suite uses a fixture called `browser` that sets up the WebDriver, navigates to the homepage, and then tears down the WebDriver after each test. It includes tests for the default location, temperature formatting, search functionality, and navigation.


## Conclusion

In this lab, you learned how to:
- Set up Selenium for UI testing
- Find elements on a web page using different selector methods
- Interact with elements (clicking, typing, etc.)
- Write tests that verify the behavior of a web application
- Use fixtures to make your tests more maintainable
- Navigate between pages and verify correct navigation

These skills will help you write effective UI tests for your own web applications, ensuring they work correctly from a user's perspective.