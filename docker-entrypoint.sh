#!/bin/bash
set -e
chown -R mysql /var/lib/mysql
chgrp -R mysql /var/lib/mysql
sudo service mysql start
sudo service cron start
mysql -e "CREATE DATABASE daudit_internal"
mysql -u root -p${DAUDIT_INTERNAL_PASS} daudit_internal < schema.sql
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DAUDIT_INTERNAL_PASS}'"
mysql -e "flush privileges" -p$DAUDIT_INTERNAL_PASS
exec "$@"
