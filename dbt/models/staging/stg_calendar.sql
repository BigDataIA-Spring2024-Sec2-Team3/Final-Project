{{ 
    config(
        materialized='view'
        ) 
        
}}

with public_holidays as(

    SELECT Period_start_date AS DATE1, ANNUAL_PERIOD AS YEAR1

    FROM {{ source('calendar','calendar_index') }}
    WHERE Period_start_date>'2008-01-01' and Period_start_date < GETDATE()
        AND Calendar_name = 'Day'
    ORDER BY Period_start_date DESC
)

SELECT * FROM public_holidays
