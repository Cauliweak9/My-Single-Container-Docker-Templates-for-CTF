#!/bin/sh

# Get the user
user=$(ls /home)

chmod 740 /app/*

python /app/src/app.py

wait