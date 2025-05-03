def test_unit_conversion():
    from app.services.unit_service import convert_temperature

    assert convert_temperature(0, "F") == 32


def test_weather_api_mocked(mocker):
    mock_resp = {"temp": 75}
    mocker.patch("app.services.weather_api.fetch_weather", return_value=mock_resp)

    from app.services import weather_service

    data = weather_service.get_weather_data("Raleigh")
    assert data["temp"] == 75
