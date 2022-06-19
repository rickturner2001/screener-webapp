import numpy as np
from numpy import array as np_array
import datetime
from typing import Union, List
from pandas import DataFrame
from abc import abstractmethod
from base.api.market_data.classes.databases import SP500Database, Database
from base.api.market_data.classes.indicators import Sefi
from base.api.market_data.classes.fetchers import GeneralMarketDataFetcher
from base.api.market_data.classes.dataframe import EnhancedDataframe
from base.api.market_data.classes.indicators import ADR, adr_signals_long, adr_signals_short

current_date = datetime.date.today()
one_year_ago = datetime.date.today() - datetime.timedelta(days=365 * 10)

"""
Investopedia 2022, https://www.investopedia.com/terms/m/market_breadth.asp

 Market breadth refers to how many stocks are participating in a given move in an index or on a stock exchange.
 An index may be rising yet more than half the stocks in the index are falling because a small number of stocks
 have such large gains that they drag the whole index higher.

Market breadth indicators can reveal this and warn traders that most stocks are not actually performing well,
even though the rising index makes it look like most stocks are doing well—an index is an average of the stocks in it.
Volume may also be added into these indicator calculations to provide additional insight into how stocks within an index
are acting overall.
"""


class MarketBreadthAnalysis:

    @staticmethod
    def new_highs_lows_index(market_data: DataFrame) -> bool:
        """compares stocks making 52-week highs to stocks making 52-week lows"""
        ...

    @staticmethod
    def ad_ratio_value(database: Database) -> List[Union[int, float]]:
        # TODO (maybe doesn't belong here)
        """The advance decline ratio (ADR) is a technical indicator used to assess stock market sentiment. The ratio
        compares the number of stocks that increased in value to the number of stocks that decreased in value. In
        other words, the ADR compares the number of stocks that rose in price versus the number of stocks that
        declined in price. """
        pass

    @staticmethod
    def on_balance_volume_indicator(dataframe: DataFrame) -> List[Union[float, int]]:
        """
        looks at volume, except up or down volume is based on whether the index rises or falls. If the index falls,
        the total volume is counted as negative. If the index rises, the total volume is negative
        """
        obv = []
        for i, date in enumerate(dataframe.index):
            previous_obv = None if not len(obv) else obv[-1]
            obv.append(
                MarketBreadthAnalysis.on_balance_volume(previous_obv, dataframe['Volume'].iloc[i],
                                                        dataframe['Close'].iloc[i], dataframe['Close'].iloc[i - 1]))
        return obv

    @staticmethod
    def sefi(self):
        pass

    @staticmethod
    def on_balance_volume(
            previous_obv: Union[float, int], volume: int, close: Union[float, int],
            previous_close: Union[float, int]) -> Union[float, int]:

        if not previous_obv:
            return volume

        if close > previous_close:
            return previous_obv + volume

        elif close < previous_close:
            return previous_obv - volume

        return previous_obv

    def count_volume_change(self, date: str, positive: bool = True) -> int:
        pass

    @abstractmethod
    def advancing_volume_index(self) -> List[int]:
        pass


class SP500Analysis(MarketBreadthAnalysis):

    # TODO implement this method
    def advancing_volume_index(self) -> List[int]:
        ...

    def __init__(self, market_data: SP500Database):
        self.sp500 = None
        self.dates = None
        self.market_data = market_data

    def sefi(self, ma_column='MA20') -> DataFrame:
        self.dates = self.market_data.query_all_dates()

        self.sp500 = GeneralMarketDataFetcher.oex_download_data(start=self.dates[0], end=self.dates[-1])
        self.sp500 = EnhancedDataframe.populate_dataframe(self.sp500, "SPX")
        self.sp500['Change'] = (self.sp500['Close'].pct_change(1) * 100).cumsum()

        # TODO  refactor this code ASAP
        results = []
        for date in self.sp500.index:
            dataframe = self.market_data.query_from_date_to_dataframe(date)
            dataframe['SEFI'] = Sefi(dataframe['Close'], dataframe[ma_column]).data

            try:
                results.append(len(dataframe[dataframe["SEFI"] == 0]) / len(dataframe))
            except ZeroDivisionError as e:
                print(f"len dataframe where sefi is 0: {len(dataframe[dataframe['SEFI'] == 0])}")
                print(f"len dataframe: {len(dataframe)}")
                print(f"date: {date}")
                results.append(0)

        assert len(results) == len(self.sp500)
        self.sp500['SEFI'] = np_array(results) * 100

        def sefi_signal_long(sefi):
            if sefi >= 75:
                return True
            return False

        def sefi_signal_short(sefi):
            if sefi <= 25:
                return True
            return False

        self.sp500['SEFI Signal Long'] = np.vectorize(sefi_signal_long)(self.sp500["SEFI"])

        self.sp500["SEFI Signal Short"] = np.vectorize(sefi_signal_short)(self.sp500['SEFI'])
        return self.sp500

    def adr_analysis(self) -> DataFrame:
        adr = ADR(market_data=self.market_data)
        # TODO

        self.sp500.rename(columns={"Adjusted Close": "Adjusted_Close"}, inplace=True)
        adr_data = adr.data
        if not len(self.sp500) == len(adr_data):
            adr_data = adr_data[-len(self.sp500):]
        self.sp500["ADR"] = adr_data
        self.sp500['ADR Signal Long'] = np.vectorize(adr_signals_long)(self.sp500["ADR"], self.sp500['Close'],
                                                                       self.sp500["MA100"], self.sp500["MA20"])
        self.sp500['ADR Signal Short'] = np.vectorize(adr_signals_short)(self.sp500["ADR"], self.sp500['Close'],
                                                                         self.sp500["MA100"], self.sp500["MA20"])

        return self.sp500
