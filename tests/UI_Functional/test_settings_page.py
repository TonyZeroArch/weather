import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

@pytest.fixture
def browser():
    """Pytest fixture for webdriver setup/takedown for testing the settings page."""

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://localhost:5000/settings")
    yield driver
    driver.quit()


class TestSettingsPage:
    def test_elements_present(self, browser):
        """Test to check if all critical settings elements are present."""

        settings_header = browser.find_element(By.TAG_NAME, "h2")
        assert settings_header.is_displayed()
        assert settings_header.text == "Settings"

        test_form = browser.find_element(By.CLASS_NAME, "settings-form")
        assert test_form.is_displayed()

        temp_unit = browser.find_element(By.ID, "temp-unit")
        assert temp_unit.is_displayed()
        # selected_option = temp_unit.find_element(By.CSS_SELECTOR, "option:checked")
        # assert selected_option.text == "Celsius (°C)"

        wind_unit = browser.find_element(By.ID, "wind-unit")
        assert wind_unit.is_displayed()

        precip_unit = browser.find_element(By.ID, "precip-unit")
        assert precip_unit.is_displayed()

        save_settings_btn = browser.find_element(By.CLASS_NAME, "btn-save")
        assert save_settings_btn.is_displayed()


    def test_form_submission(self, browser):
        """Test to check if the user can select settings by selecting whatever option
        isn't selected for all three units. Also tests if the user can submit the changes
        by checking if the save button works and reloads the same page. Finally tests if
        the settings persist after the settings page is reloaded."""

        # Part 1: Tests if other form options can be selected and the form can be submitted
        temp_unit = browser.find_element(By.ID, "temp-unit")

        old_temp_option = temp_unit.find_element(By.CSS_SELECTOR, "option:checked")
        new_temp_option = temp_unit.find_element(By.CSS_SELECTOR, "option:not(:checked)")
        assert new_temp_option.text != old_temp_option.text
        new_temp_option.click()
        assert not old_temp_option.is_selected()
        assert new_temp_option.is_selected()

        wind_unit = browser.find_element(By.ID, "wind-unit")

        old_wind_option = wind_unit.find_element(By.CSS_SELECTOR, "option:checked")
        new_wind_option = wind_unit.find_element(By.CSS_SELECTOR, "option:not(:checked)")
        assert new_wind_option.text != old_wind_option.text
        new_wind_option.click()
        assert not old_wind_option.is_selected()
        assert new_wind_option.is_selected()

        precip_unit = browser.find_element(By.ID, "precip-unit")

        old_precip_option = precip_unit.find_element(By.CSS_SELECTOR, "option:checked")
        new_precip_option = precip_unit.find_element(By.CSS_SELECTOR, "option:not(:checked)")
        assert new_precip_option.text != old_precip_option.text
        new_precip_option.click()
        assert not old_precip_option.is_selected()
        assert new_precip_option.is_selected()

        # Allows default unit selections from this page to be read after the page reloads
        # to check if the settings actually change.
        old_temp_option_text = old_temp_option.text
        old_wind_option_text = old_wind_option.text
        old_precip_option_text = old_precip_option.text
        
        old_body = browser.find_element(By.TAG_NAME, "body")
        save_settings_btn = browser.find_element(By.CLASS_NAME, "btn-save")
        save_settings_btn.click()

        WebDriverWait(browser, 10).until(
            EC.staleness_of(old_body)
        )

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "settings-form"))
        )

        assert browser.find_element(By.CLASS_NAME, "settings-form").is_displayed()
        assert "/settings" in browser.current_url

        # Part 2: Tests if settings choices remain after form submission
        # This part has a custom message to let the tester know the first
        # part passed. I would create another test for this, but that test would
        # just still need all or most of the prior code.
        try:
            temp_unit = browser.find_element(By.ID, "temp-unit")
            cur_temp_option = temp_unit.find_element(By.CSS_SELECTOR, "option:checked")
            assert cur_temp_option.text != old_temp_option_text

            wind_unit = browser.find_element(By.ID, "wind-unit")
            cur_wind_option = wind_unit.find_element(By.CSS_SELECTOR, "option:checked")
            assert cur_wind_option.text != old_wind_option_text

            precip_unit = browser.find_element(By.ID, "precip-unit")
            cur_precip_option = precip_unit.find_element(By.CSS_SELECTOR, "option:checked")
            assert cur_precip_option.text != old_precip_option_text
            
        except AssertionError as e:
            pytest.fail(f"The form was submitted correctly but settings did not persist {e}")


    def test_navigation_from_settings_to_home(self, browser):
        """Test if the user can navigate to the home page from the settings page via the Wake Tech logo."""

        home_link = browser.find_element(By.CLASS_NAME, "nav-logo")
        home_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://localhost:5000/")
        )

        assert browser.current_url == "http://localhost:5000/"


    def test_navigation_from_settings_to_hourly(self, browser):
        """Test if the user can navigate to the hourly page from the settings page via the hourly button."""

        hourly_link = browser.find_element(By.LINK_TEXT, "Hourly")
        hourly_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://localhost:5000/hourly")
        )

        assert browser.current_url == "http://localhost:5000/hourly"
    

    def test_navigation_from_settings_to_forecast(self, browser):
        """Test if the user can navigate to the forecast page from the settings page via the forcast button."""

        forecast_link = browser.find_element(By.LINK_TEXT, "Forecast")
        forecast_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://localhost:5000/forecast/")
        )

        assert browser.current_url == "http://localhost:5000/forecast/"