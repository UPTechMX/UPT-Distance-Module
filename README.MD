# UPT Distance Module

## Table of contents

- Description
- How To Use
- References
- Author Info

## Description

This project evaluates Euclidean distances.

## Main Technologies Used

- Django
- Celery
- PostgreSQL

## How To Use

This tool does not provide an user interface, so all comunication with the tool is done vía REST interfaces.

The general operation of the tools is as follows:

1. A study area must be created
1. Then Minimum Maping Units have to be attached in the study area, this data will be used as the source layer
1. All the target features have to be attached in the study area
1. Finally the tool will evaluate the shortest euclidean distance among the Minimum Mapping Units and the target features

All the previous steps can only be done by using the user interface provided by the UPT Server Extension.

## Installation

This tool has been tested only on Ubuntu Server 18.04
To proceed with the installation

### Create PostGIS database

1. install the database server with `sudo apt install postgresql-10 postgresql-10-postgis-3`
1. connecto to your database server `sudo su postgres && psql`
1. create a data base with `create database upt;`
1. create a user by typing `create user upt with password '1234567890' SUPERUSER CREATEDB LOGIN;`, the user name and pasword can be adjusted as needed.
1. connect to the database with `\c upt;`
1. create the PostGIS extencion in the database `create extension postgis`

### Install the Tool

1. first it is necesary to install the virtualenv package in the server that will host the applicaton, so execute the following command `sudo apt-get install virtualenv`
1. next, create a Python 3 virtual environment by executing the following command `virtualenv -p python3 ~/python3`, this will create the directory `python3` in the user's home directory
1. after the creation of the virutal environment have finished, the virtual environment must be enabled, this can be done by excecuting `source ~/python3/bin/activate`
1. once the virtual environmente have been enabled, the following python packages have to be installed. use the command `pip install NAME_OF_THE_PACKAGE`

    - numpy
    - shutil
    - zipfile
    - psycopg2_binary
    - architect
    - sqlalchemy
    - redis
    - Celery
    - python-decouple
    - django
    - djangorestframework
    - django-filter
    - django-filters
    - django-celery-results

1. now it is time to clone this project repository into the server, move to the user's home and  execute `git clone https://github.com/UPTechMX/UPT-Distance-Module`, this will create a directory named `UPT-Distance-Module` in the users home.
1. move to the newly created directory with `cd ~/UPT-Distance-Module`
1. inside the directory ST, create a `.env` file, use the `.env.example` as a template
1. set the appropiate credentials in the `.env` file
1. don't forget to also set a secure `SECRET_KEY` in the same file

### create the database structure for the tool

1. execute the command ` python manage.py makemigrations plup `
2. execute the command ` python manage.py migrate plup `
3. start the application with the command `python manage.py start runserver 90`

After following the previous steps, the application should be accesible over the port 90. If the server has a firewall, set up the firewall to allow incomming connections to port 90

#### Aditional settings

Edit the dictionary `PARALLEL` instantiated in the file `~/UPT-Distance-Module/ST/settings` to set the values that best fits the server resources, use the attribute `MAX_THREADS` to set the maximun cores available in the server.

Since the tool does not use any login mechanism, to avoid undesired access to the tool use the variable `ALLOWED_HOSTS` to allow only the UPT Server Extension to access the application. The variable is available in the file `~/UPT-Distance-Module/ST/settings`

Also it is possible to install the application and the databse in different servers, for that it is necessary to set appropriately the database connections.

## References

--

## Author Info

CAPSUS S.C. Capital Sustentable (CAPSUS) is a mission-oriented consulting firm, based in Mexico City, specialized in sustainability issues in the energy, environmental and urban sectors. Since 2009, the firm has executed projects that promote urban sustainable development both in Mexico and abroad. CAPSUS aims at increasing the performance of our clients by designing and promoting public policies, business practices and social behaviors that facilitate sustainable development, where energy efficiency, environmental protection, social integration, and economic development are paramount. The services offered by CAPSUS are focused on empowering best practices in sustainability through different approaches. A bottom-up approach is taken with urban and environmental management projects and a top-down angle with research, development, and public policy implementation projects. This two-end approach ensures not only the implementation of the projects but also their impact on a bigger scale and the possibility of replication.
