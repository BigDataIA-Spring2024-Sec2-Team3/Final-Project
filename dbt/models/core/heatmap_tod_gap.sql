
{{ 
    config(
        materialized='view'
        ) 
        
}}

WITH main_map as (
    SELECT
        CASE
            WHEN (incident_time> TO_TIME('00:00:00') AND incident_time<= TO_TIME('6:00:00')) THEN 'Late Night'
            WHEN (incident_time> TO_TIME('6:00:00') AND incident_time<= TO_TIME('12:00:00')) THEN 'Morning'
            WHEN (incident_time> TO_TIME('12:00:00') AND incident_time<= TO_TIME('18:00:00')) THEN 'Afternoon'
            WHEN (incident_time>TO_TIME('18:00:00') AND incident_time<= TO_TIME('23:59:59')) THEN 'Evening'
        END AS TimeofDay,
        (count(row_id)) as crimes,
        CAST(latitude AS FLOAT) as latitude,
        CAST(longitude AS FLOAT) as longitude

    FROM {{ref('stg_incident')}}
    WHERE latitude is not NULL 
            AND longitude is not NULL
    GROUP BY TimeofDay,
        latitude,
        longitude
),
 ranked as (
    SELECT ROW_NUMBER() OVER(PARTITION BY TimeofDay ORDER BY crimes DESC) as RN, * 
    FROM main_map mmap
)

SELECT TimeofDay, crimes, latitude, longitude FROM ranked WHERE RN <= 15