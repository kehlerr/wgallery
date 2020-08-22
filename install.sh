#!/bin/bash

root_link_path="wgallery/static/catalogs_root"

if [ -d "$root_link_path" ]; then
    echo "catalogs root exists, skip";
else
    echo "Enter absolute path to the root catalog:"
    read catalog_path;
    if [ -d "$catalog_path" ]; then
        echo "creating symbolic link to this catalog...";
        ln -s "$catalog_path" "$root_link_path"
    else
        echo "catalog doesn't exists; aborting..."
        exit -1;
    fi
fi;

echo "init database..."
/usr/bin/env python3 wgallery/create_db.py
echo "done"