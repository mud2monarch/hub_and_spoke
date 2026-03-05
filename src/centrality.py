import igraph as ig
import polars as pl


def get_in_degree(g: ig.Graph) -> pl.DataFrame:
    return pl.DataFrame({"station_id": g.vs["name"], "in_degree": g.degree(mode="in")})


def get_out_degree(g: ig.Graph) -> pl.DataFrame:
    return pl.DataFrame(
        {"station_id": g.vs["name"], "out_degree": g.degree(mode="out")}
    )


def get_pagerank(g: ig.Graph) -> pl.DataFrame:
    return pl.DataFrame(
        {"station_id": g.vs["name"], "pagerank": g.pagerank(directed=True)}
    )


def get_betweenness(g: ig.Graph) -> pl.DataFrame:
    return pl.DataFrame(
        {"station_id": g.vs["name"], "betweenness": g.betweenness(directed=True)}
    )
