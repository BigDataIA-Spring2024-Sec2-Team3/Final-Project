{{ 
    config(
        materialized='view'
        ) 
        
}}

with incidents as(

    SELECT 
        incident_datetime,
        incident_date,
        incident_time,
        incident_year,
        incident_day_of_week,
        report_datetime,
        row_id,
        incident_id,
        incident_number,
        report_type_code,
        report_type_description,
        incident_code,
        incident_category,
        incident_subcategory,
        incident_description,
        resolution,
        police_district,
        filed_online,
        cad_number,
        intersection,
        cnn,
        analysis_neighborhood,
        supervisor_district,
        supervisor_district_2012,
        latitude,
        longitude,
        point
    FROM {{ source('incident','incident_reports',) }}
)

SELECT * FROM incidents