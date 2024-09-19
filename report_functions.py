import pandas as pd
from sqlalchemy import create_engine

def get_database_connection(password, database_name="civitatis_airbnb"):
    """
    Create a database connection using SQLAlchemy.
    """
    connection_string = f'mysql+pymysql://root:{password}@localhost/{database_name}'
    engine = create_engine(connection_string)
    return engine

def execute_query(engine, query):
    """
    Execute a SQL query and return the result as a DataFrame.
    """
    return pd.read_sql(query, con=engine)
