
{{ 
    config(
        materialized='view'
        ) 
        
}}

WITH yearly as (
    SELECT
        count(row_id) as crimes,
        incident_year
    FROM {{ref('stg_incident')}}
    GROUP BY incident_year
    ORDER BY incident_year
)

SELECT * FROM yearly