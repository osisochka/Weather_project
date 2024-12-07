from flask import Flask, request, render_template
import requests

app = Flask(__name__)

API_KEY = "a92e99aa09fde9b14642dd11c894bc8c"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather_data(cities):
    data = []
    for city in cities:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            weather_data = response.json()
            city_data = {
                'City': city,
                'Temperature': weather_data['main']['temp'],
                'Humidity': weather_data['main']['humidity'],
                'Wind_Speed': weather_data['wind']['speed'],  # Подчеркивание вместо пробела
                'Rain_Probability': weather_data.get('rain', {}).get('1h', 0),  # Подчеркивание вместо пробела
                'Description': weather_data['weather'][0]['description'].capitalize()
            }
            data.append(city_data)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка API для города {city}: {str(e)}")
            data.append({
                'City': city,
                'Temperature': None,
                'Humidity': None,
                'Wind_Speed': None,  # Подчеркивание вместо пробела
                'Rain_Probability': None,  # Подчеркивание вместо пробела
                'Description': "Данные недоступны"
            })
    return data




def check_bad_weather(temp, wind, rain):
    if temp is None:
        return "Невозможно оценить погоду."
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
            weather_data = get_weather_data([start_city, end_city])
            for city_data in weather_data:
                try:
                    results.append({
                        'City': city_data['City'],
                        'Temperature': city_data.get('Temperature', 'Нет данных'),
                        'Humidity': city_data.get('Humidity', 'Нет данных'),
                        'Wind_Speed': city_data.get('Wind_Speed', 'Нет данных'),
                        'Rain_Probability': city_data.get('Rain_Probability', 'Нет данных'),
                        'Description': city_data.get('Description', 'Нет данных'),
                        'weather_status': check_bad_weather(
                            city_data.get('Temperature'),
                            city_data.get('Wind_Speed', 0),  # Если нет данных о ветре, устанавливаем 0
                            city_data.get('Rain_Probability', 0)  # Если нет данных о дожде, устанавливаем 0
                        )
                    })
                except Exception as e:
                    # Добавляем информацию об ошибке в результат, если что-то пошло не так
                    results.append({
                        'City': city_data['City'],
                        'Temperature': 'Ошибка',
                        'Humidity': 'Ошибка',
                        'Wind_Speed': 'Ошибка',
                        'Rain_Probability': 'Ошибка',
                        'Description': f'Ошибка: {str(e)}',
                        'weather_status': 'Невозможно оценить погоду.'
                    })

    return render_template('index.html', results=results, error=error_message)


if __name__ == "__main__":
    app.run(debug=True)