# Airflow Series - Setting Up for GCP Projects

This repository sub-folder has the objective of provide the files necessary and training to set up a Docker with Airflow containing the configuration necessary to work with GCP Projects.

This training is assuming that you have basics Docker and Docker Composer knowledge.

The traing aim to teach you how to UP docker containers (using CeleryExecutor) and setting up the Airflow to work with GCP projects.

We are using an existent [docker image](https://hub.docker.com/r/buzz84/docker-airflow) (see [git project](https://github.com/jjunior84/docker-airflow)) build by myself containing [Airflow 1.10.10](https://airflow.apache.org/docs/1.10.10/) with [Python 3.7](https://docs.python.org/3.7/) and setting up to br possible use RBAC interface

Have Fun! :smiley:

## Project structure

The training was design to explain the process of have the environment by project, assuming that all dag that you must be want to design is related with the same project, it is easy to organize that way.

Let´s look for **01_setting_up** project:

![Project Structure](./docs/project_structure.png)

## Detailing Files

### docker-composer.yml

The heart of our training, the composer file presents below is responsible by create our containers (all the four + dependency container)

<details><summary>docker-composer.yml</summary>

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
            # Uncomment to include custom plugins
            # - ./plugins://opt/airflow/plugins
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
</details>