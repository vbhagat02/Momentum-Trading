import requests
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean

''' ALpha Advantage API key'''
API_KEY = '2G8N0KHA5LRTF8BS'

'''polygon api key'''
key = 'KTbbFdgWPAwWfpxT2nWz6PrJMEA3pS0J'

symbol = 'TSLA'
def get_stock_data(symbol, output_size):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize={output_size}&apikey={API_KEY}'
    r = requests.get(url)
    data = r.json()
    return data['Time Series (Daily)']

def data_to_df(data, time_range):
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Moving Avg Price'] = df['5. adjusted close'].rolling(window=50).mean()
    df['Moving Avg Vol'] = df['6. volume'].rolling(window=30).mean()
    df = df[df['Moving Avg Price'].notna()]
    df = df.astype(float)
    df = df.sort_index()
    df = df.tail(time_range)
    df['Price Lower than Avg'] = df['Moving Avg Price'].gt(df['5. adjusted close'])
    df['Volume Higher than Avg'] = df['Moving Avg Vol'].gt(df['6. volume'])
    return df

def plt_df(df, stock):
    close_price = df['5. adjusted close']
    price_plot = df['Moving Avg Price']
    volume_plot = df['6. volume']
    moving_volume_plot = df['Moving Avg Vol']

    plt.rc('figure', figsize=(15, 10))
    plt.style.use('ggplot')

    close_price.plot(label=symbol, legend=True)
    price_plot.plot(label='mavg 30d', legend=True)
    plt.title(f'{stock} Historical Prices')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.savefig(f'{symbol}_price.png')
    plt.show()

    volume_plot.plot(label='Volume', legend=True)
    moving_volume_plot.plot(label='Volume avg 30d', legend=True)
    plt.title(f'{stock} Historical Volume')
    plt.xlabel('Date')
    plt.ylabel('Daily Volume')
    plt.savefig(f'{symbol}_volume.png')
    plt.show()


# time_data = get_stock_data('TSLA', 'full')
# df = data_to_df(time_data, 500)
# print(df.head())
#
# z = 1
# PL = 0.00
# start_price = float(df['5. adjusted close'].head(1))
# end_price = float(df['5. adjusted close'].tail(1))
# stock_return = PL / start_price
#
# dates = []
# returns = []
#
# for index, row in df.iterrows():
#     if row['Volume Higher than Avg'] == 1 and row['Price Lower than Avg'] == 1 and z ==1:
#         print(index, row['5. adjusted close'], 'BUY')
#         close_adj = row['5. adjusted close']
#         PL -= close_adj
#         z = z - 1
#     else:
#         if row['Volume Higher than Avg'] == 0 and row['Price Lower than Avg'] == 0 and z == 0:
#             print(index, row['5. adjusted close'], 'SELL')
#             close_adj = row['5. adjusted close']
#             PL += close_adj
#             stock_return = PL/start_price
#             return_pct = '{:.2%}'.format(stock_return)
#             dates.append(index)
#             returns.append(return_pct)
#             print(f'Total Profit/Loss ${round(PL, 2)}')
#             print(f'Total Return %{return_pct}\n')
#             z += 1
#
# # plt.plot(dates, returns)
# # plt.xlabel('Dates')
# # plt.ylabel('Pct Return')
# # dates = pd.date_range(start = dates[0], end=dates[-1]).tolist()
# # plt.xticks([i for i in range(len(dates))], dates)
# # plt.title(f'{symbol} Returns over Time Period')
# # plt.show()
#
# hold_return = end_price - start_price
# hold_return_pct = '{:.2%}'.format(hold_return/start_price)
# print(f'The return for holding start to end was $ {hold_return} or {hold_return_pct}')



stock_picks = ['TSLA', 'AAPL', 'AMZN', 'HUBS', 'NET', 'MSFT', 'NFLX', 'FB', 'GOOG', 'CRM']
stock_picks = ['TSLA', 'AAPL', 'AMZN', 'QQQ', 'SPY']
portfolio_val = 1000000
stock_returns = {}
hold_returns = {}

for stock in stock_picks:
    stock_data = get_stock_data(stock, 'full')
    per_stock_val = portfolio_val / len(stock_picks)
    stock_df = data_to_df(stock_data, 500)

    start_price = float(stock_df['5. adjusted close'].head(1))
    end_price = float(stock_df['5. adjusted close'].tail(1))
    hold_return = end_price - start_price
    hold_return_pct = (hold_return/start_price) * 100
    shares_bought = 0
    z = 1
    for index, row in stock_df.iterrows():
        if row['Volume Higher than Avg'] == 1 and row['Price Lower than Avg'] == 1 and z ==1:
            close_adj = row['5. adjusted close']
            shares_bought = per_stock_val / close_adj
            z -= 1
        else:
            if row['Volume Higher than Avg'] == 0 and row['Price Lower than Avg'] == 0 and z == 0:
                close_adj = row['5. adjusted close']
                per_stock_val = shares_bought * close_adj
                z += 1
    plt_df(stock_df, stock)
    pct_return = ((per_stock_val - portfolio_val / len(stock_picks)) / (portfolio_val / len(stock_picks)) ) * 100
    stock_returns[stock] = per_stock_val

    hold_returns[stock] = hold_return_pct
    print(f'{stock} Total Value: {per_stock_val}')
    print(f'{stock} Pct Return {pct_return}%')
    print(f'{stock} Holding Return {hold_return_pct}')

portfolio_value = sum(list(stock_returns.values()))
portfolio_return = ((portfolio_value - portfolio_val) / portfolio_val) * 100
portfolio_hold_returns = mean(list(hold_returns.values()))

print(f'Portfolio Value: {portfolio_value}')
print(f'Portfolio Return: {portfolio_return}%')
print(stock_returns)
print(f'Holding Portfolio Returns: {portfolio_hold_returns}%')