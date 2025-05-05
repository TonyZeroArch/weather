from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_search_weather_by_city():
    # Setup
    driver = webdriver.Chrome()  # Or use Firefox(), Edge(), etc.
    driver.get("http://127.0.0.1:5000")  #  App URL

    # Step 1: Locate the search bar
    search_input = driver.find_element(By.ID, "search-bar")  # Input field ID or name
    assert search_input is not None

    # Step 2: Simulate user typing a city
    search_input.send_keys("Cary, NC")
    search_input.send_keys(Keys.RETURN)  # Simulate pressing Enter

    # Step 3: Wait for response (can use WebDriverWait instead of sleep for better control)
    time.sleep(3)

    # Step 4: Verify weather results are shown
    result = driver.find_element(By.ID, "weather-results")  # Result container ID
    assert "New York" in result.text or "°C" in result.text

    # Cleanup
    driver.quit()
