import numpy as np
import base64
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import time
import geopandas as gpd
from streamlit_folium import folium_static
import folium
import text_cleance
import getting_coordenates
import db_connection
import requests as req
from io import BytesIO

##### credential to connect to  the database in AWS
host="igacproject.cbdjyxjidnrz.us-east-2.rds.amazonaws.com"
password="1xqIOnpQXlNDXNzVhLps"
user='uriel'
database='igac_project'


st.set_page_config(
    page_title="IGAC-PROJECT",
    page_icon="🌍",
    layout="wide",
  # initial_sidebar_state="expanded",
)



@st.cache(allow_output_mutation=True)
def load_image(image_file):
    '''
    retorna imagen
    :param image_file: Dirección de la imagen a cargar
    :return: Imagen
    '''
    img = Image.open(image_file)
    img = img.convert('RGB')
    return img


def azure_procces(read_image):
    subscription_key = "b7fd69cb2fb04870842aff9954560f3b"  # "PASTE_YOUR_COMPUTER_VISION_SUBSCRIPTION_KEY_HERE"
    endpoint = "https://igac.cognitiveservices.azure.com/"  # "PASTE_YOUR_COMPUTER_VISION_ENDPOINT_HERE"

    # Snippet client
    # Conect to compurter vision
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    df_images_result = pd.DataFrame(
        {'Toponym': [],'0':[],'1':[]})  ## Guarda los datos extraidos de la imagen en un dataframe
    read_response = computervision_client.read_in_stream(read_image, raw=True)
    # Get the operation location (URL with ID as last appendage)
    read_operation_location = read_response.headers["Operation-Location"]
    # Take the ID off and use to get results
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for the retrieval of the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            break
        st.sidebar.write('Waiting for result...')
        time.sleep(10)

    # Print results, line by line
    texto_identificado = []
    rectangle = []
    coordenada_1=[]
    coordenada_2 =[]

    if read_result.status == OperationStatusCodes.succeeded:
        status = 'OperationStatus: Succeeded'
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                texto_identificado.append(line.text)
                points = np.array(line.bounding_box)[[0, 1, 4, 5]]
                coordenada_1.append(points[0])
                coordenada_2.append(points[1])
                rectangle.append(points)

        df_images_result.Toponym = texto_identificado
        df_images_result['0']=coordenada_1
        df_images_result['1']=coordenada_2

        return df_images_result, status, rectangle
    else:
        status = 'OperationStatus: Something went wrong...'
        return df_images_result, status, rectangle

def mapa(lat,long,height='100%',width='90%'):
    '''
    Retorna un mapa centrado en el punto especificado
    :param lat: Latitud
    :param long: Longitud
    :return: Mapa centrado en los punto especificado
    '''
    fig = folium.Map(location=[lat,long], zoom_start=12, height=height,width=width)
    return fig


def download_link(object_to_download, download_filename, download_link_text):
    """
      Generates a link to download the given object_to_download.
      object_to_download (str, pd.DataFrame):  The object to be downloaded.
      download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
      download_link_text (str): Text to display for download link.
      Examples:
      download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
      """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


with st.sidebar: ### Columna lateral de control
    st.markdown('# Select a source')
    option = st.selectbox(
        '',
        ('Chaparral', 'Open Street Maps', 'Text Detection'))
    st.write('You selected:', option)


    if option == 'Text Detection':
        image_file = st.file_uploader("", type=['png', 'jpeg', 'jpg'])
        flight_input = st.text_input("Enter flight number", 'f-016')## Get the flight number from the user
        photo_input = st.text_input("Enter photo number", '328') ### Get the photo number from the user
        iniciar_proceso_OCR = st.sidebar.button(label='Compute')


    if option == 'Chaparral':
        image_file=None
        iniciar_proceso_OCR=False
        st.write('Connecting to Data Base...')
        photo_ids='An error occured'
        df= db_connection.connect_db(database,host,user,password)

        if df is not None:
            st.write('Successfully connected')
            photo_ids = db_connection.get_photos_ids()
        st.markdown('---')
        st.markdown('# Filters')
        photo_id = st.selectbox('Select Photo ID', photo_ids)
        seleted_class = st.selectbox('Select Class', ('Schools', 'Open Street Maps', 'Google Maps (Optional)'))
        seleted_second_division = st.selectbox('Select Second Division',
                                               ('Second division', 'Open Street Maps', 'Google Maps (Optional)'))
        seleted_third_division = st.selectbox('Select Third Division',
                                              ('Third division', 'Open Street Maps', 'Google Maps (Optional)'))

    if option == 'Open Street Maps':  ### Acciones para la pestaña OSM
        image_file = None
        iniciar_proceso_OCR = False
        photo_ids = db_connection.get_photos_ids()
        st.markdown('---')
        st.markdown('# Filters')
        photo_id = st.selectbox('Select Photo ID', photo_ids)
        seleted_class = st.selectbox('Select Class', ('Schools', 'Open Street Maps', 'Google Maps (Optional)'))
        seleted_second_division = st.selectbox('Select Second Division',
                                               ('Second division', 'Open Street Maps', 'Google Maps (Optional)'))
        seleted_third_division = st.selectbox('Select Third Division',
                                              ('Third division', 'Open Street Maps', 'Google Maps (Optional)'))



