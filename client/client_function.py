from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, IntegerType
from pyspark.sql.types import StructType, StructField

spark = SparkSession.builder.appName('app').master('local').getOrCreate()
usr = 'root'
pwd = 'root'
path = './data/departments.csv'
schema = StructType([
    StructField('department_id', IntegerType(), False),
    StructField('department_name', StringType(), False)
])
df = spark.read.format('csv').option('header', False).schema(schema).load(path)

df.write\
    .format('jdbc')\
    .option('driver', 'com.mysql.cj.jdbc.Driver')\
    .option('url','jdbc:mysql://db:3306/default_db')\
    .option('dbtable', 'departments')\
    .option('user', 'root')\
    .option('password', 'root')\
    .save()

# https://stackoverflow.com/questions/49011012/cant-connect-to-mysql-database-from-pyspark-getting-jdbc-error