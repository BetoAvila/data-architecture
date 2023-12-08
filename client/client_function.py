from getpass import getpass
import pandas as pd
from mysql import connector

usr = input('input the user:')
pwd = getpass('input password:')
url = './data/departments.csv'
df = pd.read_csv(url, names=['department_id', 'department_name'], header=None)

with connector.connect(user=usr,
                       password=pwd,
                       host='127.0.0.1',
                       database='employees') as cnx:

    df.to_sql(con=cnx, name='departments', if_exists='replace', flavor='mysql')
