import os

from dotenv import load_dotenv
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, Engine, text

load_dotenv()


class SnowflakeUtil:

    @staticmethod
    def get_snowflake_engine() -> Engine:
        return create_engine(
            URL(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                role=os.getenv("SNOWFLAKE_ROLE"),
            )
        )


def main():
    engine = SnowflakeUtil.get_snowflake_engine()
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT GETDATE()"))
            for row in result:
                print(row)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
