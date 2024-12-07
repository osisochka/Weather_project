from flask import Flask, request, render_template
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError
app = Flask(__name__)

#здесь лежат данные для запросов
API_KEY = "a92e99aa09fde9b14642dd11c894bc8c"
#BASE_URL = "https://api.openweathermap.org/data/2.5/weather" #для обычной инфы по погоде
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast" #для погоды с интервалами


#Здесь описаны оценочные суждения по ощущению погоды
def check_bad_weather(temp, wind, rain):
    if temp is None:
        return "Невозможно оценить погоду."
    comments = []
    if temp < 0:
        comments.append("Холодно!")
    if 0 <= temp < 10:
        comments.append("Прохладно!")
    if temp > 35:
        comments.append("Очень жарко!")
    if wind > 10:
        comments.append("Слишком ветрено!")
    if rain > 0:
        comments.append("Идёт дождь!")
    if not comments:
        comments.append("Хорошая погода!")
    return " ".join(comments)



def get_weather_data(cities, interval):
    '''
    Функция позволяет безболезненно для
    количества запросов получить все
    данные о погоде
    господь, храни открытые апишки
    '''
    data = []
    for city in cities:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        try:
            response = requests.get(BASE_URL_FORECAST, params=params, timeout=5)
            response.raise_for_status()  # Генерирует HTTPError для 4xx/5xx

            forecast_data = response.json()
            forecast_list = forecast_data['list']
            if interval == "1":
                forecast = forecast_list[0]
            elif interval == "3":
                forecast = forecast_list[1]
            elif interval == "5":
                forecast = forecast_list[2]
            else:
                forecast = forecast_list[0]

            city_data = {
                'City': city,
                'Temperature': forecast['main']['temp'],
                'Humidity': forecast['main']['humidity'],
                'Wind_Speed': forecast['wind']['speed'],
                'Rain_Probability': forecast.get('rain', {}).get('3h', 0),
                'Description': forecast['weather'][0]['description'].capitalize()
            }
            data.append(city_data)
        except ConnectionError: #Подключение не удалось
            data.append({
                'City': city,
                'Temperature': None,
                'Humidity': None,
                'Wind_Speed': None,
                'Rain_Probability': None,
                'Description': "Ошибка подключения к серверу."
            })
        except Timeout: #что-то пошло не так с ответом
            data.append({
                'City': city,
                'Temperature': None,
                'Humidity': None,
                'Wind_Speed': None,
                'Rain_Probability': None,
                'Description': "Превышено время ожидания ответа от сервера."
            })
        except HTTPError as e: #Пользователь неправильно ввёл название города
            if response.status_code == 404:
                error_desc = "Город не найден. Проверьте название."
            else:
                error_desc = f"Ошибка сервера: {response.status_code}"
            data.append({
                'City': city,
                'Temperature': None,
                'Humidity': None,
                'Wind_Speed': None,
                'Rain_Probability': None,
                'Description': error_desc
            })
        except Exception as e: # Перехватываем все ошибки
            data.append({
                'City': city,
                'Temperature': None,
                'Humidity': None,
                'Wind_Speed': None,
                'Rain_Probability': None,
                'Description': f"Неизвестная ошибка: {str(e)}"
            })
    return data


@app.route("/", methods=['GET', 'POST'])
def index():
    results = []
    error_message = None

    if request.method == 'POST':
        start_city = request.form.get('start_city')
        end_city = request.form.get('end_city')
        interval = request.form.get('interval', '1')  # По умолчанию 1 час

        if not start_city or not end_city:
            error_message = "Введите оба города!"
        else:
            weather_data = get_weather_data([start_city, end_city], interval)
            for city_data in weather_data:
                if city_data['Description'].startswith("Ошибка"):
                    error_message = city_data['Description']
                else:
                    results.append({
                        'City': city_data['City'],
                        'Temperature': city_data.get('Temperature', 'Нет данных'),
                        'Humidity': city_data.get('Humidity', 'Нет данных'),
                        'Wind_Speed': city_data.get('Wind_Speed', 'Нет данных'),
                        'Rain_Probability': city_data.get('Rain_Probability', 'Нет данных'),
                        'Description': city_data.get('Description', 'Нет данных'),
                        'weather_status': check_bad_weather(
                            city_data.get('Temperature'),
                            city_data.get('Wind_Speed', 0),
                            city_data.get('Rain_Probability', 0)
                        )
                    })

    return render_template('index.html', results=results, error=error_message)

if __name__ == "__main__":
    app.run(debug=True)
