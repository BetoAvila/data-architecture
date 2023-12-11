import uvicorn
from fastapi import FastAPI
from sqlalchemy import table
from functions import populate_tables_init, get_by_id, update_mysql, backup_mysql_to_avro


populate_tables_init()

app = FastAPI()

@app.get('/')
def home():
    return {'Endpoints':[
        '/{table}/{id} - GET method to obtain single record from table'
        '/new_records/{table} - POST method to append new entries into table, from 1 up to 1000 rows',
        '/backup/{table} - GET method to create Avro file backup from current table state',
        '/restore/{table}- Restore table from backup Avro file'
    ]}

@app.get('/{table}/{id}')
def _get_by_id(id, table):
    return get_by_id(id, table)

@app.post('/new_records/{table}')
def _update_mysql(table):
    return update_mysql(table)

@app.get('/backup/{table}')
def _backup_mysql_to_avro(table):
    return backup_mysql_to_avro(table)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

