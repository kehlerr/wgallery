#!/bin/sh

deploy_path="/var/www/html/tthottie-casting/"

if [ ! -d "$deploy_path" ]; then
    mkdir -p "$deploy_path";
    mkdir -p "$deploy_path""css/";
    mkdir -p "$deploy_path""img/";
fi

cp config.py  "$deploy_path";
cp index.py  "$deploy_path";
cp promote.py "$deploy_path";
cp -R css/* "$deploy_path""css/";
cp -R img/* "$deploy_path""img/";
