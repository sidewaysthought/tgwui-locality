# script.py

import datetime
import pytz
import geocoder
import requests
import gradio as gr

weather_code_map = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

params = {
    "display_name": "DateTime, Timezone, Location, and Weather Extension",
    "is_tab": False,
    "add_time": True,
    "add_date": True,
    "add_timezone": True,
    "add_location": True,
    "add_weather": True,
    "timezone": "UTC"  # Default timezone
}

def get_location():
    try:
        g = geocoder.ip('me')
        return g.city, g.country, g.latlng
    except Exception as e:
        return "Location unavailable", "Unknown", None

def get_weather(lat, lon):
    if not lat or not lon:
        return "Weather unavailable"
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        data = response.json()

        # Extract weather information
        weather_code = data['current_weather']['weathercode']
        temp = data['current_weather']['temperature']
        
        # Get the description from the weather code map
        weather_desc = weather_code_map.get(weather_code, "Unknown weather condition")
        return f"{weather_desc}, {temp}°C"
    except Exception as e:
        return "Weather unavailable"

def chat_input_modifier(text, visible_text, state):
    additions = []
    now = datetime.datetime.now(pytz.timezone(params["timezone"]))
    
    if params["add_time"]:
        current_time = now.strftime("%I:%M %p")
        additions.append(f"Current time: {current_time}")
    
    if params["add_date"]:
        current_date = now.strftime("%B %d, %Y")
        additions.append(f"Current date: {current_date}")
    
    if params["add_timezone"]:
        current_timezone = params["timezone"]
        additions.append(f"Timezone: {current_timezone}")
    
    if params["add_location"]:
        city, country, latlng = get_location()
        additions.append(f"Location: {city}, {country}")
        
        if params["add_weather"] and latlng:
            weather = get_weather(latlng[0], latlng[1])
            additions.append(f"Weather: {weather}")
    
    # Append metadata only to the model's input, not the visible text (chat history)
    modified_text = f"{text}\n[{' | '.join(additions)}]" if additions else text
    return modified_text, visible_text  # Leave visible_text unchanged

def ui():
    def update_add_time(value):
        params["add_time"] = value

    def update_add_date(value):
        params["add_date"] = value

    def update_add_timezone(value):
        params["add_timezone"] = value

    def update_timezone(value):
        params["timezone"] = value

    def update_add_location(value):
        params["add_location"] = value

    def update_add_weather(value):
        params["add_weather"] = value

    with gr.Accordion("DateTime, Timezone, Location, and Weather Settings"):
        add_time_checkbox = gr.Checkbox(
            label="Add Current Time", value=params["add_time"]
        )
        add_date_checkbox = gr.Checkbox(
            label="Add Current Date", value=params["add_date"]
        )
        add_timezone_checkbox = gr.Checkbox(
            label="Add Timezone", value=params["add_timezone"]
        )
        add_location_checkbox = gr.Checkbox(
            label="Add Location", value=params["add_location"]
        )
        add_weather_checkbox = gr.Checkbox(
            label="Add Weather", value=params["add_weather"]
        )
        timezone_dropdown = gr.Dropdown(
            label="Select Timezone",
            choices=pytz.all_timezones,
            value=params["timezone"]
        )

        add_time_checkbox.change(update_add_time, add_time_checkbox, None)
        add_date_checkbox.change(update_add_date, add_date_checkbox, None)
        add_timezone_checkbox.change(update_add_timezone, add_timezone_checkbox, None)
        add_location_checkbox.change(update_add_location, add_location_checkbox, None)
        add_weather_checkbox.change(update_add_weather, add_weather_checkbox, None)
        timezone_dropdown.change(update_timezone, timezone_dropdown, None)
