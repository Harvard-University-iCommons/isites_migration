# iSites Migration

***NOTE: As of 2021 the HUIT AT UW team is no longer supporting this project.***

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

#### export_files

Exports iSites files to S3. You can exclude iSites Tool types using the EXPORT_FILES_EXCLUDED_TOOL_IDS setting. You can provide 
a csv file containing iSites keyword/Canvas course ID pairs to perform a batch export.

    $ python manage.py export_files --keyword=kXXXX --canvas_course_id=XXXX --settings=isites_migration.settings.base
    $ python manage.py export_files --csv=[path to csv file] --settings=isites_migration.settings.base

#### import_files

Uploads the iSites files zip export created by export_files from S3 to Canvas. You can provide a csv file containing iSites
keyword/Canvas course ID pairs to perform a batch import.

    $ python manage.py import_files --keyword=kXXXX --canvas_course_id=XXXX --settings=isites_migration.settings.base
    $ python manage.py import_files --csv=[path to csv file] --settings=isites_migration.settings.base

#### migrate_files

Wrapper command for export_files/import_files.

    $ python manage.py migrate_files --keyword=kXXXX --canvas_course_id=XXXX --settings=isites_migration.settings.base
    $ python manage.py migrate_files --csv=[path to csv file] --settings=isites_migration.settings.base
