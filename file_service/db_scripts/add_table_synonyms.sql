CREATE SYNONYM storage_node FOR icb.storage_node;
CREATE SYNONYM file_quota FOR icb.file_quota;
CREATE SYNONYM file_repository FOR icb.file_repository;
CREATE SYNONYM file_node FOR icb.file_node;
CREATE SYNONYM file_node_attribute FOR icb.file_node_attribute;
CREATE SYNONYM metadata_cv FOR icb.metadata_cv;
CREATE SYNONYM topic_metadata_set FOR icb.topic_metadata_set;
CREATE SYNONYM image_metadata FOR icb.image_metadata;

GRANT SELECT ON storage_node TO termtool;
GRANT SELECT ON file_quota TO termtool;
GRANT SELECT ON file_repository TO termtool;
GRANT SELECT ON file_node TO termtool;
GRANT SELECT ON file_node_attribute TO termtool;
GRANT SELECT ON metadata_cv TO termtool;
GRANT SELECT ON topic_metadata_set TO termtool;
GRANT SELECT ON image_metadata TO termtool;
