GRANT SELECT ON storage_node TO termtool;
GRANT SELECT ON file_quota TO termtool;
GRANT SELECT ON file_repository TO termtool;
GRANT SELECT ON file_node TO termtool;
GRANT SELECT ON file_node_attribute TO termtool;
GRANT SELECT ON metadata_cv TO termtool;
GRANT SELECT ON topic_metadata_set TO termtool;
GRANT SELECT ON image_metadata TO termtool;
GRANT SELECT ON topic_text TO termtool;
GRANT SELECT ON page_content TO termtool;
GRANT SELECT ON page TO termtool;


CREATE SYNONYM storage_node FOR icb.storage_node;
CREATE SYNONYM file_quota FOR icb.file_quota;
CREATE SYNONYM file_repository FOR icb.file_repository;
CREATE SYNONYM file_node FOR icb.file_node;
CREATE SYNONYM file_node_attribute FOR icb.file_node_attribute;
CREATE SYNONYM metadata_cv FOR icb.metadata_cv;
CREATE SYNONYM topic_metadata_set FOR icb.topic_metadata_set;
CREATE SYNONYM image_metadata FOR icb.image_metadata;
CREATE SYNONYM topic_text FOR icb.topic_text;
CREATE SYNONYM page_content FOR icb.page_content;
CREATE SYNONYM page FOR icb.page;

/*
Index fix for character set mismatch between cx_Oracle driver and Oracle.
http://stackoverflow.com/questions/18978536/poor-performance-of-django-orm-with-oracle
 */
create index c2c_file_repository_id on file_node(SYS_OP_C2C(file_repository_id));
