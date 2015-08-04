import logging
import csv
import json
import time
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from boto.s3.connection import S3Connection

from canvas_sdk.methods import content_migrations, files
from canvas_sdk.exceptions import CanvasAPIError

from icommons_common.canvas_utils import SessionInactivityExpirationRC


logger = logging.getLogger(__name__)
SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)


class Command(BaseCommand):
    help = 'Imports iSites file repository export to Canvas'
    option_list = BaseCommand.option_list + (
        make_option(
            '--keyword',
            action='store',
            dest='keyword',
            default=None,
            help='Provide an iSites keyword'
        ),
        make_option(
            '--canvas_course_id',
            action='store',
            dest='canvas_course_id',
            default=None,
            help='Provide a Canvas course ID'
        ),
        make_option(
            '--csv',
            action='store',
            dest='csv_path',
            default=None,
            help='Provide the path to a csv file containing iSites keyword/Canvas course ID pairs'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_ACCESS_KEY)
        self.bucket = self.connection.get_bucket(settings.AWS_EXPORT_BUCKET_SLIDE_TOOL, validate=False)
        self.canvas_progress_urls = []

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        canvas_course_id = options.get('canvas_course_id')
        csv_path = options.get('csv_path')

        if csv_path:
            self._import_csv(csv_path)
        elif keyword and canvas_course_id:
            self._import_isite(keyword, canvas_course_id)
        else:
            raise CommandError(
                'You must provide either the --keyword and --canvas_course_id options or the --csv option.'
            )

        import_count = len(self.canvas_progress_urls)
        failed_count = 0
        while self.canvas_progress_urls:
            time.sleep(2)
            completed_imports = []
            failed_imports = []
            for progress_url in self.canvas_progress_urls:
                progress = json.loads(SDK_CONTEXT.session.request('GET', progress_url).text)
                workflow_state = progress['workflow_state']
                if workflow_state == 'completed':
                    self._lock_import_folder(canvas_course_id, settings.CANVAS_IMPORT_FOLDER_NAME)
                    completed_imports.append(progress_url)
                elif workflow_state == 'failed':
                    failed_imports.append(progress_url)
                    failed_count += 1

            for progress_url in completed_imports + failed_imports:
                self.canvas_progress_urls.remove(progress_url)
            count_processing = len(self.canvas_progress_urls)
            if count_processing:
                logger.info(
                    "%d Canvas imports complete, %d failed, %d processing",
                    len(completed_imports),
                    len(failed_imports),
                    count_processing
                )

        logger.info("Completed import of %d iSites file exports, %d failed.", import_count, failed_count)

    def _import_csv(self, csv_path):
        logger.info("Importing iSites file exports from csv %s", csv_path)
        try:
            with open(csv_path, 'rb') as csv_file:
                for row in csv.reader(csv_file):
                    self._import_isite(row[0], row[1])
        except (IOError, IndexError):
            raise CommandError("Failed to read csv file %s", csv_path)

    def _import_isite(self, keyword, canvas_course_id):
        import_folder = self._get_or_create_import_folder(canvas_course_id, settings.CANVAS_IMPORT_FOLDER_NAME)
        export_file_url = self._get_export_s3_url(keyword)
        logger.info("Importing iSites file export from %s to Canvas course %s", export_file_url, canvas_course_id)
        response = json.loads(content_migrations.create_content_migration_courses(
            SDK_CONTEXT,
            canvas_course_id,
            'zip_file_importer',
            settings_file_url=self._get_export_s3_url(keyword),
            settings_folder_id=import_folder['id']
        ).text)
        progress_url = response['progress_url']
        self.canvas_progress_urls.append(progress_url)
        logger.info(
            "Created Canvas content migration %s for import from %s to Canvas course %s",
            progress_url,
            export_file_url,
            canvas_course_id
        )

    def _get_export_s3_url(self, keyword):
        try:
            key = self.bucket.get_key("%s.zip" % keyword)
        except boto.exception.S3ResponseError:
            raise CommandError(
                "iSites file export for keyword %s does not exist in S3 bucket %s", keyword, self.bucket.name
            )

        return key.generate_url(settings.AWS_EXPORT_DOWNLOAD_TIMEOUT_SECONDS)

    def _get_root_folder_for_canvas_course(self, canvas_course_id):
        return json.loads(files.get_folder_courses(
            SDK_CONTEXT,
            canvas_course_id,
            'root'
        ).text)

    def _get_or_create_import_folder(self, canvas_course_id, folder_name):
        root = self._get_root_folder_for_canvas_course(canvas_course_id)
        folders = json.loads(files.list_folders(SDK_CONTEXT, root['id']).text)
        import_folder = None
        for folder in folders:
            if folder['name'] == folder_name:
                import_folder = folder
                break
        if not import_folder:
            try:
                import_folder = json.loads(files.create_folder_courses(
                    SDK_CONTEXT, canvas_course_id, folder_name, root['id'], None, None, None, None, None, None
                ).text)
                logger.info("Created import folder %s for canvas_course_id %s", folder_name, canvas_course_id)
            except CanvasAPIError:
                logger.exception("Failed to create import folder %s for canvas_course_id %s", folder_name, canvas_course_id)
                raise
        return import_folder

    def _lock_import_folder(self, canvas_course_id, folder_name):
        import_folder = self._get_or_create_import_folder(canvas_course_id, folder_name)
        try:
            files.update_folder(
                SDK_CONTEXT,
                import_folder['id'],
                import_folder['name'],
                import_folder['parent_folder_id'],
                None,
                None,
                'true',
                None,
                None
            )
            logger.info("Locked import folder %s for canvas_course_id %s", folder_name, canvas_course_id)
        except CanvasAPIError:
            logger.exception("Failed to lock import folder %s for canvas_course_id %s", folder_name, canvas_course_id)
            raise
