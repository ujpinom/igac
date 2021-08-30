import folium
import geopandas as gpd
import webbrowser
import pandas as pd
import cv2 as cv
import os
from PIL import Image,ImageDraw
import streamlit as st
import requests as req
from io import BytesIO

def get_coordenates(df_img,vuelo,foto,geoj,w,h):
    row = geoj[((geoj['No_Vuelo'] == vuelo.upper()) | (geoj['No_Vuelo'] == vuelo.lower())) & (geoj['No_foto'] == foto)]  # filtrando los datos de la foto

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


def load_image(image_file):
    '''
    retorna imagen
    :param image_file: Dirección de la imagen a cargar
    :return: Imagen
    '''
    img = Image.open(image_file)
    img = img.convert('RGB')
    return img

##Dibuja los rectangulos sobre cada uno de los toponimos identificados
def draw(fig,rectangles):
    draw = ImageDraw.Draw(fig)
    for points in rectangles:
        x1, y1, x2, y2 = float(points[0]), float(points[1]), float(points[2]), float(points[3])
        draw.rectangle(((x1, y1), (x2, y2)), outline="red", width=3)
    return fig

def markers(map,marker):

    for points in marker:
        topo=float(points[0])
        long=float(points[1])
        lat=float(points[2])
        folium.Marker(
            location=[lat, long],
            popup=topo,
            icon=folium.Icon(color="green"),
        ).add_to(map)
    return map


def dibujar_bounding_boxes(ocr_df,dir_df,photo_id,mapa):

    ## Cambiar el nombre de las columnas para un manejo conveniente
    dir_df.columns = ['photo-id', 'c1', 'c2', 'c3', 'c4', 'dir']

    ocr_df['Long']=ocr_df['Long'].astype('float')
    ocr_df['Lat'] = ocr_df['Lat'].astype('float')

    rectangles=ocr_df.loc[ocr_df['Photo-id']==photo_id,['c0','c1','c4','c5']].values
    markers=ocr_df.loc[ocr_df['Photo-id']==photo_id,['Toponimo','Long','Lat','Clase']].values
    dir_aws=dir_df.loc[dir_df['photo-id'] == photo_id, 'dir'].values[0]
    info_impo=ocr_df.loc[ocr_df['Photo-id']==photo_id,['Photo-id','Toponimo','Long','Lat','Vereda','Clase']]
    response = req.get(dir_aws)
    im_s3 = load_image(BytesIO(response.content))
    im_s3= draw(im_s3,rectangles)

    for points in markers:
        long = float(points[1])
        lat = float(points[2])
        topo = f'Toponimo: {points[0]} \nClase: {points[3]}\nLat: {lat}\n  Long: {long}'
        folium.Marker(
            location=[lat, long],
            popup=topo,
            icon=folium.Icon(color="green"),
        ).add_to(mapa)

    return im_s3,mapa,info_impo


def get_all_info(mapa,ocr_df,clase):

        info_impo=ocr_df.loc[ocr_df['Clase']==clase,['Toponimo','Long','Lat','Clase','Photo-id']]
        info_impo['Long']=info_impo['Long'].astype('float')
        info_impo['Lat'] = info_impo['Lat'].astype('float')
        markers=info_impo.values

        for points in markers:
            long = float(points[1])
            lat = float(points[2])
            topo = f'Toponimo: {points[0]} \nClase: {points[3]}\nLat: {lat}\n  Long: {long}'
            folium.Marker(
                location=[lat, long],
                popup=topo,
                icon=folium.Icon(color="green"),
            ).add_to(mapa)

        return mapa,info_impo


def get_info_osm(mapa,ocr_df,clase):
    info_impo = ocr_df.loc[ocr_df['catalogo'] == clase, ['display_name', 'lon', 'lat', 'catalogo']]
    info_impo['lon'] = info_impo['lon'].astype('float')
    info_impo['lat'] = info_impo['lat'].astype('float')
    markers = info_impo.values

    for points in markers:
        long = float(points[1])
        lat = float(points[2])
        topo = f'Toponimo: {points[0]} \nClase: {points[3]}\nLat: {lat}\n  Long: {long}'
        folium.Marker(
            location=[lat, long],
            popup=topo,
            icon=folium.Icon(color="green"),
        ).add_to(mapa)

    return mapa, info_impo