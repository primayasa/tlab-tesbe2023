import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(".env")

def get_engine():
    """Creating SQLite Engine to interact"""

    engine_uri = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_HOST"),
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_DB"),
    )

    return create_engine(engine_uri, future=True)

def run_query(query, commit: bool = False):
    """Runs a query against the given SQLite database.

    Args:
        commit: if True, commit any data-modification query (INSERT, UPDATE, DELETE)
    """
    engine = get_engine()
    if isinstance(query, str):
        query = text(query)

    with engine.connect() as conn:
        if commit:
            conn.execute(query)
            conn.commit()
        else:
            result = conn.execute(query)
            column_names = result.keys()
            result_list = [dict(zip(column_names, row)) for row in result]
            
            return result_list
            # print(result_list)
            # return 1
