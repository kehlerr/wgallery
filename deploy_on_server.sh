#!/bin/sh

deploy_path="/var/www/html/cgi-enabled/"

cp config.py  "$deploy_path"; 
cp index.py  "$deploy_path";
cp promote.py "$deploy_path";
