import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from weights import haversine_miles

BG = "#1a1a2e"
FG = "#e0e0e0"
plt.rcParams["font.family"] = "Andale Mono"
plt.rcParams["figure.facecolor"] = BG
plt.rcParams["axes.facecolor"] = BG
plt.rcParams["text.color"] = FG
plt.rcParams["axes.labelcolor"] = FG
plt.rcParams["xtick.color"] = FG
plt.rcParams["ytick.color"] = FG

data: pl.DataFrame = (
    pl.read_parquet("data/09_2025_rides.parquet")
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
    .filter(pl.col("ride_duration") < 180, pl.col("ride_distance") < 20)
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
        ax.set_title(f"{ride} / {member}", color=FG)

fig.supxlabel("Trip distance (miles)", color=FG)
fig.supylabel("Ride duration (minutes)", color=FG)
cbar = fig.colorbar(h[3], ax=axes, label="Ride count")
cbar.set_label("Ride count", color=FG)
cbar.ax.yaxis.set_tick_params(color=FG)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
plt.show()
