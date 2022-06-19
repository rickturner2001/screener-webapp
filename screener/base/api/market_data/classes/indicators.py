from dataclasses import dataclass
from typing import Union, List
import numpy as np
from pandas import Series, DataFrame
from screener.base.api.market_data.classes.databases import SP500Database


# ============================================================
#
#                     Volume Indicators
#
# ============================================================


@dataclass
class AdvancingVolume:
    volume: Union[Series, List[int]]

    def __post_init__(self) -> None:
        self.data = self.get_advancing_volume()

    def get_advancing_volume(self) -> np.ndarray:
        previous_volumes = np.array([self.volume[i - 1] if not i == 0 else np.nan for i, _ in enumerate(self.volume)],
                                    dtype=np.dtype("float32"))
        return np.array([(current_volume - previous_volume) / current_volume * 100
                         for current_volume, previous_volume in zip(self.volume, previous_volumes)],
                        dtype=np.dtype("float32"))


# ============================================================
#
#                    Volatility Indicators
#
# ============================================================


@dataclass
class Bollinger:
    closes: Series
    lows: Series
    highs: Series
    period: int = 20
    std_dev: int = 2
    offset: float = 0

    def __post_init__(self) -> None:
        self.data = self.get_bollinger()

    def get_bollinger(self) -> tuple:
        typical_price = (self.closes + self.lows + self.highs) / 3
        std = typical_price.rolling(self.period).std(ddof=self.offset)
        middle = typical_price.rolling(self.period).mean()
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std

        return lower, middle, upper


@dataclass
class Stochastic:
    closes: Series
    highs: Series
    lows: Series
    k_period: int = 14
    d_period: int = 3

    def __post_init__(self) -> None:
        self.data = self.get_stochastic()

    def get_stochastic(self) -> tuple:
        self.highs = self.highs.rolling(self.k_period).max()
        self.lows = self.lows.rolling(self.k_period).min()
        stoch_k = (self.closes - self.lows) * 100 / (self.highs - self.lows)
        stoch_d = stoch_k.rolling(self.d_period).mean()
        return stoch_k, stoch_d


# ============================================================
#
#                    Momentum Indicators
#
# ============================================================


