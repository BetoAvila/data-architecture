from datetime import datetime
import pandas as pd
import requests


tables = ['jobs', 'departments', 'employees']
for table in tables:
    if table == 'jobs': cols = ['job_id', 'job_name']
    elif table == 'departments': cols = ['department_id', 'department_name']
    elif table == 'employees': cols = ['employee_id', 'employee_name', 'hiring_date', 'department_id', 'job_id']
    df = pd.read_csv(f'./data/{table}.csv', names=cols, header=None)
    initial_rows = df.shape[0]
    df = df.dropna()
    if initial_rows - df.shape[0] > 0:
        print(f'Dropped {initial_rows - df.shape[0]} rows from {table} table as they contain null values')
    df.to_json(f'/tmp/data/{table}.json', index=False)

