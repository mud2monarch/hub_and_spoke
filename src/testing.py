import polars as pl

# (pl.read_parquet("data/*.parquet").write_parquet("data/09_2025_rides.parquet"))
print(pl.read_parquet("data/09_2025_rides.parquet").describe())
