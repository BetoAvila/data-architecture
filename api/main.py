import uvicorn
from fastapi import FastAPI
from functions import populate_tables_init, get_by_id, update_mysql, get_req1
from functions import backup_mysql_to_avro, restore_mysql_from_avro, get_req2


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

@app.get('/view/{table}/{id}')
def _get_by_id(id, table):
    return get_by_id(id, table)

@app.get('/view/req1')
def _get_req1():
    return get_req1()

@app.get('/view/req2')
def _get_req2():
    return get_req2()

@app.get('/new_records/{table}')
def _update_mysql(table):
    return update_mysql(table)

@app.get('/backup/{table}')
def _backup_mysql_to_avro(table):
    return backup_mysql_to_avro(table)

@app.get('/restore/{table}')
def _restore_mysql_from_avro(table):
    return restore_mysql_from_avro(table)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

