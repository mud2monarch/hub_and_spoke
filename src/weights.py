import polars as pl

"""Calculate great-circle distance between two points using the haversine formula.

All arguments should be Polars expressions of dtype Float64 representing degrees.

Args:
    s_lat: Start latitude.
    s_lon: Start longitude.
    e_lat: End latitude.
    e_lon: End longitude.
    unit: Unit of distance ("miles", "kilometers", "meters", "feet").

Returns:
    A Float64 expression of distances in the specified unit.
"""


def haversine_miles(
    s_lat: pl.Expr,
    s_lon: pl.Expr,
    e_lat: pl.Expr,
    e_lon: pl.Expr,
    unit: str = "miles",
) -> pl.Expr:

    EARTH_RADIUS = {
        "miles": 3958.8,
        "kilometers": 6371.0,
        "meters": 6371000.0,
        "feet": 20902231.0,
    }
    radius = EARTH_RADIUS[unit]

    s_lat, s_lon, e_lat, e_lon = (
        s_lat.radians(),
        s_lon.radians(),
        e_lat.radians(),
        e_lon.radians(),
    )

    d_lat = e_lat - s_lat
    d_lon = e_lon - s_lon

    a = (d_lat / 2).sin().pow(2) + s_lat.cos() * e_lat.cos() * (d_lon / 2).sin().pow(2)

    return radius * 2 * a.sqrt().arcsin()
