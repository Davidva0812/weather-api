import requests
from datetime import datetime


API_KEY = "eeaf414cc92dd9327bb7886f7c4e5f4b"
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
                current_wind_speed_k_h, forecast_data)

    # Handle errors
    if response_1.status_code == 401:
        if language == "hu":
            print("401: Unauthorized: hibás API kulcs!")
        elif language == "en":
            print("401: Unauthorized: Wrong API key!")
        return None  # Ensure we exit early on error
    elif response_1.status_code == 404:
        if language == "hu":
            print("404: Not Found: rosszul beírt adat!")
        elif language == "en":
            print("404: Not Found: Wrong data!")
        return None
    elif response_1.status_code == 429:
        if language == "hu":
            print("429: Too many requests: Túl sok adatlekérés!")
        elif language == "en":
            print("429: Too many requests!")
        return None
    else:
        # For other errors, provide a generic message
        if language == "hu":
            print(f"Hiba: {data_1['message']}!")
        elif language == "en":
            print(f"Error: {data_1['message']}!")
        return None


def display_weather(city, language):
    """Displays the weather datas based on the language."""
    result = get_weather(city, language)

    # If no result (error occurred)
    if result is None:
        return

    current_weather, current_temp, current_feels_like,  current_wind_speed_k_h, forecast_data = result

    # Show datas based on languages
    if language == "hu":
        print(f"{city} jelenlegi időjárása: {current_weather}.")
        print(f"Hőmérséklet: {current_temp}°C, Hőérzet: {current_feels_like}°C.")
        print(f"Szélsebesség: {current_wind_speed_k_h} km/h.")
        print(f"{city} következő 3 órás időjárás előrejelzése {forecast_data[0]["datetime"]}: {forecast_data[0]["weather"]}.")
        print(f"Várható hőmérséklet: {forecast_data[0]["temp"]}°C, "
              f"Várható hőérzet: {forecast_data[0]["feels_like"]}°C")
        print(f"Várható szélsebesség: {forecast_data[0]["wind_speed"]} km/h.")
        print(f"Eső várható: {forecast_data[0]["rain"]} mm.")
    elif language == "en":
        print(f"{city}'s current weather: {current_weather}.")
        print(f"The temperature is: {current_temp}°C, Feels-like: {current_feels_like}°C.")
        print(f"Current wind speed: {current_wind_speed_k_h} km/h.")
        print(f"{city}'s weather forecast for the next 3 hours {forecast_data[0]["datetime"]}: {forecast_data[0]["weather"]}.")
        print(f"Expected weather : {forecast_data[0]["temp"]}°C, "
              f"Expected feels_like: {forecast_data[0]["feels_like"]}°C.")
        print(f"Expected wind speed: {forecast_data[0]["wind_speed"]} km/h.")
        print(f"Rain expected: {forecast_data[0]["rain"]} mm.")


# Main code
city = input("Add the name of the location: ").strip().capitalize()
language = input("Add language(type 'hu' or 'en': ").strip().lower()

# Call the function
display_weather(city, language)
