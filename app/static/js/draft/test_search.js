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
        console.log('About to send request to:', '/api/location');
        console.log('With data:', cur_location);

        if (!parseCityState(inputValue)) {
            alert('Please enter a valid city, state, or postal code.');
            
        }
        else {
            console.log('Parsed location:', cur_location);
        }


        const response = await fetch('/api/location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cur_location)
        });
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        console.log('Response body:', response.body);

        const data = await response.json();
        console.log('Response data:', data);
        // Log the value to the console
        console.log('Search input value:', inputValue);
        
        // Optionally, show an alert to make it more visible
        // alert('You entered: ' + inputValue);
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