info_DF = pd.DataFrame(
    columns=['ID-Photo', 'Toponym', 'Class', 'Corregimiento 2nd division', 'Veredas 3rd division',
             'latitud', 'Longitud'])

st.title('IGAC DASHBOARD') ## DashBoard title
col1, col2= st.columns((1,0.9)) ### Dashboard layout ( two columns: one for showing the map and the another for showing images)


### ----------- Text Detection-------------------
#------------------------------------------------
if iniciar_proceso_OCR and image_file is not None and option == 'Text Detection':

    # Initialize the OCR proccess via Azure's API READ and returns a df with the detected text and coordinates.
    df, status, rectangles = azure_procces(image_file)
    df = text_cleance.limpieza_text_detected(df)

    all_country = gpd.read_file("Cob_Clasificacion_Analoga.json", driver="GeoJSON")

    vuelo = flight_input  # all_country['No_Vuelo']
    foto = int(photo_input)  # all_country['No_foto']
    geoj = all_country
    im = load_image(image_file)
    w = im.width
    h = im.height

    info_DF,lat,long = getting_coordenates.get_coordenates(df, vuelo, foto, geoj, w, h)
    info_DF ['ID-Photo']=image_file.name
    info_DF .drop(['0','1'],axis=1,inplace=True)
    st.markdown('---')
    st.table(info_DF.head(5))
    st.markdown('---')
    name_csv=image_file.name.split('.')[0]
    name_df =f'{name_csv}.csv'
    tmp_download_link = download_link(info_DF, name_df, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)
    m=mapa(lat,long)

    for row in info_DF.index:
        lat=info_DF.loc[row,'lat_text']
        long=info_DF.loc[row,'lon_text']
        pop_up=info_DF.loc[row,'Toponym']
        folium.Marker(
            location=[lat, long],
            popup=pop_up,
            icon=folium.Icon(color="green"),
        ).add_to(m)
    with col1:
        st.write('Visualización de datos en fuentes colaborativas')
        folium_static(m)
    with col2:
        nname_image = 'No image loaded'
        if option == 'Text Detection':
            if image_file is not None and iniciar_proceso_OCR:
                nname_image = image_file.name
                fig = load_image(image_file)
                draw = ImageDraw.Draw(fig)
                if status == 'OperationStatus: Succeeded':

                    for points in rectangles:
                        x1, y1, x2, y2 = float(points[0]), float(points[1]), float(points[2]), float(points[3])
                        draw.rectangle(((x1, y1), (x2, y2)), outline="red", width=3)

                st.write(f'Image ID: {nname_image}')
                st.image(fig)
            else:
                st.write(f'Image ID: {nname_image}')

### ----------- Chaparral-------------------
#------------------------------------------------
if option =='Chaparral':
    dir_photo= df.loc[df['photo-name']==photo_id,'s3-dir'].values[0]
    with col1:
        st.write('Visualización de datos en fuentes colaborativas')
        folium_static(mapa(3.72414, -75.4836))
    with col2:
        st.write(f'Image from S3: {photo_id}')
        response = req.get(dir_photo)
        st.image(load_image(BytesIO(response.content)))

    st.markdown('---')
    st.table(info_DF)
    if df is not None:
        st.table(df.loc[df['photo-name']==photo_id,:])

### ----------- Open Street Maps-------------------
#--------------------------------------------------

if option == 'Open Street Maps':
    st.write('Visualización de datos en fuentes colaborativas')
    folium_static(mapa(3.72414, -75.4836,width='100%'))
    st.markdown('---')
    st.table(info_DF)

