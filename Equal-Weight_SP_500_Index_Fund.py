"""
Equal-Weight S&P 500 Index Fund

The goal of this section is to create a Python script that will accept the value of your portfolio and tell you how many shares of each S&P 500 constituent you should purchase to get an equal-weight version of the index fund.
"""

import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module

#Importing Our List of Stocks
stocks = pd.read_csv('sp_500_stocks.csv') # la variable stocks tiene el listado de tickers. ¡Excluí la acción DISCA, HFC, VIAC y WLTW porque no tienen datos y me traia problemas!

#Acquiring an API Token

from secrets import IEX_CLOUD_API_TOKEN

#Making Our First API Call
symbol='MSFT'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

#Adding Our Stocks Data to a Pandas DataFrame
#Creamos la estructura vacía
my_columns = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']

#Agregamos datos (me avisó que The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead. Pero quise usar concat y me da error)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
# print(symbol_groups)  imprime los grupos

symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    # print(symbol_strings[i]) imprime todos los ticker separados por comas

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    #print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    #print(batch_api_call_url)

    data = requests.get(batch_api_call_url).json()
    #print(data)
    for symbol in symbol_string.split(','):
        n_final_dataframe = pd.DataFrame(
                                        pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'], 
                                                    data[symbol]['quote']['marketCap'], 
                                                    0],
                                                        index = my_columns), 
                                        )
        n_final_dataframe = n_final_dataframe.transpose( )
        final_dataframe = pd.concat([final_dataframe, n_final_dataframe], join="inner") # el inner es para quitar los encabezados en común

"""Calculating the Number of Shares to Buy"""
#portfolio_size = input("Enter the value of your portfolio:")
portfolio_size = 100000

try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number! \n Try again:")
    portfolio_size = input("Enter the value of your portfolio:")

position_size = float(portfolio_size) / len(final_dataframe.index)

for i in range(0, 1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = position_size/final_dataframe['Price'][i]

#Formatting Our Excel Output
writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)
#writer.save()

"""Creating the Formats We'll Need For Our .xlsx File
Formats include colors, fonts, and also symbols like % and $. We'll need four main formats for our Excel document:

String format for tickers
$XX.XX format for stock prices
$XX,XXX format for market capitalization
Integer/Float format for the number of shares to purchase"""

background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

float_format = writer.book.add_format(
        {
            'num_format':'0.0000',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

#Applying the Formats to the Columns of Our .xlsx File
column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    #'D': ['Number of Shares to Buy', integer_format],
                    'D': ['Number of Shares to Buy', float_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

#Saving Our Excel Output
writer.save()
