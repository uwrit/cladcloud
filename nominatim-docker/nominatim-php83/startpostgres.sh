#!/bin/bash

service postgresql start
tail -f /var/log/postgresql/postgresql-16-main.log
