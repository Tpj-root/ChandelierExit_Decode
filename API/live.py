#!/usr/bin/env python3

"""
LIVE DERIV CHANDELIER EXIT

Architecture:

    Deriv WebSocket
          |
          v
      TickBuffer
          |
          v
      CandleBuilder
          |
          v
     True Range
          |
          v
      ATR / RMA
          |
          v
   Chandelier Exit
          |
          v
    Direction State
          |
          v
    BUY / SELL
          |
          v
    Live Matplotlib


IMPORTANT:
    This program is MONITORING / ANALYSIS only.
    It does NOT place trades.
"""




import json
# json:
# Python's built-in JSON module.
# Used to convert Python data to JSON and JSON data back to Python.
# Useful when communicating with APIs such as the Deriv API.

import os
# os:
# Provides functions for interacting with the operating system.
# Can be used for environment variables, file paths, directories, etc.

import time
# time:
# Provides time-related functions.
# Useful for delays, timestamps, and controlling timing.
# Example: time.sleep(1) -> waits for 1 second.

import threading
# threading:
# Allows the program to run tasks in separate threads.
# Useful when one part of the program needs to continue running
# while another task works in the background.
# Example:
#   Main thread       -> GUI / chart
#   Background thread -> WebSocket / market data

from dataclasses import dataclass
# dataclass:
# Provides the @dataclass decorator.
# It is useful for classes whose main purpose is storing data.
# Python automatically creates common methods such as __init__()
# based on the fields defined inside the class.

from datetime import datetime, timezone
# datetime:
# Used to work with dates and times.
#
# timezone:
# Used to represent timezone information.
# This is useful when working with API timestamps and UTC time.

from collections import deque
# deque:
# Means "double-ended queue".
# Useful for efficiently adding/removing data from both ends.
# Very useful for keeping a limited amount of recent market data,
# such as the latest candles or ticks.

import numpy as np
# numpy:
# Numerical computing library.
# "np" is the standard short name used for NumPy.
# Useful for arrays, mathematical calculations, and numerical data.

import pandas as pd
# pandas:
# Data-analysis library.
# "pd" is the standard short name used for Pandas.
# Mainly used for DataFrame and Series objects.
# Very useful for CSV files, OHLC market data, and time-series data.

import requests
# requests:
# HTTP communication library.
# Used to send requests to web/API servers.
# For example, it can communicate with REST APIs using HTTP/HTTPS.

import websocket
# websocket:
# WebSocket communication library.
# Used to create a persistent connection with a server.
# Very useful for receiving real-time/live market data continuously.
#
# Difference:
# requests  -> normal HTTP request/response
# websocket -> continuous real-time connection

import matplotlib.pyplot as plt
# matplotlib.pyplot:
# Provides functions for creating graphs and charts.
# "plt" is the standard short name.
# Can be used to draw price charts, indicator lines,
# buy/sell points, labels, etc.

import matplotlib.dates as mdates
# matplotlib.dates:
# Provides tools for handling dates and times on Matplotlib charts.
# "mdates" is the short name.
# Useful when the chart's X-axis contains timestamps.

from matplotlib.animation import FuncAnimation
# FuncAnimation:
# Used to continuously update a Matplotlib chart.
# Useful for a live market chart.
#
# Conceptually:
#
#   Receive new market data
#           ↓
#      Update data
#           ↓
#      Update chart
#           ↓
#      Receive new data
#           ↓
#          ...
#
# This allows the chart to behave like a live/updating display.



# ============================================================
# DEBUG CONFIGURATION
# ============================================================

DEBUG = True


# ============================================================
# IMPORTS
# ============================================================

from datetime import datetime


# ============================================================
# DEBUG FUNCTION
# ============================================================

DEBUG = True

LOG_FILE = "log.txt"

# ============================================================
# DEBUG + LOG FUNCTION
# ============================================================

def debug(message):
    """
    Print a timestamped debug message when DEBUG is enabled
    and also append the same message to log.txt.
    """

    if not DEBUG:
        return None

    timestamp = datetime.now().strftime("%H:%M:%S")

    output = f"[{timestamp}] [DEBUG] {message}"

    # Print to terminal
    print(output)

    # Save to log file
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(output + "\n")

    return output



APP_ID = os.getenv(
    "DERIV_APP_ID_PY",
    "YOUR_APP_ID"
)
# APP_ID:
# Stores the Deriv application ID.
#
# os.getenv() first looks for an operating-system environment
# variable named "DERIV_APP_ID_PY".
#
# If that environment variable exists:
#     its value is used.
#
# If it does NOT exist:
#     "YOUR_APP_ID" is used as the default value.
#
# This approach is useful because the real App ID does not need
# to be written directly into the source code.
#
# Structure:
#
# os.getenv(
#     "environment variable name",
#     "default value"
# )

AUTH_TOKEN = os.getenv(
    "DERIV_API_TOKEN_PY",
    "YOUR_AUTH_TOKEN"
)
# AUTH_TOKEN:
# Stores the authentication token used to access the Deriv API.
#
# os.getenv() looks for:
#     DERIV_API_TOKEN_PY
#
# If it exists, that environment variable's value is used.
#
# Otherwise:
#     "YOUR_AUTH_TOKEN"
# is used.
#
# Keeping the token in an environment variable is useful because
# sensitive credentials do not have to be written directly into
# the Python source code.

ACCOUNT_ID = os.getenv(
    "DERIV_ACCOUNT_ID",
    "YOUR_ACCOUNT_ID"
)
# ACCOUNT_ID:
# Stores the Deriv trading account ID.
#
# os.getenv() looks for the environment variable:
#     DERIV_ACCOUNT_ID
#
# If it exists:
#     that value becomes ACCOUNT_ID.
#
# Otherwise:
#     "YOUR_ACCOUNT_ID"
# is used as the default.
#
# This allows the account ID to be changed without modifying
# the Python source code.

SYMBOL = "frxXAUUSD"
# SYMBOL:
# Stores the market/instrument symbol that the program will use.
#
# "frxXAUUSD" represents the XAU/USD market symbol used by
# the Deriv API.
#
# Keeping the symbol in a variable is useful because the rest
# of the program can refer to SYMBOL instead of repeatedly
# writing the market name.
#
# If you later want to work with another supported symbol,
# this is the configuration value that can be changed.



# ------------------------------------------------------------
# CANDLE SETTINGS
# ------------------------------------------------------------

# 60 = 1 minute
#
# Change:
#
# 15  = 15 seconds
# 30  = 30 seconds
# 60  = 1 minute
# 120 = 2 minutes
# 300 = 5 minutes
#
TIMEFRAME_SECONDS = 60


# ------------------------------------------------------------
# CHANDELIER EXIT SETTINGS
# ------------------------------------------------------------

ATR_PERIOD = 22

ATR_MULTIPLIER = 3.0

# TradingView:
#
# true  -> highest/lowest CLOSE
# false -> highest HIGH / lowest LOW
#
USE_CLOSE = True


# ------------------------------------------------------------
# GRAPH SETTINGS
# ------------------------------------------------------------

# Number of candles shown on graph
MAX_CANDLES_ON_GRAPH = 150

# Number of historical ticks requested for warm-up
HISTORY_TICKS = 1000

# Update graph every this many milliseconds
GRAPH_UPDATE_MS = 500


# ============================================================
# DATA CLASSES
# ============================================================
# This section defines classes that are mainly used to store
# structured market data.
#
# There are two different types of data here:
#
# Tick   -> one individual market price update
# Candle -> a group of price updates represented as OHLC data


@dataclass
class Tick:
    # @dataclass:
    # Tells Python that Tick is a data-holding class.
    #
    # Python automatically creates useful methods such as
    # __init__() for the fields defined below.
    #
    # So we can create a Tick object like:
    #
    # Tick(epoch, price, symbol)
    #
    # instead of manually writing an __init__() method.

    """
    One market tick.
    """
    # This is the class documentation string.
    #
    # It describes what one Tick object represents.
    #
    # A tick is one individual market price update.
    #
    # Example:
    #
    # Market sends:
    #     price = 2650.25
    #
    # That single update can be represented by one Tick object.

    epoch: int
    # epoch:
    # Stores the timestamp of the tick.
    #
    # int means the expected data type is an integer.
    #
    # An epoch timestamp represents time as a number,
    # commonly the number of seconds since:
    #
    #     1970-01-01 00:00:00 UTC
    #
    # This is useful for ordering and processing market data.

    price: float
    # price:
    # Stores the market price received in this tick.
    #
    # float means the value can contain decimal numbers.
    #
    # Example:
    #
    #     2650.25
    #     2650.50
    #     2651.10

    symbol: str
    # symbol:
    # Stores the market/instrument name associated with this tick.
    #
    # str means the value is a Python string.
    #
    # Example:
    #
    #     "frxXAUUSD"
    #
    # This tells the program which market the tick belongs to.


@dataclass
class Candle:
    # @dataclass:
    # Again, this tells Python that Candle is primarily a
    # structured data container.
    #
    # A Candle represents a collection of market price
    # movements summarized into OHLC values.

    """
    One OHLC candle.
    """
    # Documentation string describing the purpose of this class.
    #
    # OHLC means:
    #
    # O = Open
    # H = High
    # L = Low
    # C = Close
    #
    # These four values summarize price movement during
    # one candle period.

    timestamp: pd.Timestamp
    # timestamp:
    # Stores the date/time associated with this candle.
    #
    # pd.Timestamp is a Pandas timestamp type.
    #
    # Pandas Timestamp is useful when working with
    # time-series market data and DataFrames.

    open: float
    # open:
    # The first market price recorded for this candle.
    #
    # Example:
    # If the candle starts at 2650.00,
    # open = 2650.00

    high: float
    # high:
    # The highest market price reached during this candle.
    #
    # Example:
    # If prices move:
    #
    # 2650 → 2652 → 2655 → 2653
    #
    # high = 2655

    low: float
    # low:
    # The lowest market price reached during this candle.
    #
    # Example:
    # If prices move:
    #
    # 2650 → 2648 → 2645 → 2649
    #
    # low = 2645

    close: float
    # close:
    # The last market price recorded for this candle.
    #
    # Example:
    # If the final price is 2653,
    # close = 2653

    tick_count: int = 0
    # tick_count:
    # Stores how many individual ticks were used to build
    # this candle.
    #
    # int means it stores a whole number.
    #
    # "= 0" gives this field a default value of zero.
    #
    # Therefore, if a Candle is created without specifying
    # tick_count, it starts at:
    #
    #     tick_count = 0
    #
    # As ticks are received and added to the candle,
    # this value can be increased.
    #
    # Example:
    #
    #     1 candle
    #     ├── Tick 1
    #     ├── Tick 2
    #     ├── Tick 3
    #     └── Tick 4
    #
    #     tick_count = 4



# ============================================================
# DERIV CLIENT
# ============================================================
#
# This class is the main communication layer for the Deriv API.
#
# It is responsible for:
#
#   1. Getting a WebSocket URL using the REST API / OTP process.
#   2. Creating and managing the WebSocket connection.
#   3. Subscribing to live market ticks.
#   4. Requesting historical tick data.
#   5. Sending received data to callback functions.
#
# In simple terms:
#
#     Your application
#            |
#            v
#     +----------------+
#     |  DerivClient   |
#     +----------------+
#        |          |
#        v          v
#      REST      WebSocket
#        |          |
#        |          +----> Live ticks
#        |
#        +---------------> OTP / connection URL
#
# Keeping all Deriv communication inside this class makes the
# rest of your application independent from the API details.
#

