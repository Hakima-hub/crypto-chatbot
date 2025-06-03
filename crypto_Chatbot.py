
import requests
from flask import Flask, request, render_template
from openai import OpenAI
import telebot



OPENAI_API_KEY = "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"
TELEGRAM_TOKEN = "7048741698:AAEFzvrIEz2uHQ84iS2ornELOhnrVs6l-Xk"

OpenAI.api_key = OPENAI_API_KEY
tele_bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_crypto_price(symbol="bitcoin", currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies={currency.lower()}"
    try:
        response = requests.get(url)
        data = response.json()
        price = data[symbol.lower()][currency.lower()]
        return f"{symbol.capitalize()} price in {currency.upper()}: {price}"
    except:
        return "Invalid symbol or currency."

def ask_openai(message):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about cryptocurrency."},
            {"role": "user", "content": message}
        ]
        response = OpenAI.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def home():
    bot_response = ""
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if not user_input:
            bot_response = "Please enter a message."
        elif user_input.startswith("price"):
            parts = user_input.split()
            if len(parts) == 3:
                _, coin, curr = parts
                bot_response = get_crypto_price(coin, curr)
            else:
                bot_response = "Use format: price bitcoin usd"
        else:
            bot_response = ask_openai(user_input)
    return render_template("index.html", bot_response=bot_response)

@tele_bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    text = message.text
    if text.startswith("price"):
        parts = text.split()
        if len(parts) == 3:
            _, coin, curr = parts
            reply = get_crypto_price(coin, curr)
        else:
            reply = "Use format: price bitcoin usd" 
    else:
        reply = ask_openai(text)
    tele_bot.send_message(message.chat.id, reply)

if __name__ == "__main__":
    app.run(debug=False, port=5000)


