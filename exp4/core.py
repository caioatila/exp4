# AUTOGENERATED! DO NOT EDIT! File to edit: ..\00_core.ipynb.

# %% auto 0
__all__ = ['geo2buffer', 'load_relato', 'replace_val', 'get_date', 'connect_db', 'load_db', 'query2gdf']

# %% ..\00_core.ipynb 5
from pathlib import Path
import pandas as pd
import geopandas as gpd
import sqlite3
import datetime
import numpy as np
import gc


from tathu.io import spatialite
from tathu.constants import KM_PER_DEGREE

# %% ..\00_core.ipynb 6
def geo2buffer(row, buffer=20):
        
    """
    Adds an approximate buffer of inclusion around the point geometry of a GeoDataFrame row.

    Args:
        Buffer in KM
        Defaults to 20 Km
    """

    ds = (row["dx_km"] + buffer) / KM_PER_DEGREE
    
    return row.geometry.buffer(ds)

# %% ..\00_core.ipynb 7
def load_relato(pth):
    """
     Load the Relatos dataset as a geopandas dataframe
    """

    df_relatos = pd.read_csv(pth,
                         parse_dates={"date_time": ["data", "utc"]},
                         date_parser= lambda dcol: pd.to_datetime(f"{dcol.split(' ')[0]} {dcol.split(' ')[1].zfill(4)}", format="%Y%m%d %H%M", exact=True),
                         encoding="ISO-8859-1")

    df_relatos = df_relatos[df_relatos.tipo == "GRA"]

    gdf_relatos = gpd.GeoDataFrame(df_relatos,
                                geometry=gpd.points_from_xy(df_relatos.lon, df_relatos.lat),
                                crs="EPSG:4326")
    



    # Buffer points
    gdf_relatos["buffer"] = gdf_relatos.apply(geo2buffer, axis=1)
    return gdf_relatos

# %% ..\00_core.ipynb 8
def replace_val(df_set, uf_name, nested_dict):
    """
    Replace values in a dataframe based on a nested dictionary. Useful for correcting municipalities names
    """

    df_set.loc[df_set["uf"]==uf_name] = df_set.loc[df_set["uf"]==uf_name].replace(nested_dict)
    return df_set

# %% ..\00_core.ipynb 10
def get_date(db_file, date_col="date_time"):
    """ 
    Returns the start and end dates of a database file.

    Args:   
        db_file: Database file.
        date_col: Name of the date column in the database file.
    """
    return db_file[date_col].min(), db_file[date_col].max()

# %% ..\00_core.ipynb 11
def connect_db(dbname):
        
    """
    Create a connection to the database
    """
    conn = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.enable_load_extension(True)
    conn.load_extension('mod_spatialite')
    conn.execute("SELECT InitSpatialMetadata(1)")

    return conn

# %% ..\00_core.ipynb 12
def load_db(dbname, sql, params, geo_col):

    """
    Load the file
    """
    
    conn = connect_db(dbname)
    
    return gpd.GeoDataFrame.from_postgis(sql, conn, params=params, geom_col=geo_col)


# %% ..\00_core.ipynb 13
def query2gdf(conn, sql, params, geo_col):

    """
    Receives a query to perform and returns a GeoDataFrame of the results
    """
    
    return gpd.GeoDataFrame.from_postgis(sql, conn, params=params, geom_col=geo_col)

