# iSites Migration

This project provides tools to assist the migration from iSites to Canvas.

## Installation

Clone this repository to a server that has access to iSites storage nodes.

    $ cd isites_migration
    $ pip install -r isites_migration/requirements/base.txt
    $ cp isites_migration/settings/secure.py.example isites_migration/settings/secure.py
    
Edit secure.py, adding the correct settings for the environment.

## Django Commands

#### export_slide_tool

Exports iSites Slide Tool files and metadata to S3.

    $ python manage.py export_slide_tool --keyword=kXXXX --settings=isites_migration.settings.base
