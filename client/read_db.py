from getpass import getpass
import pandas as pd
from sqalchemy import create_engine

usr = input('input the user:')
pwd = getpass('input password:')
url = ''

with create_engine(f'mysql+mysqlconnector://{usr}:{pwd}@localhost:3306/db') as engine:
    df = pd.read_csv()