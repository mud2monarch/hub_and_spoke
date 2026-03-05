import sys
from pathlib import Path

from PIL.ImageChops import offset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import logging

import igraph as ig
import polars as pl

import centrality
from graphing import create_gif, graph_centrality
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

log.info("Moving on to iterative graph construction...")

weekday_edges = all_edges.filter(pl.col("started_at").dt.weekday() <= 5)

hourly_rides = [
    pl.DataFrame(
        weekday_edges.filter(pl.col("started_at").dt.hour() == h)
        .select(pl.len())
        .collect()
    ).item()
    for h in range(24)
]

for hour in range(24):
    log.info(f"Building graph for hour {hour:02d}:00...")
    hour_edges = pl.DataFrame(
        weekday_edges.filter(pl.col("started_at").dt.hour() == hour).collect()
    )

    g = ig.Graph.DataFrame(
        hour_edges.to_pandas(),
        vertices=vertices.to_pandas(),
        directed=True,
        use_vids=False,
    )

    pr = (
        centrality.get_in_degree(g)
        .rename({"in_degree": "centrality"})
        .join(station_info, on="station_id", how="left")
    )
    graph_centrality(pr, hour=hour, hourly_rides=hourly_rides)

create_gif(offset=5)
