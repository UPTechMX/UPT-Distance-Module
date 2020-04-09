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

This tool does not provide an user interface, so all comunication with the tool is done via REST interfaces.

The general operation of the tools is as follows:

1. A study area must be created
2. Then Minimum Mapping Units have to be attached to the study area; this data will be used as the source layer
3. All the target features have to be attached to the study area
4. Finally the tool will evaluate the shortest euclidean distance among the Minimum Mapping Units and the target features

All the previous steps can only be done by using the user interface provided by the UPT Server Extension.

## Installation

**Disclaimer:** This tool has only been tested on Ubuntu Server 18.04

To proceed with the installation

### Create PostGIS database

1. Install the database server with the following command  `sudo apt install postgresql-10 postgresql-10-postgis-3`
2. Connect to to your database server with the following command  `sudo su postgres && psql`
3. Create a data base with the following command `create database upt;`
4. Create a user with the following command  `create user upt with password '1234567890' SUPERUSER CREATEDB LOGIN;`; the username and pasword can be adjusted as needed.
5. Connect to the database with the following command  `\c upt;`
6. Create the PostGIS extension in the database with the following command  `create extension postgis`

### Install the Tool

1. It's necessary to install the virtualenv package in the server that will host the applicaton. To do so, execute the following command `sudo apt-get install virtualenv`
2. Create a Python 3 virtual environment by executing the following command `virtualenv -p python3 ~/python3`. This will create the directory `python3` in the user's home directory
3. After the creation of the virtual environment has finished, the virtual environment must be enabled; this can be done by excecuting the following command `source ~/python3/bin/activate`
4. Once the virtual environment has been enabled, the following python packages need to be installed. Use the command `pip install NAME_OF_THE_PACKAGE`

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

5. Once all packages have been installed, clone this project repository into the server. Move to the user's home and execute the following command  `git clone https://github.com/UPTechMX/UPT-Distance-Module`, this will create a directory named `UPT-Distance-Module` in the user's home.
6. Move to the newly created directory with the following command `cd ~/UPT-Distance-Module`
7. Inside the `ST` directory, create a `.env` file; use the `.env.example` as a template
8. Set the appropiate credentials to the newly created `.env` file
9. Don't forget to set a secure `SECRET_KEY` in the same file

### Create the database structure for the tool

1. Execute the command `python manage.py makemigrations plup`
2. Execute the command `python manage.py migrate plup`
3. Start the application with the command `python manage.py runserver 90`

After following the previous steps, the application should be accesible through port 90. If the server has a firewall, set up the firewall to allow incomming connections to port 90.

#### Aditional settings

Edit the dictionary `PARALLEL` instantiated in the file `~/UPT-Distance-Module/ST/settings` to set the values that best fits the server resources, use the attribute `MAX_THREADS` to set the maximun cores available in the server.

Since the tool does not use any login mechanism, to prevent undesired access to the tool use the variable `ALLOWED_HOSTS` to only allow the UPT Server Extension to access the application. The variable is available in the file `~/UPT-Distance-Module/ST/settings`

It's possible to install the application and the database in different servers. To achieve this, it's necessary to appropriately set up the database connections.

## References

--

## Author Info

CAPSUS S.C. Capital Sustentable (CAPSUS) is a mission-oriented consulting firm, based in Mexico City, specialized in sustainability issues in the energy, environmental and urban sectors. Since 2009, the firm has executed projects that promote urban sustainable development both in Mexico and abroad. CAPSUS aims at increasing the performance of our clients by designing and promoting public policies, business practices and social behaviors that facilitate sustainable development, where energy efficiency, environmental protection, social integration, and economic development are paramount. The services offered by CAPSUS are focused on empowering best practices in sustainability through different approaches. A bottom-up approach is taken with urban and environmental management projects and a top-down angle with research, development, and public policy implementation projects. This two-end approach ensures not only the implementation of the projects but also their impact on a bigger scale and the possibility of replication.
