import pyspark
from pyspark.sql.types import StringType, IntegerType, TimestampType
from pyspark.sql.types import StructType, StructField
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from datetime import datetime
import logging


# Logging
logging.basicConfig(
    level=logging.INFO,
    filename=f'/tmp/logs/server_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
    format='%(levelname)s | %(message)s')

# Spark
spark = SparkSession.builder.appName('app').master('local').getOrCreate()
usr = 'root'
psw = 'root'
db_port = '3306'
db_name = 'app_db'
db_host = 'db'

# Schemas
jb_schema = StructType([
    StructField('job_id', IntegerType(), False),
    StructField('job_name', StringType(), False)])
dp_schema = StructType([
    StructField('department_id', IntegerType(), False),
    StructField('department_name', StringType(), False)])
em_schema = StructType([
    StructField('employee_id', IntegerType(), False),
    StructField('employee_name', StringType(), False),
    StructField('hiring_date', TimestampType(), False),
    StructField('department_id', IntegerType(), False),
    StructField('job_id', IntegerType(), False)])

schemas = {
    'jobs':jb_schema,
    'departments': dp_schema,
    'employees':em_schema}


# Functions
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
        initial_rows = df.count()
        df.show() ###########################################################
        df = df.dropna()
        if initial_rows - df.count() > 0:
            li(f'Dropped {initial_rows - df.count()} rows from {table} table as they contain null values')
        # Initial data save into DB
        write_sql(df, table, 'overwrite')
        li(f'Saved {df.count()} rows into {table} table on MySQL')
        backup_mysql_to_avro(table)


def backup_mysql_to_avro(table: str) -> None:
    """
    Function to backup current state of MySQL `table` into an Avro file
    at `/tmp/data/{table}.avro` location.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
    """    
    df = read_sql(table)
    if df.count() > 0:
        df.write.format('avro').save(f'/tmp/data/{table}.avro')
        li(f'Saved Avro backup of {table} table /tmp/data')
    else: lw(f'{table} table contains no records, Avro backup not created')


def restore_mysql_from_avro(table: str):
    """Function to restore previous MySQL `table` state from an Avro file.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
    """    
    df = spark.read.format('avro').load(f'/tmp/data/{table}.avro').schema(schemas[table])
    write_sql(df, table, 'overwrite')
    li(f'Saved {df.count()} rows into {table} table on MySQL')
    backup_mysql_to_avro(table)


def update_mysql(table: str):
    """Function to modify `table` by appending new rows.
    It backsup data when called so every backup is updated at any table change.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
    """    
    df = read_csv(table)
    write_sql(df, table, 'append')
    li(f'Saved {df.count()} rows into {table} table on MySQL')
    backup_mysql_to_avro(table)


def write_sql(df: pyspark.sql.DataFrame, table: str, mode: str):
    """Function to modify (by appending or overwriting) a `table`. It takes
    an existing `dataframe` and a `mode` to work.

    Args:
        - `df` (pyspark.sql.DataFrame): Df containing data to save on MySQL.
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.
        - `mode` (str): Write mode either `'append' or 'overwrite'`.
    """
    if df.count() > 0:
        df.write\
            .format('jdbc')\
            .mode(mode)\
            .options(
                driver='com.mysql.cj.jdbc.Driver',
                url=f'jdbc:mysql://{db_host}:{db_port}/{db_name}',
                dbtable=table,
                user=usr,
                password=psw)\
            .save()
    else: lw(f'{table} table contains no records, not saving to MySQL')


def read_sql(table: str) -> pyspark.sql.DataFrame:
    """Function to read a `table` in MySQL and save it as a DF.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `pyspark.sql.DataFrame`: Df containing the information from the table.
    """    
    return spark.read.format('jdbc')\
        .options(
            driver='com.mysql.cj.jdbc.Driver',
            url=f'jdbc:mysql://{db_host}:{db_port}/{db_name}',
            dbtable=table,
            user=usr,
            password=psw)\
        .load()


def read_csv(table: str) -> pyspark.sql.DataFrame:
    """Function to read `.csv` files locally from `/tmp/data/` directory.

    Args:
        - `table` (str): Table name to backup, either `'jobs', 'departments' or 'employees'`.

    Returns:
        - `pyspark.sql.DataFrame`: Df containing the information from the `.csv` file.
    """    
    return spark.read\
        .format('csv')\
        .option('header',False)\
        .schema(schemas[table])\
        .load(f'./data/{table}.csv')

def get_by_id(id: str, table: str):
    df = read_sql(table)
    df = df.filter(col(table[:-1] + '_id') == int(id))
    d = dict()
    for col in df.columns:
        d[col] = df.first()[col]
    return d

