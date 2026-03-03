import polars as pl

(
    pl.read_parquet("data/2025_09_rides.parquet")
    .group_by("end_station_id")
    .agg(pl.len().alias("count"))
    .sort("count", descending=True)
    .write_csv("data/destination_counts.csv")
)
