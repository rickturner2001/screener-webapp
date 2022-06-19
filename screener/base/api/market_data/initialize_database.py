from screener.base.api.market_data.classes.databases import SP500Database
from screener.base.api.market_data.config import db_path
from screener.base.api.market_data.database_functions import populate_sp500


def main():
    database = SP500Database()
    database.connect_existing_database(db_path=db_path / "sp500.sqlite")

    # Creating the tables
    database.create_table_historical()
    database.create_table_api_data()

    # Populate tables
    populate_sp500(database, update=False)


if __name__ == "__main__":
    main()
