import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from weights import haversine_miles

plt.style.use("fast")

data: pl.DataFrame = (
    pl.read_parquet("data/2025_09_rides.parquet")
    .with_columns(
        (pl.col("ended_at") - pl.col("started_at"))
        .dt.total_minutes(fractional=True)
        .alias("ride_duration"),
        haversine_miles(
            pl.col("start_lat"),
            pl.col("start_lng"),
            pl.col("end_lat"),
            pl.col("end_lng"),
            unit="miles",
        ).alias("ride_distance"),
    )
    .select(
        [
            "rideable_type",
            "member_casual",
            "started_at",
            "ended_at",
            "ride_duration",
            "ride_distance",
        ]
    )
    .drop_nulls()
    # hard cap for outliers, unreturned bikes
    .filter(pl.col("ride_duration") < 180, pl.col("ride_distance") < 105_600)
    .filter(pl.col("ride_duration") > 1, pl.col("ride_distance") > 0.1)
)

ride_types = data["rideable_type"].unique().sort().to_list()
member_types = data["member_casual"].unique().sort().to_list()

fig, axes = plt.subplots(
    len(ride_types), len(member_types), sharex=True, sharey=True, layout="constrained"
)

x_bins = np.logspace(
    np.log10(data["ride_distance"].min()),  # type: ignore[arg-type] data are not None
    np.log10(data["ride_distance"].max()),  # type: ignore[arg-type] data are not None
    20,
)
y_bins = np.logspace(
    np.log10(data["ride_duration"].min()),  # type: ignore[arg-type] data are not None
    np.log10(data["ride_duration"].max()),  # type: ignore[arg-type] data are not None
    20,
)

for i, ride in enumerate(ride_types):
    for j, member in enumerate(member_types):
        ax = axes[i][j]
        subset = data.filter(
            pl.col("rideable_type") == ride, pl.col("member_casual") == member
        )
        h = ax.hist2d(
            subset["ride_distance"],
            subset["ride_duration"],
            bins=[x_bins, y_bins],
            cmap="RdPu",
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"{ride} / {member}")

fig.supxlabel("Trip distance (miles)")
fig.supylabel("Ride duration (minutes)")
fig.colorbar(h[3], ax=axes, label="Ride count")
plt.show()
