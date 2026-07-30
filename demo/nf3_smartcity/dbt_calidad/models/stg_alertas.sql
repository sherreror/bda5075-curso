-- El modelo de staging: lee el seed crudo. En un proyecto real, aquí irían
-- las transformaciones. Nosotros nos centramos en la CALIDAD del resultado.
select * from {{ ref('alertas_raw') }}
