-- Test SINGULAR: el índice de calidad del aire debe estar en [0, 500].
-- Un test de dbt es una consulta que devuelve las filas MALAS.
-- Si devuelve cero filas, el test pasa.
select *
from {{ ref('stg_alertas') }}
where aqi < 0 or aqi > 500
