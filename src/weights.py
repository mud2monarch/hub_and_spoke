import polars as pl

"""Calculate great-circle distance in miles between two points using the haversine formula.

All arguments should be Polars expressions of dtype Float64 representing degrees.

Args:
    s_lat: Start latitude.
    s_lon: Start longitude.
    e_lat: End latitude.
    e_lon: End longitude.

Returns:
    A Float64 expression of distances in miles.
"""
def haversine_miles(
    s_lat: pl.Expr,
    s_lon: pl.Expr,
    e_lat: pl.Expr,
    e_lon: pl.Expr,
) -> pl.Expr:

    EARTH_RADIUS = 3958.8

    s_lat, s_lon, e_lat, e_lon = s_lat.radians(), s_lon.radians(), e_lat.radians(), e_lon.radians()

    d_lat = e_lat - s_lat
    d_lon = e_lon - s_lon

    a = (d_lat / 2).sin().pow(2) + s_lat.cos() * e_lat.cos() * (d_lon / 2).sin().pow(2)

    return EARTH_RADIUS * 2 * a.sqrt().arcsin()
