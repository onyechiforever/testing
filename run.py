# Import the libraries
import ccxt
import metaapi_cloud_sdk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define the constants
API_KEY = "your_metaapi_api_key" # MetaApi API key
ACCOUNT_ID = "your_metaapi_account_id" # MetaApi account id
TOKEN = "your_telegram_bot_token" # Telegram bot token
CHANNEL = "your_telegram_channel_name" # Telegram channel name
SYMBOLS = ["EURUSD", "GBPUSD", "XAUUSD"] # Allowed symbols for trading

# Initialize the ccxt library
exchange = ccxt.metatrader4({
    "apiKey": API_KEY,
    "secret": ACCOUNT_ID,
    "enableRateLimit": True
})

# Initialize the MetaApi library
metaapi = metaapi_cloud_sdk.MetaApi(API_KEY)
account = await metaapi.metatrader_account_api.get_account(ACCOUNT_ID)
connection = await account.connect()

# Initialize the Telegram bot
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define a function to parse the signals and execute the trades
def trade(update, context):
    # Get the message text
    message = update.message.text

    # Check if the message is from the channel
    if update.message.chat.username == CHANNEL:

        # Parse the message for the order type, symbol, entry, stop loss, and take profit
        # You can modify this part according to the format of your signals
        order_type = message.split()[0].lower()
        symbol = message.split()[1].upper()
        entry = float(message.split()[2])
        stop_loss = float(message.split()[3])
        take_profit = float(message.split()[4])

        # Check if the symbol is valid
        if symbol in SYMBOLS:

            # Calculate the position size based on your risk management
            # You can modify this part according to your strategy
            balance = exchange.fetch_balance()["total"]["USD"]
            risk = 0.01 # Risk 1% of the balance per trade
            position_size = balance * risk / abs(entry - stop_loss)

            # Create the order parameters
            # You can modify this part according to your preferences
            order_params = {
                "symbol": symbol,
                "type": order_type,
                "side": "buy" if order_type == "buy" or order_type == "buy limit" or order_type == "buy stop" else "sell",
                "amount": position_size,
                "price": entry,
                "params": {
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "type_time": "GTC" # Good till cancelled
                }
            }

            # Send the order to the MT4 account
            order = exchange.create_order(**order_params)

            # Send a confirmation message to the Telegram bot
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Order executed: {order}")

        else:
            # Send an error message to the Telegram bot
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Invalid symbol: {symbol}")

# Add a message handler for the trade function
trade_handler = MessageHandler(Filters.text & (~Filters.command), trade)
dispatcher.add_handler(trade_handler)

# Start the bot
updater.start_polling()
updater.idle()
