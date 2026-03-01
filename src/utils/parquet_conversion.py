import polars as pl

(
    pl.read_csv("YOUR_CSV_HERE.csv")
    .with_columns(
        pl.col('started_at').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.3f"),
        pl.col('ended_at').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.3f"),
        pl.col('rideable_type').cast(pl.Categorical),
        pl.col('member_casual').cast(pl.Categorical)
    )
    # .head()
    .write_parquet("YOUR_PARQUET_FORMAT_HERE.parquet")
)
