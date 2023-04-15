#!/bin/bash

echo 'removing db...'
rm fog.db
rm global.db
echo 'creating db...'
touch fog.db
touch global.db
echo 'creating tables...'
python create_table_script.py

echo 'DB resetted!'