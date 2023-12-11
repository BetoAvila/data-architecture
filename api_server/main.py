from fastapi import FastAPI
from functions import populate_tables_init

populate_tables_init()
# app = FastAPI()


# @app.get('/jobs/{job_id}')
# def get_job(job_id):

#     return json.dumps({"message": "Hello World"})

