import os
from dotenv import load_dotenv
import telebot
from pyowm import OWM
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyowm.commons.exceptions

load_dotenv()

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

bot = telebot.TeleBot(TOKEN)

def save_message(message):
    try:
        with open("messages.log", "a", encoding="utf-8") as file:
            file.write(f"{message.from_user.id}: {message.text}\n")
    except Exception as e:
        print(f"Error saving message: {e}")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    save_message(message)  # Save the incoming message
    if message.text == '/weather':
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_weather)
    else:
        bot.send_message(message.from_user.id, "��апиши или нажми /weather чтобы узнать погоду")

@bot.message_handler(commands=['url'])
def send_url(message):
    markup = InlineKeyboardMarkup()
    btn_my_site = InlineKeyboardButton(text='Погода в Минске', url='https://yandex.by/pogoda/minsk')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Всегда актуальный прогноз для Минска", reply_markup=markup)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может помочь узнать погоду.")

def get_weather(message):
    city = message.text
    try:
        w = weather(city)
        bot.send_message(message.from_user.id, f'В городе {city} сейчас {round(w[0]["temp"])} градусов,'
                                               f' чувствуется как {round(w[0]["feels_like"])} градусов')
        bot.send_message(message.from_user.id, w[1])
        bot.send_message(message.from_user.id, 'Доброго времен суток! Введите название города')
    except pyowm.commons.exceptions.NotFoundError:
        bot.send_message(message.from_user.id, 'Упс... такого города нет в базе, попробуйте ещё раз')
    except Exception as e:
        bot.send_message(message.from_user.id, f'Произошла ошибка: {str(e)}')
    finally:
        bot.register_next_step_handler(message, get_weather)

def get_location(lat, lon):
    url = f"https://yandex.ru/pogoda/maps/nowcast?lat={lat}&lon={lon}&via=hnav&le_Lighting=1"
    return url

def weather(city: str):
    owm = OWM(API_KEY)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(city)
    current_weather = observation.weather
    location = get_location(observation.location.lat, observation.location.lon)
    temperature = current_weather.temperature("celsius")
    return temperature, location

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)