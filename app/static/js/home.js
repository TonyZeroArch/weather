document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const locationInput = document.getElementById('locationInput');
    
    searchButton.addEventListener('click', async function() {
        const city = locationInput.value.trim();
        
        if (city) {
            try {
                // First, save the search to database
                const saveResponse = await fetch('/api/weather', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query: city })
                });
                
                // Log if search was saved successfully
                const saveResult = await saveResponse.json();
                console.log('Search saved:', saveResult);
                
                // Then proceed with getting weather data
                const weatherResponse = await fetch(`/api/location/?city=${encodeURIComponent(city)}`);
                if (!weatherResponse.ok) throw new Error('Weather data not available');
                
                const weatherData = await weatherResponse.json();
                
                // Update the page with weather data
                document.querySelector('.location h2').textContent = city;
                document.querySelector('.temp-info h1').textContent = `${weatherData.temp}°F`;
                // Update other elements as needed
                
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        } else {
            alert("Please enter a city name or zip code");
        }
    });
    
    // Allow pressing Enter in the input
    locationInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            searchButton.click();
        }
    });
});