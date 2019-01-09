#!/usr/bin/env bash

sudo apt-get update && sudo apt-get upgrade -y

# Install MySQL
sudo apt-get install mysql-server default-libmysqlclient-dev default-jre unzip
sudo apt-get install python3-pip python3-dev redis

# Install python packages
pip3 install mysqlclient Django fuzzywuzzy rq django-rq multiqc openpyxl python-Levenshtein

# Install FastQC
cd /usr/local/src
sudo wget https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.8.zip
sudo unzip fastqc_v0.11.8.zip -d /usr/local/
sudo chmod 755 /usr/local/FastQC/fastqc
sudo ln -s /usr/local/FastQC/fastqc /usr/local/bin/fastqc
# and Redis server
sudo wget http://download.redis.io/redis-stable.tar.gz
sudo tar xvzf redis-stable.tar.gz
cd redis-stable
sudo make
sudo make install

# Run SQL security utility
sudo mysql_secure_installation
# When MySQL inevitably gives you a headache logging in:
# https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04

# Next up ----------------------------------------------------
