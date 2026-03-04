import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import igraph as ig
import polars as pl

from weights import haversine_miles

edges: pl.DataFrame = (
    pl.read_parquet("data/09_2025_rides.parquet")
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

vertices: pl.DataFrame = pl.concat(
    [
        pl.DataFrame(edges).select(pl.col("start_station_id").alias("station_id")),
        pl.DataFrame(edges).select(pl.col("end_station_id").alias("station_id")),
    ]
).unique()

g: ig.Graph = ig.Graph.DataFrame(
    edges.to_pandas(), vertices=vertices.to_pandas(), directed=True, use_vids=False
)

# Measure centrality

station_info = (
    pl.read_csv(
        "data/station_information.csv", schema_overrides={"short_name": pl.String}
    )
    .select("short_name", "name", "capacity", "region_id")
    .with_columns(pl.col("short_name").alias("station_id"))
)

station_ids = g.vs["name"]

centrality = pl.DataFrame(
    {
        "station_id": station_ids,
        "in_degree": g.degree(mode="in"),
        "out_degree": g.degree(mode="out"),
        "pagerank": g.pagerank(directed=True),
        "betweenness": g.betweenness(directed=True),
    }
)

q3: pl.DataFrame = centrality.join(station_info, on="station_id", how="left")

q3.sort("pagerank", descending=True).write_csv(
    "src/analyses/2025_09_centrality_measures.csv"
)