class DerivClient:
    """
    DerivClient manages communication with the Deriv API.

    Main responsibilities:

        REST OTP
            -> Used to obtain the WebSocket connection information.

        WebSocket connection
            -> Used for real-time communication with Deriv.

        Tick subscription
            -> Receives live market price/tick updates.

        Historical tick request
            -> Requests older tick data from Deriv.

    The class also provides callback variables so another part
    of the program can receive the data without putting all
    application logic inside this class.
    """

    # --------------------------------------------------------
    # BASE API URL
    # --------------------------------------------------------
    #
    # This is the root URL used when communicating with the
    # Deriv REST API.
    #
    # Other REST endpoints can be constructed from this URL.
    #
    # Example:
    #
    #     https://api.derivws.com/...
    #
    BASE_URL = "https://api.derivws.com"

    # --------------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------------
    #
    # __init__() runs automatically when a DerivClient object
    # is created.
    #
    # Example:
    #
    #     client = DerivClient(
    #         app_id,
    #         auth_token,
    #         account_id
    #     )
    #
    # The constructor receives the credentials/configuration
    # required by this client.
    #

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        account_id: str,
    ):

    # ----------------------------------------------------
    # STORE APPLICATION ID
    # ----------------------------------------------------
    #
    # app_id identifies the application when communicating
    # with Deriv.
    #
    # We store it in self.app_id so every other method in
    # this class can access it.
    #
        self.app_id = app_id

        # ----------------------------------------------------
        # STORE AUTHENTICATION TOKEN
        # ----------------------------------------------------
        #
        # auth_token is the authentication credential used when
        # making authenticated API requests.
        #
        # It is stored so other methods can use it later.
        #
        self.auth_token = auth_token

        # ----------------------------------------------------
        # STORE ACCOUNT ID
        # ----------------------------------------------------
        #
        # account_id identifies the Deriv account that this
        # client is working with.
        #
        # Keeping it as an instance variable means other methods
        # can access the selected account.
        #
        self.account_id = account_id

        # ----------------------------------------------------
        # WEBSOCKET OBJECT
        # ----------------------------------------------------
        #
        # At the moment the client object is created, there is
        # no WebSocket connection yet.
        #
        # Therefore we initialize self.ws with None.
        #
        # Later, when a WebSocket connection is created:
        #
        #     self.ws
        #
        # will contain the actual WebSocket object.
        #
        self.ws = None

        # ----------------------------------------------------
        # RUNNING STATE
        # ----------------------------------------------------
        #
        # This variable represents whether the client is
        # currently running.
        #
        # False means:
        #
        #     Client is not running yet.
        #
        # Later, after starting the client, another method can
        # change this to:
        #
        #     self.running = True
        #
        # Other methods can use this flag to control loops,
        # background processing, or shutdown behavior.
        #
        self.running = False

        # ----------------------------------------------------
        # LIVE TICK CALLBACK
        # ----------------------------------------------------
        #
        # A callback is a function that can be stored here and
        # called later when a live tick is received.
        #
        # Initially there is no callback function, so we use
        # None.
        #
        # Later the application might assign:
        #
        #     client.tick_callback = some_function
        #
        # Then the WebSocket code can call that function whenever
        # a new tick arrives.
        #
        # This separates:
        #
        #     API communication
        #
        # from:
        #
        #     Application logic
        #
        self.tick_callback = None

        # ----------------------------------------------------
        # HISTORICAL DATA CALLBACK
        # ----------------------------------------------------
        #
        # This callback is specifically for historical market
        # data.
        #
        # Initially no callback is registered, so it is None.
        #
        # Later another part of the program can assign a function
        # that processes historical data.
        #
        # For example, conceptually:
        #
        #     client.history_callback = process_history
        #
        # When historical data is received, another method can
        # call that function.
        #
        self.history_callback = None

        # --------------------------------------------------------
        # OTP
        # --------------------------------------------------------
        #
        # This method requests an OTP/WebSocket connection URL
        # from the Deriv REST API.
        #
        # Flow:
        #
        #     1. Build the OTP API URL
        #     2. Prepare authentication headers
        #     3. Send POST request to Deriv
        #     4. Check HTTP errors
        #     5. Convert JSON response into Python data
        #     6. Check for API-level errors
        #     7. Print/debug the complete response
        #     8. Return the WebSocket URL
        #
        # The return type is str because the method finally returns
        # the URL as a Python string.
        #

    def get_socket_url(self) -> str:

        # ----------------------------------------------------
        # BUILD OTP API URL
        # ----------------------------------------------------
        #
        # BASE_URL contains:
        #
        #     https://api.derivws.com
        #
        # Then we add the REST API path and the account ID.
        #
        # The final URL will look conceptually like:
        #
        #     https://api.derivws.com/
        #     trading/v1/options/accounts/
        #     ACCOUNT_ID/otp
        #
        # f-string allows self.account_id to be inserted
        # dynamically into the URL.
        #

        url = (
            f"{self.BASE_URL}"
            f"/trading/v1/options/accounts/"
            f"{self.account_id}/otp"
        )

        # ----------------------------------------------------
        # HTTP HEADERS
        # ----------------------------------------------------
        #
        # Headers provide additional information to the
        # Deriv server about this request.
        #
        # Two important headers are used here:
        #
        #     Deriv-App-ID
        #         Identifies the application.
        #
        #     Authorization
        #         Provides the authentication token.
        #

        headers = {
            "Deriv-App-ID": self.app_id,
            "Authorization": (
                f"Bearer {self.auth_token}"
            ),
        }

        # ----------------------------------------------------
        # SEND POST REQUEST
        # ----------------------------------------------------
        #
        # requests.post() sends an HTTP POST request.
        #
        # url
        #     The API endpoint we constructed above.
        #
        # headers
        #     Authentication and application information.
        #
        # timeout=10
        #     Do not wait forever for the server.
        #     The request will wait up to 10 seconds.
        #
        response = requests.post(
            url,
            headers=headers,
            timeout=10,
        )

        # ----------------------------------------------------
        # CHECK HTTP STATUS
        # ----------------------------------------------------
        #
        # raise_for_status() checks whether the HTTP request
        # returned an HTTP error status.
        #
        # For example:
        #
        #     200 -> normally successful
        #
        #     400 -> bad request
        #     401 -> unauthorized
        #     403 -> forbidden
        #     404 -> not found
        #     500 -> server error
        #
        # If the HTTP status represents an error,
        # raise_for_status() raises an exception.
        #
        response.raise_for_status()

        # ----------------------------------------------------
        # CONVERT JSON RESPONSE TO PYTHON DATA
        # ----------------------------------------------------
        #
        # Deriv returns JSON data.
        #
        # response.json() converts that JSON response into
        # normal Python objects such as dictionaries and lists.
        #
        # For example, JSON such as:
        #
        #     {
        #         "data": {
        #             "url": "wss://..."
        #         }
        #     }
        #
        # becomes a Python dictionary:
        #
        #     data["data"]["url"]
        #
        data = response.json()

        # ----------------------------------------------------
        # CHECK "error" RESPONSE
        # ----------------------------------------------------
        #
        # HTTP status alone is not always enough.
        #
        # The API response can contain an application-level
        # error inside the JSON data.
        #
        # This checks whether the response contains an "error"
        # key.
        #
        # If it exists, stop execution and raise RuntimeError
        # with the error information returned by Deriv.
        #

        if "error" in data:

            raise RuntimeError(
                f"Deriv API Error: {data['error']}"
            )

        # ----------------------------------------------------
        # CHECK "errors" RESPONSE
        # ----------------------------------------------------
        #
        # Some API responses may provide errors using an
        # "errors" key instead of "error".
        #
        # This check handles that response format as well.
        #
        # If "errors" exists, raise RuntimeError and include
        # the returned error information.
        #

        if "errors" in data:

            raise RuntimeError(
                f"Deriv API Error: {data['errors']}"
            )

        # ----------------------------------------------------
        # DEBUG / LOG THE RESPONSE
        # ----------------------------------------------------
        #
        # At this point:
        #
        #     - HTTP request succeeded
        #     - JSON was successfully decoded
        #     - "error" was not found
        #     - "errors" was not found
        #
        # debug() displays the complete response when DEBUG
        # mode is enabled.
        #
        # The returned value from debug() is not used here;
        # this line is simply for viewing the API response.
        #

        debug(f"URL DATA: {data}")

        # ----------------------------------------------------
        # OPTIONAL FILE LOGGING
        # ----------------------------------------------------
        #
        # This line is currently commented out.
        #
        # If enabled:
        #
        #     log_to_file(
        #         debug(f"URL DATA: {data}")
        #     )
        #
        # debug() would first process the message, and its
        # returned value would then be passed to log_to_file().
        #
        # Because the line starts with "#", Python does not
        # execute it.
        #

        # log_to_file(debug(f"URL DATA: {data}"))

        # ----------------------------------------------------
        # RETURN THE WEBSOCKET URL
        # ----------------------------------------------------
        #
        # The expected successful response contains the socket
        # URL inside:
        #
        #     data
        #       └── "data"
        #             └── "url"
        #
        # Therefore:
        #
        #     data["data"]["url"]
        #
        # accesses the actual URL.
        #
        # That URL is returned to the caller as a string.
        #
        # Example conceptually:
        #
        #     wss://...
        #
        return data["data"]["url"]
    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------
    #
    # This method creates the WebSocket connection to Deriv.
    #
    # Flow:
    #
    #     get_socket_url()
    #            ↓
    #     receive WebSocket URL
    #            ↓
    #     create WebSocket connection
    #            ↓
    #     save connection in self.ws
    #            ↓
    #     mark client as running
    #
    def connect(self):

        # ----------------------------------------------------
        # GET WEBSOCKET URL
        # ----------------------------------------------------
        #
        # get_socket_url() calls the Deriv REST OTP endpoint
        # and returns the WebSocket URL.
        #
        # The returned URL is stored in socket_url.
        #
        socket_url = self.get_socket_url()

        # ----------------------------------------------------
        # DISPLAY CONNECTION STATUS
        # ----------------------------------------------------
        #
        # print() with no text creates an empty line.
        # This makes the terminal output easier to read.
        #
        print()

        # Tell the user that the socket URL was successfully
        # received.
        #
        print("Socket URL received")

        # Tell the user that the program is now attempting
        # to establish the WebSocket connection.
        #
        print("Connecting to Deriv...")

        # ----------------------------------------------------
        # CREATE WEBSOCKET CONNECTION
        # ----------------------------------------------------
        #
        # websocket.create_connection() opens a WebSocket
        # connection using the URL received from Deriv.
        #
        # socket_url
        #     The WebSocket URL returned by get_socket_url().
        #
        # timeout=10
        #     Socket operations will wait up to 10 seconds
        #     before timing out.
        #
        # The resulting WebSocket object is stored in:
        #
        #     self.ws
        #
        # This means other methods can use:
        #
        #     self.ws.send(...)
        #     self.ws.recv(...)
        #
        # to communicate with Deriv.
        #

        self.ws = websocket.create_connection(
            socket_url,
            timeout=10,
        )

        # ----------------------------------------------------
        # MARK CLIENT AS RUNNING
        # ----------------------------------------------------
        #
        # The WebSocket connection has now been successfully
        # created.
        #
        # Change the state from:
        #
        #     False
        #
        # to:
        #
        #     True
        #
        # Other parts of the client can use this variable to
        # know that the client is active.
        #

        self.running = True

        # ----------------------------------------------------
        # CONNECTION SUCCESS MESSAGE
        # ----------------------------------------------------
        #
        # Inform the user that the WebSocket connection was
        # successfully established.
        #

        print("Connected!")


    # --------------------------------------------------------
    # REQUEST HISTORICAL TICKS
    # --------------------------------------------------------
    #
    # This method requests historical tick data from Deriv.
    #
    # It does NOT calculate anything here.
    #
    # Its job is simply:
    #
    #     1. Build the request
    #     2. Convert it to JSON
    #     3. Send it through the WebSocket
    #
    def request_history(
        self,
        symbol: str,
        count: int,
    ):

        # ----------------------------------------------------
        # BUILD HISTORICAL TICK REQUEST
        # ----------------------------------------------------
        #
        # A Python dictionary is used to represent the request.
        #
        # symbol
        #     The market symbol whose historical ticks are
        #     requested.
        #
        # count
        #     The number of historical ticks requested.
        #
        # end = "latest"
        #     Request data ending at the latest available tick.
        #
        # style = "ticks"
        #     Request individual tick data rather than candle
        #     data.
        #
        # Example conceptually:
        #
        #     {
        #         "ticks_history": "R_100",
        #         "count": 100,
        #         "end": "latest",
        #         "style": "ticks"
        #     }
        #
        request = {
            "ticks_history": symbol,
            "count": count,
            "end": "latest",
            "style": "ticks",
        }

        # ----------------------------------------------------
        # CONVERT PYTHON DICTIONARY TO JSON
        # ----------------------------------------------------
        #
        # WebSocket communication sends text data.
        #
        # json.dumps() converts the Python dictionary into a
        # JSON-formatted string.
        #
        # Example:
        #
        #     Python dictionary
        #             ↓
        #        json.dumps()
        #             ↓
        #     JSON string
        #
        # That JSON string is then sent through self.ws.
        #

        self.ws.send(
            json.dumps(request)
        )

        # ----------------------------------------------------
        # DISPLAY REQUEST STATUS
        # ----------------------------------------------------
        #
        # f-string inserts the requested count into the
        # terminal message.
        #
        # If count = 100:
        #
        #     Requested 100 historical ticks
        #
        print(
            f"Requested {count} historical ticks"
        )



    # --------------------------------------------------------
    # SUBSCRIBE
    # --------------------------------------------------------
    #
    # This method tells Deriv:
    #
    #     "Start sending me live tick data for this symbol."
    #
    # Example:
    #
    #     subscribe_ticks("R_100")
    #
    # After the subscription is successful, Deriv can send
    # live tick messages through the existing WebSocket.
    #

    def subscribe_ticks(
        self,
        symbol: str,
    ):

        # ----------------------------------------------------
        # BUILD SUBSCRIPTION REQUEST
        # ----------------------------------------------------
        #
        # "ticks": symbol
        #     Specifies which market we want to monitor.
        #
        # "subscribe": 1
        #     Tells Deriv that this is a subscription request.
        #
        # Example:
        #
        #     {
        #         "ticks": "R_100",
        #         "subscribe": 1
        #     }
        #

        request = {
            "ticks": symbol,
            "subscribe": 1,
        }

        # ----------------------------------------------------
        # SEND SUBSCRIPTION REQUEST
        # ----------------------------------------------------
        #
        # json.dumps() converts the Python dictionary into
        # a JSON string.
        #
        # self.ws.send() sends that JSON request through the
        # already-established WebSocket connection.
        #

        self.ws.send(
            json.dumps(request)
        )

        # ----------------------------------------------------
        # DISPLAY SUBSCRIPTION STATUS
        # ----------------------------------------------------
        #
        # Show which symbol was requested.
        #
        # If symbol is "R_100":
        #
        #     Subscribed: R_100
        #

        print(
            f"Subscribed: {symbol}"
        )


    # --------------------------------------------------------
    # SET CALLBACKS
    # --------------------------------------------------------
    #
    # These methods allow the main application to provide
    # functions that should be called when data is received.
    #
    # A callback is simply a function that is stored and called
    # later.
    #


    def set_tick_callback(
        self,
        callback,
    ):

        # ----------------------------------------------------
        # STORE LIVE-TICK CALLBACK
        # ----------------------------------------------------
        #
        # The supplied callback function is stored in:
        #
        #     self.tick_callback
        #
        # Later receive_loop() checks this variable.
        #
        # If a callback exists, it calls:
        #
        #     self.tick_callback(tick)
        #
        self.tick_callback = callback


    def set_history_callback(
        self,
        callback,
    ):

        # ----------------------------------------------------
        # STORE HISTORICAL-DATA CALLBACK
        # ----------------------------------------------------
        #
        # The supplied callback function is stored in:
        #
        #     self.history_callback
        #
        # Later receive_loop() uses this callback when
        # historical data arrives.
        #
        self.history_callback = callback


    # --------------------------------------------------------
    # RECEIVE LOOP
    # --------------------------------------------------------
    #
    # This is the main receiving loop of the WebSocket client.
    #
    # Its job is to continuously:
    #
    #     1. Wait for a WebSocket message.
    #     2. Convert JSON into Python data.
    #     3. Identify the message type.
    #     4. Process live ticks.
    #     5. Process historical data.
    #     6. Display API errors.
    #     7. Handle connection problems.
    #
    # The loop continues while:
    #
    #     self.running == True
    #
    # This method therefore acts like the client's
    # continuously-running message receiver.
    #

    def receive_loop(self):

        # ----------------------------------------------------
        # CONTINUE WHILE CLIENT IS RUNNING
        # ----------------------------------------------------
        #
        # As long as self.running is True, keep receiving
        # WebSocket messages.
        #
        # When another part of the program changes:
        #
        #     self.running = False
        #
        # the while loop will stop.
        #

        while self.running:

            # ------------------------------------------------
            # PROTECT THE RECEIVE OPERATION
            # ------------------------------------------------
            #
            # WebSocket communication can generate exceptions.
            #
            # try/except allows the program to handle those
            # problems instead of immediately crashing.
            #

            try:

                # --------------------------------------------
                # RECEIVE MESSAGE
                # --------------------------------------------
                #
                # self.ws.recv() waits for a message from
                # the WebSocket server.
                #
                # The received value is normally a JSON string.
                #
                message = self.ws.recv()

                # --------------------------------------------
                # IGNORE EMPTY MESSAGE
                # --------------------------------------------
                #
                # If no useful message was received, continue
                # with the next iteration of the loop.
                #
                # "continue" skips the remaining code in this
                # iteration and starts the while loop again.
                #

                if not message:
                    continue

                # --------------------------------------------
                # CONVERT JSON TO PYTHON DATA
                # --------------------------------------------
                #
                # Deriv sends JSON text.
                #
                # json.loads() converts that JSON string into
                # Python objects, normally a dictionary.
                #
                data = json.loads(
                    message
                )

                # --------------------------------------------
                # IDENTIFY MESSAGE TYPE
                # --------------------------------------------
                #
                # Deriv responses contain a "msg_type" field.
                #
                # Examples:
                #
                #     "tick"
                #     "history"
                #     "error"
                #
                # .get() safely retrieves the value.
                #
                # If "msg_type" does not exist, None is returned.
                #

                msg_type = data.get(
                    "msg_type"
                )

                # --------------------------------------------
                # LIVE TICK
                # --------------------------------------------
                #
                # If Deriv tells us this message is a live
                # market tick, msg_type will be:
                #
                #     "tick"
                #
                if msg_type == "tick":

                    # ----------------------------------------
                    # GET TICK DATA
                    # ----------------------------------------
                    #
                    # The actual tick information is contained
                    # inside the "tick" field of the response.
                    #
                    tick_data = data.get(
                        "tick"
                    )

                    # ----------------------------------------
                    # IGNORE MISSING TICK DATA
                    # ----------------------------------------
                    #
                    # If the response says it is a tick but
                    # contains no tick data, ignore it.
                    #

                    if not tick_data:
                        continue

                    # ----------------------------------------
                    # CREATE Tick OBJECT
                    # ----------------------------------------
                    #
                    # The raw Deriv dictionary is converted into
                    # your application's Tick data object.
                    #
                    # This gives the rest of your program a
                    # clean and predictable data structure.
                    #
                    # epoch
                    #     Timestamp of the tick.
                    #
                    # int() converts the value to an integer.
                    #
                    # price
                    #     Current market quote.
                    #
                    # float() converts the quote to a floating-
                    # point number.
                    #
                    # symbol
                    #     Market symbol.
                    #
                    # .get("symbol", SYMBOL)
                    #     Use the symbol from Deriv if present.
                    #     Otherwise use the global SYMBOL value.
                    #

                    tick = Tick(
                        epoch=int(
                            tick_data["epoch"]
                        ),
                        price=float(
                            tick_data["quote"]
                        ),
                        symbol=tick_data.get(
                            "symbol",
                            SYMBOL
                        ),
                    )

                    # ----------------------------------------
                    # SEND TICK TO CALLBACK
                    # ----------------------------------------
                    #
                    # Check whether a live-tick callback has
                    # been registered.
                    #
                    # A function stored in self.tick_callback
                    # is truthy, while None is false.
                    #

                    if self.tick_callback:

                        # Pass the newly-created Tick object
                        # to the callback function.
                        #
                        # Conceptually:
                        #
                        #     callback(tick)
                        #
                        self.tick_callback(
                            tick
                        )

                # --------------------------------------------
                # HISTORICAL DATA
                # --------------------------------------------
                #
                # If the received message contains historical
                # data, msg_type will be:
                #
                #     "history"
                #
                elif msg_type == "history":

                    # ----------------------------------------
                    # SEND HISTORY TO CALLBACK
                    # ----------------------------------------
                    #
                    # Check whether a historical-data callback
                    # has been registered.
                    #

                    if self.history_callback:

                        # Pass the complete API response to
                        # the history callback.
                        #
                        # Unlike the live tick section, this
                        # code passes the complete "data"
                        # dictionary.
                        #
                        self.history_callback(
                            data
                        )

                # --------------------------------------------
                # ERROR
                # --------------------------------------------
                #
                # If Deriv reports an API error, msg_type will
                # be:
                #
                #     "error"
                #
                elif msg_type == "error":

                    # ----------------------------------------
                    # PRINT ERROR HEADER
                    # ----------------------------------------
                    #
                    print(
                        "\nDeriv error:"
                    )

                    # ----------------------------------------
                    # PRINT COMPLETE ERROR RESPONSE
                    # ----------------------------------------
                    #
                    # json.dumps() converts the Python
                    # dictionary back into readable JSON text.
                    #
                    # indent=2 makes the JSON nicely formatted
                    # with indentation.
                    #
                    # This is useful for debugging because the
                    # complete response can be inspected.
                    #

                    print(
                        json.dumps(
                            data,
                            indent=2
                        )
                    )

            # ------------------------------------------------
            # WEBSOCKET TIMEOUT
            # ------------------------------------------------
            #
            # If recv() reaches the configured socket timeout,
            # websocket-client raises:
            #
            #     WebSocketTimeoutException
            #
            # A timeout does not necessarily mean that the
            # connection is broken.
            #
            # Therefore we simply continue the receive loop.
            #

            except websocket.WebSocketTimeoutException:

                continue

            # ------------------------------------------------
            # WEBSOCKET CONNECTION CLOSED
            # ------------------------------------------------
            #
            # This exception occurs when the WebSocket
            # connection has been closed.
            #

            except websocket.WebSocketConnectionClosedException:

                # Tell the user that the connection ended.
                #

                print(
                    "\nWebSocket connection closed."
                )

                # Mark the client as no longer running.
                #
                # This causes:
                #
                #     while self.running:
                #
                # to stop.
                #

                self.running = False

            # ------------------------------------------------
            # OTHER UNEXPECTED ERRORS
            # ------------------------------------------------
            #
            # Any other exception that occurs inside the
            # receive loop reaches this block.
            #
            # "as error" stores the exception object in the
            # variable named error.
            #

            except Exception as error:

                # Display the actual exception message.
                #
                # This helps identify unexpected problems.
                #

                print(
                    f"\nWebSocket error: {error}"
                )

                # Stop the receive loop because an unexpected
                # error occurred.
                #

                self.running = False

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------
    #
    # This method safely shuts down the Deriv client.
    #
    # Main jobs:
    #
    #     1. Stop the receive loop.
    #     2. Close the WebSocket connection.
    #     3. Remove the WebSocket object.
    #     4. Show a disconnected message.
    #

    def close(self):

        # ----------------------------------------------------
        # STOP THE CLIENT
        # ----------------------------------------------------
        #
        # receive_loop() contains:
        #
        #     while self.running:
        #
        # Changing this to False tells the receive loop to stop.
        #
        self.running = False

        # ----------------------------------------------------
        # CHECK WHETHER A WEBSOCKET EXISTS
        # ----------------------------------------------------
        #
        # self.ws is None when there is no WebSocket object.
        #
        # If a WebSocket object exists, this condition is True
        # and we continue with the closing process.
        #

        if self.ws:

            # ------------------------------------------------
            # TRY TO CLOSE THE WEBSOCKET
            # ------------------------------------------------
            #
            # Closing a network connection can sometimes raise
            # an exception.
            #
            # We use try/except so that an error while closing
            # does not crash the application.
            #

            try:
                self.ws.close()

            # -----------------------------------------------
            # IGNORE CLOSE ERRORS
            # -----------------------------------------------
            #
            # If any exception happens while closing the
            # WebSocket, simply ignore it.
            #
            # The client is already trying to shut down, so
            # there is no need to stop the program because of
            # a close error.
            #

            except Exception:
                pass

            # ------------------------------------------------
            # REMOVE THE WEBSOCKET OBJECT
            # ------------------------------------------------
            #
            # After closing the connection, set self.ws to None.
            #
            # This clearly represents:
            #
            #     No active WebSocket connection exists.
            #
            # It also prevents the program from accidentally
            # treating the old WebSocket object as active.
            #

            self.ws = None

        # ----------------------------------------------------
        # DISPLAY DISCONNECTED MESSAGE
        # ----------------------------------------------------
        #
        # Tell the user that the client has been disconnected.
        #

        print(
            "\nDisconnected."
        )



