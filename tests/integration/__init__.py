def test_forecast_repository_fetch():
    from app.services.repository import get_cached_forecast

    result = get_cached_forecast("New York")
    assert result is not None
