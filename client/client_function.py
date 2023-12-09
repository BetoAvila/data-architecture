from getpass import getpass
import pandas as pd
from mysql import connector
from sqlalchemy import create_engine

usr = 'root'
pwd = 'root'
url = './data/departments.csv'
df = pd.read_csv(url, names=['department_id', 'department_name'], header=None)

with connector.connect(user=usr,
                       password=pwd,
                       host='db',
                       database='default_db') as cnx:

    df.to_sql(con=cnx, name='departments', if_exists='replace')
