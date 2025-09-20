"""
Utility class for connecting to Snowflake and executing queries.
"""
import os

from dotenv import load_dotenv
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, Engine, text

load_dotenv()


class SnowflakeUtil:
    """
    Utility class for connecting to Snowflake and executing queries.
    """

    @staticmethod
    def get_snowflake_engine() -> Engine:
        """
        Get an SQL Alchemy engine connected to Snowflake.
        :return:
        """
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

    def execute_query(query: str):
        """
        Execute a SQL query against Snowflake and return the results.
        :return:
        """

        resultValue = {
            "success": False,
            "error": "Only SELECT queries are allowed",
            "data": []
        }
        # Security: Only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return resultValue

        engine = SnowflakeUtil.get_snowflake_engine()
        try:
            with engine.connect() as connection:
                result = connection.execute(text(query))
                data = result.fetchall()
                resultValue["success"] = True
                resultValue["error"] = ""
                resultValue["data"] = [dict(row._mapping) for row in data]
        except Exception as e:
            resultValue["error"] = str(e)
        finally:
            engine.dispose()

        return resultValue


def main():
    result = SnowflakeUtil.execute_query("SELECT GETDATE()")
    print(result)


if __name__ == "__main__":
    main()
