import folium
import geopandas as gpd
import webbrowser
import pandas as pd
import cv2 as cv
import os

def get_coordenates(df_img,vuelo,foto,geoj,w,h):
    row = geoj[(geoj['No_Vuelo'] == vuelo) & (geoj['No_foto'] == foto)]  # filtrando los datos de la foto

    west, south, east, north = row['geometry'].bounds.values[0,:]  # Aqui saca los limites de la foto
    for row in df_img.index:
        'longitudes'
        point_0 = float(df_img.loc[row, '0'])  # pixel 0 width - longitude
        lon_text = west + ((abs(west - east) / w) * point_0)
        'latitudes'
        point_1 = float(df_img.loc[row, '1']) # pixel 0 heigth - latitude
        lat_text = north - ((abs(north - south) / h) * point_1)

        df_img.loc[row, 'lon_text'] = lon_text.copy()  # Add calculated longitude
        df_img.loc[row, 'lat_text'] = lat_text.copy()  # Add calculated latitude

    return df_img,north,east