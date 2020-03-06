#!/bin/bash
set -e
sudo service mysql start
mysql -e "create database daudit_internal"
mysql -u root -p${DAUDIT_INTERNAL_PASS} daudit_internal < schema.sql
exec "$@"
