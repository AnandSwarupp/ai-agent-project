#!/usr/bin/env bash

# Update packages and install dependencies
apt-get update && apt-get install -y curl gnupg apt-transport-https

# Add Microsoft package repository
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install the ODBC Driver 18 and unixODBC
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# Install Python dependencies
pip install -r requirements.txt