# ============================================================
# CANDLE BUILDER
# ============================================================
#
# This class converts individual market ticks into fixed-time
# OHLC candles.
#
# A tick is one price update.
#
# Example:
#
#     Tick 1 -> 4300.10
#     Tick 2 -> 4300.20
#     Tick 3 -> 4299.90
#     Tick 4 -> 4300.50
#
# These ticks can be grouped into one candle:
#
#     Open  = 4300.10
#     High  = 4300.50
#     Low   = 4299.90
#     Close = 4300.50
#
# For a 60-second timeframe, ticks are grouped into one-minute
# time periods.
#
# Example:
#
#     10:45:00 -> 10:45:59
#     10:46:00 -> 10:46:59
#     10:47:00 -> 10:47:59
#
# The class keeps one candle "current" while ticks are arriving.
# When the time period changes, the current candle becomes
# completed and a new candle starts.
#

class LiveCandleBuilder:
    """
    Converts ticks into fixed-time OHLC candles.

    Example for 60 seconds:

        10:45:00 -> 10:45:59
        10:46:00 -> 10:46:59
        10:47:00 -> 10:47:59
    """

    # --------------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------------
    #
    # This runs when LiveCandleBuilder is created.
    #
    # timeframe_seconds specifies the size of each candle.
    #
    # Examples:
    #
    #     60  -> 1 minute
    #     300 -> 5 minutes
    #     900 -> 15 minutes
    #
    def __init__(
        self,
        timeframe_seconds: int,
    ):

        # ----------------------------------------------------
        # STORE TIMEFRAME
        # ----------------------------------------------------
        #
        # Save the candle timeframe so other methods can use it.
        #
        self.timeframe_seconds = (
            timeframe_seconds
        )

        # ----------------------------------------------------
        # CURRENT CANDLE
        # ----------------------------------------------------
        #
        # This stores the candle that is currently being built.
        #
        # At the beginning there is no candle because no tick
        # has been received yet.
        #
        # Therefore it starts as None.
        #
        self.current_candle = None

        # ----------------------------------------------------
        # COMPLETED CANDLES
        # ----------------------------------------------------
        #
        # This list stores candles that have finished.
        #
        # Every time a candle period ends, the completed candle
        # is appended to this list.
        #
        self.completed_candles = []

    # --------------------------------------------------------
    # GET CANDLE START
    # --------------------------------------------------------
    #
    # This method calculates the beginning timestamp of the
    # candle to which a tick belongs.
    #
    # epoch is a Unix timestamp measured in seconds.
    #
    # Example with a 60-second timeframe:
    #
    #     epoch = 10:45:37
    #
    # The method calculates:
    #
    #     10:45:00
    #
    # So every tick between 10:45:00 and 10:45:59 gets the
    # same candle start timestamp.
    #

    def candle_start(
        self,
        epoch: int,
    ) -> int:

        # ----------------------------------------------------
        # ROUND DOWN TO CANDLE BOUNDARY
        # ----------------------------------------------------
        #
        # // performs integer/floor division.
        #
        # Multiplying by timeframe_seconds moves the result
        # back to the exact beginning of the time period.
        #
        # Example:
        #
        #     timeframe = 60
        #
        #     125 // 60 = 2
        #
        #     2 * 60 = 120
        #
        # Therefore:
        #
        #     epoch 125 belongs to candle starting at 120.
        #
        return (
            epoch
            // self.timeframe_seconds
        ) * self.timeframe_seconds

    # --------------------------------------------------------
    # PROCESS TICK
    # --------------------------------------------------------
    #
    # This method receives one Tick at a time and uses it to
    # build/update the current OHLC candle.
    #
    # There are three main situations:
    #
    #     1. No current candle exists.
    #     2. Tick belongs to the current candle.
    #     3. Tick belongs to a new candle.
    #
    def process_tick(
        self,
        tick: Tick,
    ):

        # ----------------------------------------------------
        # FIND CANDLE START TIME
        # ----------------------------------------------------
        #
        # Determine which candle period this tick belongs to.
        #
        # tick.epoch is the tick's Unix timestamp.
        #
        start_epoch = self.candle_start(
            tick.epoch
        )

        # ----------------------------------------------------
        # CONVERT EPOCH TO PANDAS TIMESTAMP
        # ----------------------------------------------------
        #
        # Convert the candle start Unix timestamp into a
        # pandas Timestamp.
        #
        # unit="s"
        #     Means the epoch value is measured in seconds.
        #
        # utc=True
        #     Makes the timestamp explicitly UTC.
        #
        # Example:
        #
        #     Unix epoch
        #          ↓
        #     pandas UTC timestamp
        #
        timestamp = pd.to_datetime(
            start_epoch,
            unit="s",
            utc=True,
        )

        # --------------------------------------------
        # NO CURRENT CANDLE
        # --------------------------------------------
        #
        # This is the first tick received by the builder.
        #
        # Since there is no existing candle, create the first
        # candle using this tick's price.
        #

        if self.current_candle is None:

            # ------------------------------------------------
            # CREATE FIRST CANDLE
            # ------------------------------------------------
            #
            # Since this is the first tick:
            #
            #     Open  = tick.price
            #     High  = tick.price
            #     Low   = tick.price
            #     Close = tick.price
            #
            # tick_count starts at 1 because one tick has been
            # processed.
            #

            self.current_candle = Candle(
                timestamp=timestamp,
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                tick_count=1,
            )

            # ------------------------------------------------
            # NOTHING COMPLETED YET
            # ------------------------------------------------
            #
            # The first candle is still being built.
            #
            # Therefore there is no completed candle to return.
            #
            return None

        # ----------------------------------------------------
        # GET CURRENT CANDLE START EPOCH
        # ----------------------------------------------------
        #
        # current_candle.timestamp contains the beginning of
        # the current candle.
        #
        # .timestamp() converts the pandas Timestamp into a
        # Unix timestamp.
        #
        # int() converts that timestamp into an integer.
        #
        current_epoch = int(
            self.current_candle.timestamp.timestamp()
        )

        # --------------------------------------------
        # SAME CANDLE
        # --------------------------------------------
        #
        # If the new tick belongs to the same time period as
        # the current candle, update the existing OHLC values.
        #

        if start_epoch == current_epoch:

            # ------------------------------------------------
            # UPDATE HIGH
            # ------------------------------------------------
            #
            # Compare the current high with the new tick price.
            #
            # Whichever value is larger becomes the new high.
            #

            self.current_candle.high = max(
                self.current_candle.high,
                tick.price,
            )

            # ------------------------------------------------
            # UPDATE LOW
            # ------------------------------------------------
            #
            # Compare the current low with the new tick price.
            #
            # Whichever value is smaller becomes the new low.
            #

            self.current_candle.low = min(
                self.current_candle.low,
                tick.price,
            )

            # ------------------------------------------------
            # UPDATE CLOSE
            # ------------------------------------------------
            #
            # The newest tick becomes the current candle's
            # latest closing price.
            #
            # While the candle is still forming, this is the
            # latest/current close.
            #

            self.current_candle.close = (
                tick.price
            )

            # ------------------------------------------------
            # INCREMENT TICK COUNT
            # ------------------------------------------------
            #
            # One more tick has been added to this candle.
            #

            self.current_candle.tick_count += 1

            # ------------------------------------------------
            # CANDLE IS STILL OPEN
            # ------------------------------------------------
            #
            # The current candle has not finished yet.
            #
            # Therefore return None.
            #

            return None

        # --------------------------------------------
        # NEW CANDLE STARTED
        # --------------------------------------------
        #
        # If execution reaches here, start_epoch is different
        # from current_epoch.
        #
        # That means the new tick belongs to a different
        # time period.
        #
        # Therefore the old current candle is now completed.
        #

        # ----------------------------------------------------
        # SAVE COMPLETED CANDLE
        # ----------------------------------------------------
        #
        # Keep a reference to the old candle before replacing
        # self.current_candle with the new one.
        #
        completed = self.current_candle

        # ----------------------------------------------------
        # STORE COMPLETED CANDLE
        # ----------------------------------------------------
        #
        # Add the finished candle to the list of completed
        # candles.
        #

        self.completed_candles.append(
            completed
        )

        # ----------------------------------------------------
        # CREATE NEW CURRENT CANDLE
        # ----------------------------------------------------
        #
        # The current tick is the first tick of the new candle.
        #
        # Therefore:
        #
        #     Open  = tick.price
        #     High  = tick.price
        #     Low   = tick.price
        #     Close = tick.price
        #
        # And because this is the first tick:
        #
        #     tick_count = 1
        #
        self.current_candle = Candle(
            timestamp=timestamp,
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            tick_count=1,
        )

        # ----------------------------------------------------
        # RETURN COMPLETED CANDLE
        # ----------------------------------------------------
        #
        # Return the candle that just finished.
        #
        # This is useful because the calling code can now take
        # the completed candle and perform further processing,
        # such as:
        #
        #     - store it
        #     - display it
        #     - calculate indicators
        #     - calculate Chandelier Exit
        #     - generate signals
        #
        return completed

    # --------------------------------------------------------
    # ADD HISTORICAL CANDLES
    # --------------------------------------------------------
    #
    # This method loads already-existing historical candles
    # into the candle builder.
    #
    # This is useful when the program first starts and you
    # already have historical candle data.
    #
    # Instead of waiting for live ticks to create all the
    # previous candles, we directly place the historical
    # candles into completed_candles.
    #

    def load_candles(
        self,
        candles,
    ):

        # ----------------------------------------------------
        # STORE HISTORICAL CANDLES
        # ----------------------------------------------------
        #
        # list(candles) creates a new Python list from the
        # supplied candles collection.
        #
        # The result replaces the existing completed_candles
        # list.
        #
        # Example:
        #
        #     candles
        #       ↓
        #     [candle1, candle2, candle3]
        #       ↓
        #     self.completed_candles
        #
        # This means the candle builder now has the historical
        # candles available as completed candles.
        #
        self.completed_candles = list(
            candles
        )

