from pandas import read_sql, DataFrame
import numpy as np
from screener.base.api.market_data.classes.fetchers import GeneralMarketDataFetcher
from cython import cfunc
import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from sqlite3 import Connection, Cursor, connect, Row
from enum import Enum
from dataclasses import dataclass
from typing import List, Union, Iterator


numeric = Union[int, float]


class ColumnType(Enum):
    Null = 0
    Integer = 1
    Float = 2
    Text = 3


@dataclass
class Column(ABC):
    label: str
    col_type: str = ""
    nullable: bool = False
    unique: bool = False
    attribute: str = ""
    valid_attributes = ["", "primary_key", "secondary_key"]

    @property
    def column_stmt(self) -> str:
        return f"""{self.label} {self.col_type} {self.attribute_string() if self.attribute else ''}{' NOT NULL' if not self.nullable else ''}{' UNIQUE' if self.unique else ''}"""

    def validate_column_attribute(self):
        if not self.attribute.lower() in self.valid_attributes:
            raise ColumnAttributeError(self.attribute, "Invalid attribute field")

    def attribute_string(self) -> str:
        stmt = " ".join(f"{word.upper()}" if not word == self.attribute.split("_")[-1]
                        else word.upper() + ' ' for word in self.attribute.split("_")
                        )
        return stmt


class DefaultColumn(Column):
    pass


@dataclass
class IntegerColumn(Column):
    def __post_init__(self) -> None:
        self.validate_column_attribute()
        self.col_type = ColumnType(1).name.upper()


@dataclass
class FloatColumn(Column):
    def __post_init__(self) -> None:
        self.validate_column_attribute()
        self.col_type = ColumnType(2).name.upper()


@dataclass
class TextColumn(Column):
    def __post_init__(self) -> None:
        self.validate_column_attribute()
        self.col_type = ColumnType(3).name.upper()


class ColumnAttributeError(Exception):
    """Exception for invalid attributes for column class"""

    def __init__(self, attr: str, msg: str) -> None:
        self.attr = attr
        self.msg = msg
        super().__init__(msg)



@dataclass
class Table:
    table_name: str
    columns: List[Column]

    def parse_columns_opt(self):
        return " ".join(col.column_stmt + "," if not col == self.columns[-1]
                        else col.column_stmt for col in self.columns)

    @property
    def stmt(self):
        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({self.parse_columns_opt()})"





@dataclass
class Database(ABC):
    path: Union[str, Path] = None
    filename: str = None
    extension: str = None
    db_path: Union[str, Path] = None
    _tablenames = []
    _connection: Connection = None
    _cursor: Cursor = None

    def connect_existing_database(self, db_path) -> None:
        self._connection = sqlite3.connect(db_path)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()

    def create_database_file(self, path, filename, extension) -> None:
        self.path = path
        self.filename = filename
        self.extension = extension
        self.db_path: Union[str, Path] = f"{self.path}/{self.filename}.{self.extension}"

        with open(self.db_path, "w") as f:
            f.write("")

    def establish_connection(self) -> None:
        self._connection = connect(self.db_path)
        self._cursor = self._connection.cursor()

    @staticmethod
    def create_table(tablename: str, columns: List[Column], pk: Column = None) -> str:
        """

        :param tablename: Name of the table
        :param columns: List of Column objects
        :param pk: Primary key ("col_name", "type")
        :return: string representation of sql statement to create the table
        """
        stmt = f"""
                      CREATE TABLE IF NOT EXISTS {tablename} (
                      {f"{pk.column_stmt}" if pk else ""},
                      {Database.dynamic_table_columns_create(columns)}
                      )
                      """
        return stmt

    @staticmethod
    def dynamic_table_columns_create(columns: List[Column]):
        stmt = " ".join([f"{col.column_stmt},"
                         if not col == columns[-1] else col.column_stmt for col in columns])
        return stmt

    @abstractmethod
    def do_populate(self, *args: Union[str, int, float]) -> None:
        pass

    def clear_table(self, table: str) -> None:
        self._cursor.execute(f"DELETE FROM ?", (table,))

    def drop_table(self, table: str) -> None:
        self._cursor.execute("DROP TABLE ?", (table,))

    def query_all(self, table: str) -> List[tuple]:
        return self._cursor.execute(f"SELECT * FROM {table}").fetchall()

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection


