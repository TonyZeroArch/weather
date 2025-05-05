import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


# Constants for the default home page location and the test search location.
DEFAULT_LOCATION = "Cary, NC"
TEST_LOCATION = "Raleigh, NC"


@pytest.fixture(scope="class")
def browser():
    """Pytest fixture for webdriver setup and takedown for the home page."""

    driver = webdriver.Chrome()
    driver.maximize_window()
    # This line SHOULD work for any localhost ip.
    driver.get("http://localhost:5000")
    yield driver
    driver.quit()


@pytest.fixture(scope="class")
def hour_cards(browser):
    """Pytest fixture to give tests the hour cards they need to test for the home page hourly forecast."""
    hour_card_section = browser.find_element(By.CLASS_NAME, "hourly-forecast")
    hour_cards = hour_card_section.find_elements(By.CSS_SELECTOR, "div[class^='hour']")
    return hour_cards


class TestDefaultHomePage:
    def test_default_location(self, browser):
        """Tests to make sure that the correct default location is displayed."""

        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.ID, "city_state"), DEFAULT_LOCATION)
        )

        location_header = browser.find_element(By.ID, "city_state")
        assert location_header.text == DEFAULT_LOCATION


    def test_time_updated(self, browser):
        """Tests if the time of weather update is in the correct format of "Updated at Local Time: hh:mm"."""
        # Is the default page actually supposed to be different? It says "Updated: hh:mm" instead.
        # I was testing with both versions being valid, but decided this changing text is probably a bug.
        # Switch to the commented out code if it isn't.

        time_updated = browser.find_element(By.ID, "updated_time")

        pattern = r"^(Updated at Local Time:) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        time_updated_correct = bool(re.match(pattern, time_updated.text))
        assert time_updated_correct

        # """Tests if the time of weather update is in the correct format of "Updated at Local Time: hh:mm" or "Updated: hh:mm" for first load."""

        # time_updated = browser.find_element(By.ID, "updated_time")

        # pattern = r"^Updated: (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        # time_updated_before_search = bool(re.match(pattern, time_updated.text))

        # pattern = r"^(Updated at Local Time:) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        # time_updated_after_search = bool(re.match(pattern, time_updated.text))
        
        # assert time_updated_before_search or time_updated_after_search


    def test_current_temp(self, browser):
        """Tests if the current temperature is a number followed by °F or °C with no space.
        It allows there to be a negative sign."""

        current_temp = browser.find_element(By.ID, "current_temp")
        pattern = r"^-?\d+(°F|°C)$"
        assert bool(re.match(pattern, current_temp.text))


    def test_feels_like_temp(self, browser):
        """Tests if current feels like temp is a number followed by °F or °C with no space.
        It allows there to be a negative sign."""

        feels_like_temp = browser.find_element(By.ID, "like_temp")
        pattern = r"^(Feels like) -?\d+(°F|°C)$"
        assert bool(re.match(pattern, feels_like_temp.text))


    def test_weather_icon_and_text(self, browser):
        """Tests if the current weather icon and weather condition description are displayed and
        the weather icons's alt text matches the weather condition description."""
        
        current_weather_icon = browser.find_element(By.CLASS_NAME, "weather-icon")
        current_weather_description = browser.find_element(By.CLASS_NAME, "cur_condition")

        assert current_weather_icon.is_displayed()
        assert current_weather_description.is_displayed()

        assert current_weather_icon.get_attribute("alt") == current_weather_description.text


    def test_weather_table(self, browser):
        """Tests if the table in the current weather card displays the correct information by checking
        if maximum and minimum temperature, uv, precipitation, and wind speed are correctly displayed.
        This means these formats should be being used:
        Temperature: An optional negative sign then a number followed by °F or °C with no spaces
        UV: A number from 0 to 10 or 11+ with no spaces. 11+ is the highest uv index and the only one with a plus.
        Precipitation: A number from 0 - 100 followed by a % with no spaces.
        Wind Speed: A number followed by mph or km/h with a space in the middle."""
        
        max_temp = browser.find_element(By.ID, "max_temp")
        min_temp = browser.find_element(By.ID, "min_temp")
        uv = browser.find_element(By.ID, "uv")
        precipitation = browser.find_element(By.ID, "precip")
        wind_speed = browser.find_element(By.ID, "wind_speed")

        temp_pattern = r"^-?\d+(°F|°C)$"
        assert bool(re.match(temp_pattern, max_temp.text)) and bool(re.match(temp_pattern, min_temp.text))

        uv_pattern = r"^([0-9]|10|11\+)$"
        assert bool(re.match(uv_pattern, uv.text))

        precip_pattern = r"^(\d{1,2}|100)%$"
        assert bool(re.match(precip_pattern, precipitation.text))

        wind_speed_pattern = r"\d+ (mph|km/h)"
        assert bool(re.match(wind_speed_pattern, wind_speed.text))


    def test_hourly_forecast_card_hours(self, hour_cards):
        """Tests if there are six cards, the hours in each of the hour cards are in the format "hh:00",
        the hour doesn't go past 23, and each is one more hour than the previous."""

        assert len(hour_cards) == 6

        time_pattern = r"(0[0-9]|1[0-9]|2[0-3]):00"
        prev_time = -1
        for i in range(6):
            time = hour_cards[i].find_element(By.CLASS_NAME, f"time{i}").text
            assert bool(re.match(time_pattern, time))

            time = int(time.split(":")[0])
            if i != 0:
                if prev_time == 23 and time == 0:
                    pass
                else:
                    assert time == prev_time + 1
            
            prev_time = time


    def test_hourly_forecast_card_temperature(self, hour_cards):
        """Tests if there are six cards and if the temperatures in each of the hour cards are in the format of
        a number with an optional negative sign followed by °F or °C with no spaces."""

        assert len(hour_cards) == 6

        pattern = r"^-?\d+(°F|°C)$"
        for i in range(6):
            temp = hour_cards[i].find_element(By.CLASS_NAME, f"temp{i}").text
            assert bool(re.match(pattern, temp))


    def test_hourly_forecast_card_precip_chance(self, hour_cards):
        """Tests if there are six hour cards and if the precipitation chance in each of the cards is in
        the correct format of a number without trailing zeroes from 1 - 100 with a % with no spaces."""

        assert len(hour_cards) == 6

        precip_pattern = r"^(\d{1,2}|100)%$"
        for i in range(6):
            chance = hour_cards[i].find_element(By.CLASS_NAME, f"precip{i}").text
            assert bool(re.match(precip_pattern, chance))


    def test_hourly_forecast_card_icon_and_text(self, hour_cards):
        """Tests if there are six hour cards, the weather icon and weather condition description are displayed in each,
        and the weather icons's alt text matches the weather condition description in each."""

        assert len(hour_cards) == 6

        for i in range(6):
            weather_desc = hour_cards[i].find_element(By.CLASS_NAME, f"description{i}").text
            weather_icon_element = hour_cards[i].find_element(By.CLASS_NAME, f"hour-icon{i}")
            weather_icon_alt = weather_icon_element.get_attribute("alt")

            assert weather_desc == weather_icon_alt




