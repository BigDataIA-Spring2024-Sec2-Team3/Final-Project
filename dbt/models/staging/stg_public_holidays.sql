{{ 
    config(
        materialized='view'
        ) 
        
}}

with public_holidays as(

    SELECT GEO_ID,
        ISO_ALPHA2,
        DATE,
        HOLIDAY_NAME,
        SUBDIVISION,
        IS_FINANCIAL

    FROM {{ source('public_holidays','public_holiday_calendar') }}
    WHERE GEO_ID = 'country/USA' 
        AND IS_FINANCIAL = TRUE
        AND DATE>'2020-03-11' and DATE<GETDATE()
)

SELECT * FROM public_holidays
