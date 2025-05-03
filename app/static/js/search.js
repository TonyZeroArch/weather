cur_location = { postal_code: "27587", city: "", state: "" };
        
document.addEventListener('DOMContentLoaded', function () {
    // Get references to the input field and button
    const searchButton = document.getElementById('searchButton');
    const locationInput = document.getElementById('locationInput');
    
    // Add click event listener to the search button
    searchButton.addEventListener('click', async function(event) {
        // Prevent the form from submitting and refreshing the page
        event.preventDefault();
        // cur_location = {postal_code: "27587", city: "", state: ""};
        // Get the input value and trim whitespace
        const inputValue = locationInput.value.trim();
        console.log('About to send request to:', '/search');
        console.log('With data:', cur_location);

        if (!parseCityState(inputValue)) {
            alert('Please enter a valid city, state, or postal code. For example: "Raleigh, NC" or "27587".');
            
        }
        else {

            console.log('Parsed location:', cur_location);

            const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cur_location)
            });
            //debugging
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            console.log('Response body:', response.body);

            
            // After getting the response object
            try {
                console.log('About to parse response data...');
                
                // Show a loading indicator if you have one
                // document.getElementById('loadingIndicator').style.display = 'block';
                
                // Parse the JSON response - this awaits the full data download
                const data = await response.json();
                
                // Hide loading indicator
                // document.getElementById('loadingIndicator').style.display = 'none';
                
                console.log('Data received and parsed:', data);
                
                // First, verify we have valid data
                if (JSON.stringify(data) === '{}') {
                    console.log('Data is null or undefined');
                    alert('Invalid Zip Code or city. Please try again.');
                    return;
                }
                else {
                    console.log('Data is valid:', data);
                    //deal with the data
                    try { 
                            // Update location and time
                            document.getElementById('city_state').textContent = 
                                `${data.city || 'Unknown'}, ${data.state || ''}`;
                        
                            // Create a proper link element
                            const cityState = `${data.city || 'Unknown'}, ${data.state || ''}`;
                            // Clear existing content
                            document.getElementById('city_state').innerHTML = '';  // Clear existing content
                            
                            const locationLink = document.createElement('a');
                            locationLink.href = `/forecast/`;
                            locationLink.textContent = cityState;
                            locationLink.className = 'forecast-link';  // Optional - for styling
                            
                            // Append the new link to the city_state element
                            document.getElementById('city_state').appendChild(locationLink);       
                        
                                // Update current time
                            const now = new Date();
                            document.getElementById('updated_time').textContent = 
                                // `Updated: ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                                `Updated at Local Time: ${data.updated_time}`;                            
                            // Update temperatures
                            document.getElementById('current_temp').textContent = 
                                `${Math.round(data.current_temperature_2m)}°F`;
                            document.getElementById('like_temp').textContent = 
                                `Feels like ${Math.round(data.current_apparent_temperature)}°F`;
                            
                            // Update high/low temperatures
                            document.getElementById('max_temp').textContent = 
                                `${Math.round(data.daily_temperature_2m_max)}°F`;
                            document.getElementById('min_temp').textContent = 
                                `${Math.round(data.daily_temperature_2m_min)}°F`;
                            
                            // Update other weather information
                            document.getElementById('uv').textContent = 
                                Math.round(data.daily_uv_index_max);
                            document.getElementById('precip').textContent = 
                                `${data.daily_precipitation_probability_max}`;
                            document.getElementById('wind_speed').textContent = 
                                `${Math.round(data.current_wind_speed_10m)} mph`;
                            // document.getElementById('humidity').textContent = 
                            //     `${data.humidity || 0}%`;
                            
                            // Update weather condition and icon
                            const weatherDesc = data.description || 'Unknown';
                            document.querySelector('.cur_condition').textContent = weatherDesc;

                                //debugging
                            console.log('Weather description:', weatherDesc);
                            

                        
                            document.querySelector('.weather-info img').src = 
                                data.icon;
                            document.querySelector('.weather-info img').alt = weatherDesc;   
                        
                        
                            // Update hourly forecast
                            updateHourlyForecast(data);
                            //debugging
                            console.log('Weather icon URL:', data.icon);
                        

                    } catch (error) {
                        console.error('Error processing data:', error);
                        alert('Failed to process server data: ' + error.message);
                    }
                    
                }
                

    
            } catch (error) {
                // Hide loading indicator if there was an error
                // document.getElementById('loadingIndicator').style.display = 'none';
                
                console.error('Error processing response:', error);
                alert('Failed to process server response: ' + error.message);
}

        }
        
    });
    
    // Also handle pressing Enter in the input field
    locationInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            // Prevent default form submission
            event.preventDefault();
            // Trigger the button click
            searchButton.click();
        }
    });



});

