# Open-Meteo Weather API Postman Test Case Guide

This guide explains how to use the Postman collection and environment files to test the Open-Meteo Weather API based on the Python script `test_wea_hour_api.py`.

## Importing the Collection and Environment

1. Open Postman.

2. Click on the **Import** button in the top left corner, import both the `Collection.json` and `Environment.json` files.

3. Drag and drop both JSON files into the import dialog or click **Upload Files** to select them.

4. Click **Import** to add them to your Postman workspace.

## Setting Up the Environment

1. In the top right corner of Postman, click on the environment dropdown and select **Open-Meteo Environment**.

2. The environment contains predefined variables:
   - `baseUrl`: Base URL for the API
   - `latitude`: Set to 35.7915 (North Carolina)
   - `longitude`: Set to -78.7811 (North Carolina)
   - `timezone`: Will be populated after the first request
   - `elevation`: Will be populated after the first request

## Running the Test

1. In the Collections sidebar, open the **Open-Meteo Weather API** collection.

2. Click on the **Get 2-Day Weather Forecast** request.

3. Review the request parameters to ensure they match your requirements:
   - `latitude`: 35.7915
   - `longitude`: -78.7811
   - `hourly`: temperature_2m,weather_code,precipitation_probability
   - `daily`: sunrise,sunset
   - `timezone`: auto
   - `forecast_days`: 2
   - `wind_speed_unit`: mph
   - `temperature_unit`: fahrenheit

4. Click the **Send** button to execute the request.

5. View the response in the lower panel.

## Understanding the Test Results

After sending the request, the Tests tab will show the results of automated tests:

1. **Status code is 200**: Verifies the API responded successfully.

2. **Response contains expected properties**: Checks for latitude, longitude, timezone, hourly, and daily data.

3. **Hourly data contains expected properties**: Verifies the hourly data structure.

4. **Daily data contains expected properties**: Verifies the daily data structure.

5. **Hourly data length matches forecast days**: Ensures you received 48 hours (2 days) of hourly data.

6. **Daily data length matches forecast days**: Ensures you received 2 days of daily data.

7. **Timezone is correct**: Checks that the timezone is "America/New_York".

8. **Location coordinates match**: Verifies the returned coordinates match your input.

## Comparing with Python Script Results

The response should match the data from the `collection.json` file:

- **Coordinates**: Should be approximately 35.7915°N, -78.7811°E
- **Elevation**: Should be around 154.0 m asl
- **Timezone**: Should be America/New_York
- **Hourly Data**: Should contain 48 hours of data with:
  - Temperature in Fahrenheit
  - Weather codes
  - Precipitation probability
- **Daily Data**: Should contain 2 days of data with:
  - Sunrise times
  - Sunset times
