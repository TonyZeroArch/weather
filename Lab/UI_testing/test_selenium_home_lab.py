import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestHomePage(unittest.TestCase):
    def setUp(self):
        """Set up the Selenium WebDriver."""
        self.driver = webdriver.Chrome()  # Ensure you have the ChromeDriver installed
        self.driver.get("http://127.0.0.1:5000/")  # Replace with your local server URL

    def test_search_weather(self):
        """Test the search functionality on the home page."""
        driver = self.driver

        # Locate the search input and button
        location_input = driver.find_element(By.ID, "locationInput")
        search_button = driver.find_element(By.ID, "searchButton")

        # Enter a location and click search
        location_input.send_keys("Denver,CO")
        search_button.click()

        # Wait for the weather data to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "city_state"))
        )

        # Verify the displayed weather data
        city_state = driver.find_element(By.ID, "city_state").text
        updated_time = driver.find_element(By.ID, "updated_time").text
        current_temp = driver.find_element(By.ID, "current_temp").text
        like_temp = driver.find_element(By.ID, "like_temp").text
        max_temp = driver.find_element(By.ID, "max_temp").text

        min_temp = driver.find_element(By.ID, "min_temp").text
        uv_index = driver.find_element(By.ID, "uv").text
        precip = driver.find_element(By.ID, "precip").text
        wind_speed = driver.find_element(By.ID, "wind_speed").text

        # Assertions to verify the weather data
        self.assertIn("Cary, NC", city_state)
        # self.assertTrue(updated_time.startswith("Updated:"))
        self.assertTrue(current_temp.endswith("°F"))
        self.assertTrue(like_temp.startswith("Feels Like"))
        self.assertTrue(
            any(char.isdigit() for char in max_temp),
            f"Max temp '{max_temp}' contains no digits",
        )
        self.assertTrue(
            any(char.isdigit() for char in min_temp),
            f"Min temp '{min_temp}' contains no digits",
        )

        self.assertTrue(precip.endswith("%"))
        self.assertTrue(wind_speed.endswith("mph"))

    def tearDown(self):
        """Close the browser after the test."""
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
