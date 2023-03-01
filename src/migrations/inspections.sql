

CREATE TABLE inspections.kafka_stream
(
    `inspection_id` UUID,
    `worker_id` UUID,
    `device_id` UUID,
    `event_type` LowCardinality(String),
    `event_data` String,
    `datetime` DateTime64
)
ENGINE=Kafka
SETTINGS
    kafka_broker_list = 'rc1a-g31oe8fl2r0n9vmc.mdb.yandexcloud.net:9091',
    kafka_topic_list = 'inspections_events',
    kafka_group_name = 'sample_group',
    kafka_format = 'JSONEachRow';

 CREATE MATERIALIZED VIEW inspections.materialize_kafka_events TO inspections.event_log
 AS SELECT
 	inspection_id,
 	worker_id,
 	device_id,
 	event_type,
 	event_data as `payload`,
 	`datetime`
FROM inspections.kafka_stream


CREATE TABLE inspections.event_log
(
    `inspection_id` UUID,
    `worker_id` UUID,
    `device_id` UUID,
    `event_type` LowCardinality(String),
    `payload` String,
    `datetime` DateTime64
)
ENGINE=MergeTree
PRIMARY KEY (`inspection_id`, `datetime`);

CREATE TABLE inspections.materialized_start_events
(
	`inspection_id` UUID,
    `worker_id` UUID,
    `worker_path` Array(UUID),
    `device_id` UUID,
    `device_path` Array(UUID),
    `start_time` DateTime64
)
ENGINE=MergeTree
PRIMARY KEY (`inspection_id`, `start_time`)
;

PARTITION BY toYYYYMMDD(`start_time`)
TTL toYYYYMMDD(`start_time`) + INTERVAL 1 DAY DELETE;


CREATE MATERIALIZED VIEW inspections.materialize_start_event TO inspections.materialized_start_events
AS SELECT
	inspection_id,
	worker_id,
	JSONExtract(JSONExtract(replaceAll(payload, '\'', '"'), 'worker', 'String'), 'materialized_path', 'Array(UUID)') as worker_path,
	device_id,
	JSONExtract(JSONExtract(replaceAll(payload, '\'', '"'), 'device', 'String'), 'materialized_path', 'Array(UUID)') as device_path,
	`datetime` as start_time
FROM inspections.event_log WHERE event_type = 'START';


/* TODO: add TTL */
CREATE TABLE inspections.materialized_end_events
(
	`inspection_id` UUID,
    `end_time` DateTime64
)
ENGINE=MergeTree
PRIMARY KEY (`inspection_id`);

CREATE MATERIALIZED VIEW inspections.materialize_end_event TO inspections.materialized_end_events
AS SELECT
	inspection_id,
	`datetime` as end_time
FROM inspections.event_log WHERE event_type = 'END';


CREATE TABLE inspections.materialized_inspections
(
	`inspection_id` UUID,
    `worker_id` UUID,
    `worker_path` Array(UUID),
    `device_id` UUID,
    `device_path` Array(UUID),
    `start_time` DateTime64,
    `end_time` DateTime64,
    `data` Array(String)
)
ENGINE=MergeTree
PRIMARY KEY (`inspection_id`, `end_time`); /* Do we need worker ID or something else here? */


CREATE MATERIALIZED VIEW inspections.materialize_inspection TO inspections.materialized_inspections
AS SELECT
	ee.inspection_id as `inspection_id`,
	se.worker_id as `worker_id`,
	se.worker_path as `worker_path`,
	se.device_id as `device_id`,
	se.device_path as `device_path`,
	se.start_time as `start_time`,
	ee.end_time as `end_time`,
	d.`data` as `data`
FROM inspections.materialized_end_events ee
JOIN (
	SELECT *
	FROM inspections.materialized_start_events se
	WHERE se.inspection_id IN (
		SELECT ee.inspection_id FROM inspections.materialized_end_events ee
	)
) as se ON se.inspection_id = ee.inspection_id
INNER JOIN (
	SELECT el.inspection_id, groupArray(payload) as `data`
	FROM inspections.event_log el
	WHERE
	el.inspection_id IN (SELECT ee.inspection_id FROM inspections.materialized_end_events ee)
	AND
		el.event_type = 'DATA'
	GROUP BY el.inspection_id
) as d ON d.inspection_id = ee.inspection_id
;


CREATE TABLE inspections.materialized_result_events
(
	`inspection_id` UUID,
	`result_time` DateTime64,
	`result` LowCardinality(String),
	`result_data` String
)
ENGINE=MergeTree
PRIMARY KEY `inspection_id`;

CREATE MATERIALIZED VIEW inspections.materialize_result TO inspections.materialized_result_events
AS SELECT
	inspection_id,
	`datetime` as `result_time`,
	JSONExtract(replaceAll(payload, '\'', '"'), 'result', 'String') as `result`,
	JSONExtract(replaceAll(payload, '\'', '"'), 'data', 'String') as `result_data`
FROM inspections.event_log
WHERE event_type = 'RESULT';



CREATE TABLE inspections.materialized_inspections_with_results
(
	`inspection_id` UUID,
    `worker_id` UUID,
    `worker_path` Array(UUID),
    `device_id` UUID,
    `device_path` Array(UUID),
    `inspection_start_time` DateTime64,
    `inspection_end_time` DateTime64,
    `data` Array(String),
    `result_time` DateTime64,
    `result` LowCardinality(String),
    `result_data` String
)
ENGINE=MergeTree
PRIMARY KEY (`inspection_end_time`, `worker_id`);


CREATE MATERIALIZED VIEW inspections.materialize_inspections_with_results TO inspections.materialized_inspections_with_results
AS SELECT
	inspection_id,
	ins.`worker_id`,
	ins.`worker_path`,
	ins.`device_id`,
	ins.`device_path`,
	ins.`start_time` as `inspection_start_time`,
	ins.`end_time` as `inspection_end_time`,
	ins.`data` as `data`,
	result_time,
	`result`,
	result_data
FROM inspections.materialized_result_events mre
INNER JOIN (
	SELECT *
	FROM materialized_inspections mi
	WHERE mi.inspection_id IN (SELECT mre.inspection_id  FROM materialized_result_events mre)
) as ins
ON ins.inspection_id = mre.inspection_id;


SET stream_like_engine_allow_direct_select = 1;
select * from inspections.kafka_stream ks;