# ============================================================
# TRUE RANGE
# ============================================================
#
# True Range (TR) measures the actual price movement/range
# of each candle.
#
# Normal candle range is:
#
#     High - Low
#
# But True Range also considers gaps between the current candle
# and the previous candle's close.
#
# For every candle, three possible ranges are calculated:
#
#     A = High - Low
#     B = |High - Previous Close|
#     C = |Low  - Previous Close|
#
# True Range is the largest of A, B, and C.
#
# This is the standard True Range calculation used as the
# foundation for ATR (Average True Range).
#

class TrueRangeCalculator:

    # --------------------------------------------------------
    # CALCULATE TRUE RANGE
    # --------------------------------------------------------
    #
    # candles is expected to be a pandas DataFrame containing:
    #
    #     high
    #     low
    #     close
    #
    # The method returns a pandas Series containing one True
    # Range value for each candle.
    #

    def calculate(
        self,
        candles: pd.DataFrame,
    ) -> pd.Series:

        # ----------------------------------------------------
        # GET HIGH VALUES
        # ----------------------------------------------------
        #
        # Select the "high" column from the DataFrame.
        #
        high = candles["high"]

        # ----------------------------------------------------
        # GET LOW VALUES
        # ----------------------------------------------------
        #
        # Select the "low" column.
        #
        low = candles["low"]

        # ----------------------------------------------------
        # GET CLOSE VALUES
        # ----------------------------------------------------
        #
        # Select the "close" column.
        #
        close = candles["close"]

        # ----------------------------------------------------
        # PREVIOUS CLOSE
        # ----------------------------------------------------
        #
        # shift(1) moves every close value down by one row.
        #
        # Example:
        #
        #     Current close:
        #
        #     100
        #     102
        #     101
        #
        #     close.shift(1):
        #
        #     NaN
        #     100
        #     102
        #
        # Therefore each candle gets the previous candle's
        # closing price.
        #

        previous_close = (
            close.shift(1)
        )

        # ----------------------------------------------------
        # RANGE A
        # ----------------------------------------------------
        #
        # The normal candle range:
        #
        #     High - Low
        #
        a = high - low

        # ----------------------------------------------------
        # RANGE B
        # ----------------------------------------------------
        #
        # Difference between the current High and the previous
        # candle's Close.
        #
        # .abs() converts negative values to positive values.
        #
        b = (
            high - previous_close
        ).abs()

        # ----------------------------------------------------
        # RANGE C
        # ----------------------------------------------------
        #
        # Difference between the current Low and the previous
        # candle's Close.
        #
        # Again, .abs() gives the absolute distance.
        #

        c = (
            low - previous_close
        ).abs()

        # ----------------------------------------------------
        # FIND TRUE RANGE
        # ----------------------------------------------------
        #
        # pd.concat() combines A, B, and C side-by-side.
        #
        # axis=1 means:
        #
        #     combine as columns
        #
        # .max(axis=1) then finds the largest value across
        # those three columns for every candle.
        #
        # Therefore:
        #
        #     TR = max(
        #         High - Low,
        #         |High - Previous Close|,
        #         |Low - Previous Close|
        #     )
        #

        tr = pd.concat(
            [a, b, c],
            axis=1,
        ).max(axis=1)

        # ----------------------------------------------------
        # FIRST CANDLE
        # ----------------------------------------------------
        #
        # The first candle has no previous candle.
        #
        # Therefore previous_close for the first row is NaN.
        #
        # For the first candle, True Range is simply:
        #
        #     High - Low
        #
        # iloc[0] means the first row/value.
        #

        tr.iloc[0] = (
            high.iloc[0]
            - low.iloc[0]
        )

        # ----------------------------------------------------
        # RETURN TRUE RANGE
        # ----------------------------------------------------
        #
        # Return the complete True Range Series.
        #

        return tr


# ============================================================
# ATR
# ============================================================
#
# ATR = Average True Range.
#
# ATR measures market volatility using True Range values.
#
# This implementation uses Wilder's RMA
# (Wilder's Moving Average).
#
# Initial ATR:
#
#     ATR = SUM(TR for first N candles) / N
#
# In this code that is calculated using:
#
#     np.mean(values[:n])
#
# After the initial ATR, Wilder's recursive formula is used:
#
#     ATR =
#         Previous ATR +
#         (Current TR - Previous ATR) / N
#
# This produces the same recursive smoothing method used by
# Wilder's ATR calculation.
#

class ATRCalculator:
    """
    Wilder's RMA.

    Initial:

        ATR = SUM(TR) / N

    Afterwards:

        ATR =
            Previous ATR +
            (Current TR - Previous ATR) / N
    """

    # --------------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------------
    #
    # period specifies how many True Range values are used for
    # the initial ATR calculation.
    #
    # Example:
    #
    #     period = 14
    #
    # means the initial ATR requires 14 TR values.
    #

    def __init__(
        self,
        period: int,
    ):

        # Store the requested ATR period so calculate() can
        # use it later.
        #
        self.period = period

    # --------------------------------------------------------
    # CALCULATE ATR
    # --------------------------------------------------------
    #
    # tr is a pandas Series containing True Range values.
    #
    # The method returns another pandas Series containing ATR
    # values.
    #

    def calculate(
        self,
        tr: pd.Series,
    ) -> pd.Series:

        # ----------------------------------------------------
        # CONVERT SERIES TO NUMPY ARRAY
        # ----------------------------------------------------
        #
        # Convert the pandas Series into a NumPy array.
        #
        # dtype=float ensures the calculations use floating-
        # point numbers.
        #
        values = tr.to_numpy(
            dtype=float
        )

        # ----------------------------------------------------
        # CREATE RESULT ARRAY
        # ----------------------------------------------------
        #
        # Create an array having the same number of elements
        # as the input TR values.
        #
        # Every value initially contains NaN.
        #
        # NaN means "not available".
        #
        # The first ATR values cannot be calculated until enough
        # TR data exists.
        #

        result = np.full(
            len(values),
            np.nan,
        )

        # ----------------------------------------------------
        # STORE ATR PERIOD
        # ----------------------------------------------------
        #
        # Use a shorter variable name locally.
        #
        # If period = 14:
        #
        #     n = 14
        #

        n = self.period

        # ----------------------------------------------------
        # NOT ENOUGH DATA
        # ----------------------------------------------------
        #
        # If there are fewer TR values than the requested ATR
        # period, the initial ATR cannot be calculated.
        #
        # Example:
        #
        #     period = 14
        #     values = 10
        #
        # There are only 10 values, so ATR cannot be initialized.
        #

        if len(values) < n:

            # Return a Series containing NaN values.
            #
            # index=tr.index preserves the original pandas
            # index from the TR Series.
            #

            return pd.Series(
                result,
                index=tr.index,
            )

        # ----------------------------------------------------
        # INITIAL ATR
        # ----------------------------------------------------
        #
        # The first ATR is calculated using the first N TR
        # values.
        #
        # np.mean() calculates their arithmetic average.
        #
        # Example with N = 3:
        #
        #     TR = [2, 4, 3]
        #
        #     Initial ATR = (2 + 4 + 3) / 3
        #                 = 3
        #
        # n - 1 is used because Python indexes start at zero.
        #
        # For N = 14:
        #
        #     first 14 values -> indexes 0 through 13
        #
        #     initial ATR -> result[13]
        #

        result[n - 1] = np.mean(
            values[:n]
        )

        # ----------------------------------------------------
        # WILDER RMA
        # ----------------------------------------------------
        #
        # Starting from the next TR value, calculate ATR using
        # Wilder's recursive smoothing formula.
        #
        # Formula:
        #
        #     ATR[i] =
        #         ATR[i-1]
        #         +
        #         (TR[i] - ATR[i-1]) / n
        #
        # The loop starts at index n because index n-1 already
        # contains the initial ATR.
        #

        for i in range(
            n,
            len(values)
        ):

            # ------------------------------------------------
            # CALCULATE CURRENT ATR
            # ------------------------------------------------
            #
            # result[i - 1]
            #     Previous ATR.
            #
            # values[i]
            #     Current True Range.
            #
            # (values[i] - result[i - 1])
            #     Difference between current TR and previous ATR.
            #
            # Divide that difference by n to apply Wilder's
            # smoothing.
            #
            # Add it to the previous ATR to obtain the new ATR.
            #

            result[i] = (
                result[i - 1]
                +
                (
                    values[i]
                    - result[i - 1]
                )
                / n
            )

        # ----------------------------------------------------
        # RETURN ATR SERIES
        # ----------------------------------------------------
        #
        # Convert the NumPy result array back into a pandas
        # Series.
        #
        # index=tr.index
        #     Preserves the original TR index.
        #
        # name="ATR"
        #     Gives the returned Series the name "ATR".
        #

        return pd.Series(
            result,
            index=tr.index,
            name="ATR",
        )

# ============================================================
# CHANDELIER EXIT
# ============================================================
#
# This class calculates the Chandelier Exit indicator.
#
# The calculation is built in several stages:
#
#     Candles
#        |
#        v
#     True Range (TR)
#        |
#        v
#     ATR
#        |
#        v
#     ATR Distance
#        |
#        v
#     Highest / Lowest
#        |
#        v
#     Raw Long / Short Stops
#        |
#        v
#     Trailing Stops
#        |
#        v
#     Direction
#        |
#        v
#     Buy / Sell Signals
#
# The final DataFrame contains the original candle data plus
# the calculated indicator columns.
#

