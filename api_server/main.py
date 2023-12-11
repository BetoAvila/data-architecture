# from fastapi import FastAPI
# from functions import populate_tables_init
import pandas as pd
from sqlalchemy import create_engine


df = pd.read_csv('/tmp/data/departments.csv', header=None, names=['department_id', 'department_name'])
conn = create_engine(url='mysql+pymysql://root:root@db:3306/app_db')
df.to_sql(name='departments', con=conn, index=False)

# populate_tables_init()
# app = FastAPI()


# @app.get('/jobs/{job_id}')
# def get_job(job_id):

#     return json.dumps({"message": "Hello World"})

