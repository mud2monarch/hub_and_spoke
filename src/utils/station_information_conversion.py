import polars as pl

(
    pl.read_json("data/station_information.json")
    .unnest("data")
    .explode("stations")
    .unnest("stations")
    .select([
        'name',
        'short_name',
        'station_id',
        'lon',
        'lat',
        'region_id',
        'capacity',
    ])
    .with_columns(
        pl.col('region_id').cast(pl.Int64)
    )
    .write_csv("station_information.csv")
)
