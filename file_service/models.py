import logging

from django.db import models

from icommons_common.models import Topic


logger = logging.getLogger(__name__)


class StorageNode(models.Model):
    storage_node_id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=500)
    internal_url = models.CharField(max_length=500)
    protocol = models.CharField(max_length=20, blank=True, null=True)
    physical_location = models.CharField(max_length=4000, blank=True, null=True)
    allocation_hint = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        db_table = 'storage_node'

    def __unicode__(self):
        return self.storage_node_id


class FileQuota(models.Model):
    quota_id = models.CharField(primary_key=True, max_length=200)
    soft_limit = models.IntegerField()
    hard_limit = models.IntegerField()

    class Meta:
        db_table = 'file_quota'

    def __unicode__(self):
        return self.quota_id


class FileRepository(models.Model):
    file_repository_id = models.CharField(primary_key=True, max_length=200)
    storage_node = models.ForeignKey(StorageNode, blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    repository_type = models.CharField(max_length=100)
    quota = models.ForeignKey(FileQuota)
    proc_description = models.CharField(max_length=4000, blank=True, null=True)
    proc_type = models.CharField(max_length=20, blank=True, null=True)
    sort_order = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        db_table = 'file_repository'

    def __unicode__(self):
        return self.file_repository_id


class FileNode(models.Model):
    file_node_id = models.IntegerField(primary_key=True)
    file_repository = models.ForeignKey(FileRepository)
    storage_node = models.ForeignKey(StorageNode, blank=True, null=True)
    file_name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()
    file_creator = models.CharField(max_length=50)
    file_modifier = models.CharField(max_length=50)
    last_modified = models.DateTimeField()
    created_on = models.DateTimeField()
    permission_id = models.CharField(max_length=200, blank=True, null=True)
    file_type = models.CharField(max_length=200)
    physical_location = models.CharField(max_length=4000, blank=True, null=True)
    last_served = models.DateTimeField()
    serve_status = models.CharField(max_length=1, blank=True, null=True)
    content_type = models.CharField(max_length=4000, blank=True, null=True)
    encoding = models.CharField(max_length=15, blank=True, null=True)
    parent_file_node_id = models.IntegerField()
    attribute = models.CharField(max_length=255, blank=True, null=True)
    disk_size = models.IntegerField()
    confirmation_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'file_node'

    def __unicode__(self):
        return self.file_name


class FileNodeAttribute(models.Model):
    # FILE_NODE_ATTRIBUTE does not have a primary key
    # Using file_node_id so that this table can be mapped
    file_node_id = models.IntegerField(primary_key=True)
    attribute = models.CharField(max_length=200)
    value = models.CharField(max_length=4000)
    attribute_creator = models.CharField(max_length=50)
    created_time = models.DateTimeField()

    class Meta:
        db_table = 'file_node_attribute'

    def __unicode__(self):
        return self.attribute


class MetadataCv(models.Model):
    metadata_cv_id = models.IntegerField(primary_key=True)
    metadata_section_id = models.IntegerField(blank=True, null=True)
    datatype = models.IntegerField(blank=True, null=True)
    cv_section = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'metadata_cv'

    def __unicode__(self):
        return self.label


class TopicMetadataSet(models.Model):
    topic_metadata_set_id = models.IntegerField(primary_key=True)
    metadata_cv = models.ForeignKey(MetadataCv)
    topic = models.ForeignKey(Topic)
    alt_name = models.CharField(max_length=255, blank=True, null=True)
    display = models.IntegerField()
    display_order = models.IntegerField()
    last_modified = models.DateTimeField()
    deleted = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        db_table = 'topic_metadata_set'

    def __unicode__(self):
        return self.topic_metadata_set_id


class ImageMetadata(models.Model):
    image_metadata_id = models.IntegerField(primary_key=True)
    topic_metadata_set = models.ForeignKey(TopicMetadataSet)
    file_node = models.ForeignKey(FileNode)
    metadata_data = models.CharField(max_length=4000)

    class Meta:
        db_table = 'image_metadata'

    def __unicode__(self):
        return self.file_name


class TopicText(models.Model):
    text_id = models.IntegerField(primary_key=True)
    topic_id = models.IntegerField()
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=250)
    type = models.CharField(max_length=20)
    default_text = models.CharField(max_length=1)
    source_text = models.TextField()
    processed_text = models.TextField()
    modified_on = models.DateTimeField()
    modified_by = models.CharField(max_length=50)

    class Meta:
        db_table = 'topic_text'

    def __unicode__(self):
        return self.title