@dataclass
class RSI:
    closes: Series
    period: int = 14

    def __post_init__(self) -> None:
        self.data: Series = self.get_rsi()

    def get_rsi(self) -> Series:
        delta = self.closes.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=self.period - 1 if self.period > 0 else 0, adjust=False).mean()
        ema_down = down.ewm(com=self.period - 1 if self.period > 0 else 0, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        rsi[:15] = None
        return rsi


@dataclass
class MACD:
    adj_closes: Series
    slow_length: int = 26
    fast_length: int = 12
    signal_smoothing: int = 9

    def __post_init__(self):
        self.data = self.get_macd()

    def get_macd(self):
        fast_ema = self.adj_closes.ewm(span=self.fast_length).mean()
        slow_ema = self.adj_closes.ewm(span=self.slow_length).mean()
        macd = (slow_ema - fast_ema) * -1
        macd_signal_line = macd.ewm(span=self.signal_smoothing).mean()
        histogram = macd - macd_signal_line
        return macd, macd_signal_line, histogram


def get_tr(high, low, previous_close):
    return max([(high - low), abs(high - previous_close), abs(low - previous_close)])


def get_atr(df: DataFrame) -> Series:
    df["TR"] = np.vectorize(get_tr)(df['High'], df['Low'], df['Close'].shift(1))
    atr = df["TR"].ewm(span=14, adjust=False).mean()
    return atr


def get_pdm(high, previous_high, low, previous_low) -> float:
    move_up = high - previous_high
    move_down = previous_low - low
    if (move_up > 0) and (move_up > move_down):
        return move_up
    return float(0)


def get_ndm(high, previous_high, low, previous_low) -> float:
    move_up = high - previous_high
    move_down = previous_low - low
    if (move_down > 0) and move_down > move_up:
        return float(move_down)
    return float(0)


def get_di(dm: Series, atr) -> Series:
    """Pass pdm for pdi / ndm for ndi"""
    return (dm.ewm(span=14, adjust=False).mean() / atr) * 100


def get_adx(pdi, ndi):
    return ((abs(pdi - ndi) / (pdi + ndi)).ewm(span=14, adjust=False).mean()) * 100


def compute_adx(df: DataFrame):
    df['TR'] = np.vectorize(get_tr)(df['High'], df['Low'], df['Close'].shift())
    df['ATR'] = get_atr(df)
    df['PDM'] = np.vectorize(get_pdm)(df['High'], df['High'].shift(), df['Low'], df['Low'].shift())
    df['NDM'] = np.vectorize(get_ndm)(df['High'], df['High'].shift(), df['Low'], df['Low'].shift())
    df['PDI'] = get_di(df['PDM'], df['ATR'])
    df['NDI'] = get_di(df['NDM'], df['ATR'])
    df['ADX'] = get_adx(df['PDI'], df['NDI'])


# ============================================================
#
#                   Miscellaneous Indicators
#
# ============================================================


@dataclass
class MovingAverages:
    closes: Series

    @property
    def ma_20(self):
        return self.closes.rolling(window=20).mean()

    @property
    def ma_50(self):
        return self.closes.rolling(window=50).mean()

    @property
    def ma_100(self):
        return self.closes.rolling(window=100).mean()

    @property
    def ma_200(self):
        return self.closes.rolling(window=200).mean()


@dataclass
class Sefi:
    close: list
    ma20: list

    def __post_init__(self) -> None:
        self.data = self.get_sefi()

    def get_sefi(self) -> list:
        return [self.evaluate(close, ma20) for close, ma20 in zip(self.close, self.ma20)]

    @staticmethod
    def evaluate(close: float, ma20: float) -> Union[float, int]:
        return 1 if close > ma20 else 0


# MARKETS ONLY
class ADR:
    def __init__(self, market_data: SP500Database):
        self.market_data = market_data

    def ad_ratio_value(self) -> List[Union[int, float]]:
        dates = self.market_data.query_all_dates()
        values = []
        for date in dates:
            dataframe = self.market_data.query_from_date_to_dataframe(date)

            # TODO division by 0
            values.append(len(dataframe[dataframe['Change'] > 0]) / len(dataframe[dataframe['Change'] <= 0]))
        return values

    @property
    def data(self):
        return self.ad_ratio_value()


class CVI:
    def __init__(self, market_data: SP500Database):
        self.market_data = market_data

    def advancing_volume_index(self) -> List[int]:
        dates = self.market_data.query_all_dates()
        return [self.count_volume_change(date) - self.count_volume_change(date, positive=False) for date in dates]

    def count_volume_change(self, date: str, positive: bool = True) -> int:
        return self.market_data.cursor.execute(
            f"""select count(Volume_Change) from historical_data
                where date = '{date}' and volume_change {'>' if positive else '<'} 0""").fetchone()['count('
                                                                                                    'Volume_Change)']

    def cumulative_volume_index(self):
        return np.array(self.advancing_volume_index()).cumsum()

    @property
    def data(self):
        return self.cumulative_volume_index()


def inject_ichimoku(dataframe: DataFrame):
    nine_period_high = dataframe['High'].rolling(window=9).max()
    nine_period_low = dataframe['Low'].rolling(window=9).min()

    dataframe['tenkan_sen'] = (nine_period_high + nine_period_low) / 2

    period26_high = dataframe['High'].rolling(window=26).max()
    period26_low = dataframe['Low'].rolling(window=26).min()

    dataframe['kijun_sen'] = (period26_high + period26_low) / 2
    dataframe['senkou_span_a'] = ((dataframe['tenkan_sen'] + dataframe['kijun_sen']) / 2).shift(26)

    period52_high = dataframe['High'].rolling(window=52).max()
    period52_low = dataframe['Low'].rolling(window=52).min()

    dataframe['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)


# ============================================================
#
#                       Signals
#
# ============================================================

def adr_signals_long(adr: float, close: float, ma100: float, ma20: float) -> bool:
    if (adr >= 2) and (close > ma100) and (close < ma20):
        return True
    return False


def adr_signals_short(adr: float, close: float, ma100: float, ma20: float) -> bool:
    if (adr <= .5) and (close < ma100) and (close > ma20):
        return True
    return False
