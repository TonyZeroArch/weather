document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const locationInput = document.getElementById('locationInput');
    
    searchButton.addEventListener('click', function() {
        const location = locationInput.value.trim();
        if (location) {
            fetchWeatherData(location);
        }
    });
    
    locationInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const location = locationInput.value.trim();
            if (location) {
                fetchWeatherData(location);
            }
        }
    });
    
    function fetchWeatherData(location) {
        // Show loading indicator
        document.querySelector('.weather-info').innerHTML = '<p>Loading weather data...</p>';
        
        fetch(`/api/weather?location=${encodeURIComponent(location)}`)
            .then(response => response.json())
            .then(data => {
                updateWeatherUI(data, location);
            })
            .catch(error => {
                console.error('Error fetching weather data:', error);
                document.querySelector('.weather-info').innerHTML = 
                    '<p>Sorry, we couldn\'t load the weather data. Please try again.</p>';
            });
    }
    
    function updateWeatherUI(data, location) {
        // Update city name with link to forecast
        const cityLink = `<a href="/forecast/${encodeURIComponent(location)}">${location}</a>`;
        
        // Update main weather info
        document.querySelector('.weather-info').innerHTML = `
            <h1 class="location">${cityLink}</h1>
            <h1 class="temp">${data.current.temp}&deg;C</h1>
            <p class="description">${data.current.description}</p>
            <div class="metrics">
                <span>🌬️ Wind: ${data.current.wind}km/h</span>
                <span>💧 Humidity: ${data.current.humidity}%</span>
            </div>
        `;
        
        // Update weather icon
        document.querySelector('.weather-icon img').src = `/static/images/${data.current.icon}`;
        document.querySelector('.weather-icon img').alt = data.current.description;
        
        // Update hourly forecast
        const hourlyForecast = document.querySelector('.hourly-forecast');
        hourlyForecast.innerHTML = '';
        
        data.hourly.forEach((hour, index) => {
            const hourElement = document.createElement('div');
            hourElement.className = `hour ${index === 0 ? 'current' : ''}`;
            hourElement.innerHTML = `
                <p>${hour.time}</p>
                <p>${hour.temp}&deg;</p>
            `;
            hourlyForecast.appendChild(hourElement);
        });
    }
});