class ChandelierExit:

    # --------------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------------
    #
    # Creates a ChandelierExit calculator.
    #
    # period:
    #     Number of candles used for ATR and highest/lowest
    #     calculations.
    #
    #     Default = 22
    #
    # multiplier:
    #     ATR multiplier used to place the stops.
    #
    #     Default = 3.0
    #
    # use_close:
    #     True  -> use closing prices for Highest / Lowest.
    #
    #     False -> use candle High / Low.
    #

    def __init__(
        self,
        period: int = 22,
        multiplier: float = 3.0,
        use_close: bool = True,
    ):

        # Store the ATR/lookback period.
        #
        self.period = period

        # Store the ATR multiplier.
        #
        self.multiplier = multiplier

        # Store whether close prices should be used when finding
        # the highest and lowest values.
        #
        self.use_close = use_close

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------
    #
    # This method performs the complete Chandelier Exit
    # calculation.
    #
    # Input:
    #
    #     candles -> pandas DataFrame containing OHLC data.
    #
    # Output:
    #
    #     DataFrame containing the original data plus:
    #
    #     TR
    #     ATR
    #     ATR_Distance
    #     Highest
    #     Lowest
    #     LongStopRaw
    #     ShortStopRaw
    #     LongStop
    #     ShortStop
    #     Direction
    #     BuySignal
    #     SellSignal
    #

    def calculate(
        self,
        candles: pd.DataFrame,
    ) -> pd.DataFrame:

        # ----------------------------------------------------
        # COPY INPUT DATA
        # ----------------------------------------------------
        #
        # Make a copy instead of modifying the original
        # DataFrame directly.
        #
        # This means calculations performed here will not
        # overwrite the caller's original DataFrame.
        #

        df = candles.copy()

        # ----------------------------------------------------
        # EMPTY DATA CHECK
        # ----------------------------------------------------
        #
        # If there are no candles, there is nothing to
        # calculate.
        #
        # Return the empty DataFrame immediately.
        #

        if len(df) == 0:
            return df

        # ====================================================
        # TRUE RANGE
        # ====================================================
        #
        # Create a TrueRangeCalculator object.
        #
        tr_calculator = (
            TrueRangeCalculator()
        )

        # Calculate True Range for every candle.
        #
        # The resulting Series is stored in a new DataFrame
        # column called "TR".
        #

        df["TR"] = (
            tr_calculator.calculate(df)
        )

        # ====================================================
        # ATR
        # ====================================================
        #
        # Create an ATRCalculator using the configured
        # Chandelier Exit period.
        #
        # If period = 22:
        #
        #     ATRCalculator(22)
        #
        atr_calculator = (
            ATRCalculator(
                self.period
            )
        )

        # Calculate ATR from the True Range values.
        #
        # The resulting ATR Series is stored in:
        #
        #     df["ATR"]
        #

        df["ATR"] = (
            atr_calculator.calculate(
                df["TR"]
            )
        )

        # ====================================================
        # ATR DISTANCE
        # ====================================================
        #
        # Chandelier Exit uses ATR multiplied by a configurable
        # multiplier.
        #
        # Formula:
        #
        #     ATR Distance = ATR × Multiplier
        #
        # With:
        #
        #     ATR = 10
        #     multiplier = 3
        #
        # result:
        #
        #     ATR Distance = 30
        #

        df["ATR_Distance"] = (
            df["ATR"]
            * self.multiplier
        )

        # ====================================================
        # EXTREMUM
        # ====================================================
        #
        # Determine which price source will be used to find the
        # highest and lowest values.
        #
        # When use_close=True:
        #
        #     Highest -> rolling highest Close
        #     Lowest  -> rolling lowest Close
        #
        # When use_close=False:
        #
        #     Highest -> rolling highest High
        #     Lowest  -> rolling lowest Low
        #

        if self.use_close:

            # Use closing prices as the source for both
            # highest and lowest calculations.

            highest_source = (
                df["close"]
            )

            lowest_source = (
                df["close"]
            )

        else:

            # Use candle High values for Highest.

            highest_source = (
                df["high"]
            )

            # Use candle Low values for Lowest.

            lowest_source = (
                df["low"]
            )

        # ----------------------------------------------------
        # HIGHEST VALUE
        # ----------------------------------------------------
        #
        # rolling(self.period) creates a moving window.
        #
        # max() finds the highest value inside that window.
        #
        # Example with period = 3:
        #
        #     Close:     100  105  103  110
        #
        #     Highest:   NaN  NaN  105  110
        #
        # The first complete value requires three candles.
        #

        df["Highest"] = (
            highest_source
            .rolling(
                self.period
            )
            .max()
        )

        # ----------------------------------------------------
        # LOWEST VALUE
        # ----------------------------------------------------
        #
        # Same concept as Highest, but finds the minimum value
        # inside the rolling window.
        #

        df["Lowest"] = (
            lowest_source
            .rolling(
                self.period
            )
            .min()
        )

        # ====================================================
        # RAW STOPS
        # ====================================================
        #
        # Calculate the initial/raw long and short stop levels.
        #
        # Long Stop:
        #
        #     Highest - ATR Distance
        #
        # Short Stop:
        #
        #     Lowest + ATR Distance
        #
        # These are called "raw" stops because they have not yet
        # been converted into trailing stops.
        #

        df["LongStopRaw"] = (
            df["Highest"]
            - df["ATR_Distance"]
        )

        df["ShortStopRaw"] = (
            df["Lowest"]
            + df["ATR_Distance"]
        )

        # ====================================================
        # TRAILING STOPS
        # ====================================================
        #
        # Create NumPy arrays to hold the final trailing stop
        # values.
        #
        # Every value starts as NaN.
        #

        long_stop = np.full(
            len(df),
            np.nan,
        )

        short_stop = np.full(
            len(df),
            np.nan,
        )

        # ----------------------------------------------------
        # CLOSE VALUES
        # ----------------------------------------------------
        #
        # Convert the close column into a NumPy floating-point
        # array.
        #
        # This makes the following loop easier and faster to
        # process.
        #

        closes = (
            df["close"]
            .to_numpy(
                dtype=float
            )
        )

        # ----------------------------------------------------
        # RAW LONG STOPS
        # ----------------------------------------------------
        #
        # Convert LongStopRaw into a NumPy array.
        #

        raw_long = (
            df["LongStopRaw"]
            .to_numpy(
                dtype=float
            )
        )

        # ----------------------------------------------------
        # RAW SHORT STOPS
        # ----------------------------------------------------
        #
        # Convert ShortStopRaw into a NumPy array.
        #

        raw_short = (
            df["ShortStopRaw"]
            .to_numpy(
                dtype=float
            )
        )

        # ----------------------------------------------------
        # PROCESS EVERY CANDLE
        # ----------------------------------------------------
        #
        # The trailing-stop calculation depends on the previous
        # stop value.
        #
        # Therefore this calculation is performed sequentially.
        #

        for i in range(len(df)):

            # ------------------------------------------------
            # NO RAW LONG STOP
            # ------------------------------------------------
            #
            # Before enough candles exist to calculate the
            # rolling Highest/Lowest and ATR, raw_long can be NaN.
            #
            # There is no valid stop to calculate yet.
            #
            # Skip this candle and move to the next one.
            #

            if np.isnan(
                raw_long[i]
            ):

                continue

            # ------------------------------------------------
            # FIRST VALID STOP
            # ------------------------------------------------
            #
            # If this is the first row of the DataFrame, there
            # is no previous stop to compare with.
            #
            # Therefore use the raw values directly.
            #

            if i == 0:

                long_stop[i] = (
                    raw_long[i]
                )

                short_stop[i] = (
                    raw_short[i]
                )

                continue

            # ------------------------------------------------
            # GET PREVIOUS STOPS
            # ------------------------------------------------
            #
            # Retrieve the previous candle's trailing stops.
            #

            previous_long = (
                long_stop[i - 1]
            )

            previous_short = (
                short_stop[i - 1]
            )

            # ------------------------------------------------
            # PREVIOUS STOP NOT AVAILABLE
            # ------------------------------------------------
            #
            # If the previous LongStop is NaN, this is the first
            # valid stop after the initial unavailable period.
            #
            # Start the trailing stops using the raw values.
            #

            if np.isnan(
                previous_long
            ):

                long_stop[i] = (
                    raw_long[i]
                )

                short_stop[i] = (
                    raw_short[i]
                )

                continue

            # --------------------------------------------
            # LONG STOP
            # --------------------------------------------
            #
            # This implements the trailing behavior of the
            # Long Stop.
            #
            # Check whether the previous candle's close was
            # above the previous Long Stop.
            #
            # If it was, the Long Stop is not allowed to move
            # downward.
            #
            # Therefore use:
            #
            #     max(current raw stop, previous stop)
            #
            # Otherwise, reset to the current raw stop.
            #

            if (
                closes[i - 1]
                > previous_long
            ):

                long_stop[i] = max(
                    raw_long[i],
                    previous_long,
                )

            else:

                long_stop[i] = (
                    raw_long[i]
                )

            # --------------------------------------------
            # SHORT STOP
            # --------------------------------------------
            #
            # Check whether the previous candle's close was
            # below the previous Short Stop.
            #
            # If it was, the Short Stop is not allowed to move
            # upward.
            #
            # Therefore use:
            #
            #     min(current raw stop, previous stop)
            #
            # Otherwise, reset to the current raw stop.
            #

            if (
                closes[i - 1]
                < previous_short
            ):

                short_stop[i] = min(
                    raw_short[i],
                    previous_short,
                )

            else:

                short_stop[i] = (
                    raw_short[i]
                )

        # ----------------------------------------------------
        # STORE TRAILING STOPS
        # ----------------------------------------------------
        #
        # Add the calculated NumPy arrays back into the
        # DataFrame.
        #

        df["LongStop"] = (
            long_stop
        )

        df["ShortStop"] = (
            short_stop
        )

        # ====================================================
        # DIRECTION STATE MACHINE
        # ====================================================
        #
        # Direction represents the current Chandelier Exit
        # market direction.
        #
        # Convention used here:
        #
        #     1  = bullish / long direction
        #
        #    -1  = bearish / short direction
        #
        # The direction is stateful.
        #
        # That means the current direction can remain unchanged
        # until the price crosses one of the previous stops.
        #

        direction = np.full(
            len(df),
            np.nan,
        )

        # ----------------------------------------------------
        # INITIAL DIRECTION
        # ----------------------------------------------------
        #
        # Start with direction = 1.
        #
        # Therefore the initial state is bullish/long.
        #

        current_direction = 1

        # ----------------------------------------------------
        # PROCESS EVERY CANDLE
        # ----------------------------------------------------
        #
        # Direction must be calculated sequentially because the
        # current direction depends on the previous state.
        #

        for i in range(len(df)):

            # ------------------------------------------------
            # FIRST ROW
            # ------------------------------------------------
            #
            # For the first candle there is no previous stop.
            #
            # Simply store the initial direction.
            #

            if i == 0:

                direction[i] = (
                    current_direction
                )

                continue

            # ------------------------------------------------
            # PREVIOUS TRAILING STOPS
            # ------------------------------------------------
            #
            # Get the previous candle's LongStop and ShortStop.
            #

            previous_long = (
                long_stop[i - 1]
            )

            previous_short = (
                short_stop[i - 1]
            )

            # ------------------------------------------------
            # PREVIOUS STOPS NOT AVAILABLE
            # ------------------------------------------------
            #
            # If either previous stop is NaN, there is not
            # enough valid stop information to determine a
            # direction change.
            #
            # Keep the current direction unchanged.
            #

            if (
                np.isnan(
                    previous_long
                )
                or
                np.isnan(
                    previous_short
                )
            ):

                direction[i] = (
                    current_direction
                )

                continue

            # --------------------------------------------
            # TRADINGVIEW-STYLE DIRECTION LOGIC
            # --------------------------------------------
            #
            # The logic is:
            #
            #     if current close > previous short stop:
            #
            #         direction = 1
            #
            #     else if current close < previous long stop:
            #
            #         direction = -1
            #
            #     otherwise:
            #
            #         keep previous direction
            #
            # This creates a state machine.
            #
            # The direction does not automatically change on
            # every candle.
            #
            # It changes only when one of the crossing conditions
            # is satisfied.
            #

            if (
                closes[i]
                > previous_short
            ):

                # Price crossed above the previous Short Stop.
                #
                # Set direction to bullish/long.

                current_direction = 1

            elif (
                closes[i]
                < previous_long
            ):

                # Price crossed below the previous Long Stop.
                #
                # Set direction to bearish/short.

                current_direction = -1

            # ------------------------------------------------
            # STORE CURRENT DIRECTION
            # ------------------------------------------------
            #
            # Store the state after applying the crossing logic.
            #

            direction[i] = (
                current_direction
            )

        # ----------------------------------------------------
        # STORE DIRECTION
        # ----------------------------------------------------
        #
        # Add the direction array to the DataFrame.
        #

        df["Direction"] = (
            direction
        )

        # ====================================================
        # SIGNALS
        # ====================================================
        #
        # Buy/Sell signals are generated from a direction change.
        #
        # A signal is not generated simply because the direction
        # is currently 1 or -1.
        #
        # Instead, the code looks for a transition:
        #
        #     -1 -> 1  = BuySignal
        #
        #      1 -> -1 = SellSignal
        #

        # ----------------------------------------------------
        # PREVIOUS DIRECTION
        # ----------------------------------------------------
        #
        # shift(1) moves the Direction column one row down.
        #
        # Therefore each row can be compared with the previous
        # candle's direction.
        #

        previous_direction = (
            df["Direction"].shift(1)
        )

        # ----------------------------------------------------
        # BUY SIGNAL
        # ----------------------------------------------------
        #
        # BuySignal is True only when:
        #
        #     Current Direction  == 1
        #
        # AND
        #
        #     Previous Direction == -1
        #
        # So this detects a transition:
        #
        #     SHORT -> LONG
        #

        df["BuySignal"] = (
            (df["Direction"] == 1)
            &
            (previous_direction == -1)
        )

        # ----------------------------------------------------
        # SELL SIGNAL
        # ----------------------------------------------------
        #
        # SellSignal is True only when:
        #
        #     Current Direction  == -1
        #
        # AND
        #
        #     Previous Direction == 1
        #
        # So this detects a transition:
        #
        #     LONG -> SHORT
        #

        df["SellSignal"] = (
            (df["Direction"] == -1)
            &
            (previous_direction == 1)
        )

        # ====================================================
        # RETURN RESULT
        # ====================================================
        #
        # Return the complete DataFrame.
        #
        # It contains the original candle information together
        # with all calculated Chandelier Exit values and signals.
        #

        return df

# ============================================================
# LIVE DATA ENGINE
# ============================================================

class LiveChandelierEngine:
    """
    Connects:

        Tick
          ↓
        Candle
          ↓
        Chandelier

    This class is the main LIVE processing engine.

    Its job is to connect the different parts of the system:

        1. Receive live Tick data
        2. Send each Tick to LiveCandleBuilder
        3. Build/update OHLC candles
        4. When a candle is completed, calculate Chandelier Exit
        5. Detect BUY / SELL signals
        6. Keep the latest data available for other parts
           of the application.

    In simple terms:

        Deriv Tick
             ↓
        on_tick()
             ↓
        LiveCandleBuilder
             ↓
        Completed Candle
             ↓
        build_dataframe()
             ↓
        ChandelierExit.calculate()
             ↓
        BUY / SELL
    """

    def __init__(
        self,
        timeframe_seconds: int,
        atr_period: int,
        atr_multiplier: float,
        use_close: bool,
    ):

        # ----------------------------------------------------
        # CANDLE BUILDER
        # ----------------------------------------------------

        # Create the object responsible for converting
        # individual live ticks into OHLC candles.
        #
        # Example:
        #
        # Tick 1 -> 100
        # Tick 2 -> 101
        # Tick 3 -> 99
        #
        # becomes:
        #
        # Open  = 100
        # High  = 101
        # Low   = 99
        # Close = 99
        #
        # timeframe_seconds determines how long one candle is.
        #
        # Example:
        #
        # 60  = 1-minute candle
        # 300 = 5-minute candle
        # 900 = 15-minute candle

        self.candle_builder = (
            LiveCandleBuilder(
                timeframe_seconds
            )
        )

        # ----------------------------------------------------
        # CHANDELIER EXIT CALCULATOR
        # ----------------------------------------------------

        # Create the ChandelierExit calculation object.
        #
        # atr_period:
        #     Number of candles used for ATR calculation.
        #
        # atr_multiplier:
        #     ATR multiplier used to calculate stop distance.
        #
        # use_close:
        #     Determines whether Chandelier uses close prices
        #     or high/low prices for the rolling extrema.

        self.chandelier = (
            ChandelierExit(
                period=atr_period,
                multiplier=atr_multiplier,
                use_close=use_close,
            )
        )

        # ----------------------------------------------------
        # THREAD LOCK
        # ----------------------------------------------------

        # Create a threading lock.
        #
        # The live engine may be accessed by multiple threads.
        #
        # For example:
        #
        # Thread 1:
        #     receiving ticks
        #
        # Thread 2:
        #     reading DataFrame for UI
        #
        # The lock prevents both threads from modifying/reading
        # shared data at the same time.
        #
        # This protects shared variables such as:
        #
        #     self.df
        #     self.last_tick
        #     candle_builder
        #     current_signal

        self.lock = threading.Lock()

        # ----------------------------------------------------
        # MAIN DATAFRAME
        # ----------------------------------------------------

        # Store the latest calculated candle + Chandelier data.
        #
        # Initially there is no data, so create an empty
        # pandas DataFrame.
        #
        # Later this will contain columns such as:
        #
        # timestamp
        # open
        # high
        # low
        # close
        # TR
        # ATR
        # ATR_Distance
        # Highest
        # Lowest
        # LongStopRaw
        # ShortStopRaw
        # LongStop
        # ShortStop
        # Direction
        # BuySignal
        # SellSignal

        self.df = pd.DataFrame()

        # ----------------------------------------------------
        # LAST TICK
        # ----------------------------------------------------

        # Stores the most recently received Tick object.
        #
        # Initially there is no tick.

        self.last_tick = None

        # ----------------------------------------------------
        # LAST COMPLETED CANDLE
        # ----------------------------------------------------

        # Stores the most recently completed candle.
        #
        # This is useful when another part of the application
        # wants to know which candle has just finished.

        self.last_completed_candle = None

        # ----------------------------------------------------
        # CURRENT SIGNAL
        # ----------------------------------------------------

        # Stores the latest detected trading signal.
        #
        # Initially:
        #
        #     NONE
        #
        # When a BUY transition occurs:
        #
        #     BUY
        #
        # When a SELL transition occurs:
        #
        #     SELL

        self.current_signal = "NONE"

    # --------------------------------------------------------
    # LOAD HISTORICAL CANDLES
    # --------------------------------------------------------

    def load_history(
        self,
        candles,
    ):

        # Acquire the lock before modifying shared engine data.
        #
        # This makes loading historical candles thread-safe.

        with self.lock:

            # Give the historical candles to the candle builder.
            #
            # These candles become the initial candle history
            # before live ticks start arriving.

            self.candle_builder.load_candles(
                candles
            )

            # Immediately calculate Chandelier values using
            # the loaded historical candles.
            #
            # This is important because ATR and Chandelier Exit
            # need previous candle data.
            #
            # Without history, the live engine would need to wait
            # for enough new candles to build the indicator.

            self.recalculate()

    # --------------------------------------------------------
    # TICK
    # --------------------------------------------------------

    def on_tick(
        self,
        tick: Tick,
    ):

        # Lock the engine while processing the incoming tick.
        #
        # This protects the shared state from concurrent access.

        with self.lock:

            # Save the newest Tick.
            #
            # Other parts of the application can later retrieve
            # it using get_current_tick().

            self.last_tick = tick

            # Send the tick into LiveCandleBuilder.
            #
            # The candle builder decides whether:
            #
            #     1. The tick belongs to the current candle
            #        OR
            #
            #     2. The tick starts a new candle.
            #
            # If a new candle starts, process_tick() returns the
            # previous completed candle.

            completed = (
                self.candle_builder
                .process_tick(tick)
            )

            # ------------------------------------------------
            # NEW CANDLE COMPLETED?
            # ------------------------------------------------

            # If completed is not None, a candle has just finished.
            #
            # This means we now have a new completed OHLC candle
            # that can be used to recalculate Chandelier Exit.

            if completed is not None:

                # Save the newly completed candle.
                #
                # This can be accessed later by other parts of
                # the application.

                self.last_completed_candle = (
                    completed
                )

                # Recalculate the entire indicator DataFrame.
                #
                # The new completed candle may create:
                #
                #     BUY signal
                #     SELL signal
                #     direction change
                #     new stop levels
                #
                # Therefore the Chandelier calculation is updated
                # whenever a candle completes.

                self.recalculate()

    # --------------------------------------------------------
    # BUILD DATAFRAME
    # --------------------------------------------------------

    def build_dataframe(
        self,
    ) -> pd.DataFrame:

        # Get all completed candles from the candle builder.
        #
        # These are candles that have already finished.

        candles = (
            self.candle_builder
            .completed_candles
        )

        # ----------------------------------------------------
        # ADD CURRENT UNFINISHED CANDLE
        # ----------------------------------------------------

        # A live candle may currently be forming.
        #
        # Example:
        #
        # 14:00:00 -> candle starts
        # 14:00:10 -> tick arrives
        # 14:00:20 -> tick arrives
        # 14:00:30 -> tick arrives
        #
        # The 14:00 candle is still unfinished.
        #
        # Add that current candle to the temporary list so the
        # returned DataFrame represents the latest market state.

        if (
            self.candle_builder
            .current_candle
            is not None
        ):

            candles = (
                candles
                + [
                    self.candle_builder
                    .current_candle
                ]
            )

        # ----------------------------------------------------
        # NO CANDLES
        # ----------------------------------------------------

        # If there are no completed candles and no current candle,
        # there is nothing to build.

        if not candles:

            return pd.DataFrame()

        # ----------------------------------------------------
        # CONVERT CANDLE OBJECTS INTO ROWS
        # ----------------------------------------------------

        # This list will contain one dictionary for every candle.
        #
        # Later pandas will convert these dictionaries into
        # DataFrame rows.

        rows = []

        # Process every Candle object.

        for candle in candles:

            # Convert the Candle object's important fields into
            # a dictionary.
            #
            # Each dictionary becomes one DataFrame row.

            rows.append(
                {
                    "timestamp": candle.timestamp,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "tick_count": (
                        candle.tick_count
                    ),
                }
            )

        # ----------------------------------------------------
        # CREATE PANDAS DATAFRAME
        # ----------------------------------------------------

        # Convert the list of dictionaries into a DataFrame.
        #
        # Conceptually:
        #
        # rows
        #   ↓
        # pandas.DataFrame
        #
        # Example:
        #
        # timestamp             open   high   low   close
        # 2026-09-17 10:00       100    105    98     103
        # 2026-09-17 10:01       103    108   101     107

        df = pd.DataFrame(
            rows
        )

        # ----------------------------------------------------
        # SET TIMESTAMP AS INDEX
        # ----------------------------------------------------

        # Move the timestamp column into the DataFrame index.
        #
        # This makes the DataFrame time-series oriented.
        #
        # Instead of:
        #
        # column: timestamp
        #
        # timestamp becomes the row index.

        df = df.set_index(
            "timestamp"
        )

        # Return the completed DataFrame.

        return df

    # --------------------------------------------------------
    # RECALCULATE
    # --------------------------------------------------------

    def recalculate(self):

        # Build the latest candle DataFrame.
        #
        # This includes:
        #
        #     completed candles
        #     +
        #     current unfinished candle, if present

        candles = (
            self.build_dataframe()
        )

        # ----------------------------------------------------
        # EMPTY DATA CHECK
        # ----------------------------------------------------

        # If there are no candles, there is nothing to calculate.
        #
        # Return immediately instead of calling ChandelierExit
        # with an empty DataFrame.

        if candles.empty:
            return

        # ----------------------------------------------------
        # CHANDELIER CALCULATION
        # ----------------------------------------------------

        # Send the candle DataFrame into ChandelierExit.
        #
        # ChandelierExit.calculate() performs the complete
        # indicator pipeline:
        #
        #     Candle
        #       ↓
        #     True Range
        #       ↓
        #     ATR
        #       ↓
        #     ATR Distance
        #       ↓
        #     Highest / Lowest
        #       ↓
        #     Raw Stops
        #       ↓
        #     Trailing Stops
        #       ↓
        #     Direction
        #       ↓
        #     BUY / SELL signals
        #
        # The resulting DataFrame is stored in self.df.

        self.df = (
            self.chandelier
            .calculate(candles)
        )

        # --------------------------------------------
        # Detect newest signal
        # --------------------------------------------

        # We need at least two rows to detect a direction
        # transition.
        #
        # Example:
        #
        # Previous candle = -1
        # Current candle  =  1
        #
        # This creates a BUY signal.
        #
        # Or:
        #
        # Previous candle = 1
        # Current candle  = -1
        #
        # This creates a SELL signal.

        if len(self.df) >= 2:

            # Get the newest row from the calculated DataFrame.
            #
            # iloc[-1] means:
            #
            #     last row

            latest = self.df.iloc[-1]

            # ------------------------------------------------
            # BUY SIGNAL
            # ------------------------------------------------

            # Check whether the newest row contains a BUY signal.
            #
            # BuySignal was generated by ChandelierExit when
            # Direction changed from -1 to 1.

            if latest["BuySignal"]:

                # Store the current signal as BUY.

                self.current_signal = (
                    "BUY"
                )

                # Print a blank line to visually separate this
                # signal from previous terminal output.

                print()

                # Print a visible BUY header.

                print(
                    "========== BUY =========="
                )

                # Display the current/latest candle close price.
                #
                # :.3f means:
                #
                #     format the number with 3 decimal places.
                #
                # Example:
                #
                # 4301.123456
                #
                # becomes:
                #
                # 4301.123

                print(
                    f"Price: "
                    f"{latest['close']:.3f}"
                )

                # Display the latest calculated Long Stop.
                #
                # This is the Chandelier trailing stop associated
                # with the long/buy side.

                print(
                    f"Long Stop: "
                    f"{latest['LongStop']:.3f}"
                )

                # Print the bottom border of the BUY message.

                print(
                    "========================="
                )

            # ------------------------------------------------
            # SELL SIGNAL
            # ------------------------------------------------

            # If there was no BUY signal, check for a SELL signal.
            #
            # SellSignal means Direction changed from 1 to -1.

            elif latest["SellSignal"]:

                # Store the current signal as SELL.

                self.current_signal = (
                    "SELL"
                )

                # Print a blank line before the SELL message.

                print()

                # Print the SELL header.

                print(
                    "========= SELL =========="
                )

                # Display the current/latest candle close price.

                print(
                    f"Price: "
                    f"{latest['close']:.3f}"
                )

                # Display the latest Short Stop.
                #
                # This is the Chandelier trailing stop associated
                # with the short/sell side.

                print(
                    f"Short Stop: "
                    f"{latest['ShortStop']:.3f}"
                )

                # Print the bottom border.

                print(
                    "========================"
                )

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    def get_dataframe(self):

        # Acquire the lock before reading self.df.
        #
        # This prevents another thread from changing self.df
        # while it is being read.

        with self.lock:

            # Return a COPY of the DataFrame.
            #
            # Returning a copy is important because the caller
            # receives its own DataFrame object.
            #
            # The caller can work with the returned DataFrame
            # without directly modifying self.df inside the engine.

            return self.df.copy()

    # --------------------------------------------------------
    # GET CURRENT TICK
    # --------------------------------------------------------

    def get_current_tick(self):

        # Lock access to the shared last_tick variable.

        with self.lock:

            # Return the most recently received Tick object.

            return self.last_tick

    # --------------------------------------------------------
    # CURRENT CANDLE
    # --------------------------------------------------------

    def get_current_candle(self):

        # Lock access because the current candle can be modified
        # by the live tick-processing thread.

        with self.lock:

            # Return the candle that is currently being built.
            #
            # This candle is NOT necessarily completed yet.
            #
            # It contains the latest live market information.
            #
            # Example:
            #
            # 10:00 candle:
            #
            # Open  = 4300.100
            # High  = 4301.500
            # Low   = 4299.800
            # Close = 4301.200
            #
            # If the 1-minute period has not finished, this is
            # still the current unfinished candle.

            return (
                self.candle_builder
                .current_candle
            )

