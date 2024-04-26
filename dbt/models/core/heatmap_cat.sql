
{{ 
    config(
        materialized='view'
        ) 
        
}}

WITH main_map as (
    SELECT
        incident_category,
        count(row_id) as crimes,
        CAST(latitude AS FLOAT) as latitude,
        CAST(longitude AS FLOAT) as longitude

    FROM {{ref('stg_incident')}}
    WHERE latitude is not NULL 
            AND longitude is not NULL
            AND incident_date > '03/11/2020'
    GROUP BY incident_category,
        latitude,
        longitude
),
 ranked as (
    SELECT ROW_NUMBER() OVER(PARTITION BY incident_category ORDER BY crimes DESC) as RN, * 
    FROM main_map mmap
)

SELECT incident_category, crimes, latitude, longitude FROM ranked WHERE RN <= 15