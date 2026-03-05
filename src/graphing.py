from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import polars as pl
from PIL import Image

FIGURES_DIR = Path("centrality figures")
FIGURES_DIR.mkdir(exist_ok=True)

REQUIRED_COLUMNS = {"lon", "lat", "centrality", "station_id"}


def graph_centrality(
    df: pl.DataFrame,
    hour: int,
    hourly_rides: list[int],
) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.drop_nulls(subset=["lon", "lat"])
    time = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
    plt.rcParams["font.family"] = "Andale Mono"
    BG = "#1a1a2e"
    FG = "#e0e0e0"

    fig, (ax_map, ax_bar) = plt.subplots(
        2,
        1,
        figsize=(12, 12),
        gridspec_kw={"height_ratios": [4, 1]},
        facecolor=BG,
    )

    # Scatter map
    ax_map.set_facecolor(BG)
    ax_map.scatter(
        df["lon"].to_list(),
        df["lat"].to_list(),
        c=df["centrality"].to_list(),
        cmap="RdPu",
        s=10,
        alpha=0.8,
    )
    ax_map.set_aspect("equal")
    ax_map.set_axis_off()
    ax_map.text(
        0.01,
        0.98,
        "Citi Bike station use\nSeptember 2025 weekdays",
        transform=ax_map.transAxes,
        ha="left",
        va="top",
        fontsize="xx-large",
        color=FG,
    )

    # Bar chart
    ax_bar.set_facecolor(BG)
    colors = ["HotPink" if h == hour else "#444466" for h in range(24)]
    labels = [f"{h % 12 or 12}{'a' if h < 12 else 'p'}" for h in range(24)]
    ax_bar.bar(range(24), hourly_rides, color=colors)
    ax_bar.set_xticks(range(0, 24, 3))
    ax_bar.set_xticklabels(labels[::3], fontsize="large", color=FG)
    ax_bar.set_ylabel("Rides during month", fontsize="large", color=FG)
    ax_bar.tick_params(axis="y", labelsize="large", colors=FG)
    ax_bar.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f"{x / 1000:.0f}k")
    )
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.spines[["bottom", "left"]].set_color(FG)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / f"{hour:02d} - {time}.png", dpi=80)
    plt.close(fig)


def create_gif(
    output_name: str = "output.gif", duration: int = 900, offset: int = 0
) -> None:
    frames = sorted(FIGURES_DIR.glob("*.png"))
    frames = frames[offset:] + frames[:offset]
    images = [Image.open(f) for f in frames]
    images[0].save(
        FIGURES_DIR / output_name,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
    )
