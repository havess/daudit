#!/bin/bash
set -e
chown -R mysql /var/lib/mysql
chgrp -R mysql /var/lib/mysql
sudo service mysql start
sudo service cron start
mysql -e "CREATE DATABASE daudit_internal"
mysql -u root -p${DAUDIT_INTERNAL_PASS} daudit_internal < schema.sql
exec "$@"