# ============================================================
# HISTORICAL DATA CONVERTER
# ============================================================

class HistoryConverter:
    """
    Converts Deriv ticks_history response into candles.

    The purpose of this class is to convert historical data
    received from the Deriv API into the SAME Candle format
    used by the live data engine.

    Data flow:

        Deriv ticks_history response
                    ↓
                history
                    ↓
              prices + times
                    ↓
                  Tick
                    ↓
          LiveCandleBuilder
                    ↓
                Candles

    This is useful because the rest of the application does
    not need to care whether candles came from:

        Historical data
        OR
        Live ticks

    Both can become the same Candle objects.
    """

    def __init__(
        self,
        timeframe_seconds: int,
    ):

        # Store the candle timeframe.
        #
        # Example:
        #
        # 60 seconds  -> 1-minute candles
        # 300 seconds -> 5-minute candles
        #
        # This value will later be given to
        # LiveCandleBuilder.

        self.timeframe_seconds = (
            timeframe_seconds
        )

    def convert(
        self,
        data,
    ):

        # ----------------------------------------------------
        # GET HISTORY OBJECT
        # ----------------------------------------------------

        # Deriv's response is expected to contain a "history"
        # object.
        #
        # Example structure:
        #
        # {
        #     "history": {
        #         "times": [...],
        #         "prices": [...]
        #     }
        # }
        #
        # .get("history") safely retrieves the value.
        #
        # If "history" does not exist, None is returned instead
        # of causing a KeyError.

        history = data.get(
            "history"
        )

        # ----------------------------------------------------
        # CHECK HISTORY
        # ----------------------------------------------------

        # If there is no history data, return an empty list.
        #
        # This means:
        #
        #     No historical candles available.

        if not history:

            return []

        # ----------------------------------------------------
        # GET PRICES
        # ----------------------------------------------------

        # Extract the historical prices from the history object.
        #
        # Deriv provides the tick prices as a list.
        #
        # Example:
        #
        # prices = [
        #     4300.10,
        #     4300.25,
        #     4300.05,
        #     4300.80
        # ]

        prices = history.get(
            "prices",
            []
        )

        # ----------------------------------------------------
        # GET TIMES
        # ----------------------------------------------------

        # Extract the timestamp corresponding to each price.
        #
        # Example:
        #
        # times = [
        #     1789450200,
        #     1789450201,
        #     1789450202,
        #     1789450203
        # ]
        #
        # Each time is paired with the price at the same
        # position.

        times = history.get(
            "times",
            []
        )

        # ----------------------------------------------------
        # VALIDATE PRICES AND TIMES
        # ----------------------------------------------------

        # Both lists are required.
        #
        # Without prices:
        #     We cannot create Tick objects.
        #
        # Without times:
        #     We do not know when each price occurred.
        #
        # If either one is empty, return no candles.

        if not prices or not times:

            return []

        # ----------------------------------------------------
        # CREATE TICK LIST
        # ----------------------------------------------------

        # This list will contain Tick objects.
        #
        # The raw Deriv API data will be converted into the
        # internal Tick representation used by the application.

        ticks = []

        # ----------------------------------------------------
        # PAIR TIME + PRICE
        # ----------------------------------------------------

        # zip() combines the two lists element by element.
        #
        # Example:
        #
        # times  = [100, 101, 102]
        # prices = [10, 11, 12]
        #
        # zip() produces:
        #
        # (100, 10)
        # (101, 11)
        # (102, 12)
        #
        # epoch = timestamp
        # price = market price

        for epoch, price in zip(
            times,
            prices
        ):

            # Create an internal Tick object.
            #
            # int(epoch):
            #     Makes sure the timestamp is an integer.
            #
            # float(price):
            #     Makes sure the price is represented as a
            #     floating-point number.
            #
            # symbol=SYMBOL:
            #     Associates this tick with the configured
            #     trading symbol.

            ticks.append(
                Tick(
                    epoch=int(epoch),
                    price=float(price),
                    symbol=SYMBOL,
                )
            )

        # ----------------------------------------------------
        # CREATE CANDLE BUILDER
        # ----------------------------------------------------

        # Create a temporary LiveCandleBuilder.
        #
        # Notice that this is the SAME candle-building class
        # used for live ticks.
        #
        # That means historical ticks and live ticks follow
        # exactly the same candle-building rules.

        builder = (
            LiveCandleBuilder(
                self.timeframe_seconds
            )
        )

        # ----------------------------------------------------
        # CONVERT TICKS INTO CANDLES
        # ----------------------------------------------------

        # Process every historical Tick through the candle
        # builder.
        #
        # The builder will:
        #
        #     create the first candle
        #     update OHLC values
        #     detect candle boundaries
        #     complete old candles
        #     create new candles

        for tick in ticks:

            # Send one historical tick into the candle builder.
            #
            # process_tick() updates the current candle and,
            # whenever a candle boundary is reached, moves the
            # previous candle into completed_candles.

            builder.process_tick(
                tick
            )

        # ----------------------------------------------------
        # RETURN COMPLETED CANDLES
        # ----------------------------------------------------

        # Return all candles that the builder considers
        # completed.
        #
        # The current unfinished candle is NOT returned here.
        #
        # The result is therefore a list of Candle objects that
        # can be loaded into the LiveChandelierEngine.
        #
        # Overall:
        #
        #     Deriv JSON
        #          ↓
        #     history
        #          ↓
        #     prices + times
        #          ↓
        #     Tick objects
        #          ↓
        #     LiveCandleBuilder
        #          ↓
        #     completed Candle objects

        return builder.completed_candles


# ============================================================
# LIVE PLOTTER
# ============================================================

