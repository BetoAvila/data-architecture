from datetime import datetime
import requests
import logging
import shutil
import os


# Logging
url = 'http://api:8000'
logging.basicConfig(
    level=logging.INFO,
    filename=f'/tmp/logs/client_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
    format='%(levelname)s | %(message)s')

# Logging functions
def li(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.info(msg)


def lw(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.warning(msg)


def le(msg: str) -> None:
    msg = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} | {msg}'
    print(msg)
    logging.error(msg)


def add_new_records(table: str) -> None:
    if os.path.exists(f'/tmp/data/{table}.csv'): os.remove(f'/tmp/data/{table}.csv')
    shutil.copy2(f'/home/data/{table}.csv', f'/tmp/data/{table}.csv')
    print(requests.get(url + f'/new_records/{table}').text)
    li('finished "add_new_records" function')


def backup(table: str) -> None:
    print(requests.get(url + f'/backup/{table}').text)
    li('finished "backup" function')


def restore(table: str) -> None:
    print(requests.get(url + f'/restore/{table}').text)
    li('finished "restore" function')


def get_by_id(id: str, table: str) -> None:
    print(requests.get(url + f'/view/{table}/{id}').text)
    li('finished "get_by_id" function')


def req1():
    print(requests.get(url + '/view/req1').text)
    li('finished "req1" function')


def req2():
    print(requests.get(url + '/view/req2').text)
    li('finished "req2" function')