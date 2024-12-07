from flask import Flask, request, render_template
import requests

app = Flask(__name__)

API_KEY = "a92e99aa09fde9b14642dd11c894bc8c"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather_data(cities):
    """
    Получает погодные данные для списка городов.
    """
    data = []
    for city in cities:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            weather_data = response.json()
            city_data = {
                'City': city,
                'Temperature': weather_data['main']['temp'],
                'Humidity': weather_data['main']['humidity'],
                'Wind Speed': weather_data['wind']['speed'],
                'Rain Probability': weather_data.get('rain', {}).get('1h', 0)  # мм осадков за последний час
            }
            data.append(city_data)
        else:
            print(f"Не удалось получить данные для {city}: {response.status_code}")
    return data


def check_bad_weather(temp, wind, rain):
    """
    Проверяет неблагоприятные погодные условия.
    """
    comments = []
    if temp < 10:
        comments.append("Очень холодно!")
    if temp > 35:
        comments.append("Очень жарко!")
    if wind > 10:
        comments.append("Слишком ветрено!")
    if rain > 0:
        comments.append("Идёт дождь!")
    if not comments:
        comments.append("Хорошая погода!")
    return ", ".join(comments)


@app.route("/", methods=['GET', 'POST'])
def index():
    results = []
    error_message = None

    if request.method == 'POST':
        start_city = request.form.get('start_city')
        end_city = request.form.get('end_city')

        if not start_city or not end_city:
            error_message = "Введите оба города!"
        else:
            try:
                weather_data = get_weather_data([start_city, end_city])
                for city_data in weather_data:
                    results.append({
                        'City': city_data['City'],
                        'weather_status': check_bad_weather(
                            city_data['Temperature'],
                            city_data['Wind Speed'],
                            city_data['Rain Probability']
                        )
                    })
            except Exception as e:
                error_message = f"Ошибка при получении данных: {str(e)}"

    return render_template('index.html', results=results, error=error_message)


if __name__ == "__main__":
    app.run(debug=True)