// Function to update hourly forecast with indexed classes
function updateHourlyForecast(data) {
    // Get the hourly forecast container
    const hourlyForecastContainer = document.querySelector('.hourly-forecast');
    
    // Clear existing content
    hourlyForecastContainer.innerHTML = '';
    
    // Check if we have hourly data
    if (data.hours && data.hours.length > 0) {
        // Loop through the hours data and create elements with indexed classes
        for (let i = 0; i < data.hours.length; i++) {
            // Create hour div with indexed class
            const hourDiv = document.createElement('div');
            hourDiv.className = `hour${i}`;
            
            // Create time paragraph with indexed class
            const timeP = document.createElement('p');
            timeP.className = `time${i}`;
            timeP.textContent = data.hours[i];
            
            // Create temperature paragraph with indexed class
            const tempP = document.createElement('p');
            tempP.className = `temp${i}`;
            tempP.textContent = `${Math.round(data.hourly_temperature_2m[i])}°F`;
            
            // Create precipitation paragraph with indexed class
            const precipP = document.createElement('p');
            precipP.className = `precip${i}`;
            precipP.textContent = `${Math.round(data.hourly_precipitation_probability[i])}%`;
            
            // Create description paragraph with indexed class
            const descP = document.createElement('p');
            descP.className = `description${i}`;
            descP.textContent = data.description_hourly[i] || 'Unknown';
            
            // Create weather icon with indexed class
            const iconImg = document.createElement('img');
            iconImg.src = data.icon_hourly[i];
            iconImg.alt = data.description_hourly[i] || 'Weather icon';
            iconImg.className = `hour-icon${i}`;
            
            // Append all elements to hour div
            hourDiv.appendChild(timeP);
            hourDiv.appendChild(tempP);
            hourDiv.appendChild(precipP);
            hourDiv.appendChild(descP);
            hourDiv.appendChild(iconImg);
            
            // Append hour div to container
            hourlyForecastContainer.appendChild(hourDiv);
        }
    } else {
        // If no hourly data is available
        hourlyForecastContainer.innerHTML = '<p class="no-data">Hourly forecast not available</p>';
    }
}

function parseCityState(input) {
    const validStates = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
        "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
        "VA", "WA", "WV", "WI", "WY", "DC"
    ];

    
    const trimmed = input.trim();
    const code_regex = /^\d{5}$/;
    const loc_regex = /^([A-Za-z\s.'-]+),\s*([A-Za-z]{2})$/;
  
    if (code_regex.test(trimmed)) {
        cur_location.postal_code = trimmed;
        cur_location.city = "";
        cur_location.state = "";
        return true
    }
    else if (loc_regex.test(trimmed)) {
        const match = trimmed.match(loc_regex);
        cur_location.postal_code = "";
        cur_location.city = match[1].trim();
        cur_location.state = match[2].toUpperCase();
        return true
    }
    else
       
        return false;
    // Check if the state code is valid
}

// Helper function to determine weather icon in local files
// function getWeatherIcon(weatherCode) {
//     // Map weather codes to icon filenames
//     const iconMap = {
//         0: 'sunny.png',          // Clear sky
//         1: 'partly-cloudy.png',  // Mainly clear
//         2: 'partly-cloudy.png',  // Partly cloudy
//         3: 'cloudy.png',         // Overcast
//         // Add more mappings as needed
//     };
    
//     return iconMap[weatherCode] || 'unknown.png';
// }