#database.py
import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd

# Database configuration with environment-specific defaults
def get_database_url():
    """Get database URL based on environment"""
    # Check if we're in Docker container
    if os.path.exists('/.dockerenv'):
        # In Docker container - use host.docker.internal to reach host
        return os.getenv("DATABASE_URL", "postgresql://postgres:password@host.docker.internal:5432/fastapi_db")
    else:
        # Local development - use localhost
        return os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fastapi_db")

DATABASE_URL = get_database_url()
TABLE_NAME = "uploaded_data"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_connection():
    """Get database session"""
    return SessionLocal()

def initialize_db():
    """Initialize the database and drop/recreate the table if needed"""
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS uploaded_data"))

        print("Database connection successful")

    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def create_table_from_df(df):
    """Create table based on DataFrame structure using SQLAlchemy only"""
    metadata = MetaData()
    columns = [Column('id', Integer, primary_key=True, autoincrement=True)]

    for col_name in df.columns:
        columns.append(Column(col_name, String))

    table = Table(TABLE_NAME, metadata, *columns)

    # Drop and recreate table
    metadata.drop_all(bind=engine, tables=[table])
    metadata.create_all(bind=engine, tables=[table])
    
    print(f"Created table {TABLE_NAME} with columns: id, {', '.join(df.columns)}")

def insert_csv_data(df):
    """Insert CSV data into PostgreSQL table"""
    try:
        # Ensure table exists and has 'id' primary key
        create_table_from_df(df)

        # Insert data using SQLAlchemy directly to ensure id column is handled properly
        metadata = MetaData()
        table = Table(TABLE_NAME, metadata, autoload_with=engine)
        
        # Convert DataFrame to list of dictionaries (excluding id since it's auto-increment)
        records_to_insert = df.to_dict('records')
        
        with engine.begin() as conn:
            conn.execute(table.insert(), records_to_insert)
        
        print(f"Inserted {len(df)} records into {TABLE_NAME}")
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise

def fetch_records(column=None, value=None):
    """Fetch records from the database with optional filtering"""
    try:
        # Check if table exists first
        inspector = inspect(engine)
        if not inspector.has_table(TABLE_NAME):
            print(f"Table {TABLE_NAME} does not exist yet")
            return []
        
        with engine.connect() as conn:
            if column and value:
                query = text(f"SELECT * FROM {TABLE_NAME} WHERE {column} = :value")
                result = conn.execute(query, {'value': value})
            else:
                query = text(f"SELECT * FROM {TABLE_NAME}")
                result = conn.execute(query)
            
            # Convert result to list of dictionaries
            columns = result.keys()
            records = []
            for row in result:
                records.append(dict(zip(columns, row)))
            
            return records
    except Exception as e:
        print(f"Error fetching records: {e}")
        return []

def update_record(record_id, updates):
    """Update a specific record"""
    try:
        # Check if table exists first
        inspector = inspect(engine)
        if not inspector.has_table(TABLE_NAME):
            print(f"Table {TABLE_NAME} does not exist yet")
            return False
        
        set_clause = ", ".join([f"{key} = :{key}" for key in updates.keys()])
        query = text(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = :id")
        
        with engine.begin() as conn:
            result = conn.execute(query, {**updates, 'id': record_id})
            return result.rowcount > 0
    except Exception as e:
        print(f"Error updating record: {e}")
        return False

def delete_record(record_id):
    """Delete a specific record"""
    try:
        # Check if table exists first
        inspector = inspect(engine)
        if not inspector.has_table(TABLE_NAME):
            print(f"Table {TABLE_NAME} does not exist yet")
            return False
        
        query = text(f"DELETE FROM {TABLE_NAME} WHERE id = :id")
        
        with engine.begin() as conn:
            result = conn.execute(query, {'id': record_id})
            return result.rowcount > 0
    except Exception as e:
        print(f"Error deleting record: {e}")
        return False

def get_record_by_id(record_id):
    """Get a specific record by ID"""
    try:
        # Check if table exists first
        inspector = inspect(engine)
        if not inspector.has_table(TABLE_NAME):
            print(f"Table {TABLE_NAME} does not exist yet")
            return None
        
        with engine.connect() as conn:
            query = text(f"SELECT * FROM {TABLE_NAME} WHERE id = :id")
            result = conn.execute(query, {'id': record_id})
            
            # Get the first row
            row = result.fetchone()
            if row is None:
                return None
            
            # Convert to dict
            columns = result.keys()
            return dict(zip(columns, row))
            
    except Exception as e:
        print(f"Error fetching record: {e}")
        return None