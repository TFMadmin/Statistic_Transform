import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import random
import datetime

def generate_filler_data(number = 100):
    symbols = ["C", "SM", "BO", "S", "W", "LH", "GC", "ES", "CL", "HG", "FC"]
    directions = [-1, 1]
    dates = pd.date_range('2023-01-01', '2023-06-28')
    initial_value = 1000000
    equity_dict = []
    for date in dates:
        initial_value = initial_value * (np.random.randn() * .01 + 1.001)
        equity_dict.append((date, initial_value))

    equity = pd.DataFrame(equity_dict)
    equity.columns = ["date", "equity"]
    equity.set_index("date", inplace=True)

    random_entries = 10 * np.random.randn(number) + 50
    random_returns = .05 * np.random.randn(number) + .01
    random_exits = random_entries * (1 + random_returns)
    random_contracts = np.round(abs(5 * np.random.randn(number) + 20))
    date_list = []
    symbol_list = []
    dir_list = []
    exit_dates = []
    duration_list = []
    random_profit_total = random_returns * 1000000
    random_profit_per = random_profit_total / random_contracts
    for i in range(0, number):
        j = np.round(abs(np.random.randn() * 2 + 3))
        entry = random.choice(dates)
        exit = entry + datetime.timedelta(days=j)
        duration = exit - entry
        exit_dates.append(exit)
        date_list.append(entry)
        duration_list.append(duration)
        symbol_list.append(random.choice(symbols))
        dir_list.append(random.choice(directions))
    trade_dataFrame = pd.DataFrame(
        [date_list, exit_dates, duration_list, random_entries, random_exits, random_contracts, symbol_list,
         random_profit_total, random_profit_per, dir_list]).T
    trade_dataFrame.columns = ["Entry Date", "Exit Date", "Duration", "Entry Price", "Exit Price", "Contracts",
                               "symbol", "Profit Total", "Profit Per Contract", "Direction"]
    trade_dataFrame["Entry Order"] = 0
    trade_dataFrame["Exit Order"] = 0

    with open("TRADE_DATAFRAME.pkl", "wb") as f:  # "wb" because we want to write in binary mode
        pickle.dump(trade_dataFrame, f)
    with open("EQUITY_DATAFRAME.pkl", "wb") as f:  # "wb" because we want to write in binary mode
        pickle.dump(equity, f)

def calculate_trade_stats():
    with open("G:\My Drive\EQUITY_DATAFRAME.pkl", "rb") as f:  # "rb" because we want to read in binary mode
        equity = pickle.load(f)
    with open("G:\My Drive\TRADE_DATAFRAME.pkl", "rb") as f:  # "rb" because we want to read in binary mode
        trades = pickle.load(f)

    trades["Starting Equity"] = pd.Series([equity.loc[d,"equity"] for d in trades["Entry Date"]])
    trades["Ending Equity"] = trades["Starting Equity"] + trades["Profit Total"]
    trades["Return"] = trades["Profit Total"]/trades["Starting Equity"]
    trades["Profitable"] = (trades["Return"] > 0) * 1
    trades["Dir Label"] = pd.Series(["LONG" if d == 1 else "SHORT" for d in trades["Direction"]])
    trades.to_csv("TRADE_OUTPUT.csv")

def monthly_sharpe(y):
    return np.sqrt(21) * (y.mean()/y.std())

def month3_sharpe(y):
    return np.sqrt(63) * (y.mean()/y.std())

def month6_sharpe(y):
    return np.sqrt(126) * (y.mean()/y.std())

def yearly_sharpe(y):
    return np.sqrt(252) * (y.mean()/y.std())

def monthly_sortino(y):
    return np.sqrt(21) * (y.mean()/y[y <0].std())

def month3_sortino(y):
    return np.sqrt(63) * (y.mean()/y[y <0].std())

def month6_sortino(y):
    return np.sqrt(126) * (y.mean()/y[y <0].std())

def yearly_sortino(y):
    return np.sqrt(252) * (y.mean()/y[y <0].std())

def rolling_drawdown(y):
    cummax = y.cummax()
    drawdown  = cummax - y
    return max(drawdown)

def calculate_equity_curve_stats():
    with open("G:\My Drive\EQUITY_DATAFRAME.pkl", "rb") as f:  # "rb" because we want to read in binary mode
        equity = pickle.load(f)

    equity["cummax"] = equity["equity"].cummax()
    equity["drawdown"] = (equity["cummax"] - equity["equity"])/equity["cummax"]
    equity["return"] = equity["equity"].pct_change()
    equity["Sortino Monthly"] = equity["return"].rolling(21).apply(lambda x: monthly_sortino(x))
    equity["Sortino 3 Month"] = equity["return"].rolling(63).apply(lambda x: month3_sortino(x))
    equity["Sortino 6 Month"] = equity["return"].rolling(126).apply(lambda x: month6_sortino(x))
    equity["Sortino Yearly"] = equity["return"].rolling(252).apply(lambda x: yearly_sortino(x))
    equity["Sharpe Monthly"] = equity["return"].rolling(21).apply(lambda x: monthly_sharpe(x))
    equity["Sharpe 3 Month"] = equity["return"].rolling(63).apply(lambda x: month3_sharpe(x))
    equity["Sharpe 6 Month"] = equity["return"].rolling(126).apply(lambda x: month6_sharpe(x))
    equity["Sharpe Yearly"] = equity["return"].rolling(252).apply(lambda x: yearly_sharpe(x))
    equity["Monthly Return"] = equity["equity"].pct_change(21)
    equity["Quarterly Return"] = equity["equity"].pct_change(63)
    equity["Yearly Return"] = equity["equity"].pct_change(252)
    equity["Monthly Drawdown"] = equity["drawdown"].rolling(21).apply(lambda x: rolling_drawdown(x))
    equity["3 Month Drawdown"] = equity["drawdown"].rolling(63).apply(lambda x: rolling_drawdown(x))
    equity["Yearly Drawdown"] = equity["drawdown"].rolling(252).apply(lambda x: rolling_drawdown(x))
    equity.to_csv("EQUITY_CSV.csv")

def open_positions():
    with open("G:\My Drive\open_positions.pkl", "rb") as f:  # "rb" because we want to read in binary mode
        pos = pickle.load(f)
    pos_data = pd.DataFrame(pos).T
    pos_data.to_csv("pos_data.csv")

def account_balance():
    with open("G:\My Drive\account_balance.pkl", "rb") as f:  # "rb" because we want to read in binary mode
        bal = pickle.load(f)

    bal = bal["Balances"][0]

    for k,v in bal["BalanceDetail"].items():
        bal[k] = v
    del bal["BalanceDetail"]
    del bal["CurrencyDetails"]
    bal_data = pd.Series(bal.values(), index = bal.keys())
    bal_data.to_csv("bal_data.csv")

if __name__ == '__main__':
    open_positions()