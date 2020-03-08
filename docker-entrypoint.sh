#!/bin/bash
set -e
chown -R mysql /var/lib/mysql
chgrp -R mysql /var/lib/mysql
sudo service mysql start
mysql -e "create database daudit_internal"
mysql -u root -p${DAUDIT_INTERNAL_PASS} daudit_internal < schema.sql
exec "$@"

sudo service cron start