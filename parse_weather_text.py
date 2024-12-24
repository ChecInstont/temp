
import json
import re
from datetime import datetime

def parse_weather_text(weather_text):
    # Define a dictionary to store the structured data
    weather_data = {}

    # Extract the date, city, and temperature details using regular expressions
    # date_time_match = re.search(r"(\w+\s\d{1,2},\s\d{1,2}:\d{2}[apm]+)", weather_text)
    # Get the current date and time
    current_datetime = datetime.now()
    
    # Format the date and time in a specific format (e.g., "Dec 24, 01:33pm")
    formatted_datetime = current_datetime.strftime("%b %d, %I:%M%p")
    
    city_match = re.search(r"([A-Za-z]+,\sIN)", weather_text)
    temperature_match = re.search(r"(\d{1,2}°C)", weather_text)
    
    # Update to capture the full description after "Feels like"
    description_match = re.search(r"Feels like \d{1,2}°C\.\s([A-Za-z\s.]+)", weather_text)
    feels_like_match = re.search(r"Feels like \d{1,2}°C", weather_text)  # Capture the "Feels like" part
    
    wind_match = re.search(r"(\d+\.\d+)m/s\s([A-Za-z]+)", weather_text)
    pressure_match = re.search(r"(\d{4})hPa", weather_text)
    humidity_match = re.search(r"Humidity:\s(\d+)%", weather_text)
    uv_match = re.search(r"UV:\s(\d+)", weather_text)
    dew_point_match = re.search(r"Dew point:\s(\d{1,2}°C)", weather_text)
    visibility_match = re.search(r"Visibility:\s(\d+\.\d+)km", weather_text)

    # Populate the dictionary with extracted values
    weather_data['city'] = city_match.group(1) if city_match else None
    weather_data['utc_date_time'] = formatted_datetime
    weather_data['temperature'] = temperature_match.group(1) if temperature_match else None
    
    # Include "Feels like" temperature and the rest of the description in the description field
    if feels_like_match and description_match:
        weather_data['description'] = f"{feels_like_match.group(0)}. {description_match.group(1).strip()}"
    else:
        weather_data['description'] = None

    weather_data['wind'] = {
        "speed": f"{wind_match.group(1)} m/s" if wind_match else None,
        "direction": wind_match.group(2) if wind_match else None
    }
    weather_data['pressure'] = f"{pressure_match.group(1)} hPa" if pressure_match else None
    weather_data['humidity'] = f"{humidity_match.group(1)}%" if humidity_match else None
    weather_data['UV_index'] = uv_match.group(1) if uv_match else None
    weather_data['dew_point'] = dew_point_match.group(1) if dew_point_match else None
    weather_data['visibility'] = f"{visibility_match.group(1)} km" if visibility_match else None

    # Return the structured weather data as a JSON object
    return weather_data
