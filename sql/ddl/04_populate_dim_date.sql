USE DATABASE LAKEHOUSE_DB;
USE SCHEMA GOLD;


INSERT INTO dim_date (date_key, full_date, day_of_week, month, year, is_weekend)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT,
    d,
    DAYNAME(d),
    MONTH(d),
    YEAR(d),
    DAYOFWEEK(d) IN (0, 6)
FROM (
    SELECT DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY NULL) - 1, '2020-01-01'::DATE) AS d
    FROM TABLE(GENERATOR(ROWCOUNT => 4018))
) AS dates;

select *
from DIM_DATE;