class LivePlotter:
    """
    Matplotlib live graph.

    This class is responsible ONLY for visualization.

    It does not calculate:

        ATR
        Chandelier Exit
        BUY / SELL signals
        Candle values

    Those calculations are already handled by:

        LiveChandelierEngine
            ↓
        ChandelierExit

    LivePlotter simply reads the latest calculated DataFrame
    from the engine and draws it on a Matplotlib graph.

    Overall flow:

        Live Tick
             ↓
        LiveChandelierEngine
             ↓
        Calculated DataFrame
             ↓
        LivePlotter
             ↓
        Matplotlib graph
    """

    def __init__(
        self,
        engine: LiveChandelierEngine,
        symbol: str,
    ):

        # Store a reference to the live engine.
        #
        # The plotter uses this object to retrieve:
        #
        #     calculated DataFrame
        #     current Tick
        #
        # It does NOT create another engine.

        self.engine = engine

        # Store the trading symbol.
        #
        # Example:
        #
        #     R_100
        #     XAUUSD
        #     EURUSD
        #
        # This is mainly used for graph titles and information.

        self.symbol = symbol

        # Matplotlib Figure object.
        #
        # Initially there is no graph window.

        self.fig = None

        # Matplotlib Axes object.
        #
        # This will contain the actual graph:
        #
        #     price lines
        #     stop lines
        #     BUY markers
        #     SELL markers
        #     information panel

        self.ax = None

    # --------------------------------------------------------
    # CREATE GRAPH
    # --------------------------------------------------------

    def create(self):

        # ----------------------------------------------------
        # MATPLOTLIB STYLE
        # ----------------------------------------------------

        # Select Matplotlib's dark background style.
        #
        # This affects the appearance of the graph:
        #
        #     background
        #     axes
        #     text
        #     grid
        #
        # The actual data is not changed.

        plt.style.use(
            "dark_background"
        )

        # ----------------------------------------------------
        # CREATE FIGURE + AXES
        # ----------------------------------------------------

        # Create a Matplotlib figure and one plotting area.
        #
        # figsize=(15, 8) means:
        #
        #     width  = 15 inches
        #     height = 8 inches
        #
        # self.fig:
        #     The complete window/figure.
        #
        # self.ax:
        #     The actual plotting area.

        self.fig, self.ax = plt.subplots(
            figsize=(15, 8)
        )

        # ----------------------------------------------------
        # WINDOW TITLE
        # ----------------------------------------------------

        # Change the operating-system window title.
        #
        # This is the title shown by the GUI window itself.

        self.fig.canvas.manager.set_window_title(
            "Live Chandelier Exit"
        )

        # ----------------------------------------------------
        # GRAPH TITLE
        # ----------------------------------------------------

        # Set the initial graph title.
        #
        # Example:
        #
        #     R_100 - Live Chandelier Exit

        self.ax.set_title(
            f"{self.symbol} - "
            "Live Chandelier Exit"
        )

        # Label the horizontal axis.

        self.ax.set_xlabel(
            "Time"
        )

        # Label the vertical axis.

        self.ax.set_ylabel(
            "Price"
        )

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        # Display a grid behind the graph.
        #
        # alpha=0.15 makes the grid relatively transparent.

        self.ax.grid(
            True,
            alpha=0.15
        )

        # Automatically adjust the layout so labels and other
        # graph elements fit inside the figure.

        self.fig.tight_layout()

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        frame,
    ):

        # ----------------------------------------------------
        # GET LATEST DATA
        # ----------------------------------------------------

        # Ask the LiveChandelierEngine for its latest DataFrame.
        #
        # get_dataframe() returns a COPY of the engine's data.
        #
        # Therefore the plotter works with its own DataFrame
        # instead of directly modifying the engine's DataFrame.

        df = (
            self.engine
            .get_dataframe()
        )

        # ----------------------------------------------------
        # EMPTY DATA CHECK
        # ----------------------------------------------------

        # If there is no data yet, there is nothing to draw.
        #
        # This can happen when the graph starts before historical
        # data or live candles have arrived.

        if df.empty:

            return

        # --------------------------------------------
        # Last N candles
        # --------------------------------------------

        # Only display the newest MAX_CANDLES_ON_GRAPH candles.
        #
        # This prevents the graph from becoming unnecessarily
        # large after a long-running session.
        #
        # Example:
        #
        # MAX_CANDLES_ON_GRAPH = 100
        #
        # Then only the latest 100 candles are displayed.

        df = df.tail(
            MAX_CANDLES_ON_GRAPH
        )

        # ----------------------------------------------------
        # CLEAR PREVIOUS GRAPH
        # ----------------------------------------------------

        # Remove the previous lines, markers, text, etc.
        #
        # The graph will then be redrawn using the newest data.

        self.ax.clear()

        # --------------------------------------------
        # Close
        # --------------------------------------------

        # Draw the candle closing price as a line.
        #
        # df.index:
        #     Candle timestamps.
        #
        # df["close"]:
        #     Closing prices.
        #
        # This creates the main price line.

        self.ax.plot(
            df.index,
            df["close"],
            color="white",
            linewidth=1.5,
            label="Price",
        )

        # --------------------------------------------
        # Long Stop
        # --------------------------------------------

        # Take the LongStop values only when the current
        # direction is LONG/BULLISH.
        #
        # When Direction is not 1, .where() produces NaN.
        #
        # NaN causes Matplotlib to leave a gap in the line.
        #
        # Therefore the long stop is visually shown only during
        # the long direction.

        long_stop = (
            df["LongStop"]
            .where(
                df["Direction"] == 1
            )
        )

        # Draw the long trailing stop.

        self.ax.plot(
            df.index,
            long_stop,
            color="#00ff66",
            linewidth=2.0,
            label="Long Stop",
        )

        # --------------------------------------------
        # Short Stop
        # --------------------------------------------

        # Take ShortStop values only when the current direction
        # is SHORT/BEARISH.
        #
        # For Direction != -1, .where() creates NaN.
        #
        # This makes the short stop line appear only during
        # the short direction.

        short_stop = (
            df["ShortStop"]
            .where(
                df["Direction"] == -1
            )
        )

        # Draw the short trailing stop.

        self.ax.plot(
            df.index,
            short_stop,
            color="#ff3355",
            linewidth=2.0,
            label="Short Stop",
        )

        # --------------------------------------------
        # BUY
        # --------------------------------------------

        # Select only rows where BuySignal is True.
        #
        # These are the candles where Chandelier Direction
        # changed from:
        #
        #     -1 → 1
        #
        # meaning a BUY transition was detected.

        buys = df[
            df["BuySignal"]
        ]

        # ----------------------------------------------------
        # DRAW BUY MARKERS
        # ----------------------------------------------------

        # Only draw BUY markers if at least one BUY signal
        # exists in the displayed DataFrame.

        if not buys.empty:

            # scatter() draws individual points instead of
            # connecting them with a line.
            #
            # buys.index:
            #     Time of BUY signals.
            #
            # buys["LongStop"]:
            #     Vertical position of the BUY marker.
            #
            # marker="^":
            #     Upward-pointing triangle.
            #
            # s=120:
            #     Marker size.
            #
            # zorder=10:
            #     Places the marker above normal graph lines.

            self.ax.scatter(
                buys.index,
                buys["LongStop"],
                color="#00ff66",
                marker="^",
                s=120,
                zorder=10,
                label="BUY",
            )

        # --------------------------------------------
        # SELL
        # --------------------------------------------

        # Select only rows where SellSignal is True.
        #
        # These are the candles where Direction changed from:
        #
        #     1 → -1
        #
        # meaning a SELL transition was detected.

        sells = df[
            df["SellSignal"]
        ]

        # ----------------------------------------------------
        # DRAW SELL MARKERS
        # ----------------------------------------------------

        # Draw SELL markers only when SELL signals exist.

        if not sells.empty:

            # Draw downward-pointing triangles at the
            # ShortStop values.
            #
            # marker="v":
            #     Downward triangle.
            #
            # This visually represents SELL transitions.

            self.ax.scatter(
                sells.index,
                sells["ShortStop"],
                color="#ff3355",
                marker="v",
                s=120,
                zorder=10,
                label="SELL",
            )

        # --------------------------------------------
        # Current tick
        # --------------------------------------------

        # Ask the engine for the latest live Tick.

        tick = (
            self.engine
            .get_current_tick()
        )

        # Check whether a Tick is available.
        #
        # Before the first live tick arrives, this can be None.

        if tick:

            # Extract the current live market price from the Tick.

            current_price = (
                tick.price
            )

            # ------------------------------------------------
            # CURRENT PRICE LINE
            # ------------------------------------------------

            # Draw a horizontal line across the entire graph
            # at the current live tick price.
            #
            # axhline() means:
            #
            #     horizontal axis-aligned line.
            #
            # linestyle="--":
            #     dashed line.
            #
            # This lets the user quickly see where the current
            # live market price is relative to the Chandelier
            # stop levels.

            self.ax.axhline(
                current_price,
                color="#00bfff",
                linestyle="--",
                linewidth=1,
                alpha=0.7,
            )

            # ------------------------------------------------
            # CURRENT PRICE LABEL
            # ------------------------------------------------

            # Display the current price inside the graph.
            #
            # 0.99:
            #     99% from the left side.
            #
            # 0.95:
            #     95% from the bottom.
            #
            # transform=self.ax.transAxes means these coordinates
            # are relative to the graph area rather than price
            # coordinates.
            #
            # Therefore the label stays near the top-right even
            # when the price scale changes.

            self.ax.text(
                0.99,
                0.95,
                f"PRICE  {current_price:.3f}",
                transform=self.ax.transAxes,
                ha="right",
                va="top",
                fontsize=13,
                color="#00bfff",
                fontweight="bold",
            )

        # --------------------------------------------
        # Latest calculation
        # --------------------------------------------

        # Get the newest displayed row.
        #
        # iloc[-1] means:
        #
        #     last row

        latest = df.iloc[-1]

        # ----------------------------------------------------
        # GET LATEST DIRECTION
        # ----------------------------------------------------

        # Read the latest Chandelier direction.
        #
        # Expected values:
        #
        #     1  = LONG
        #    -1  = SHORT
        #
        # .get() is used to retrieve the value from the Series.

        direction = latest.get(
            "Direction"
        )

        # ----------------------------------------------------
        # GET LATEST ATR
        # ----------------------------------------------------

        # Read the latest ATR value.

        atr = latest.get(
            "ATR"
        )

        # ----------------------------------------------------
        # GET LATEST LONG STOP
        # ----------------------------------------------------

        # Read the latest LongStop value.

        long_value = latest.get(
            "LongStop"
        )

        # ----------------------------------------------------
        # GET LATEST SHORT STOP
        # ----------------------------------------------------

        # Read the latest ShortStop value.

        short_value = latest.get(
            "ShortStop"
        )

        # --------------------------------------------
        # Direction text
        # --------------------------------------------

        # Convert the numeric direction into human-readable
        # text and select a matching display color.

        if direction == 1:

            # Direction 1 means the Chandelier state is LONG.

            direction_text = (
                "LONG / BULLISH"
            )

            # Color used by the information panel.

            direction_color = (
                "#00ff66"
            )

        elif direction == -1:

            # Direction -1 means the Chandelier state is SHORT.

            direction_text = (
                "SHORT / BEARISH"
            )

            # Color used by the information panel.

            direction_color = (
                "#ff3355"
            )

        else:

            # Any other state is represented as WAIT.

            direction_text = "WAIT"

            # Use white for the neutral state.

            direction_color = "white"

        # --------------------------------------------
        # Information panel
        # --------------------------------------------

        # Build the text shown in the information panel.
        #
        # This gives the user a quick overview of the latest
        # calculated values without looking at the graph lines.

        info = (
            f"SYMBOL     : {self.symbol}\n"
            f"DIRECTION  : {direction_text}\n"
            f"ATR        : "
            f"{atr:.4f}\n"
            f"LONG STOP  : "
            f"{long_value:.4f}\n"
            f"SHORT STOP : "
            f"{short_value:.4f}\n"
            f"TIMEFRAME  : "
            f"{TIMEFRAME_SECONDS}s\n"
            f"ATR PERIOD : "
            f"{ATR_PERIOD}\n"
            f"MULTIPLIER : "
            f"{ATR_MULTIPLIER}"
        )

        # ----------------------------------------------------
        # DRAW INFORMATION PANEL
        # ----------------------------------------------------

        # Put the information text inside the graph.
        #
        # x=0.02:
        #     2% from the left.
        #
        # y=0.97:
        #     97% from the bottom.
        #
        # transform=self.ax.transAxes means these coordinates
        # are relative to the graph area.
        #
        # family="monospace":
        #     Gives the text aligned terminal-style appearance.
        #
        # bbox:
        #     Creates a box behind the information.

        self.ax.text(
            0.02,
            0.97,
            info,
            transform=self.ax.transAxes,
            ha="left",
            va="top",
            fontsize=10,
            color=direction_color,
            family="monospace",
            bbox={
                "boxstyle": "round",
                "facecolor": "#111111",
                "alpha": 0.85,
                "edgecolor": direction_color,
            },
        )

        # --------------------------------------------
        # Title
        # --------------------------------------------

        # Get the current UTC time.
        #
        # timezone.utc makes the timestamp explicitly UTC.
        #
        # strftime("%H:%M:%S UTC") formats it as:
        #
        #     14:32:05 UTC

        current_time = datetime.now(
            timezone.utc
        ).strftime(
            "%H:%M:%S UTC"
        )

        # ----------------------------------------------------
        # UPDATE GRAPH TITLE
        # ----------------------------------------------------

        # Update the title every time the graph refreshes.
        #
        # Example:
        #
        #     R_100 | LIVE CHANDELIER EXIT | 14:32:05 UTC

        self.ax.set_title(
            f"{self.symbol} | "
            f"LIVE CHANDELIER EXIT | "
            f"{current_time}",
            fontsize=15,
            fontweight="bold",
        )

        # Set the horizontal axis label.

        self.ax.set_xlabel(
            "Candle Time"
        )

        # Set the vertical axis label.

        self.ax.set_ylabel(
            "Price"
        )

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        # Redraw the graph grid after ax.clear().
        #
        # clear() removed the previous axes configuration,
        # so the grid must be configured again.

        self.ax.grid(
            True,
            alpha=0.15
        )

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        # Display the labels associated with the plotted objects.
        #
        # Possible entries include:
        #
        #     Price
        #     Long Stop
        #     Short Stop
        #     BUY
        #     SELL

        self.ax.legend(
            loc="upper left"
        )

        # ----------------------------------------------------
        # TIME AXIS FORMAT
        # ----------------------------------------------------

        # Tell Matplotlib how to display datetime values on
        # the X axis.
        #
        # "%H:%M:%S" means:
        #
        #     hour : minute : second
        #
        # Example:
        #
        #     14:32:05

        self.ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%H:%M:%S"
            )
        )

        # Automatically rotate/format the X-axis date labels
        # so they do not overlap.

        self.fig.autofmt_xdate()

        # ----------------------------------------------------
        # FINAL LAYOUT
        # ----------------------------------------------------

        # Recalculate the layout after adding:
        #
        #     title
        #     labels
        #     information panel
        #     legend
        #
        # This helps prevent these elements from being clipped.

        self.fig.tight_layout()



# ============================================================
# APPLICATION
# ============================================================

