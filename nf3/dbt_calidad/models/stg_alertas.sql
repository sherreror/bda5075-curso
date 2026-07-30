select * from read_parquet('{{ var("alertas", "../datos/raw/alertas.parquet") }}')
