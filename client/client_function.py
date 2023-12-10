from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, IntegerType, TimestampType
from pyspark.sql.types import StructType, StructField

# Configs
spark = SparkSession.builder.appName('app').master('local').getOrCreate()
usr = 'root'
psw = 'root'
db_port = '3306'
db_name = 'app_db'
db_host = 'db'
tables = ['jobs', 'departments', 'employees']

# Schema definitions
jb_schema = StructType([
    StructField('job_id', IntegerType(), False),
    StructField('job_name', StringType(), False)
])
dp_schema = StructType([
    StructField('department_id', IntegerType(), False),
    StructField('department_name', StringType(), False)
])
em_schema = StructType([
    StructField('employee_id', IntegerType(), False),
    StructField('employee_name', StringType(), False),
    StructField('hiring_date', TimestampType(), False),
    StructField('department_id', IntegerType(), False),
    StructField('job_id', IntegerType(), False)
])
schemas = [jb_schema, dp_schema, em_schema]

for table, schema in zip(tables, schemas):
    # Reading data
    df = spark.read.format('csv').option('header',False).schema(schema).load(f'./data/{table}.csv')

    # Initial data save into DB
    df.write\
        .format('jdbc')\
        .mode('overwrite')\
        .options(
            driver='com.mysql.cj.jdbc.Driver',
            url=f'jdbc:mysql://{db_host}:{db_port}/{db_name}',
            dbtable=table,
            user=usr,
            password=psw)\
        .save()

# https://stackoverflow.com/questions/49011012/cant-connect-to-mysql-database-from-pyspark-getting-jdbc-error
