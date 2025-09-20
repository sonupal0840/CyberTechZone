#!/usr/bin/env bash
set -o errexit

# Update system
apt-get update -y

# Microsoft repo key add karo
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
apt-get update -y
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
