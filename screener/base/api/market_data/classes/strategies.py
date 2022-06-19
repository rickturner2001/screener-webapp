from typing import Union
from numpy import vectorize
from pandas import DataFrame
from dataclasses import dataclass
from base.api.market_data.classes.dataframe import EnhancedDataframe


@dataclass
class TickerStrategy:
    def __init__(self, ticker: str, dataframe: DataFrame) -> None:
        self.ticker = ticker
        self.dataframe = EnhancedDataframe.populate_dataframe(dataframe, ticker=self.ticker)

    def r_ma20_ma50(self) -> bool:
        signal = vectorize(self.r_ma20_ma50_signal)(self.dataframe['RSI'],
                                                    self.dataframe['MA20'], self.dataframe["MA50"])[-1]
        print(f"r_ma20_ma50 returned a {signal} value for {self.ticker}")
        return signal

    def r_sd_m(self) -> bool:
        signal = vectorize(self.r_sd_m_signal)(self.dataframe['RSI'], self.dataframe['STOCH_K'],
                                               self.dataframe["MACD_histogram"])[-1]
        print(f"rsi_stoch_macd returned a {signal} value for {self.ticker} ")
        return signal

    def ma_bol_rsi(self) -> bool:
        signal = vectorize(self.ma_bol_rsi_signal)(self.dataframe['Close'], self.dataframe["MA50"],
                                                   self.dataframe['BB_Lower'], self.dataframe['RSI'])[-1]

        print(f"ma_bol_rsi returned a {signal} value for {self.ticker} ")
        return signal

    @staticmethod
    def ichimoku_entry(span_a: float, span_b: float, rsi: float) -> bool:
        return ((span_b - span_a) / span_b) > 0.15 and rsi < 35

    @staticmethod
    def ma_bol_rsi_signal(close: Union[float, int], ma50: Union[float, int], bollinger_lower: Union[float, int],
                          rsi: Union[float, int]) -> Union[float, int]:
        return rsi <= 35 and close < ma50 and close < bollinger_lower

    @staticmethod
    def r_sd_m_signal(
            rsi: Union[float, int], stoch_d: Union[float, int], macd: Union[float, int]) -> Union[float, int]:
        return rsi <= 35 and macd <= -1 and stoch_d <= 15

    @staticmethod
    def r_ma20_ma50_signal(
            rsi: Union[float, int], ma20: Union[float, int], ma50: Union[float, int]) -> Union[float, int]:
        return rsi < 35 and (ma20 < ma50)

    @staticmethod
    def rsima_signal(close, rsi, ma_rsi, bb_lower):
        return (close < bb_lower) and (rsi < 35) and (ma_rsi < 35)

    @staticmethod
    def good_sefi_oversold(sefi, rsi, bollinger, close):
        return (sefi > 65) and (rsi < 35) and (close < bollinger)
