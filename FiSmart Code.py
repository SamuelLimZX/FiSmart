from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import ChatAction, ParseMode
from datetime import date, datetime
import json
import os
import requests
import logging
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from urllib.parse import urljoin


#import urllib2


# Load bot token
with open("token.txt", "r") as file:
    BOT_TOKEN = file.read()



#Load persistent state
if os.path.isfile("data.txt"):
    with open("data.txt","r") as file:
        watchlist_dict = json.load(file)
else:
    watchlist_dict = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#create the bot
updater = Updater(token = BOT_TOKEN, use_context = True)
dispatcher = updater.dispatcher

def start(update, context):

    user_id = update.effective_chat.id

    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Hello! Welcome to FiSmart, your integrated telegram bot \
for your financial updates! Please choose from the list of commands: \n\n \
/stocklist to choose from a list of stocks \n\n \
/mywl to view stocks on your watchlist \n\n \
"/add aapl" to add aapl to your watchlist \n\n \
"/del aapl" to delete aapl from your watchlist \n\n \
"/chart aapl" to receive the chart for aapl'
        )
    



#ADD WATCHLIST
def add_wl(update, context):
    print("add_wl")
    st = update.message.text.upper()
    yf.pdr_override()
    if len(st) == 4:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Please add the Stock code behind. E.g "/awl AAPL"'
        )

    else:
        st = st[5:]
        user_key = str(update.effective_chat.id)
        if user_key not in watchlist_dict:
           watchlist_dict[user_key] = [st]
           context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = f"{st} has been added to your watchlist!")
        else:
            
            data = pdr.get_data_yahoo(st, start=date.today())
        
            if len(data) == 0:
                context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = f'Invalid stock code.')
            else:
                
                if st in watchlist_dict[user_key]:
                    context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text = f"{st} is already in your watchlist"
                    )
                else:
                    watchlist_dict[user_key].append(st)
                    context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text = f"{st} has been added to your watchlist! :D"
                    )
        print(watchlist_dict)

            
def stockinfo(update, context):
    user_text = update.message.text.upper()
    yf.pdr_override()
    
    data = pdr.get_data_yahoo(user_text, start=date.today())
    if len(data) == 0:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Invalid stock code.')
    else:
        stat = pdr.get_data_yahoo(user_text, start=date.today())
        tick = yf.Ticker(user_text)
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'{user_text} Stock Information: \n\n \
Open: {round(float(stat["Open"][0]),2)} \n\n \
High: {round(float(stat["High"][0]),2)} \n\n \
Low: {round(float(stat["Low"][0]),2)} \n\n \
Close: {round(float(stat["Close"][0]),2)} \n\n \
Adj Close: {round(float(stat["Adj Close"][0]),2)} \n\n \
Volume: {round(float(stat["Volume"][0]),2)} \n\n\n\n \
Buy Ratings from Top Banks:\n \
{tick.recommendations["To Grade"][-4:-1]} \n\n \
For more info, visit www.bloomberg.com/quote/{user_text}:US ')

    print(tick.recommendations)

def stocklist(update, context):
    ####PRINT LIST OF SYMBOLS HERE IDK HOW TO###
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Type the code of the stock if you are interested to find out more.'
        )
    fn_stockinfo = MessageHandler(Filters.text, stockinfo)
    dispatcher.add_handler(fn_stockinfo)


    


def del_wl(update,context):
    print("del_wl")
    st = update.message.text.upper()
    if len(st) == 4:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Please add the Stock code behind. E.g "/del AAPL"'
        )
    else:
        st = st[5:]
        user_key = str(update.effective_chat.id)
        if user_key not in watchlist_dict:
            context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f"You do not have a watchlist"
            )
            
           
        else:
        
            if st in watchlist_dict[user_key]:
                watchlist_dict[user_key].remove(st)
                context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = f"{st} has been removed from your watchlist"
                )
            else:
                
                context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = f"{st} is not in your watchlist"
                )
                
        print(watchlist_dict)
        

def my_wl(update,context):
    print("my_wl")
    user_key = str(update.effective_chat.id)
    if user_key not in watchlist_dict:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"You do not have a watchlist"
        )
        
       
    else:
        l = "My Watchlist: \n\n"
        for i in watchlist_dict[user_key]:
            l = l + f"{i} \n"
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = l
        )

def chart(update, context):
    st = update.message.text.upper()
    yf.pdr_override()
    if len(st) == 6:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Please add the Stock code behind. E.g "/chart AAPL"'
        )
    else:
        st = st[7:]
        print(st)
        data = pdr.get_data_yahoo(st, start=date.today())
        
        if len(data) == 0:
            context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = f'Invalid stock code.')
        else:
            
            user_key = str(update.effective_chat.id)
            url = f'https://finviz.com/quote.ashx?t={st}'
            content = requests.get(url).content
            soup = BeautifulSoup(urlopen(url),"lxml")
            for img in soup.find_all('img'):
                if img.get("id") == "chart0":
                    img_url = urljoin(url, img['src'])
                    context.bot.send_photo(chat_id = user_key, photo= img_url)

def end(update, context):
    with open("data.txt", "w") as file:
        json.dump(watchlist_dict, file)
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f'Watchlist has been updated! See Ya Again!'
        )


def wlprices(update, context):
    user_key = str(update.effective_chat.id)
    yf.pdr_override()
    if user_key not in watchlist_dict or not watchlist_dict[user_key]:
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"You do not have a watchlist"
        )
        
       
    else:
        l = "My Watchlist: \n\n"
        for i in watchlist_dict[user_key]:
            stat = pdr.get_data_yahoo(i, start=date.today())
            l = l + f'{i}           {round(float(stat["Close"][0]),2)}\n'
        context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = l
        )



#Handle command
updater.dispatcher.add_handler(
    CommandHandler("add", add_wl) #when the user type /dice
)

updater.dispatcher.add_handler(
    CommandHandler("del", del_wl) #when the user type /dice
)

updater.dispatcher.add_handler(
    CommandHandler("start", start) #when the user type /start
)

updater.dispatcher.add_handler(
    CommandHandler("stocklist", stocklist)
    )

updater.dispatcher.add_handler(
    CommandHandler("stocklist", stocklist) #when the user type /start
)

updater.dispatcher.add_handler(
    CommandHandler("mywl", my_wl) #when the user type /start
)

updater.dispatcher.add_handler(
    CommandHandler("chart", chart)
    )

updater.dispatcher.add_handler(
    CommandHandler("end", end)
    )

updater.dispatcher.add_handler(
    CommandHandler("wlprices", wlprices)
    )


##watchlist_info = MessageHandler(Filters.text, watchlist)
##dispatcher.add_handler(watchlist_info)

#Start the bot
updater.start_polling()
print("Bot started!")


#wait for the bot to stop to update dict into data
updater.idle()


# Dump persistent state
with open("data.txt", "w") as file:
    json.dump(watchlist_dict, file)


print("Bot stopped!")

