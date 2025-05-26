import requests
import pygame
import sys
from datetime import datetime
from io import BytesIO
from config import my_key

API_KEY = my_key
URL_DATA = "https://api.openweathermap.org/data/2.5/weather"
URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather(city, language):
    """Gets the weather in Hungarian or in English based on the location's name."""
    # Request for current weather
    response_1 = requests.get(URL_DATA,
                              params={"q": city, "appid": API_KEY,
                                      "lang": language, "units": "metric"})
    # Request for weather forecast
    response_2 = requests.get(URL_FORECAST,
                              params={"q": city, "appid": API_KEY,
                                      "lang": language, "units": "metric"})

    data_1 = response_1.json()
    data_2 = response_2.json()

    # Handling status codes
    if response_1.status_code == 200:
        # Datas for current weather
        current_weather = data_1["weather"][0]["description"]
        current_temp = int(data_1["main"]["temp"])
        current_feels_like = int(data_1["main"]["feels_like"])
        current_wind_speed_m_s = data_1["wind"]["speed"]
        current_wind_speed_k_h = int(current_wind_speed_m_s * 3.6)  # m/s-->km/h
        icon_code = data_1["weather"][0]["icon"]

        # Datas for weather forecast
        forecast_data = []
        for entry in data_2["list"]:
            if "rain" in entry and "3h" in entry["rain"]:
                forecast_rain = entry["rain"]["3h"]
            else:
                forecast_rain = 0
            timestamp = entry["dt"]
            date_time = datetime.fromtimestamp(timestamp)
            formatted_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
            forecast_entry = {
                "datetime": formatted_date,
                "weather": entry["weather"][0]["main"],
                "temp": int(entry["main"]["temp"]),
                "feels_like": int(entry["main"]["feels_like"]),
                "wind_speed": int(entry["wind"]["speed"] * 3.6),  #m/s-->km/h
                "rain": forecast_rain
            }
            forecast_data.append(forecast_entry)

        # Return the data so we can use it later
        return (current_weather, current_temp, current_feels_like,
                current_wind_speed_k_h, forecast_data, icon_code)

    # Handle errors
    if response_1.status_code == 401:
        print("401: Unauthorized: hibás API kulcs!" if language == "hu" else "401: Unauthorized: Wrong API key!")
    elif response_1.status_code == 404:
        print("404: Not Found: rosszul beírt adat!" if language == "hu" else "404: Not Found: Wrong data!")
    elif response_1.status_code == 429:
        print("429: Too many requests: Túl sok adatlekérés!" if language == "hu" else "429: Too many requests!")
    else:
        # For other errors, provide a generic message
        print(f"Hiba: {data_1['message']}!" if language == "hu" else f"Error: {data_1['message']}!")
    return None


def load_weather_icon(icon_code):
    """Loads the icons based on the weather"""
    url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    response = requests.get(url)
    icon_data = BytesIO(response.content)  # loads the image, but won't save it
    return pygame.image.load(icon_data)


# PYGAME
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Időjárás alkalmazás / Weather app")
font = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()
icon = pygame.image.load("sun.png")
pygame.display.set_icon(icon)

input_box = pygame.Rect(100, 100, 200, 40)
lang_button = pygame.Rect(320, 100, 100, 40)
color_inactive = pygame.Color('gray')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ""
language = "hu"
weather_data = None
weather_icon = None

def draw_text(surface, text, pos, font, color=(255, 255, 255)):
    surface.blit(font.render(text, True, color), pos)

# Main loop
while True:
    screen.fill((40, 40, 60))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
            if lang_button.collidepoint(event.pos):
                language = "en" if language == "hu" else "hu"

        # Check if a key is pressed and the input field is active
        if event.type == pygame.KEYDOWN and active:
            # If the user presses Enter (Return key):
                # Capitalize the city name from the typed text
                # Get weather data for the entered city
            if event.key == pygame.K_RETURN:
                city = text.strip().capitalize()
                result = get_weather(city, language)
                # If the weather data is successfully fetched
                if result:
                    current_weather, current_temp, current_feels_like, wind_speed, forecast_data, icon_code = result
                # Store the data in a dictionary for easy access
                    weather_data = {
                        "weather": current_weather,
                        "temp": current_temp,
                        "feels_like": current_feels_like,
                        "wind": wind_speed,
                        "forecast": forecast_data[0]
                    }
                    weather_icon = load_weather_icon(icon_code)
                # Clear the input text after Enter is pressed
                text = ""

            # If the user presses Backspace, remove the last character from text
            elif event.key == pygame.K_BACKSPACE:
                text = text[:-1]
            # Otherwise, add the typed character to the text
            else:
                text += event.unicode

        # Input field
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Language changing button
        pygame.draw.rect(screen, (70, 70, 90), lang_button)
        draw_text(screen, "EN" if language == "hu" else "HU",
                  (lang_button.x + 30, lang_button.y + 10), font)

        # Show datas based on languages
        if weather_data:
            if language == "hu":
                draw_text(screen, f"Jelenlegi időjárás: {weather_data['weather']}",
                          (100, 180), font)
                draw_text(screen, f"Hőmérséklet: {weather_data['temp']}°C",
                          (100, 220), font)
                draw_text(screen, f"Hőérzet: {weather_data['feels_like']}°C",
                          (100, 260), font)
                draw_text(screen, f"Szélsebesség: {weather_data['wind']} km/h",
                          (100, 300), font)
                draw_text(screen,
                          f"3 óra múlva: {weather_data['forecast']['weather']}, "
                          f"{weather_data['forecast']['temp']}°C",
                          (100, 340), font)
            elif language == "en":
                draw_text(screen, f"Current weather: {weather_data['weather']}",
                          (100, 180), font)
                draw_text(screen, f"Temperature: {weather_data['temp']}°C",
                          (100, 220), font)
                draw_text(screen, f"Feels like: {weather_data['feels_like']}°C",
                          (100, 260), font)
                draw_text(screen, f"Wind speed: {weather_data['wind']} km/h",
                          (100, 300), font)
                draw_text(screen,
                          f"In 3 hours: {weather_data['forecast']['weather']}, "
                          f"{weather_data['forecast']['temp']}°C",
                          (100, 340), font)

            if weather_icon:
                screen.blit(weather_icon, (500, 200))

        pygame.display.flip()
        clock.tick(30)





