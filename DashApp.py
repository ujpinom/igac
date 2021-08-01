import numpy as np
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import time
import copy
import streamlit.components.v1 as components
import folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import geopandas as gpd

@st.cache(allow_output_mutation=True)
def load_image(image_file):
    img = Image.open(image_file)
    img = img.convert('RGB')
    return img



st.set_page_config(
    page_title="IGAC-PROJECT",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

def mapa():
    df = px.data.election()
    geojson = px.data.election_geojson()

    fig = px.choropleth_mapbox(df, geojson=geojson, color="Bergeron",width=1300,height=400,
                               center={"lat": 4.570868, "lon": -74.297333},
                               mapbox_style="carto-positron", zoom=5)
    fig.update_layout(margin={"r": 2, "t": 0, "l": 1, "b": 2})
    return fig


with st.sidebar:
    st.markdown('## Select a source')
    option = st.selectbox(
        '',
        ('OCR', 'Open Street Maps', 'Google Maps (Optional)'))
    st.write('You selected:', option)

    st.write('If OCR is selected you must load an new image.')

    if option == 'OCR':
        image_file = st.file_uploader("", type=['png', 'jpeg', 'jpg'])

    st.markdown('---')
    st.subheader('Filters')
    photo_id = st.selectbox('Select Photo ID', ('OCR', 'Open Street Maps', 'Google Maps (Optional)'))
    seleted_class = st.selectbox('Select Class', ('OCR', 'Open Street Maps', 'Google Maps (Optional)'))
    seleted_second_division = st.selectbox('Select Second Division',
                                           ('OCR', 'Open Street Maps', 'Google Maps (Optional)'))
    seleted_third_division = st.selectbox('Select Third Division',
                                          ('OCR', 'Open Street Maps', 'Google Maps (Optional)'))

st.title('IGAC DASHBOARD (SE PUEDE PONER OTRA COSA)')

st.write('Visualización de datos de fuentes colaborativas')
fig=mapa()
st.write(fig)

info_DF= pd.DataFrame(columns=['ID-Photo','Toponym','Class','Corregimiento 2nd division','Veredas 3rd division','latitud','Longitud'])
st.markdown('---')
st.dataframe(info_DF,1200, 100)
