-- Migration script to add ON DELETE CASCADE to foreign key constraints
-- Run this against your PostgreSQL database

-- First, drop the existing foreign key constraints
ALTER TABLE tbl_scan_log DROP CONSTRAINT IF EXISTS tbl_scan_log_scan_instance_id_fkey;
ALTER TABLE tbl_scan_config DROP CONSTRAINT IF EXISTS tbl_scan_config_scan_instance_id_fkey;
ALTER TABLE tbl_scan_results DROP CONSTRAINT IF EXISTS tbl_scan_results_scan_instance_id_fkey;
ALTER TABLE tbl_scan_correlation_results DROP CONSTRAINT IF EXISTS tbl_scan_correlation_results_scan_instance_id_fkey;
ALTER TABLE tbl_scan_correlation_results_events DROP CONSTRAINT IF EXISTS tbl_scan_correlation_results_events_correlation_id_fkey;
ALTER TABLE tbl_scan_correlation_results_events DROP CONSTRAINT IF EXISTS tbl_scan_correlation_results_events_event_hash_fkey;

-- Now add them back with ON DELETE CASCADE
ALTER TABLE tbl_scan_log
    ADD CONSTRAINT tbl_scan_log_scan_instance_id_fkey
    FOREIGN KEY (scan_instance_id) REFERENCES tbl_scan_instance(guid) ON DELETE CASCADE;

ALTER TABLE tbl_scan_config
    ADD CONSTRAINT tbl_scan_config_scan_instance_id_fkey
    FOREIGN KEY (scan_instance_id) REFERENCES tbl_scan_instance(guid) ON DELETE CASCADE;

ALTER TABLE tbl_scan_results
    ADD CONSTRAINT tbl_scan_results_scan_instance_id_fkey
    FOREIGN KEY (scan_instance_id) REFERENCES tbl_scan_instance(guid) ON DELETE CASCADE;

ALTER TABLE tbl_scan_correlation_results
    ADD CONSTRAINT tbl_scan_correlation_results_scan_instance_id_fkey
    FOREIGN KEY (scan_instance_id) REFERENCES tbl_scan_instance(guid) ON DELETE CASCADE;

ALTER TABLE tbl_scan_correlation_results_events
    ADD CONSTRAINT tbl_scan_correlation_results_events_correlation_id_fkey
    FOREIGN KEY (correlation_id) REFERENCES tbl_scan_correlation_results(id) ON DELETE CASCADE;

ALTER TABLE tbl_scan_correlation_results_events
    ADD CONSTRAINT tbl_scan_correlation_results_events_event_hash_fkey
    FOREIGN KEY (event_hash) REFERENCES tbl_scan_results(hash) ON DELETE CASCADE;