class TestHomePageSearch:
    def test_search_location(self, browser):
        """Tests to make sure that the correct location is displayed when searched for."""

        location_input = browser.find_element(By.ID, "locationInput")
        search_button = browser.find_element(By.ID, "searchButton")

        location_input.send_keys(TEST_LOCATION)
        search_button.click()

        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.ID, "city_state"), TEST_LOCATION)
        )

        location_header = browser.find_element(By.ID, "city_state")
        assert location_header.text == TEST_LOCATION


    def test_time_updated(self, browser):
        """Tests if the time of weather update is in the correct format of "Updated at Local Time: hh:mm"."""
        # Is the default page actually supposed to be different? It says "Updated: hh:mm" instead.
        # I was testing with both versions being valid, but decided this changing text is probably a bug.
        # Switch to the commented out code if it isn't.

        time_updated = browser.find_element(By.ID, "updated_time")

        pattern = r"^(Updated at Local Time:) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        time_updated_correct = bool(re.match(pattern, time_updated.text))
        assert time_updated_correct

        # """Tests if the time of weather update is in the correct format of "Updated at Local Time: hh:mm" or "Updated: hh:mm" for first load."""

        # time_updated = browser.find_element(By.ID, "updated_time")

        # pattern = r"^Updated: (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        # time_updated_before_search = bool(re.match(pattern, time_updated.text))

        # pattern = r"^(Updated at Local Time:) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"
        # time_updated_after_search = bool(re.match(pattern, time_updated.text))
        
        # assert time_updated_before_search or time_updated_after_search


    def test_current_temp(self, browser):
        """Tests if the current temperature is a number followed by °F or °C with no space.
        It allows there to be a negative sign."""

        current_temp = browser.find_element(By.ID, "current_temp")
        pattern = r"^-?\d+(°F|°C)$"
        assert bool(re.match(pattern, current_temp.text))


    def test_feels_like_temp(self, browser):
        """Tests if current feels like temp is a number followed by °F or °C with no space.
        It allows there to be a negative sign."""

        feels_like_temp = browser.find_element(By.ID, "like_temp")
        pattern = r"^(Feels like) -?\d+(°F|°C)$"
        assert bool(re.match(pattern, feels_like_temp.text))


    def test_weather_icon_and_text(self, browser):
        """Tests if the current weather icon and weather condition description are displayed and
        the weather icons's alt text matches the weather condition description."""
        
        current_weather_icon = browser.find_element(By.CLASS_NAME, "weather-icon")
        current_weather_description = browser.find_element(By.CLASS_NAME, "cur_condition")

        assert current_weather_icon.is_displayed()
        assert current_weather_description.is_displayed()

        assert current_weather_icon.get_attribute("alt") == current_weather_description.text


    def test_weather_table(self, browser):
        """Tests if the table in the current weather card displays the correct information by checking
        if maximum and minimum temperature, uv, precipitation, and wind speed are correctly displayed.
        This means these formats should be being used:
        Temperature: An optional negative sign then a number followed by °F or °C with no spaces
        UV: A number from 0 to 10 or 11+ with no spaces. 11+ is the highest uv index and the only one with a plus.
        Precipitation: A number from 0 - 100 followed by a % with no spaces.
        Wind Speed: A number followed by mph or km/h with a space in the middle."""
        
        max_temp = browser.find_element(By.ID, "max_temp")
        min_temp = browser.find_element(By.ID, "min_temp")
        uv = browser.find_element(By.ID, "uv")
        precipitation = browser.find_element(By.ID, "precip")
        wind_speed = browser.find_element(By.ID, "wind_speed")

        temp_pattern = r"^-?\d+(°F|°C)$"
        assert bool(re.match(temp_pattern, max_temp.text)) and bool(re.match(temp_pattern, min_temp.text))

        uv_pattern = r"^([0-9]|10|11\+)$"
        assert bool(re.match(uv_pattern, uv.text))

        precip_pattern = r"^(\d{1,2}|100)%$"
        assert bool(re.match(precip_pattern, precipitation.text))

        wind_speed_pattern = r"\d+ (mph|km/h)"
        assert bool(re.match(wind_speed_pattern, wind_speed.text))


    def test_hourly_forecast_card_hours(self, hour_cards):
        """Tests if there are six cards, the hours in each of the hour cards are in the format "hh:00",
        the hour doesn't go past 23, and each is one more hour than the previous."""

        assert len(hour_cards) == 6

        time_pattern = r"(0[0-9]|1[0-9]|2[0-3]):00"
        prev_time = -1
        for i in range(6):
            time = hour_cards[i].find_element(By.CLASS_NAME, f"time{i}").text
            assert bool(re.match(time_pattern, time))

            time = int(time.split(":")[0])
            if i != 0:
                if prev_time == 23 and time == 0:
                    pass
                else:
                    assert time == prev_time + 1
            
            prev_time = time


    def test_hourly_forecast_card_temperature(self, hour_cards):
        """Tests if there are six cards and if the temperatures in each of the hour cards are in the format of
        a number with an optional negative sign followed by °F or °C with no spaces."""

        assert len(hour_cards) == 6

        pattern = r"^-?\d+(°F|°C)$"
        for i in range(6):
            temp = hour_cards[i].find_element(By.CLASS_NAME, f"temp{i}").text
            assert bool(re.match(pattern, temp))


    def test_hourly_forecast_card_precip_chance(self, hour_cards):
        """Tests if there are six hour cards and if the precipitation chance in each of the cards is in
        the correct format of a number without trailing zeroes from 1 - 100 with a % with no spaces."""

        assert len(hour_cards) == 6

        precip_pattern = r"^(\d{1,2}|100)%$"
        for i in range(6):
            chance = hour_cards[i].find_element(By.CLASS_NAME, f"precip{i}").text
            assert bool(re.match(precip_pattern, chance))


    def test_hourly_forecast_card_icon_and_text(self, hour_cards):
        """Tests if there are six hour cards, the weather icon and weather condition description are displayed in each,
        and the weather icons's alt text matches the weather condition description in each."""

        assert len(hour_cards) == 6

        for i in range(6):
            weather_desc = hour_cards[i].find_element(By.CLASS_NAME, f"description{i}").text
            weather_icon_element = hour_cards[i].find_element(By.CLASS_NAME, f"hour-icon{i}")
            weather_icon_alt = weather_icon_element.get_attribute("alt")

            assert weather_desc == weather_icon_alt




class TestNavigationFromHomePage:
    def test_navigation_to_settings(self, browser):
        settings_link = browser.find_element(By.LINK_TEXT, "Settings")
        settings_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_contains("/settings")
        )

        assert "/settings" in browser.current_url
        browser.back()


    def test_navigation_to_hourly(self, browser):
        hourly_link = browser.find_element(By.LINK_TEXT, "Hourly")
        hourly_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_contains("/hourly")
        )

        assert "/hourly" in browser.current_url
        browser.back()
    

    def test_navigation_to_forecast(self, browser):
        forecast_link = browser.find_element(By.LINK_TEXT, "Forecast")
        forecast_link.click()

        WebDriverWait(browser, 10).until(
            EC.url_contains("/forecast")
        )

        assert "/forecast" in browser.current_url
        browser.back()
