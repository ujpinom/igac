import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon #to create Polygons and Points
import requests
import zipfile as zipfile
import io
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np

def leer_chaparral_polygon():
    '''
    Lee el archivo que contiene los puntos que conforman el poligono de Chaparral y retorna el poligono formado por estos puntos
    :return:
    '''
    cha = pd.read_csv(r'chaparral_poly.csv')
    lon_point_list = cha.lon_point_list.values
    lat_point_list = cha.lat_point_list.values
    polygon_geom = Polygon(zip(lat_point_list, lon_point_list))
    crs = {'init': 'epsg:4686'}  # 4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    return polygon

def leer_veredas_chaparral():
    '''
    Lee el archivo que contiene los poligonos de las veredas de Chaparral
    :return:
    '''
    df = pd.read_pickle(r'geo_veredas2.pkl')
    df = df.reset_index()
    df.columns = ['Veredas', 'Puntos']
    return df

def polygon_vereda_seleccionada(f):
    '''

    :param f:
    :return: Retorna el poligono de la vereda seleccinada
    '''
    index=f.index[0]
    lon_point_list=np.array(f['Puntos'][index])[:,1]
    lat_point_list=np.array(f['Puntos'][index])[:,0]
    polygon_geom = Polygon(zip(lat_point_list, lon_point_list))
    crs = {'init': 'epsg:4686'}  # 4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
    return polygon