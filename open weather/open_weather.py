import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
import requests
# Your OpenWeather API key
API="################################"
# Map weather descriptions to emojis
WEATHER_EMOJI = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌁",
    "haze": "🌫️",
}

def get_weather_emoji(desc):
    desc = desc.lower()
    for key in WEATHER_EMOJI:
        if key in desc:
            return WEATHER_EMOJI[key]
    return "🌈"  # default emoji

def get_weather_and_forecast(city_name):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city_name, "appid": API, "units": "metric"}

    try:
        current_response = requests.get(base_url, params=params)
        forecast_response = requests.get(forecast_url, params=params)

        if current_response.status_code != 200:
            messagebox.showerror("Error", f"City not found or API error: {current_response.json().get('message','')}")
            return None, None

        return current_response.json(), forecast_response.json()
    except requests.RequestException as e:
        messagebox.showerror("Network Error", str(e))
        return None, None

def format_forecast(forecast_data):
    forecast_list = forecast_data.get("list", [])
    daily_forecast = {}
    for entry in forecast_list:
        dt_txt = entry["dt_txt"]
        date = dt_txt.split(" ")[0]
        time = dt_txt.split(" ")[1]
        if time == "12:00:00":
            daily_forecast[date] = entry

    forecast_str = ""
    for date, info in daily_forecast.items():
        temp = info["main"]["temp"]
        desc = info["weather"][0]["description"].capitalize()
        emoji = get_weather_emoji(desc)
        forecast_str += f"{date}: {emoji} {temp}°C, {desc}\n"
    return forecast_str.strip()

def update_maps(lat, lon, city_name):
    for map_obj in [street_map, satellite_map, water_map]:
        map_obj.set_position(lat, lon)
        map_obj.set_marker(lat, lon, text=city_name)
        map_obj.set_zoom(10)

def search_weather():
    city_name = city_entry.get().strip()
    if not city_name:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    current_data, forecast_data = get_weather_and_forecast(city_name)
    if current_data is None:
        return

    weather_desc = current_data["weather"][0]["description"].capitalize()
    emoji = get_weather_emoji(weather_desc)
    temp = current_data["main"]["temp"]
    feels_like = current_data["main"]["feels_like"]
    humidity = current_data["main"]["humidity"]
    wind_speed = current_data["wind"]["speed"]
    pressure = current_data["main"]["pressure"]

    weather_info = (
        f"Weather in {city_name}:\n"
        f"{emoji} Condition: {weather_desc}\n"
        f"🌡️ Temperature: {temp}°C (Feels like {feels_like}°C)\n"
        f"💧 Humidity: {humidity}%\n"
        f"🌬️ Wind Speed: {wind_speed} m/s\n"
        f"🔽 Pressure: {pressure} hPa"
    )
    weather_label.config(text=weather_info)

    forecast_str = format_forecast(forecast_data)
    forecast_label.config(text=f"5-Day Forecast (at 12:00):\n{forecast_str}")

    lat = current_data["coord"]["lat"]
    lon = current_data["coord"]["lon"]
    update_maps(lat, lon, city_name)

# --- Tkinter UI setup ---

root = tk.Tk()
root.title("Weather App with 3 Maps and Forecast")
root.geometry("1500x800")
root.configure(bg="#e6f0ff")

# Load and display logo
try:
    logo_img = tk.PhotoImage(file="logo.png")  # Put your logo image here
    logo_label = ttk.Label(root, image=logo_img, background="#e6f0ff")
    logo_label.pack(pady=5)
except Exception as e:
    print("Logo not loaded:", e)

# Search input
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

city_entry = ttk.Entry(input_frame, width=40, font=("Arial", 14))
city_entry.pack(side=tk.LEFT, padx=5)

search_btn = ttk.Button(input_frame, text="Search Weather", command=search_weather)
search_btn.pack(side=tk.LEFT)

# Maps frame (top)
maps_frame = ttk.Frame(root)
maps_frame.pack(pady=10, fill=tk.X)

# Map 1: Street
street_map = TkinterMapView(maps_frame, width=480, height=350, corner_radius=15)
street_map.grid(row=0, column=0, padx=10, pady=5)
street_map.set_tile_server("https://tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)

# Map 2: Satellite
satellite_map = TkinterMapView(maps_frame, width=480, height=350, corner_radius=15)
satellite_map.grid(row=0, column=1, padx=10, pady=5)
satellite_map.set_tile_server("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", max_zoom=19)

# Map 3: Water Map + OpenSeaMap overlay
water_map = TkinterMapView(maps_frame, width=480, height=350, corner_radius=15)
water_map.grid(row=0, column=2, padx=10, pady=5)
water_map.set_tile_server("https://tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)
try:
    water_map.add_tile_layer(
        "OpenSeaMap Overlay",
        "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        tile_size=256,
        max_zoom=18,
        min_zoom=0,
        opacity=0.7,
    )
except Exception as e:
    print("Could not add OpenSeaMap overlay:", e)

# Bottom frame for weather info and forecast
bottom_frame = ttk.Frame(root)
bottom_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

# Weather info (left)
weather_frame = ttk.LabelFrame(bottom_frame, text="Current Weather", width=700)
weather_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10), pady=10)

weather_label = ttk.Label(weather_frame, text="Enter city and press Search", font=("Arial", 12), justify=tk.LEFT)
weather_label.pack(padx=10, pady=10)

# Forecast info (right)
forecast_frame = ttk.LabelFrame(bottom_frame, text="5-Day Forecast (12:00 PM)", width=700)
forecast_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=10)

forecast_label = ttk.Label(forecast_frame, text="", font=("Arial", 11), justify=tk.LEFT)
forecast_label.pack(padx=10, pady=10)

root.mainloop()