class ChandelierLiveApplication:
    """
    Main application controller.

    This class connects ALL major components together.

    The complete application flow is:

        Deriv API
            ↓
        DerivClient
            ↓
        Tick
            ↓
        ChandelierLiveApplication
            ↓
        LiveChandelierEngine
            ↓
        LiveCandleBuilder
            ↓
        ChandelierExit
            ↓
        DataFrame
            ↓
        LivePlotter
            ↓
        Live Graph

    Historical data follows another path:

        Deriv History
            ↓
        DerivClient
            ↓
        HistoryConverter
            ↓
        Tick objects
            ↓
        LiveCandleBuilder
            ↓
        Historical Candles
            ↓
        LiveChandelierEngine

    This class is therefore the APPLICATION ORCHESTRATOR.

    It does not perform the actual ATR or Chandelier
    calculations itself.

    Instead, it tells the other classes what to do and
    connects them together.
    """

    def __init__(self):

        # ----------------------------------------------------
        # DERIV CLIENT
        # ----------------------------------------------------

        # Create the DerivClient.
        #
        # DerivClient is responsible for communication with
        # the Deriv API.
        #
        # It handles:
        #
        #     REST OTP request
        #     WebSocket connection
        #     Historical tick request
        #     Live tick subscription
        #     Receiving WebSocket messages
        #
        # APP_ID:
        #     Application ID.
        #
        # AUTH_TOKEN:
        #     Authentication token.
        #
        # ACCOUNT_ID:
        #     Deriv trading account ID.

        self.client = DerivClient(
            app_id=APP_ID,
            auth_token=AUTH_TOKEN,
            account_id=ACCOUNT_ID,
        )

        # ----------------------------------------------------
        # LIVE CHANDELIER ENGINE
        # ----------------------------------------------------

        # Create the LiveChandelierEngine.
        #
        # This object receives Tick objects from the client and
        # converts them into candles and Chandelier calculations.
        #
        # The configuration values come from the global
        # application settings.

        self.engine = (
            LiveChandelierEngine(
                # Length of each candle in seconds.
                timeframe_seconds=(
                    TIMEFRAME_SECONDS
                ),

                # Number of candles used for ATR.
                atr_period=(
                    ATR_PERIOD
                ),

                # ATR multiplier used by Chandelier Exit.
                atr_multiplier=(
                    ATR_MULTIPLIER
                ),

                # Whether Chandelier uses closing prices
                # for the rolling highest/lowest calculation.
                use_close=(
                    USE_CLOSE
                ),
            )
        )

        # ----------------------------------------------------
        # HISTORY CONVERTER
        # ----------------------------------------------------

        # Create the HistoryConverter.
        #
        # Deriv gives historical data as tick timestamps and
        # prices.
        #
        # HistoryConverter converts those raw historical ticks
        # into Candle objects.

        self.history_converter = (
            HistoryConverter(
                TIMEFRAME_SECONDS
            )
        )

        # ----------------------------------------------------
        # LIVE PLOTTER
        # ----------------------------------------------------

        # Create the graph/visualization object.
        #
        # The plotter receives:
        #
        #     self.engine
        #         ↓
        #     calculated DataFrame
        #
        # and:
        #
        #     SYMBOL
        #         ↓
        #     graph title / information panel

        self.plotter = (
            LivePlotter(
                self.engine,
                SYMBOL,
            )
        )

        # ----------------------------------------------------
        # RECEIVER THREAD
        # ----------------------------------------------------

        # Placeholder for the thread that will continuously
        # receive WebSocket messages from Deriv.
        #
        # The actual Thread object is created inside start().

        self.receiver_thread = None

    # --------------------------------------------------------
    # LIVE TICK
    # --------------------------------------------------------

    def on_tick(
        self,
        tick: Tick,
    ):

        # ----------------------------------------------------
        # SEND TICK TO ENGINE
        # ----------------------------------------------------

        # Pass the newly received Tick to the live engine.
        #
        # The engine then:
        #
        #     Tick
        #       ↓
        #     CandleBuilder
        #       ↓
        #     Candle
        #       ↓
        #     Chandelier calculation
        #
        # If the tick completes a candle, the engine can also
        # detect a new BUY or SELL signal.

        self.engine.on_tick(
            tick
        )

        # --------------------------------------------
        # Terminal live display
        # --------------------------------------------

        # Ask the engine for the currently forming candle.
        #
        # This is the candle that is receiving live ticks right
        # now and may not be completed yet.

        candle = (
            self.engine
            .get_current_candle()
        )

        # ----------------------------------------------------
        # CURRENT CANDLE AVAILABLE?
        # ----------------------------------------------------

        # If there is a current candle, display its live values.

        if candle:

            # Convert the Tick's Unix epoch timestamp into a
            # timezone-aware UTC datetime.
            #
            # Example epoch:
            #
            #     1789450200
            #
            # becomes a UTC date/time.

            now = datetime.fromtimestamp(
                tick.epoch,
                tz=timezone.utc,
            )

            # ------------------------------------------------
            # LIVE TERMINAL LINE
            # ------------------------------------------------

            # Print the current tick and current candle data.
            #
            # \r:
            #     Return the cursor to the beginning of the
            #     current terminal line.
            #
            # end="":
            #     Do not move to a new line.
            #
            # flush=True:
            #     Immediately send the output to the terminal.
            #
            # Therefore the same terminal line is continuously
            # updated instead of printing one new line for every
            # tick.
            #
            # Displayed information:
            #
            #     Current UTC time
            #     Symbol
            #     Current tick price
            #     Candle Open
            #     Candle High
            #     Candle Low
            #     Candle Close
            #     Number of ticks inside candle

            print(
                f"\r"
                f"{now.strftime('%H:%M:%S')} "
                f"{SYMBOL} "
                f"PRICE={tick.price:.3f} "
                f"CANDLE="
                f"O:{candle.open:.3f} "
                f"H:{candle.high:.3f} "
                f"L:{candle.low:.3f} "
                f"C:{candle.close:.3f} "
                f"TICKS:{candle.tick_count}",
                end="",
                flush=True,
            )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def on_history(
        self,
        data,
    ):

        # The historical-data processing is wrapped in try/except
        # so that an unexpected historical-data problem does not
        # immediately crash the whole application.

        try:

            # ------------------------------------------------
            # CONVERT HISTORY
            # ------------------------------------------------

            # Pass the raw Deriv history response to
            # HistoryConverter.
            #
            # HistoryConverter performs:
            #
            #     Deriv history response
            #          ↓
            #     prices + times
            #          ↓
            #     Tick objects
            #          ↓
            #     CandleBuilder
            #          ↓
            #     completed candles

            candles = (
                self.history_converter
                .convert(data)
            )

            # ------------------------------------------------
            # HISTORY FOUND
            # ------------------------------------------------

            # Check whether the converter produced candles.

            if candles:

                # Print the number of historical candles created.

                print(
                    f"\nHistorical candles: "
                    f"{len(candles)}"
                )

                # Give the historical candles to the live engine.
                #
                # The engine loads them and recalculates
                # Chandelier Exit.
                #
                # This is the WARM-UP stage.
                #
                # ATR and Chandelier need previous candle data,
                # so historical candles provide the required
                # initial context before live processing.

                self.engine.load_history(
                    candles
                )

            # ------------------------------------------------
            # NO HISTORY
            # ------------------------------------------------

            else:

                # Tell the user that the API response did not
                # produce usable historical candles.

                print(
                    "\nNo historical candles."
                )

        # ----------------------------------------------------
        # HISTORY ERROR
        # ----------------------------------------------------

        # Catch any exception generated while converting or
        # loading historical data.

        except Exception as error:

            # Print the error instead of terminating the entire
            # application immediately.

            print(
                f"\nHistory error: {error}"
            )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    def start(self):

        # ----------------------------------------------------
        # APPLICATION HEADER
        # ----------------------------------------------------

        # Print an empty line before the application header.

        print()

        # Print a separator made from 75 "=" characters.

        print("=" * 75)

        # Print the application name.

        print(
            "LIVE CHANDELIER EXIT MONITOR"
        )

        # Print another separator.

        print("=" * 75)

        # ----------------------------------------------------
        # CONFIGURATION DISPLAY
        # ----------------------------------------------------

        # Show the symbol being monitored.

        print(
            f"Symbol          : {SYMBOL}"
        )

        # Show the candle timeframe.
        #
        # Example:
        #
        #     Timeframe : 60 seconds

        print(
            f"Timeframe       : "
            f"{TIMEFRAME_SECONDS} seconds"
        )

        # Show the ATR period.

        print(
            f"ATR Period      : "
            f"{ATR_PERIOD}"
        )

        # Show the ATR multiplier.

        print(
            f"ATR Multiplier  : "
            f"{ATR_MULTIPLIER}"
        )

        # Show whether the Chandelier calculation uses close
        # prices.

        print(
            f"Use Close       : "
            f"{USE_CLOSE}"
        )

        # Print the bottom separator.

        print("=" * 75)

        # ----------------------------------------------------
        # Connect
        # ----------------------------------------------------

        # Register this application's on_tick() method as the
        # callback for incoming live Tick objects.
        #
        # Later, when DerivClient receives a tick:
        #
        #     DerivClient
        #          ↓
        #     tick_callback
        #          ↓
        #     self.on_tick(tick)

        self.client.set_tick_callback(
            self.on_tick
        )

        # ----------------------------------------------------
        # HISTORY CALLBACK
        # ----------------------------------------------------

        # Register on_history() as the callback for historical
        # data responses.
        #
        # Later:
        #
        #     DerivClient receives history
        #          ↓
        #     self.on_history(data)

        self.client.set_history_callback(
            self.on_history
        )

        # ----------------------------------------------------
        # CONNECT TO DERIV
        # ----------------------------------------------------

        # Establish the WebSocket connection.
        #
        # Internally the DerivClient first obtains the required
        # WebSocket URL and then connects to it.

        self.client.connect()

        # ----------------------------------------------------
        # Historical warm-up
        # ----------------------------------------------------

        # Request historical tick data from Deriv.
        #
        # SYMBOL:
        #     Market symbol.
        #
        # HISTORY_TICKS:
        #     Number of historical ticks requested.
        #
        # The response will eventually be passed to
        # self.on_history() through the registered callback.

        self.client.request_history(
            SYMBOL,
            HISTORY_TICKS,
        )

        # ----------------------------------------------------
        # Subscribe live
        # ----------------------------------------------------

        # Subscribe to the live tick stream for the selected
        # symbol.
        #
        # After subscription, Deriv will send new ticks through
        # the WebSocket.

        self.client.subscribe_ticks(
            SYMBOL
        )

        # ----------------------------------------------------
        # Receiver thread
        # ----------------------------------------------------

        # Create a background thread responsible for receiving
        # WebSocket messages.
        #
        # target:
        #     The function executed by the thread.
        #
        # Here it is:
        #
        #     self.client.receive_loop
        #
        # This means the WebSocket receive loop runs separately
        # from the Matplotlib GUI.
        #
        # Without a separate receiving thread, a continuously
        # running WebSocket receive loop could block the graph.

        self.receiver_thread = (
            threading.Thread(
                target=(
                    self.client
                    .receive_loop
                ),

                # daemon=True means this background thread does
                # not prevent the Python process from exiting
                # when the main application finishes.

                daemon=True,
            )
        )

        # Start the receiver thread.
        #
        # From this point the thread begins executing
        # self.client.receive_loop().

        self.receiver_thread.start()

        # ----------------------------------------------------
        # RUNNING MESSAGE
        # ----------------------------------------------------

        # Tell the user that the main live-monitoring system
        # has started.

        print()
        print(
            "Live monitor running..."
        )

        # Tell the user how to stop the application.

        print(
            "Press Ctrl+C to stop."
        )

        # ----------------------------------------------------
        # CREATE GRAPH
        # ----------------------------------------------------

        # Create the Matplotlib figure and axes.

        self.plotter.create()

        # ----------------------------------------------------
        # MATPLOTLIB ANIMATION
        # ----------------------------------------------------

        # Create a Matplotlib animation.
        #
        # FuncAnimation repeatedly calls:
        #
        #     self.plotter.update
        #
        # allowing the graph to refresh continuously.
        #
        # self.plotter.fig:
        #     The figure to update.
        #
        # self.plotter.update:
        #     Function that redraws the graph.
        #
        # interval:
        #     Number of milliseconds between update calls.
        #
        # cache_frame_data=False:
        #     Prevents Matplotlib from unnecessarily caching
        #     animation frames.

        animation = FuncAnimation(
            self.plotter.fig,
            self.plotter.update,
            interval=GRAPH_UPDATE_MS,
            cache_frame_data=False,
        )

        # ----------------------------------------------------
        # KEEP ANIMATION ALIVE
        # ----------------------------------------------------

        # Keep a reference to the animation object.
        #
        # This is important because Python's garbage collector
        # could otherwise remove the FuncAnimation object when
        # there is no reference to it.
        #
        # self.animation keeps the animation alive while the
        # application is running.

        self.animation = animation

        # ----------------------------------------------------
        # START MATPLOTLIB EVENT LOOP
        # ----------------------------------------------------

        try:

            # Open the Matplotlib graph window and start its
            # GUI event loop.
            #
            # This call normally keeps running while the graph
            # is active.
            #
            # Meanwhile, the receiver thread continues receiving
            # live WebSocket data in the background.

            plt.show()

        # ----------------------------------------------------
        # USER PRESSES CTRL+C
        # ----------------------------------------------------

        except KeyboardInterrupt:

            # Ctrl+C generates KeyboardInterrupt.
            #
            # The application intentionally ignores the exception
            # here because cleanup will happen in finally.

            pass

        # ----------------------------------------------------
        # ALWAYS STOP CLEANLY
        # ----------------------------------------------------

        finally:

            # Whether plt.show() finishes normally or an
            # interruption occurs, call stop().
            #
            # This ensures the WebSocket connection is closed.

            self.stop()

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(self):

        # Print a message showing that shutdown has started.

        print(
            "\nStopping..."
        )

        # Close the Deriv connection.
        #
        # DerivClient.close() will:
        #
        #     stop the receive loop
        #     close the WebSocket
        #     clear the WebSocket object
        #
        # This provides a clean shutdown instead of leaving
        # the network connection running.

        self.client.close()



# ============================================================
# MAIN
# ============================================================

# This is the ENTRY POINT of the entire Python application.
#
# Everything we built earlier:
#
#     DerivClient
#     LiveCandleBuilder
#     TrueRangeCalculator
#     ATRCalculator
#     ChandelierExit
#     LiveChandelierEngine
#     HistoryConverter
#     LivePlotter
#     ChandelierLiveApplication
#
# is finally started from here.
#
# Overall program flow:
#
#     Python starts
#          ↓
#     main()
#          ↓
#     Check credentials
#          ↓
#     Create ChandelierLiveApplication
#          ↓
#     application.start()
#          ↓
#     Connect to Deriv
#          ↓
#     Request historical data
#          ↓
#     Subscribe to live ticks
#          ↓
#     Start receiver thread
#          ↓
#     Start Matplotlib graph
#          ↓
#     Live monitoring
#
# ============================================================

def main():

    # --------------------------------------------------------
    # CHECK DERIV CREDENTIALS
    # --------------------------------------------------------

    # Before starting the application, check whether the user
    # has replaced the placeholder credentials.
    #
    # APP_ID:
    #     Must not still contain "YOUR_APP_ID".
    #
    # AUTH_TOKEN:
    #     Must not still contain "YOUR_AUTH_TOKEN".
    #
    # ACCOUNT_ID:
    #     Must not still contain "YOUR_ACCOUNT_ID".
    #
    # The "or" means that if ANY ONE of these three values is
    # still a placeholder, the application will not start.

    if (
        APP_ID == "YOUR_APP_ID"
        or
        AUTH_TOKEN == "YOUR_AUTH_TOKEN"
        or
        ACCOUNT_ID == "YOUR_ACCOUNT_ID"
    ):

        # ----------------------------------------------------
        # ERROR MESSAGE
        # ----------------------------------------------------

        # Print an empty line for better terminal readability.

        print()

        # Tell the user that the required Deriv credentials
        # have not been configured.

        print(
            "ERROR: Configure your Deriv credentials."
        )

        # Print another empty line.

        print()

        # Tell the user that environment variables are the
        # recommended way to provide the credentials.

        print(
            "Recommended:"
        )

        # Show the environment variable for the Deriv
        # Application ID.
        #
        # The command itself is only printed as an instruction.
        # It does not execute the command.

        print(
            "export DERIV_APP_ID='your_app_id'"
        )

        # Show the environment variable for the authentication
        # token.

        print(
            "export DERIV_AUTH_TOKEN='your_token'"
        )

        # Show the environment variable for the account ID.

        print(
            "export DERIV_ACCOUNT_ID='your_account_id'"
        )

        # Stop main() here.
        #
        # return exits the function before creating the
        # application or connecting to Deriv.
        #
        # Therefore the program will not attempt to connect with
        # placeholder credentials.

        return

    # --------------------------------------------------------
    # CREATE APPLICATION
    # --------------------------------------------------------

    # Create the main application object.
    #
    # This executes:
    #
    #     ChandelierLiveApplication.__init__()
    #
    # which creates:
    #
    #     DerivClient
    #     LiveChandelierEngine
    #     HistoryConverter
    #     LivePlotter
    #
    # At this point the objects are created, but the live system
    # has not started yet.

    application = (
        ChandelierLiveApplication()
    )

    # --------------------------------------------------------
    # START APPLICATION
    # --------------------------------------------------------

    # Put the application startup inside try/except.
    #
    # This allows the program to handle interruptions and
    # unexpected errors more cleanly.

    try:

        # Start the complete live application.
        #
        # application.start() performs the full startup process:
        #
        #     callbacks registered
        #          ↓
        #     Deriv connected
        #          ↓
        #     historical ticks requested
        #          ↓
        #     live tick subscription
        #          ↓
        #     receiver thread started
        #          ↓
        #     graph created
        #          ↓
        #     Matplotlib event loop
        #
        # This is the main operating point of the program.

        application.start()

    # --------------------------------------------------------
    # USER PRESSES CTRL+C
    # --------------------------------------------------------

    except KeyboardInterrupt:

        # Ctrl+C generates KeyboardInterrupt.
        #
        # This is treated as a normal user-requested shutdown
        # instead of being displayed as a Python error.

        print(
            "\nStopped by user."
        )

        # Explicitly stop the application.
        #
        # This closes the Deriv WebSocket connection and performs
        # the application's shutdown procedure.

        application.stop()

    # --------------------------------------------------------
    # UNEXPECTED ERROR
    # --------------------------------------------------------

    except Exception as error:

        # Catch other unexpected exceptions.
        #
        # "as error" stores the exception object in the variable
        # named error.
        #
        # This allows the actual error message to be displayed.

        print(
            f"\nFatal error: {error}"
        )

        # Even when an unexpected error occurs, attempt to close
        # the Deriv connection cleanly.

        application.stop()


# ============================================================
# PYTHON ENTRY-POINT CHECK
# ============================================================

# Python provides the special variable:
#
#     __name__
#
# When this file is executed directly:
#
#     python3 your_script.py
#
# Python sets:
#
#     __name__ == "__main__"
#
# Therefore main() is called.
#
# ------------------------------------------------------------
# IMPORTANT
# ------------------------------------------------------------
#
# If this file is imported by another Python file:
#
#     import your_script
#
# then:
#
#     __name__
#
# will contain the module's name instead of "__main__".
#
# Therefore main() will NOT automatically run.
#
# This makes the file usable both as:
#
#     1. A standalone application
#     2. An importable Python module
#
# ============================================================

if __name__ == "__main__":

    # Start the entire application.

    main()