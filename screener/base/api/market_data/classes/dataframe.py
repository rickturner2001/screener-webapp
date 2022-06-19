from dataclasses import dataclass
import numpy as np
from pandas import DataFrame
from base.api.market_data.classes.indicators import MovingAverages, inject_ichimoku, RSI, MACD, Bollinger, Stochastic


@dataclass
class EnhancedDataframe:
    dataframe: DataFrame

    def __post_init__(self):
        self.populate_dataframe(self.dataframe, "NULL")

    @staticmethod
    def populate_dataframe(dataframe, ticker: str) -> DataFrame:
        dataframe.index.name = "Date"
        dataframe.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)
        dataframe['Ticker'] = np.array([ticker for _ in range(len(dataframe))])

        closes = dataframe['Close']
        highs = dataframe['High']
        lows = dataframe['Low']
        opens = dataframe['Open']
        adj_closes = dataframe['Adj_Close']

        change = closes.pct_change(1) * 100
        rsi = RSI(closes).data
        macd, macd_signal, macd_histogram = MACD(adj_closes).data
        lower, middle, upper = Bollinger(closes, lows, highs).data
        stoch_k, stoch_d = Stochastic(closes, highs, lows).data
        moving_averages = MovingAverages(closes)

        dataframe['MA20'] = moving_averages.ma_20
        dataframe['MA50'] = moving_averages.ma_50
        dataframe['MA100'] = moving_averages.ma_100
        dataframe['RSI'] = rsi
        dataframe['MACD_histogram'] = macd_histogram
        dataframe['BB_lower'] = lower
        dataframe['BB_middle'] = middle
        dataframe['BB_upper'] = upper
        dataframe['STOCH_K'] = stoch_k
        dataframe['STOCH_D'] = stoch_d
        dataframe['Volume_Change'] = dataframe['Volume'].pct_change(1)
        dataframe["Change"] = change
        inject_ichimoku(dataframe)
        dataframe.dropna(inplace=True)

        return dataframe
