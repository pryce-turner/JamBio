#!/usr/bin/env bash

sudo apt-get update && sudo apt-get upgrade -y

# Install MySQL
sudo apt-get install mysql-server default-libmysqlclient-dev default-jre

sudo apt-get install python3-pip python3-dev

# Run SQL security utility
sudo mysql_secure_installation
# When MySQL inevitably gives you a headache logging in:
# https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04

# Next up ----------------------------------------------------
# pip3 install mysqlclient Django fuzzywuzzy rq django-rq multiqc
# Install FastQC
