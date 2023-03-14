CREATE DATABASE inspections ON CLUSTER '{cluster}';

/* Создаем таблицу для хранения данных */
CREATE TABLE inspections.inspections ON CLUSTER 'data-shards'
(
    `inspection_id` UUID,
    `worker_id` UUID,
    `worker_path` Array(UUID),
    `device_id` UUID,
    `device_path` Array(UUID),
    `start_time` DateTime64,
    `end_time` DateTime64,
    `data` String,
    PROJECTION search_inspections_projection
    (
        SELECT `end_time`, `worker_id`
        ORDER BY (`worker_id`, `end_time`)
    ),
    PROJECTION search_by_date_and_path
    (
        SELECT `end_time`, `worker_path`
        ORDER BY (`worker_path`, `end_time`)
    )
)
ENGINE=ReplicatedReplacingMergeTree('/tables/{shard}/inspections', '{replica}')
PRIMARY KEY (`end_time`, `inspection_id`)
ORDER BY (`end_time`, `inspection_id`)
PARTITION BY toYYYYMM(`end_time`);

/* Создаем распреденную таблицу для доступа */
CREATE TABLE inspections.inspections_distributed ON CLUSTER coordinators
(
	`inspection_id` UUID,
    `worker_id` UUID,
    `worker_path` Array(UUID),
    `device_id` UUID,
    `device_path` Array(UUID),
    `start_time` DateTime64,
    `end_time` DateTime64,
    `data` String
)
ENGINE = Distributed('data-shards', inspections, inspections, xxHash64(`inspection_id`));
/*
 * используем xxHash64 потому что он самый быстрый(http://cyan4973.github.io/xxHash/),
 * а нам просто нужно что бы записи с одинаковым inspections_id попадали на одну и ту же шарду,
 * чтобы работало удаление повторов.
 */


/*
 * Секция импорта данных
 */
 INSERT INTO inspections.inspections_distributed
SELECT
	`inspection_id`,
    `worker_id`,
    `worker_path`,
    `device_id`,
    `device_path`,
    `start_time`,
    `end_time`,
    `data`
FROM s3(
	'https://storage.yandexcloud.net/dfalko-testing-files/materialized_inspections_80kk.csv.lz4',
	'CSV',
	'inspection_id UUID, worker_id UUID, worker_path Array(UUID), device_id UUID, device_path Array(UUID), start_time DateTime64, end_time DateTime64, data String'
);


INSERT INTO inspections.inspections_distributed
SELECT
	generateUUIDv4(`end_time`) as `inspection_id`,
    `worker_id`,
    `worker_path`,
    `device_id`,
    `device_path`,
    `start_time` - INTERVAL 64 DAY,
    `end_time` - INTERVAL 64 DAY,
    `data`
FROM s3(
	'https://storage.yandexcloud.net/dfalko-testing-files/materialized_inspections_80kk.csv.lz4',
	'CSV',
	'inspection_id UUID, worker_id UUID, worker_path Array(UUID), device_id UUID, device_path Array(UUID), start_time DateTime64, end_time DateTime64, data String'
);



/*
 *  Экспорт осмотров в S3
 */
INSERT INTO FUNCTION s3('https://storage.yandexcloud.net/dfalko-testing-files/materialized_inspections_30kk.csv.lz4', 'YCAJEcDZIBbF9i5zQIqVouyP3', 'YCN8M6V3rHLhrCdDC84znxgDhTHA5Tc7zXhEevUU', 'CSV')
SELECT * FROM inspections.inspections_distributed LIMIT 30000000;


INSERT INTO FUNCTION s3(
	'https://storage.yandexcloud.net/dfalko-testing-files/inspections/inspections_{_partition_id}.csv',
	'YCAJEcDZIBbF9i5zQIqVouyP3',
	'YCN8M6V3rHLhrCdDC84znxgDhTHA5Tc7zXhEevUU',
	'CSV'
)
PARTITION BY xxHash64(`worker_id`) % 10
SELECT * FROM inspections.inspections_distributed LIMIT 30000000;


/*
 * Настройки
 */
ALTER USER admin SETTINGS max_threads = 1, use_uncompressed_cache = 1 ON CLUSTER '{cluster}';
ALTER USER admin SETTINGS max_threads = 16, use_uncompressed_cache = 1 ON CLUSTER 'data-shards';

SELECT *
FROM system.settings
WHERE name = 'max_threads' or name = 'use_uncompressed_cache';


/*
 * Словарь
 */
CREATE DICTIONARY inspections.workers_dictionary_file ON CLUSTER '{cluster}'
(
    `id` UUID,
    `fio` String,
    `drivers_license` String,
    `active` Boolean,
    `organization_unit_id` UUID
)
PRIMARY KEY `id`
SOURCE(HTTP(url 'https://storage.yandexcloud.net/dfalko-testing-files/workers.csv' format 'CSV'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED())
;

INSERT INTO FUNCTION s3('https://storage.yandexcloud.net/dfalko-testing-files/inspections_month_fio.csv', 'YCAJEcDZIBbF9i5zQIqVouyP3', 'YCN8M6V3rHLhrCdDC84znxgDhTHA5Tc7zXhEevUU', 'CSV')
select
	inspection_id,
	worker_id,
	worker_path,
	device_id,
	device_path,
	start_time,
	end_time,
	data,
	dictGetOrNull('inspections.workers_dictionary_file', 'fio', tuple(worker_id))
from inspections.inspections_distributed
LIMIT 30000000;


SELECT
	worker_id as id,
	groupArray(10)(
		array(
			toString(inspection_id),
			toString(worker_id),
			toString(worker_path),
			toString(device_id),
			toString(device_path),
			toString(start_time),
			toString(end_time),
			data
		)
	)
FROM inspections.inspections
GROUP BY worker_id
LIMIT 10
;
