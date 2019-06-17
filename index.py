import logging
import requests
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

currency_codes = {
    'bitcoin':'btc',
    'ripple':'xrp',
    'litecoin':'ltc',
    'ethereum':'eth'
}

def coindelta(coin, currency):
    MarketName = "{}-{}".format(coin,currency)
    r = requests.get('https://coindelta.com/api/v1/public/getticker/')
    if r.status_code != requests.codes.ok:
        return None
    data = [item for item in r.json() if item['MarketName'] == MarketName.lower()]
    if len(data) and 'Last' in data[0]:
        return data[0]['Last']
    else:
        return None

def koinex(coin, currency):
    if currency.lower() != 'inr':
        return None

    r = requests.get('https://koinex.in/api/ticker')
    if r.status_code != requests.codes.ok:
        return None

    data = r.json()
    if coin.upper() in data['prices'].keys():
        return data['prices'][coin.upper()]
    else:
        return None

@ask.launch
def init():
    welcome_msg = render_template('welcome')
    print "In init"
    print welcome_msg
    return question(welcome_msg)

@ask.intent("ExchangeRateIntent")
def answer(coin, exchange):
    currency = 'INR'
    if coin not in currency_codes:
         return question('Sorry, currency either not exist or not supported yet. Please select from {}.'.format(",".join(currency_codes.keys())))
    coin_code = currency_codes[coin]
    if exchange in globals():
        rate = globals()[exchange](coin_code, currency)
        msg = render_template('rate', coin= coin, exchange=exchange, rate = rate, currency = currency)
        return statement(msg)
    else:
        return question('Sorry, exchange either not exist or not supported yet.'.format(exchange))

if __name__ == '__main__':
    app.run(debug=True)
