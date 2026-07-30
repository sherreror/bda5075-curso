TODO: crea aquí un test SINGULAR llamado puntuacion_sospecha_en_rango.sql que devuelva
las filas con puntuacion_sospecha < 0 o puntuacion_sospecha > 500 (deben ser 0 para pasar).
Ejemplo de estructura:
  select * from {{ ref('stg_alertas') }} where ...
