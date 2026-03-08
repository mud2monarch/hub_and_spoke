import logging

import igraph as ig
import polars as pl
from PIL.ImageChops import offset

import centrality
from graphing import create_gif, graph_centrality_hourly
from weights import haversine_miles

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initial object construction
log.info("Loading all edges, vertices, and station info.")

all_edges: pl.LazyFrame = (
    pl.scan_parquet("data/09_2025_rides.parquet")
    .with_columns(
        (pl.col("ended_at") - pl.col("started_at")).alias("ride_duration"),
        haversine_miles(
            pl.col("start_lat"),
            pl.col("start_lng"),
            pl.col("end_lat"),
            pl.col("end_lng"),
            unit="miles",
        ).alias("trip_distance"),
    )
    .select(
        [
            "start_station_id",
            "end_station_id",
            "rideable_type",
            "member_casual",
            "started_at",
            "ended_at",
            "ride_duration",
            "trip_distance",
        ]
    )
    .drop_nulls(subset=["start_station_id", "end_station_id"])
)

vertices: pl.DataFrame = pl.DataFrame(
    pl.concat(
        [
            all_edges.select(pl.col("start_station_id").alias("station_id")),
            all_edges.select(pl.col("end_station_id").alias("station_id")),
        ]
    )
    .unique()
    .collect()
)

station_info: pl.DataFrame = (
    pl.read_csv(
        "data/station_information.csv", schema_overrides={"short_name": pl.String}
    )
    .select("short_name", "name", "capacity", "region_id", "lon", "lat")
    .with_columns(pl.col("short_name").alias("station_id"))
)
