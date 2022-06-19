import json
from datetime import datetime
from pandas import DataFrame
from numpy import vectorize
from base.api.market_data.config import db_path
from base.api.market_data.classes.databases import SP500Database
from base.api.market_data.classes.analysis import SP500Analysis
from base.api.market_data.classes.strategies import TickerStrategy
from base.api.market_data.database_functions import populate_sp500


def get_market_breadth_status(market_analysis: SP500Analysis) -> bool:
    if market_analysis.sp500['SEFI Signal Long'].iloc[-1] or market_analysis.sp500['ADR Signal Long'].iloc[-1]:
        return True
    return False


def run_strategies_on_dataframe(df: DataFrame) -> None:
    """Apply all available strategies to `df`"""
    df["Ichimoku_strategy"] = vectorize(TickerStrategy.ichimoku_entry)(df['senkou_span_a'], df['senkou_span_b'],
                                                                       df['RSI'])
    df["Signal_R_MA20_MA50"] = vectorize(TickerStrategy.r_ma20_ma50_signal)(df['RSI'], df['MA20'], df['MA50'])
    df['Signal_MA_BOL_RSI'] = vectorize(TickerStrategy.ma_bol_rsi_signal)(df['Close'], df['MA50'],
                                                                          df['BB_lower'], df["RSI"])
    df["Signal_RSI_STOCH_MACD"] = vectorize(TickerStrategy.r_sd_m_signal)(df["RSI"], df["STOCH_D"],
                                                                          df['MACD_histogram'])


def get_entries_from_indicators(df: DataFrame) -> DataFrame:
    """
    Returns boolean mask of `df` where at least one of the available strategies
    is true
    """
    run_strategies_on_dataframe(df)
    return df[(df["Signal_R_MA20_MA50"]) | (df["Signal_MA_BOL_RSI"])
              | (df["Signal_RSI_STOCH_MACD"]) | df['Ichimoku_strategy']]


def parse_entries(entries: DataFrame) -> dict or bool:
    """

    :param entries: rturn of `parse_entries(get_entries_from_indicators())`
    :return: entries dictionary
    """
    data = {}
    if len(entries) == 0:
        return False
    for i, row in enumerate(entries.index):
        data[entries['Ticker'].loc[row]] = {
            "Ichimoku": {
                "status": bool(entries['Ichimoku_strategy'].loc[row]),
                "values": {
                    "senkou_span_a": entries['senkou_span_a'].loc[row],
                    "senkou_span_b": entries['senkou_span_b'].loc[row],
                    "rsi": entries['RSI'].loc[row],
                }
            },
            "oversold_slow_over_fast": {
                "status": bool(entries['Signal_R_MA20_MA50'].loc[row]),
                "values": {
                    "rsi": entries['RSI'].loc[row],
                    "ma20": entries['MA20'].loc[row],
                    "ma50": entries['MA50'].loc[row]
                }
            },
            "oversold_stochastic": {
                "status": bool(entries['Signal_MA_BOL_RSI'].loc[row]),
                "values": {
                    "close": entries['Close'].loc[row],
                    "ma50": entries['MA50'].loc[row],
                    "bollinger_lower": entries['BB_lower'].loc[row],
                    "rsi": entries["RSI"].loc[row]
                }
            },
            "oversold_MACD": {
                "status": bool(entries['Signal_RSI_STOCH_MACD'].loc[row]),
                "values": {
                    "rsi": entries["RSI"].loc[row],
                    "stochastic_d": entries["STOCH_D"].loc[row],
                    "macd": entries['MACD_histogram'].loc[row]
                }
            },
        }
    return data


def plotting_data_entries(database: SP500Database, tickers: list) -> dict:
    data = {}
    for ticker in tickers:
        df = database.query_ticker_data(ticker)
        data[ticker] = {
            "index": list(df['Date']),
            "Closes": list(df['Close']),
            "MA20": list(df['MA20']),
            "MA50": list(df['MA50'])
        }
    return data


def plotting_data_breadth(database: SP500Database) -> dict:
    changes, volume_changes = database.query_breadth_specifics()

    return {
        "SEFI": {
            "values": changes
        },
        "ADR": {
            "values": volume_changes
        }
    }


def market_status_to_dict() -> dict:
    """
    Executes all utility functions for API data and puts them all together in a dictionary
    """
    sp500_database = SP500Database()
    sp500_database.connect_existing_database(db_path / "sp500.sqlite")
    market_analysis = SP500Analysis(sp500_database)
    market_analysis.sefi()
    market_analysis.adr_analysis()
    dates = sp500_database.query_all_dates()
    df = sp500_database.query_from_date_to_dataframe(dates[-1])
    entries = parse_entries(get_entries_from_indicators(df))

    data = {"market_breadth": {
        'is_entry': bool(get_market_breadth_status(market_analysis)),
        "SEFI": {
            "value": market_analysis.sp500['SEFI'].iloc[-1],
            "short": bool(market_analysis.sp500['SEFI Signal Short'].iloc[-1]),
            "long": bool(market_analysis.sp500['SEFI Signal Long'].iloc[-1])
        },

        "ADR": {
            "value": market_analysis.sp500['ADR'].iloc[-1],
            "short": bool(market_analysis.sp500['ADR Signal Short'].iloc[-1]),
            "long": bool(market_analysis.sp500['ADR Signal Long'].iloc[-1]),
        },

        "strategies": {
            "good_SEFI_oversold": bool(vectorize(TickerStrategy.good_sefi_oversold)(market_analysis.sp500['SEFI'],
                                                                                    market_analysis.sp500['RSI'],
                                                                                    market_analysis.sp500['BB_lower'],
                                                                                    market_analysis.sp500['Close'])[-1])
        }

    }, 'entries': entries,

        "plotting": {
            # "entries": plotting_data(sp500_database, [ticker for ticker in entries])
            "breadth": plotting_data_breadth(sp500_database)
        }

    }
    return data


def parse_last_request(database: SP500Database, request_on_none: bool) -> tuple or None:
    last_request = database.get_last_api_request()
    if not last_request:
        if request_on_none:
            data = market_status_to_dict()
            database.insert_api_data(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), data)
            parse_last_request(database, False)
        else:
            return
    dtime = last_request['Datetime']
    data = last_request['Data']
    return dtime, data


def general_market_data_request():
    """
    Checks if the market is open and if it is it will update the database with last minute data and store
    the result, which will be reused for the next requests until market is open again. If the market is open
    this will simply download last minute data and run the strategies as it normally would.
    """
    sp500_database = SP500Database()
    sp500_database.connect_existing_database(db_path / "sp500.sqlite")
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
    dtime, data = parse_last_request(sp500_database, True)
    dtime = datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S")
    year, month, day, hour, minute, _, _, _, _ = current_datetime.timetuple()
    req_year, req_month, req_day, req_hour, req_minute, _, _, _, _ = dtime.timetuple()
    is_weekend = True if current_datetime.weekday() in [5, 6] else False
    is_afterhours = True if hour >= 16 or (hour < 9) else False
    if is_weekend or is_afterhours:
        if [req_year, req_month, req_day] == [year, month, day] or 1 == 1:
            _, data = parse_last_request(sp500_database, True)
            return json.loads(data)
        else:
            data = market_status_to_dict()
            sp500_database.insert_api_data(str(current_datetime), data)
            return data
    else:
        populate_sp500(sp500_database, update=True)
        return market_status_to_dict()


