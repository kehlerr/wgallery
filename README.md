wgallery is an web application written in python3, Flask for organizing and viewing videos.  
With this app you can play and explore videos from your disk right in web-browser and pick your favorite videos or delete some, duplicates, for instance.

Install:  
    0. Activate your virtual env if you need.  
    1. `<pip3 install -r requirements.txt>`  
    2. Run setup.py script:  
        `<python3 setup.py install>`  
    3. Prepare root catalog, which contains other catalog(s) with video files.  
       For example, let's create one in home directory:  
       `<cd && mkdir example_root && cd example_root;>`  
       Then add a few catalogs:  
       `<mkdir movies camera raw_sources;>`  
       and move videos to this catalogs or you can just move catalogs with videos to example_root;
    4. Go back to the wgallery catalog and run:  
        `<chmod +x install.sh && ./install.sh>`  
        Here you'll need to specify absolute path to example_root and if no message errors shown - application is ready to use.  

Run:  
    1. Run script:  
        `<chmod +x run.sh && ./run.sh>`  
    2. Open any web-browser and type in address-box:  
        http://localhost:5000  

Usage:  
    1. When you installed and ran the app first time, you need specify the type and category(optional) of each catalog  
    2. Go to index page (http://localhost:5000)  
    3. In section "New catalogs" you'll see all catalogs requiring type and category(optional) assignment.  
    4. Press "+" button on catalog's cell and choose or enter new type and category in modal; save changes.  
    5. Changed catalog will appear in overall table of catalogs, now you can browse videos from that catalog.  

Now you can filter catalogs by type and category (if you've created any) with corresponding buttons on top panels on index page.  

When browsing catalog, you can pick videos for promotion (right check box) or for deletion (left check box).  
Press "Submit" button on the bottom of page to make changes (if you press buttons with arrows (back and forward) nothing will be changed, all checkboxes will be cleared).
Buttons "PROMOTE" and/or "TODELETE" will appear on the top of page, and you can filter videos with this buttons.  
When you checked all videos you want, you can commit changes with buttons "PROMOTE" and "DELETE" on the right side of top panel.  
All current checked videos will be moved to the automatic-created folders with prefixes "promoted_" and "deleted_" respectively and won't be shown in overall list anymore.