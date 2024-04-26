
{{ 
    config(
        materialized='view'
        ) 
        
}}

WITH incidents AS(
    SELECT *
    FROM {{ref('stg_incident')}}
),
public_holidays AS(
    SELECT *
    FROM {{ref('stg_public_holidays')}}
),
main_map as (
    SELECT
        HOLIDAY_NAME,
        (count(row_id)) as crimes,
        CAST(latitude AS FLOAT) as latitude,
        CAST(longitude AS FLOAT) as longitude
    FROM incidents as i
        JOIN public_holidays as pb 
        ON i.incident_date = pb.date
    WHERE latitude is not NULL 
            AND longitude is not NULL
    GROUP BY HOLIDAY_NAME,
        latitude,
        longitude
),
 ranked as (
    SELECT ROW_NUMBER() OVER(PARTITION BY HOLIDAY_NAME ORDER BY crimes DESC) as RN, * 
    FROM main_map mmap
)

SELECT HOLIDAY_NAME, crimes, latitude, longitude FROM ranked WHERE RN <= 15