from pyclbr import Function
from fastavro import writer, reader, parse_schema
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from sqlalchemy import create_engine


# Logging
logging.basicConfig(
    level=logging.INFO,
    filename=f'/tmp/logs/server_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
    format='%(levelname)s | %(message)s')

# MySQL connection
usr = 'root'
psw = 'root'
db_port = '3306'
db_name = 'app_db'
db_host = 'db'
url = f'mysql+pymysql://{usr}:{psw}@{db_host}:{db_port}/{db_name}'

# Schemas
jb_sc_av = {
    'type': 'record',
    'name': 'jobs',
    'fields': [
        {'name': 'job_id', 'type': 'int'},
        {'name': 'job_name',  'type': 'string'}]}
dp_sc_av = {
    'type': 'record',
    'name': 'departments',
    'fields': [
        {'name': 'department_id', 'type': 'int'},
        {'name': 'department_name',  'type': 'string'}]}
em_sc_av = {
    'type': 'record',
    'name': 'employees',
    'fields': [
        {'name': 'employee_id', 'type': 'int'},
        {'name': 'employee_name',  'type': 'string'},
        {'name': 'hiring_date',  'type': 'string'},
        {'name': 'department_id', 'type': 'int'},
        {'name': 'job_id', 'type': 'int'}]}
jb_sc_pd = ['job_id','job_name']
dp_sc_pd = ['department_id', 'department_name']
em_sc_pd = ['employee_id', 'employee_name',
            'hiring_date', 'department_id', 'job_id']
schemas = {
    'jobs': (jb_sc_pd, jb_sc_av),
    'departments': (dp_sc_pd, dp_sc_av),
    'employees': (em_sc_pd, em_sc_av)}

# Logging functions
def li(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.info(msg)


def lw(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.warning(msg)


def le(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.error(msg)

# Functions
def populate_tables_init():
    """
    Function to populate MySQL tables as soon as the server starts.
    Function reads from `/tmp/data/{table}.json` file to populate 
    corresponding table.
    Once reading is finished it saves the data onto MySQL and creates
    an Avro backup file while logging all these steps to `/tmp/logs/server.log` files.
    """    
    for table in schemas:
        # Reading data
        df = read_csv(table)
        initial_rows = df.shape[0]
        df = df.dropna()
        if initial_rows - df.shape[0] > 0:
            lw(f'Dropped {initial_rows - df.shape[0]} rows from {table} file as they contain null values')
        if table == 'employees':
            df.hiring_date = pd.to_datetime(df.hiring_date, format='%Y-%m-%dT%H:%M:%SZ')
        # Initial data save into DB
        write_mysql(df, table, 'replace')
        li(f'Successful initial data load of {df.shape[0]} rows into {table} table on MySQL')


def backup_mysql_to_avro(table: str) -> dict:
    """
    Function to backup current state of MySQL `table` into an Avro file
    at `/tmp/data/{table}.avro` location.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `dict`: Response of query
    """
    try:
        df = read_mysql(table)
        if df.shape[0] > 0:
            if table == 'employees': df.hiring_date = df.hiring_date.dt.strftime('%Y-%m-%d %H:%M:%S')
            data = df.to_dict(orient='records')
            sc = parse_schema(schemas[table][1])
            with open(f'/tmp/data/{table}.avro', 'wb') as out:
                writer(out, sc, data)
            li(f'Saved Avro backup file of {table} table at /tmp/data, {df.shape[0]} records saved')
        else: lw(f'{table} table contains no records, Avro file backup not created')
        return {'response': f'Successfully backed {df.shape[0]} rows from {table} table to Avro file'}
    except Exception as e:
        le(f'Error when backing data up from table {table}: {e}')
        return {'response': f'Incorrect table name: {table}'}


def restore_mysql_from_avro(table: str):
    """Function to restore previous MySQL `table` state from an Avro file.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
    """
    with open(f'/tmp/data/{table}.avro', 'rb') as fo:
        avro_reader = reader(fo)
        data = [record for record in avro_reader]
    df = pd.DataFrame(data)
    if table == 'employees':
        df.hiring_date = pd.to_datetime(df.hiring_date, format='%Y-%m-%d %H:%M:%S')
    write_mysql(df, table, 'replace')
    li(f'Restored {df.shape[0]} rows into {table} table on MySQL from Avro file')


def update_mysql(table: str) -> dict:   
    """Function to modify `table` by appending new rows.
    It backups data when called so every backup is updated at any table change.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `dict`: Response of query
    """
    try:
        df = read_csv('new_records_' + table)
        write_mysql(df, table, 'append')
        li(f'Appended {df.shape[0]} new rows into {table} table on MySQL')
        return {'response':f'{df.shape[0]} new records updated into {table} table'}
    except Exception as e:
        le(f'Error reading update info from csv file: {e}')
        return {'response': 'Unexpected data format, please check format is correct'}


def write_mysql(df: pd.DataFrame, table: str, mode: str):
    """Function to modify (by appending or replacing) a `table`. It takes
    an existing `dataframe` and a `mode` to work.

    Args:
        - `df` (pd.DataFrame): Df containing data to save on MySQL.
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
        - `mode` (str): Write mode either `'fail', 'replace', 'append'`.
    """
    if df.shape[0] > 0:
        if table == 'employees': df.hiring_date = df.hiring_date.dt.strftime('%Y-%m-%d %H:%M:%S')
        conn = create_engine(url=url, pool_size=5)
        df.to_sql(name=table, con=conn, index=False, if_exists=mode)
        conn.dispose()
        li(f'{table} table with {df.shape[0]} entries successfully saved into MySQL')
    else: lw(f'{table} table contains no records, not saving to MySQL')


def read_mysql(table: str) -> pd.DataFrame:
    """Function to read a `table` in MySQL and save it as a DF.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `pd.DataFrame`: Df containing the information from the table.
    """
    conn = create_engine(url=url, pool_size=5)
    df = pd.read_sql(sql=f'SELECT * FROM {table};',
                         con=conn,
                         index_col=None)
    conn.dispose()
    if table == 'employees':
        df.hiring_date = pd.to_datetime(df.hiring_date, format='%Y-%m-%d %H:%M:%S')
    li(f'Successful data read from {table} MySQL table, {df.shape[0]} entries found')
    return df


def read_csv(table: str) -> pd.DataFrame:
    """Function to read `.csv` files locally from `/tmp/data/` directory.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `pd.DataFrame`: Df containing the information from the `.csv` file.
    """
    df = pd.read_csv(f'/tmp/data/{table}.csv',
                     names=schemas[table][0],
                     header=None)
    li(f'Successful reading of {table} csv file, {df.shape[0]} entries found')
    return df


def get_by_id(id: str, table: str) -> dict:
    """Get single record from MySQL `table` by `id`.

    Args:
        - `id` (str): Index of the requested entry.
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `dict`: Response of query
    """
    try:
        df = read_mysql(table)
        df = df[df[table[:-1] + '_id'] == int(id)]
        return df.to_dict(orient='records')
    except Exception as e:
        le(f'Error while querying {table} MySQL table: {e}')
        return {'response': f'no records with id {id} on table {table}'}

