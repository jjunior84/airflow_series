# Airflow Series - Setting Up for GCP Projects

This repository sub-folder has the objective of providing the files necessary and training to set up a Docker with Airflow containing the configuration necessary to work with GCP Projects.

This training is assuming that you have basics Docker and Docker Composer knowledge.

The training aims to teach you how to UP docker containers (using CeleryExecutor) and setting up the Airflow to work with GCP projects.

We are using an existent [docker image](https://hub.docker.com/r/buzz84/docker-airflow) (see [git project](https://github.com/jjunior84/docker-airflow)) built by myself containing [Airflow 1.10.10](https://airflow.apache.org/docs/1.10.10/) with [Python 3.7](https://docs.python.org/3.7/) and setting up to be possible to use RBAC interface.

Have Fun! :smiley:

## Information and Prerequisites

- Basic knowledge in bash commands
- Basic knowledge in python
- Installed [Docker](https://www.docker.com)
- Installed [Docker Compose](https://docs.docker.com/compose/install/)


## Project structure

The training was design to explain the process of having the environment by project, assuming that all dag that you must want to design is related to the same project, it is easy to organize that way.

Let´s look for **01_setting_up** project:

![Project Structure](./docs/project_structure.png)

## Detailing Files

### docker-composer.yml

The heart of our training, the composer file presents below is responsible by create our containers (all the four + dependency container)

<details><summary>docker-composer.yml</summary>
<span style="font-size:0.7em;">

```yml
version: '2.3'
services:
    redis:
        image: 'redis:5.0-buster'
        ports:
            - "6379:6379"

    postgres:
        image: 'postgres:9.6'
        ports:
            - "5432:5432"
        environment:
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow

    flower:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - redis
        environment:
            - EXECUTOR=Celery
        ports:
            - "5555:5555"
        command: flower            
                
    webserver:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - postgres
            - redis
        environment:
            - AIRFLOW__WEBSERVER__RBAC=true
            - LOAD_EX=n
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow          
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
services:
    redis:
        image: 'redis:5.0-buster'
        ports:
            - "6379:6379"

    postgres:
        image: 'postgres:9.6'
        ports:
            - "5432:5432"
        environment:
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow

    flower:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - redis
        environment:
            - EXECUTOR=Celery
        ports:
            - "5555:5555"
        command: flower            
                
    webserver:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - postgres
            - redis
        environment:
            - AIRFLOW__WEBSERVER__RBAC=true
            - LOAD_EX=n
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow          
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
            - ./config_files:/opt/airflow/configs
            - ./scripts:/opt/airflow/scripts
            - ./requirements.txt:/requirements.txt
        ports:
            - "8080:8080"
        command: webserver
        healthcheck:
            test: ["CMD-SHELL", "[ -f /opt/airflow/airflow-webserver.pid ]"]
            interval: 30s
            timeout: 30s
            retries: 3

    scheduler:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - webserver
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
        environment:
            - LOAD_EX=n
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
        command: scheduler

    worker:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - scheduler
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
        environment:
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
        command: worker
```
</span>
</details>

I will not get deep in all points of the file, but small overview and detail the most relevant parts

#### Database services
This part is responsible to up two database services:
 - Redis would be database in memory to support message broker services (using standard port).
 - Postgres would be the database responsible to store Airflow metadata information, we are already setting the database name, user and password (using standard port).

<span style="font-size:0.7em;">

```yml
    redis:
        image: 'redis:5.0-buster'
        ports:
            - "6379:6379"

    postgres:
        image: 'postgres:9.6'
        ports:
            - "5432:5432"
        environment:
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow 
```
</span>

#### Celery monitoring
Once we are opting by use CeleryExecutor to run our Airflow tasks, We are using Flower as the tool for monitoring and administrating Celery cluster.
Observe that this service has dependency of the redis service to start (that makes perfectly sense since without the database it is not possible have the workers working well)

<span style="font-size:0.7em;">

```yml
    flower:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - redis
        environment:
            - EXECUTOR=Celery
        ports:
            - "5555:5555"
        command: flower 
```
</span>

#### Airflow containers
For the correct working of our Airflow environment based on CeleryExecutor, we separate in three distinct services, where I intent to detail well;

<span style="font-size:0.7em;">

```yml
    webserver:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - postgres
        environment:
            - AIRFLOW__WEBSERVER__RBAC=true
            - LOAD_EX=n
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow          
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
            - ./config_files:/opt/airflow/configs
            - ./scripts:/opt/airflow/scripts
            - ./requirements.txt:/requirements.txt
        ports:
            - "8080:8080"
        command: webserver
        healthcheck:
            test: ["CMD-SHELL", "[ -f /opt/airflow/airflow-webserver.pid ]"]
            interval: 30s
            timeout: 30s
            retries: 3
```
</span>

- webserver: 
    - depends on: it means that the service has dependency of postgres service to go start, as mentioned before, postgres will be our metadata repository.
    - environment variables: Determine variables that will be used to when up the service and it is setting up options that really interfere in correct working of the services
        - AIRFLOW__WEBSERVER__RBAC=true, setting that we want to used RBAC interface, since Airflow 1.10 was add the option to have a UI with more options, access control based in roles, modern, we are going to use it once that the Airflow next version (2.0) will be the only option available (=false would disable the RBAC interface)
        - LOAD_EX=n, setting Airflow without load sample dags, Airflow have some sample DAGs to support new adventurer(=y would show the sample dags)
        - FERNET_KEY, it is mainly used to encrypt connections in Airflow (it could be generate new fernet keys to be used)
        - EXECUTOR=Celery, it determines that we want to use Celery executors in our Airflow environment
        - POSTGRES_*, variables that determine user, password, database, host and port from postgres database service that Airflow will use as metadata base (it should fit with the postgres service configured previously).
        -AIRFLOW__CORE__SQL_ALCHEMY_CONN: parameter used to set sel alchemy connection string,  it coud be observed that it is the same information of the postgres parameters.
    - volumes: we use to map some folder or file from our local disk to a volume mounted into our docker container, it is really useful to have any change in your local environment instantlly reflected in your docker, we map for now:
        - dags folder to the dags folder inside of airflow directory, it will permit you develop in you local environment and see your dag reflecting the changes
        - resources folders to the resources folder inside of airflow directory, it is a good practice have a resource folder where you could use to keep the support files to your dags working well (as sql files, schemas, others ...)
        - config_files folder to the configs folder inside of airflow directory, it will be explained i details further but it will contain files to support of setting up the Airflow environment with the necessary information to work in your projects
        - scripts folder to the scripts folder inside of airflow directory, it will mounted the directory with the programs that will support the Airflow environment setup
        - requirements.txt file to requirements.txt file inside of the root folde of your docker, the entry point of our container if detect this file will install the python dependencies inside of the file, very useful to set new packages that you want in your docker
    - ports: indicates the port that will be used to the web service and for each port will mapping for your local machine, in this case, the webservice will use 8080 port and map to 8080 in you machine, if you already have some service using that port, it is necessary adjust that.
    - command: webserver, it the command that will be executed as parameter for the entrypoint program, in this case, indicates webserver.
    - healthcheck: it is a command to check if the webserver is already working, and it is set to do 3 tries of 30 seconds with intervals of 30 seconds, after this time the docker is set as unhealthy.

    It was an extensive a really extensive explaination, but the next two follow the same principles, with few differences:

<span style="font-size:0.7em;">

```yml
     scheduler:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - webserver
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
            - ./requirements.txt:/requirements.txt
        environment:
            - LOAD_EX=n
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
        command: scheduler

    worker:
        image: 'buzz84/docker-airflow:latest'
        restart: always
        depends_on:
            - scheduler
        volumes:
            - ../dags:/opt/airflow/dags
            - ../resources:/opt/airflow/resources
            - ./requirements.txt:/requirements.txt
        environment:
            - FERNET_KEY="gM2oAD_fTG99c2i7Tv3-kE3FuoNPWP_CjVVR3q62vvg="
            - EXECUTOR=Celery
            - POSTGRES_USER=airflow
            - POSTGRES_PASSWORD=airflow
            - POSTGRES_DB=airflow
            - POSTGRES_HOST=postgres
            - POSTGRES_PORT=5432
            - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
        command: worker
```
</span>

The configuration is almost the same of the webserver for worker and schedule, with very few changes:
 - dependencies will change, where the worker depends on the webserver and scheduler depends on the worker to started
 - volumes: config_files and scripts folder are no longer necessary for this services, it will just use the webserver container to load the parameters (the metadata database is shared for all services)
 - ports and health check are no longer necessary too
 - commands: changes to adapt to each one of the services

### **Config Files**

#### variables.json
We are going to have the variables that we want to load to our Airflow environment, that could be recovery inside of our dags and used them.
I used to have a group of common variables that I used to have in all dags (like environment, resource folder path, email, slack parameters ...) and also, have a variable from the dag, where I used to have it as a dictionary, it is easy to parse inside of any dag and also avoid too much variables in your Airflow.

<span style="font-size:0.7em;">

```json
{
    "ENVIRONMENT": "DEV",
    "RESOURCE_FOLDER": "/opt/airflow/resources",
    "PRJ_SETTING_UP_PARAMETERS":{
        "GCP_PROJECT_ID": "gcp-buzz84-training",
        "GCP_SERVICE_ACCOUNT_FILE": "/opt/airflow/config/gcp_service_account.json",
        "GCP_SERVICE_ACCOUNT_ID": "owner_access@gcp-buzz84-training.iam.gserviceaccount.com",
        "AIRFLOW_GCP_CONN": "GCP_CONNECTION"
    } 
}
```
</span>

#### connections.json
It is the same concept of variables but for connections, we are going to use this file to create the connections, in our example we will create a connection named GCP_CONNECTION of the type google_cloud_platform, tha points to an specific gcp project (this is mine, you must use yours here) and service account file (likewise gcp project, it must be yours here)

<span style="font-size:0.7em;">

```json
[
    {
        "CONN_ID": "GCP_CONNECTION",
        "CONN_URI": "",
        "CONN_TYPE": "google_cloud_platform",
        "CONN_HOST": "",
        "CONN_LOGIN": "",
        "CONN_PASSWORD": "",
        "CONN_SCHEMA": "",
        "CONN_PORT": "",
        "CONN_EXTRA": {
            "extra__jdbc__drv_path": "",
            "extra__google_cloud_platform__scope": "https://www.googleapis.com/auth/cloud-platform",
            "extra__google_cloud_platform__project": "gcp-buzz84-training", 
            "extra__google_cloud_platform__key_path": "/usr/local/airflow/config/gcp_service_account.json",
            "extra__jdbc__drv_clsname": "",
            "extra__google_cloud_platform__keyfile_dict": ""
        }
    }
]
```
</span>

#### pools.json
It is the same concept of variables but for pools, create or update pools that are used to limit the usage of resource of the Airflow, it means that the our task related with an specific pool will be managed accordingly with the capacity indicates in slots

<span style="font-size:0.7em;">

```json
{
    "default_pool": {
        "description": "Default pool",
        "slots": 30
    },
    "general_pool": {
        "description": "Pool used to be associated to general purpose tasks (dummy, branch, sensors, etc)",
        "slots": 10
    },
    "bigquery_pool": {
        "description": "Pool used to be associated to bigquery operator tasks",
        "slots": 5
    }
}

```
</span>


#### users.json
As soon as we are using RBAC user interface the access for the Airflow UI is controlled by username and password, this file will help us to create users with specifics roles.

<span style="font-size:0.7em;">

```json
{
        "buzz84": {
            "role": "Admin",
            "email": "buzz84@company.com",
            "firstname": "Jonatas",
            "lastname": "Junior",
            "password": "admin"
        },
        "john_doe": {
            "role": "User",
            "email": "john_doe@company.com",
            "firstname": "Jonatas",
            "lastname": "Junior",
            "password": "teste"
        }
}
```
</span>

#### gcp_service_account.json
It is the file used to connect with GCP services that will be referred into your connections or used by bash commands, this file could be generated into google cloud console [here, google page](https://cloud.google.com/iam/docs/service-accounts).
For 

<span style="font-size:0.7em;">
some information was ommited by security reasons, use from your GCP project instead.

```json
{
    "type": "service_account",
    "project_id": "gcp-buzz84-training",
    "private_key_id": "ommited by security reasons",
    "private_key": "ommited by security reasons",
    "client_email": "owner-access@gcp-buzz84-training.iam.gserviceaccount.com",
    "client_id": "ommited by security reasons",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/owner-access%40gcp-buzz84-training.iam.gserviceaccount.com"
  }
  ```
</span>

### **Script Files**
Airflow already have a command line tool that enable us to do a lot of things as for example create users, add variables, pools and connections and more...

Unfortunately, some of this commands are not so practical as another, for example, we are able to load the json files with variables and and pools in batch, but for users and connections have to be performed one user or one connection each time.

The scripts bellow are used to turn this jobs easier for us, I will not explain each program but left the code here.

<details><summary>airflow_create_connections.py</summary>
<span style="font-size:0.7em;">

```yml
import sys, io, json, subprocess, pathlib, os

def build_connection_commands(connection_file_path):
    bash_cmds = []
    file = open(connection_file_path, "r")
    json_connections = json.load(file)
    file.close()

    for connection in json_connections:
        bashCmd = []
        bashCmd.append("airflow")
        bashCmd.append("connections")
        bashCmd.append("-a")
        bashCmd.append("--conn_id=" + str(connection["CONN_ID"]))
        bashCmd.append("--conn_type=" + str(connection["CONN_TYPE"]))
        bashCmd = append_arguments(bashCmd, connection, 'CONN_URI')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_HOST')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_LOGIN')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_PASSWORD')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_SCHEMA')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_PORT')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_EXTRA')

        bash_cmds.append(bashCmd)     

    return bash_cmds       

def append_arguments(bashCmd, connection, argStr):
     if str(connection[argStr]) != "" and str(connection[argStr]) is not None:
            new_arg = ("--" + argStr.lower() + "='" + (str(json.dumps(connection[argStr])) if isinstance(connection[argStr], dict) else str(connection[argStr]).replace("'", '"')) + "'")
            bashCmd.append(new_arg)
     return bashCmd
            
def execute_bash_command(cmd):
    print("Executing: " + ' '.join([str(arg) for arg in cmd]) )
    os.system(' '.join([str(arg) for arg in cmd]))


def main(argv):
   inputfile = argv[0]
   if pathlib.Path(inputfile).name != "connections.json":
       print("connections.json did not find")
       sys.exit()

   cmds = build_connection_commands(inputfile)
   for cmd in cmds:
        execute_bash_command(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
```
</span>
</details>


<details>

<summary>airflow_create_users.py</summary>
<span style="font-size:0.7em;">

```yml
import argparse
import sys, io, json, subprocess, pathlib, os

def build_connection_commands(user_file_path, delete_before = False):
    bash_cmds = []
    file = open(user_file_path, "r")
    json_users = json.load(file)
    file.close()
    
    for user in json_users:
        if (delete_before):
            bashCmd = []
            bashCmd.append("airflow")
            bashCmd.append("delete_user")
            bashCmd.append("-u")
            bashCmd.append(str(user))  
            bash_cmds.append(bashCmd)               

        bashCmd = []
        bashCmd.append("airflow")
        bashCmd.append("create_user")
        bashCmd.append("-u")
        bashCmd.append(str(user))
        bashCmd.append("-r")
        bashCmd.append(str(json_users[user]["role"]))       
        bashCmd.append("-e")
        bashCmd.append(str(json_users[user]["email"]))
        bashCmd.append("-f")
        bashCmd.append(str(json_users[user]["firstname"]))
        bashCmd.append("-l")
        bashCmd.append(str(json_users[user]["lastname"]))
        bashCmd.append("-p")
        bashCmd.append(str(json_users[user]["password"]))                               
        bash_cmds.append(bashCmd)     

    return bash_cmds       


def execute_bash_command(cmd):
    print("Executing: " + ' '.join([str(arg) for arg in cmd]) )
    os.system(' '.join([str(arg) for arg in cmd]))


def main(argv):

    if (argv[0] == "-d"):
       delete_before = True
       inputfile = argv[1]
    else:
        delete_before = False
        inputfile = argv[0]

    if pathlib.Path(inputfile).name != "users.json":
       print("users.json did not find")
       sys.exit()

    cmds = build_connection_commands(inputfile, delete_before)
    for cmd in cmds:
        execute_bash_command(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
```
</span>
</details>

## Running Container

After have the project structure with all the files necessary and set up, it is time to run our docker compose file and up docker containers with all services.

Assuming that you are fine with the prerequisites, we will need pull the docker image with the necessary features to up the containers. we do that with running the command bellow in our favorite command tool.

```
docker pull buzz84/docker-airflow:latest
```
It could take a while, I need to work in smaller image
(sorry for that :disappointed: )


