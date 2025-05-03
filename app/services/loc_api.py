# refactored by tony
# add _process_location_components()
# using logging instead of print


import requests
import logging

from app.utils.constants import STATE_TO_ABBREV

# Create module-level logger
logger = logging.getLogger(__name__)


class LocService:
    def __init__(self, location):
        """Initialize with location data"""
        # Check if location dictionary has required keys
        if location and len(location) > 0:
            # Use direct dictionary access with proper error handling
            try:
                self.loc = {
                    "postal_code": (
                        location["postal_code"] if location["postal_code"] else None
                    ),
                    "city": location["city"] if location["city"] else None,
                    "state": location["state"] if location["state"] else None,
                }
            except KeyError:
                # If any key is missing, initialize with None values
                self.loc = {"postal_code": None, "city": None, "state": None}
        else:
            self.loc = {"postal_code": None, "city": None, "state": None}

    def fetch_location(self, params, s_type=0):
        """Fetch location data from Nominatim API"""
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "weather-dashboard-app/1.0 (tony@example.com)"}

        try:
            logger.debug(f"Calling Nominatim API with params: {params}")
            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            # Find US location in results
            index_num = -1
            for i in range(len(data)):
                if "United States" in data[i]["display_name"]:
                    index_num = i
                    break

            # Handle missing data cases
            if not data:
                logger.warning("No location data returned from API")
                return {}

            if index_num == -1:
                # Use proper logging instead of print
                logger.warning(f"No US location found for params: {params}")
                return {}

            # Process location data
            loc_str = [
                part.strip() for part in data[index_num]["display_name"].split(",")
            ]

            # Create return data structure
            return_data = self._process_location_components(
                loc_str, data[index_num], params, s_type
            )

            return return_data

        except Exception as e:
            logger.error(f"Error fetching location data: {e}")
            return {}

    def _process_location_components(self, components, location_data, params, s_type):
        """Process location components based on format and search type"""
        return_data = {
            "lat": location_data["lat"],
            "lon": location_data["lon"],
            "postal_code": "",
            "city": "",
            "state": "",
        }

        # Add city_state as a convenience field
        if return_data["city"] and return_data["state"]:
            return_data["city_state"] = f"{return_data['city']}, {return_data['state']}"

        try:
            component_count = len(components)

            # Handle different component formats based on length
            if component_count == 3:
                if s_type == 1:  # City/state search
                    return_data["city"] = components[0]
                    return_data["state"] = STATE_TO_ABBREV.get(
                        components[1], components[1]
                    )

            elif component_count == 4:
                if s_type == 0:  # Postal code search
                    return_data["postal_code"] = params.get("postalcode", "")
                    return_data["city"] = components[1]
                    try:
                        return_data["state"] = STATE_TO_ABBREV[components[2]]
                    except KeyError:
                        return_data["state"] = components[2]
                elif s_type == 1:  # City/state search
                    return_data["city"] = components[0]
                    try:
                        return_data["state"] = STATE_TO_ABBREV[components[2]]
                    except KeyError:
                        return_data["state"] = components[2]

            elif component_count == 5:
                if s_type == 0:
                    return_data["postal_code"] = components[0]
                    return_data["city"] = components[1]
                    try:
                        return_data["state"] = STATE_TO_ABBREV[components[3]]
                    except KeyError:
                        return_data["state"] = components[3]
                elif s_type == 1:
                    return_data["city"] = components[0]
                    try:
                        return_data["state"] = STATE_TO_ABBREV[components[2]]
                    except KeyError:
                        return_data["state"] = components[2]

            elif component_count == 6:
                return_data["postal_code"] = components[0]
                return_data["city"] = components[1]
                try:
                    return_data["state"] = STATE_TO_ABBREV[components[4]]
                except KeyError:
                    return_data["state"] = components[4]

        except (IndexError, KeyError) as e:
            logger.error(f"Error processing location components: {e}")
            # Use default values if parsing fails
            return_data["city"] = return_data["city"] or "Unknown"
            return_data["state"] = return_data["state"] or "US"

        return return_data

    def get_lat_lon(self, location):
        """Get location data from postal code or city/state"""
        params = {}
        search_type = 0

        try:
            if location["postal_code"]:
                params = {
                    "postalcode": location["postal_code"],
                    "format": "json",
                }
            elif location["city"] and location["state"]:
                params = {
                    "city": location["city"],
                    "state": location["state"],
                    "format": "json",
                }
                search_type = 1
            else:
                logger.warning("Empty location data provided")
                return {}
        except KeyError as e:
            logger.error(f"Missing key in location data: {e}")
            return {}

        return self.fetch_location(params, s_type=search_type)

    def show_lat_lon(self):
        """Get location data using the object's stored location information"""
        try:
            # Use the get_lat_lon method to avoid code duplication
            return self.get_lat_lon(self.loc)
        except Exception as e:
            logger.error(f"Error in show_lat_lon: {e}")
            return {}


# # debug
# cur_location = {"postal_code": "92210", "city": "", "state": ""}  # 92210

# loc_service = LocService(cur_location)
# print(f"\n-----------------------------------------------")
# print(f"show  {loc_service.show_lat_lon()}")
# print(f"-----------------------------------------------")
# lat_json = loc_service.get_lat_lon(cur_location)
# print(f"lat_json: {lat_json}")
# print(f"-----------------------------------------------")
# if lat_json:
#     print(f"Location found: {lat_json}")
# # print(f"Latitude: {lat_json['lat']}, Longitude: {lat_json['lon']}")
# # debug
