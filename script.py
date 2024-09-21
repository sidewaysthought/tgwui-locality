"""
This script is an extension for Text Generation WebUI
"""

import json
import datetime
import pytz
import geocoder
import requests
import gradio as gr
import os

# Get the path of the current script (script.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path for the settings file
SETTINGS_FILE = "settings.json"

# Default settings
default_params = {
    "add_time": True,
    "add_date": True,
    "add_timezone": True,
    "add_location": True,
    "add_weather": True,
    "timezone": "UTC"  # Default timezone
}

# Open Meteo weather code map
weather_code_map = {
    0: "Clear",
    1: "Mostly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm: Slight or Moderate",
    96: "Thunderstorm With Light Hail",
    99: "Thunderstorm With Heavy Hail"
}

params = {
    "display_name": "Locality",
    "is_tab": False,
    "add_time": True,
    "add_date": True,
    "add_timezone": True,
    "add_location": True,
    "add_weather": True,
    "timezone": "UTC"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        return default_params
    
def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(params, f)

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
    
    modified_text = f"{text}\n[{' | '.join(additions)}]" if additions else text
    return modified_text, visible_text

def ui():
    def update_add_time(value):
        params["add_time"] = value
        save_settings()

    def update_add_date(value):
        params["add_date"] = value
        save_settings()

    def update_add_timezone(value):
        params["add_timezone"] = value
        save_settings()

    def update_timezone(value):
        params["timezone"] = value
        save_settings()

    def update_add_location(value):
        params["add_location"] = value
        save_settings()

    def update_add_weather(value):
        params["add_weather"] = value
        save_settings()

    with gr.Accordion("Locality Settings", open=False):  # Render closed by default
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

params = load_settings()