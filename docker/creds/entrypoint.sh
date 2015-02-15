#!/bin/bash

# create database if not exists
python /srv/creds/docker/creds/create_database.py /srv/creds/development.ini

# setup
creds -f /srv/creds/development.ini setup

# python setup.py compile_catalog

exec "$@"