# 1. Data Architecture use case
# 2. Introduction
This [project](https://github.com/BetoAvila/data-architecture) exemplifies an architecture proposal for a data engineering use case.
It mimics a fictional data migration process with certain instructions and requirements.
- [1. Data Architecture use case](#1-data-architecture-use-case)
- [2. Introduction](#2-introduction)
- [3. Project definition](#3-project-definition)
  - [3.1. Requirement 1](#31-requirement-1)
    - [3.1.1. Specifications](#311-specifications)
    - [3.1.2. Clarifications](#312-clarifications)
    - [3.1.3. Data structure](#313-data-structure)
  - [3.2. Requirement 2](#32-requirement-2)
    - [3.2.1. Specifications](#321-specifications)
- [4. Proposed solution](#4-proposed-solution)
  - [4.1. Solution description](#41-solution-description)
  - [4.2. Solution details](#42-solution-details)
    - [4.2.1. Project structure](#421-project-structure)
    - [4.2.2. The client service](#422-the-client-service)
      - [4.2.2.1. Client functions](#4221-client-functions)
    - [4.2.3. The API service](#423-the-api-service)
      - [4.2.3.1. REST API](#4231-rest-api)
      - [4.2.3.2. MySQL](#4232-mysql)
      - [4.2.3.3. Avro backups and restores](#4233-avro-backups-and-restores)
      - [4.2.3.4. Data exploration](#4234-data-exploration)
      - [4.2.3.5. Logs](#4235-logs)
    - [4.2.4. The DB service](#424-the-db-service)
    - [4.2.5. compose.yaml](#425-composeyaml)
  - [4.3. Usage](#43-usage)
    - [4.3.1. Build](#431-build)
    - [4.3.2. Access containers](#432-access-containers)
    - [4.3.3. Shut containers down](#433-shut-containers-down)
- [5. Discussion and conclussions](#5-discussion-and-conclussions)
- [6. Further work](#6-further-work)


# 3. Project definition
Assume you are a data engineer who designs an architecture for a data migration project. Consider the following:

## 3.1. Requirement 1
Migration process:

### 3.1.1. Specifications
1. Move historical data in CSV format to the new database.
2. Create a Rest API service to receive new data with the conditions:
   1. Each transaction for all tables must comply with data dictionary rules.
   2. Be able to batch ingest transactions from 1 up to 1000 rows with one request.
   3. Receive data for each table in the same service.
3. Create a feature to backup each table and save it in the file system in AVRO format.
4. Create a feature to restore any table with its backup.

### 3.1.2. Clarifications 
1. You decide the origin where the CSV files are located.
2. You decide the destination database type, but it must be a SQL database.
3. The CSV file is comma separated.
4. Consider "feature" as either "Rest API, Stored Procedure, Database functionality, Cron job, or any other way to accomplish the requirements".
5. Transactions that don't accomplish the rules must not be inserted but they must be logged.
6. All the fields are mandatory.

### 3.1.3. Data structure
The migration considers 3 tables: `jobs`, `departments` and `employees` and these are defined by the schemas below:

`employees`
| Column        | Data type | Description                          | Example                |
| ------------- | --------- | ------------------------------------ | ---------------------- |
| employee_id   | INTEGER   | Id of employee                       | `4535`                 |
| employee_name | STRING    | Name and surname of the employee     | `Marcelo Gonzalez`     |
| hiring_date   | STRING    | Hire datetime in ISO format          | `2021-07-27T16:02:08Z` |
| department_id | INTEGER   | Id of department employee belongs to | `1`                    |
| job_id        | INTEGER   | Id of job employee performs          | `2`                    |

`jobs`
| Column   | Data type | Description | Example         |
| -------- | --------- | ----------- | --------------- |
| job_id   | INTEGER   | Job ID      | `4`             |
| job_name | STRING    | Name of job | `Data engineer` |

`departments`
| Column          | Data type | Description        | Example        |
| --------------- | --------- | ------------------ | -------------- |
| department_id   | INTEGER   | Department ID      | `3`            |
| department_name | STRING    | Name of department | `Supply chain` |

## 3.2. Requirement 2
Data exploration and exploitation. Stakeholders as for specific metrics and KPIs:

### 3.2.1. Specifications
1. Create an endpoint on the API to provide the number of employees hired for each job and department in 2021 divided by quarter. The table must be ordered alphabetically by department and job. Consider the sample output:

| Department   | Job       | Q1  | Q2  | Q3  | Q4  |
| ------------ | --------- | --- | --- | --- | --- |
| Staff        | Manager   | 0   | 0   | 1   | 0   |
| Staff        | Recruiter | 3   | 2   | 1   | 4   |
| Supply chain | Manager   | 2   | 1   | 4   | 0   |

2. List departments, their IDs and people hired in 2021 of the departments that hired more people than the average hires by department. Order by hired employees in descending manner.

| ID  | Department   | hired |
| --- | ------------ | ----- |
| 7   | Staff        | 45    |
| 9   | Supply chain | 12    |
| 19  | HR           | 3     |

3. Create a visual report for each requirement.

# 4. Proposed solution
Below is a graphic representation of the designed architecture:
![alt text](./imgs/DA.png 'architecture')
**Heads up!** This is not the intial state of the system but its final state when all operations have been performed.

## 4.1. Solution description
This is a multi-container architecture implemented with [Docker]( https://www.docker.com/) technology coded in Python.

It has 3 containers each one performing a single service, despite their inherent isolation paradigm, they communicate with each other using 2 networks:
-	`front-net` designed to communicate the client and the API i.e., the frontend and,
-	`back-net` for the communication with the API and the DB.

This design prevents interactions to the DB from anywhere except the API, which is a good practice on the industry. Not even the client, which belongs to the same deployment, can connect directly to the DB.

The first container is the Client, this is the entry point of the app, it job is to query the API to trigger each action. It also logs all the interactions and events from its perspective and saves this information to the `client_{datetime}.log` files. It can’t communicate directly to the DB which is a desired feature.

The second container is called API, here is where the API server is defined and runs, it has access to both front and backend networks and it performs multiple operations:
-	Receive requests from the client and deliver the results.
-	Communicate with the DB.
-	Perform data transformations.
-	Log events (INFO, WARNINGS and ERRORS).
-	Create backups using `.avro` files.
-	Restore DB from backups.
-	Create reports in both tabular and graphic format (deliverables).

Lastly, the third container defines the MySQL DB service, this service interacts with the API and returns queried information through a connection engine (defined in the API service). Basically, it stores information and allows its access.

Please note that the Client and the API containers have a shared volume, this is a [Docker feature]( https://docs.docker.com/storage/volumes/#volumes) that allows to share data between containers, and from and to the host (the computer you use to run this app) even when the containers are shut down, and it does not increase the size of the container, regardless of the amount of data stored. Hence for this case, it’s perfect for logging, backing up, reporting and moving data.

Given that this is a multi-container application, I use [`docker compose`](https://docs.docker.com/get-started/08_using_compose/#use-docker-compose) feature with the [`compose.yaml`](./compose.yaml) file. We can consider this file as the minimum set of instructions needed to build and start all containers, their relating infrastructure, and their communications they use. And we can also see a container as the minimum computer instance with its own filesystem, kernel, memory, and storage, basically this is the simplest working computer possible.

## 4.2. Solution details
### 4.2.1. Project structure
This project is structured as follows:
```
/data-architecture
    /client
        client.py
        Dockerfile
        requirements.txt
        start.sh
    /api
        /data
            departments.csv
            jobs.csv
            employees.csv
        main.py
        functions.py
        Dockerfile
        requirements.txt
        start.sh
    /db
        Dockerfile
        init.sql
    compose.yaml
    up.sh
    README.md
```
Please note that other folders are included in this repo as it is easier to share the results and its functioning. The folder [`deliverables/`](./deliverables/) contains the results of the [Requirement 2](#32-requirement-2), [`new_records/`](./new_records/) folder groups the `.csv` files used to update the DB.

A file worth mentioning is the [`up.sh`](./up.sh) file which I used to test repeatedly this deployment as it contains useful commands to clean, build and start this app.

### 4.2.2. The client service
As mentioned above, this service oversees connecting to the API to manipulate the data migration process. It was designed to be a program running on a python shell by typing commands.

It is build with its [`Dockerfile`](./client/Dockerfile) which summarized instructions are:
-	Build container from [`python 3.11-slim`]( https://hub.docker.com/_/python/) image which is the minimum working python environment.
-	Set environment configurations.
-	Copy files into container and execute [`start.sh`](./client/start.sh) file, which delegates linux environment update and installation of python dependencies to an external file, this way allows to keep the `Dockerfile` clean and short which enhances maintainability.

The [`requirements.txt`]() file contains all the python libraries needed, first I list the packages names and then I list the exact versions that did successfully run on the container for future package version reference.

#### 4.2.2.1. Client functions
Finally, the client executes the functions defined with in file [`client.py`](./client/client.py), these are the following:
```
# Requirement 1 functions

add_new_records(table: str)
backup(table: str)
restore(table: str)
get_by_id(id: str, table: str)


# Requirement 2 functions

req1()
req2()
```
All these functions will connect to the corresponding API endpoint and will perform the actions defined. The base URL used by the client is `http://api:8000` since Docker automatically resolves the hostname, and regardless of the container restart or rebuild, this hostname will point to the correct machine always.

### 4.2.3. The API service
This is by far the most complex service defined in the project as it contains many functions. Similarly to the client service, Docker builds this container using its [`Dockerfile`](./api/Dockerfile), delegating environment setup to the [`start.sh`](./api/start.sh) file and installing dependencies defined in the [`requirements.txt`](./api/requirements.txt) file.

#### 4.2.3.1. REST API
To build the REST API, I implemented [FastAPI]( https://fastapi.tiangolo.com/) with an [Uvicorn]( https://www.uvicorn.org/) python ASGI web server in the [`main.py`](./api/main.py) file. It defines the endpoints of the API and performs the tasks defined in the requirements. The functions the server performs are defined in the [`functions.py`](./api/functions.py) file.

The API endpoints are:
| Endpoint               | Use                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------- |
| `/view/{table}/{id}`   | Get single row of data based on `id` and `table`                                    |
| `/view/req1`           | Perform requirement 1 of data exploration and save resulting files on shared volume |
| `/view/req2`           | Perform requirement 2 of data exploration and save resulting files on shared volume |
| `/new_records/{table}` | Add new records to `table`                                                          |
| `/backup/{table}`      | Generate `.avro` file to backup current state of table                              |
| `/restore/{table}`     | Restore table from `.avro` file                                                     |

These are the endpoints [`the client`](#422-the-client-service) accesses to and result in a confirmation message with the form:
```
{
    "response": "Response message"
}
```

#### 4.2.3.2. MySQL
The initial DB setup is performed once the API server starts, this means that before API server starts running, the initial DB population starts.

For this process, the files copied in the image build step, are placed at `/tmp/data` folder which is the shared volume, then the files are read using pandas and sent to the DB using [SQLAlchemy](https://www.sqlalchemy.org/) connection engine and [PyMySQL](https://pymysql.readthedocs.io/en/latest/user/installation.html) driver.

The connection engine is configured to have a connection pool to prevent idle connections from crashing the DB, hence when a new connection tries to start communication, the last one in the pool is removed.

To update the database, the endpoint `/new_records/{table}` must be queried. This will copy the `.csv` header-less files at `/home/data/` into the shared volume at `/tmp/data/` from the client service and thus giving access from the API side, then these are read by pandas and sent (by appending) to the DB. To do this, one most first copy the `.csv` files from the host into the client container, use [`docker cp`](https://docs.docker.com/engine/reference/commandline/cp/) to achieve this:

```
docker cp /local_path_to/csv_files.csv client:/home/data/
```

This also ensures that duplicate files are not created.

#### 4.2.3.3. Avro backups and restores
To create the backup files, I used [Avro](https://avro.apache.org/docs/1.11.1/specification/) files as these present several advantages in storing and streaming tasks.

Avro files have a `json` format schema which makes them self-describing, meaning the file itself is a documentation of the data stored in it, this is datatypes, column names and other information.

They are great for streaming purposes since these are serialized formats and thus also allow compression (snappy format by default).

This project uses [fastavro](https://fastavro.readthedocs.io/en/latest/) package to create, read and save `.avro` files.

The `/backup/{table}` endpoint described in the previous section reads the `{table}` current state and stores its contents into an `.avro` file, first checking if the same backup file exists to keep the most up to date backup in storage. The location of the file is the sahed volume in the subfolder `/tmp/data`.

The `/restore/{table}` endpoint described in the previous section reads the corresponding `/tmp/data/{table}.avro` file to overwrite MySQL `{table}` with such file. This opens the file, converts it into pandas df and opens a connection engine to overwrite the MySQL table with it.

The schemas used for the tables are:

```
### jobs schema
{
    'type': 'record',
    'name': 'jobs',
    'fields': [
        {'name': 'job_id', 'type': 'int'},
        {'name': 'job_name',  'type': 'string'}
    ]
}

### departments schema
{
    'type': 'record',
    'name': 'departments',
    'fields': [
        {'name': 'department_id', 'type': 'int'},
        {'name': 'department_name',  'type': 'string'}
    ]
}

### employees schema
{
    'type': 'record',
    'name': 'employees',
    'fields': [
        {'name': 'employee_id', 'type': 'int'},
        {'name': 'employee_name',  'type': 'string'},
        {'name': 'hiring_date',  'type': 'string'},
        {'name': 'department_id', 'type': 'int'},
        {'name': 'job_id', 'type': 'int'}
    ]
}
```
This ensures data consistency between pandas, MySQL and avro files.

#### 4.2.3.4. Data exploration
The data exploration task is performed by querying the API with either endpoints `/view/req1` or `/view/req2`, this will query the DB with a connection engine and transforming the resulting data using pandas. Then use [Plotly](https://plotly.com/) to create interactive reporting dashboards in `.html` format.

These dashboards allow actions like drag and drop, zoom, select, and highlight elements in the plot. Both files, interactive `.html` dashboards and reporting `.csv` files are placed at `/tmp/data/` location. Please refer to the [`deliverables/`](./deliverables/) folder to see a sample of these files.

#### 4.2.3.5. Logs
Logging was possible thanks to the built-in [logging](https://docs.python.org/3/library/logging.html) feature of python, resulting log files are placed on the shared volume of this app `app-vol` at the location `/tmp/logs/`. It creates 2 kind of logs for both the client and API which can be accessed and retrieved even after container shut down.

### 4.2.4. The DB service
The DB service is the simplest of them all, it is build with its [`Dockerfile`](./db/Dockerfile) in which we set the necessary environment variable `ENV MYSQL_ROOT_PASSWORD=root` and execute the [`init.sql`](./db/init.sql) file. This files creates a new database calles `app_db` and defines the 3 tables with its corresponting columns and datatypes.

### 4.2.5. compose.yaml
Once we have defined all the services the [`compose.yaml`](./compose.yaml) comes into action. As mentioned previously, it is an instruction set of how to build and name the individual services, attach a volume, create and connect to a network, establish dependencies among many other [possible configurations]( https://docs.docker.com/compose/).

It is defined by a `.yaml` text file which hierarchically defines items and its configurations in a key-value fashion.

For instance, the service `DB`, is named simply `db` by the first instruction, then the build property points to the `Dockerfile` that builds the image of this container. Then attaches the backend network `back-net` and exposes the ports `3306, 33060` which are the default ports of MySQL. This [`expose`]( https://docs.docker.com/engine/reference/builder/#expose) instruction does not publish the port to the host, but allows containers in the same network to communicate to this one using that port.

In the case of the `api` service, I define instructions to be executed with the terminal listening to commands I type, which allows me to interact with it. The compose file, also defines for this service both networks, and the shared volume. It also exposes the port `8000` which is used by the API and the Client to communicate with each other. Finally, the `depends_on` property, makes sure that only when the DB service is up and running this API server should start. This provides the possibility to control the start order.

At the bottom of the [`compose.yaml`](./compose.yaml) file, I defined the network and shared volumes, it is enough to Docker with the existance of these properties to start and interconnect them.


## 4.3. Usage
### 4.3.1. Build
To start this ecosystem, execute the command on the project parent folder:
```
docker compose build --no-cache
```
This will start the build of all the services by reading the `compose.yaml` and running the instructions to build images on the `Dockerfile` files.

Use the `--no-cache` flag to always build from scratch and never used cached layers, this prevents issues when building images.

To start the containers, use:
```
docker compose up -d
```
and this will run them in [`detach`]( https://docs.docker.com/engine/reference/run/#detached-vs-foreground) mode.

**The whole ecosystem is now running!**

### 4.3.2. Access containers
To start using the API start access the API container:
```
docker exec -it data-architecture-api-1 /bin/bash
```
then run the command to start the API server:
```
python main.py
```
open another terminal and run:
```
docker exec -it data-architecture-client-1 /bin/bash
```
open the python shell
```
python
```
and import and run any of the [`functions`](#4221-client-functions) defined in the client service, you will receive a response describing the result.

For example:
```
# Import all functions from client

from client import *


# Run functions

add_new_records('jobs')
>>> {
>>>     'response': '7 new records updated into jobs table'
>>> }
```

### 4.3.3. Shut containers down
Once you finished all transactions, run command to stop all containers safely:
```
docker compose down
```
If you want to remove volumes, networks containers and images use `docker prune` command, or refer to the [`up.sh`](./up.sh) file.

# 5. Discussion and conclussions
Containers solution was selected as it offers several advantages over traditional monolithic approaches:
-	This was implemented using python as it is widely popular and has a great support community base, as well as its ease of development, debugging and maintenance.
-	Every container lives isolated from others, enhancing safety and security of the system.
-	[Docker volumes]( https://docs.docker.com/storage/volumes/) offer a great solution for sharing files and data with multiple containers simultaneously, while also persisting data and keeping it secure without increasing the size of the container even after container are shut down.
-	Two networks were created to improve security of system, the DB and API services communicate with each other using `back-net` and the Client and API interact using `front-net`. This isolates even more the DB from external instances and it is only accessible through the API, which in turn is accessed by the client as no ports are published with the [`docker port`](https://docs.docker.com/engine/reference/commandline/port/) command.
-	Docker resolves IP addresses when referring a remote connection simply as `api` or `db`, so calling these hosts on the correct network enables communication. Refer to the MySQL connection engine and API connection string to see an example.
-	Everything is built with with [`docker compose`](https://docs.docker.com/compose/) command and file. Hence, this can be implemented in a wide variety of hosts, from cloud solutions to local environments, and it offers great flexibility of design and incredible development speed as most of configurations are simplified by the [`compose.yaml`](./compose.yaml) file and handled by Docker.
-	Further features could have been implemented on the API side, but the creation of more features would require instances like a load balancer, a gateway or such. Thus, this solution is simple yet functional and secure.
-	To build the API, [fastAPI]( https://fastapi.tiangolo.com/) was selected as it is remarkably easy to use and offers awesome configurations during development process.
-	[MySQL](https://www.mysql.com/) was selected as DB of choice as per the experience I have with it and the fact that it is, fast, simple to use, popular and can be easily integrated with other tools.
-	Logs are creating using the logging feature, this allows both debuging and informing about the state of the system and provide record files for further analysis.
-	The resulting deliverable files consists of 2 types of file, `.csv` and `.html` in regards to the [data exploration requirements](#32-requirement-2). The former contains the information in a tabular format easily readable, the latter contains graphic reports which are interactive plots showing the data from the `.csv` files thanks to the [Plotly](https://plotly.com/) library. Please refer to the [`deliverables/`](./deliverables/) folder.

# 6. Further work
During the development of this project I want to suggest a few points.

- [`Secrets`](https://docs.docker.com/compose/use-secrets/#how-to-use-secrets-in-docker-compose). Docker provides this feature to safely manage sensitive information like API keys or passwords. This would be a great improvement to the system.
- Authetication. Another great way to improve security and control access to the API would be authentication.
- Load balancind, reverse proxy or API Gateway. Systems like [nginx](https://www.nginx.com/) can help this and will improve ths architecture.
- [k8s](https://kubernetes.io/). Kubernetes is the natural progression of a system this type and would automate features like failsafes, rebuilds or container restarts.
- Cloud. Another great improvement of this project would be the implementation on cloud. This would decrease the amount of work as there are many cloud tools to migrate databases, build infrastructure and manage containers.