@dataclass
class SP500Database(Database):
    _historical_tablename: str = "historical_data"
    _api_data_tablename: str = "api_data"
    _oex_data: str = "sp500_prices"

    columns = np.array(["Date", "Ticker", 'Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume', 'MA20', 'MA50',
                        'MA100', 'RSI', 'MACD_histogram', 'BB_lower',
                        'BB_middle', 'BB_upper', 'STOCH_K', 'STOCH_D', 'Volume_Change',
                        'Change', 'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b',
                        ], dtype=np.dtype("U25"))

    int_cols = ['Volume']
    str_cols = ['Date', "Ticker"]

    tickers = GeneralMarketDataFetcher.tickers

    def change_default_historical_table_name(self, table_name: str):
        self._historical_tablename = table_name

    def create_table_historical(self) -> None:
        columns = [IntegerColumn(col) if col in self.int_cols else TextColumn(col) if
        col in self.str_cols else FloatColumn(col) for col in self.columns]

        stmt = SP500Database.create_table(self._historical_tablename, columns,
                                          pk=(IntegerColumn("tests", attribute="primary_key", nullable=True)))

        self._cursor.execute(stmt)
        self._connection.commit()
        self._tablenames.append(self._historical_tablename)

    def create_table_api_data(self):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self._api_data_tablename} (id INTEGER PRIMARY KEY, Datetime TEXT, Data STRING)")
        self.connection.commit()

    @cfunc
    def do_populate(self, dataframe: DataFrame):
        """
        Populates the tables containing historical data
        :param dataframe: Pandas dataframe with columns = args
        """
        dataframe.to_sql(self._historical_tablename, self._connection, if_exists="append")
        self._connection.commit()

    def query_ticker_data(self, ticker: str) -> Iterator[DataFrame] or DataFrame:
        return read_sql(f"SELECT * FROM {self._historical_tablename} WHERE ticker = '{ticker}'", self._connection)

    def initial_date(self):
        beginning_date = self._cursor.execute(
            f"""SELECT date from {self._historical_tablename}
                                                WHERE ticker = 'AAPL'"""
        ).fetchone()
        beginning_date = beginning_date['date']
        print(beginning_date)
        return beginning_date

    def clear_historical(self):
        self._cursor.execute(f"delete from {self._historical_tablename}")
        self._connection.commit()

    # def update_db(self):
    #     self._cursor.execute(
    #         f"""DELETE FROM {self._historical_tablename}
    #                             WHERE date = ?
    #                             """, (self.initial_date()))

    @property
    def historical_tablename(self):
        return self._historical_tablename

    def query_data_by_date(self, date: str) -> List[Row]:
        data = self._cursor.execute(f"""
                                      SELECT * from {self._historical_tablename}
                                      WHERE date = ?
                                      """, (date,)).fetchall()
        return data

    def query_by_id(self) -> List[Row]:
        return self._cursor.execute(f"SELECT * from {self._historical_tablename} where id < 10").fetchall()

    def stmt_query_by_date(self, date: str) -> str:
        return f"SELECT * FROM {self._historical_tablename} WHERE date = '{date}'"

    def query_from_date_to_dataframe(self, date: str) -> DataFrame:
        """Build a dataframe from sql query for data on a give date"""
        return read_sql(self.stmt_query_by_date(date), self._connection)

    def query_all_dates(self) -> List[str]:
        dates = self._cursor.execute(f"SELECT DISTINCT (date) FROM {self._historical_tablename}").fetchall()
        return [date['date'] for date in dates]

    def get_latest_date(self) -> str:
        date = self._cursor.execute(f"""
                                        SELECT DISTINCT (date) from {self._historical_tablename}
                                        ORDER BY date DESC LIMIT 1
                                    """).fetchone()
        return date['date']

    def get_date_before_latest_date(self) -> str:
        date = self._cursor.execute(f"""
                                        SELECT DISTINCT (date) from {self._historical_tablename}
                                        ORDER BY date DESC LIMIT 2
                                    """).fetchall()
        return date[-1]['date']

    def query_breadth_specifics(self) -> tuple:
        last_date = self.query_all_dates()[-1]
        changes = self.cursor.execute \
            (f"SELECT * FROM {self._historical_tablename} WHERE Date = ?", (last_date,)).fetchall()

        def parse_query(query, colname: str):
            return [(val['Ticker'], val[colname]) for val in query]

        return parse_query(changes, "Change"), parse_query(changes, "Volume_Change")

    def get_last_api_request(self):
        data = self.cursor.execute(f"SELECT * FROM {self._api_data_tablename} ORDER BY id DESC LIMIT 1").fetchone()
        return data

    def insert_api_data(self, datetime, data):
        data = json.dumps(data)
        print("Adding to Table")
        self.cursor.execute(f"INSERT INTO {self._api_data_tablename} (Datetime, Data) VALUES (?, ?)", (datetime, data))
        self.connection.commit()

    @cfunc
    def query_all_testing_data(self):
        data = self.cursor.execute("SELECT * FROM api_data_tester").fetchall()
        return data
