import logging
import os
import shutil
import gzip
import zipfile
import mimetypes
import json
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from icommons_common.models import Site, Topic, CourseSite

from file_service.models import FileRepository, FileNode, FileNodeAttribute, ImageMetadata, TopicText


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Exports iSites file repositories to AWS S3'
    option_list = BaseCommand.option_list + (
        make_option(
            '--term_id',
            action='store',
            dest='term_id',
            default=None,
            help='Provide an SIS term ID'
        ),
        make_option(
            '--keyword',
            action='store',
            dest='keyword',
            default=None,
            help='Provide an iSites keyword'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.export_directory = settings.EXPORT_DIR
        self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_ACCESS_KEY)
        self.bucket = self.connection.get_bucket(settings.AWS_EXPORT_BUCKET_SLIDE_TOOL, validate=False)

    def handle(self, *args, **options):
        term_id = options.get('term_id')
        keyword = options.get('keyword')
        if term_id:
            self._export_term(term_id)
        elif keyword:
            self._export_keyword(keyword)
        else:
            raise CommandError('You must provide either the --term_id or --keyword option.')

    def _export_term(self, term_id):
        keyword_sql_query = """
        SELECT cs.external_id AS external_id
        FROM course_instance ci, site_map sm, course_site cs
        WHERE
        ci.term_id = %d AND
        sm.course_instance_id = ci.course_instance_id AND
        sm.map_type_id = 'official' AND
        sm.course_site_id = cs.course_site_id AND
        cs.site_type_id = 'isite';
        """
        for cs in CourseSite.objects.raw(keyword_sql_query % term_id):
            self._export_keyword(cs.external_id)

    def _export_keyword(self, keyword):
        logger.info("Beginning iSites file export for keyword %s to S3 bucket %s", keyword, self.bucket.name)
        try:
            site = Site.objects.get(keyword=keyword)
        except Site.DoesNotExist:
            raise CommandError('Could not find iSite for the keyword provided.')

        topics = Topic.objects.filter(site=site).exclude(tool_id__in=settings.EXPORT_FILES_EXCLUDED_TOOL_IDS)
        for topic in topics:
            file_repository_id = "icb.topic%s.files" % topic.topic_id
            try:
                file_repository = FileRepository.objects.get(file_repository_id=file_repository_id)
            except FileRepository.DoesNotExist:
                logger.info("FileRepository does not exist for %s", file_repository_id)
                continue

            if topic.title:
                topic_title = topic.title.strip().replace(' ', '_')
            else:
                topic_title = 'no_title_%s' % topic.topic_id

            logger.info("Exporting files for topic %d %s", topic.topic_id, topic_title)
            self._export_file_repository(file_repository, topic_title)
            self._export_topic_text(topic, topic_title)

        keyword_export_path = os.path.join(self.export_directory, keyword)
        z_file = zipfile.ZipFile(os.path.join(self.export_directory, "%s.zip" % keyword), 'w')
        for root, dirs, files in os.walk(keyword_export_path):
            for file in files:
                z_file.write(os.path.join(root, file))
        z_file.close()
        shutil.rmtree(keyword_export_path)

        export_key = Key(self.bucket)
        export_key.key = "%s.zip" % keyword
        export_key.set_metadata('Content-Type', 'application/zip')
        keyword_export_file = os.path.join(self.export_directory, export_key.key)
        export_key.set_contents_from_filename(keyword_export_file)
        logger.info("Uploaded file export for keyword %s to S3 Key %s", keyword, export_key.key)

        os.remove(keyword_export_file)

        logger.info("Finished exporting files for keyword %s to S3 bucket %s", keyword, self.bucket.name)

    def _export_file_repository(self, file_repository, topic_title):
        for file_node in FileNode.objects.filter(file_repository=file_repository):
            if file_node.file_type == 'file':
                if file_node.storage_node:
                    storage_node_location = file_node.storage_node.physical_location
                elif file_repository.storage_node:
                    storage_node_location = file_repository.storage_node.physical_location
                else:
                    logger.error("Failed to find storage node for file node %d", file_node.file_node_id)
                    continue

                source_file = os.path.join(storage_node_location, file_node.physical_location)
                export_file = os.path.join(
                    self.export_directory, keyword, topic_title, file_node.physical_location
                )
                try:
                    os.makedirs(os.dirname(export_file))
                except os.error:
                    pass

                if file_node.encoding == 'gzip':
                    with gzip.open(source_file, 'rb') as s_file:
                        with open(export_file, 'w') as d_file:
                            for line in s_file:
                                d_file.write(line)
                else:
                    shutil.copy(source_file, export_file)

                logger.info("Copied file %s to export location %s", source_file, export_file)

    def _export_topic_text(self, topic, topic_title):
        for topic_text in TopicText.objects.filter(topic_id=topic.topic_id):
            export_file = os.path.join(
                self.export_directory, keyword, topic_title, topic_text.name
            )
            try:
                os.makedirs(os.dirname(export_file))
            except os.error:
                pass

            with open(export_file, 'w') as f:
                f.write(topic_text.source_text)

            logger.info("Copied TopicText %d to export location %s", topic_text.text_id, export_file)
