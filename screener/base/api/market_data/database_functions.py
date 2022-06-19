from pathlib import Path
from typing import Union
from screener.base.api.market_data.classes.dataframe import EnhancedDataframe
from screener.base.api.market_data.classes.fetchers import GeneralMarketDataFetcher
from screener.base.api.market_data.classes.databases import SP500Database
from screener.base.api.market_data.config import db_path
from cython import cfunc


def create_database_sp500(filename: str, extension: str, database_dir: Union[Path, str] = db_path) -> SP500Database:
    database = SP500Database()
    database.create_database_file(path=database_dir, filename=filename, extension=extension)
    database.establish_connection()
    database.create_table_historical()
    return database


@cfunc
def populate_sp500(database: SP500Database, update: bool = True) -> None:
    """
     Populates SP500 database with (OHLCV, adj close, and indicators )

    :param database: database to be updated
    :param verbose: shows progress in % if set to True
    :param update: updates only last day if set to True
    """
    sp100_historical = GeneralMarketDataFetcher()
    tickers = sp100_historical.tickers

    if update:
        tickers_data = sp100_historical.download_data(period='1d', interval='1d')
        # database.update_db()
    else:
        database.clear_historical()
        print(f"Cleared {database.historical_tablename} table")
        tickers_data = sp100_historical.download_data(period="1y", interval="1d")

    for n, ticker in enumerate(tickers):
        percent = 100 * (n / float(len(tickers)))
        print(f"status:  {percent:.2f}")

        df = tickers_data.loc[ticker].T
        df = EnhancedDataframe.populate_dataframe(df, ticker)
        database.do_populate(df)


