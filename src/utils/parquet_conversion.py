import polars as pl

(
    pl.read_csv(
        "YOUR CSV HERE.csv",
        schema_overrides={
            "start_station_id": pl.String,
            "end_station_id": pl.String,
        },
    )
    .with_columns(
        pl.col("started_at").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.3f"),
        pl.col("ended_at").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.3f"),
        pl.col("rideable_type").cast(pl.Categorical),
        pl.col("member_casual").cast(pl.Categorical),
    )
    .write_parquet("YOUR PARQUET NAME HERE.parquet")
)
