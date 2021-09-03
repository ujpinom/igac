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
import Chaparral
import psycopg2 as pg2


###Estilos de color para los poligonos
style1 = {'fillColor': '#CD200B ', 'color': '#CD200B '}
style2 = {'fillColor': '#00FFFFFF', 'color': '#00FFFFFF'}

### Distintos tipos de clase para los topónimos identificados
clases = ['TODO','ALTO', 'ARROYO', 'CASERÍO', 'CAÑADA', 'CAÑO', 'CERRO', 'CHORRO',
          'CIÉNAGA', 'CUCHILLA', 'HACIENDA', 'INSPECCIÓN DE POLICÍA', 'ISLA',
          'LAGUNA', 'LOMA', 'MORRO', 'NOMBRE', 'PARAMO', 'PEÑÓN', 'PUNTA',
          'QUEBRADA', 'RAUDAL', 'RIO', 'RÍO', 'SABANA', 'SERRANÍA',
          'SIN CATEGORIZAR', 'SITIO', 'VEREDA', 'ZANJA', 'ZANJÓN']

##### credential to connect to  the database in AWS
database='postgres'
host='ls-52e8d6e6954df847f43dfed612cffff918fd05d2.ce51052aqdsa.us-east-1.rds.amazonaws.com'
user='dbmasteruser'
password='0+Gor71OC-[^8!%vvflRnqW35!G;Jbb['

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

## Inicia el proceso para la extración de los toponimos y sus respectivas bounding boxes
@st.cache(allow_output_mutation=True)
def azure_process(read_image):
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
    fig = folium.Map(location=[lat,long], zoom_start=12, width=width, height=height,tiles="stamenterrain")
    return fig


def get_image_download_link(img,filename,text):
    '''
    Retorna un link para descargar la imagen ya procesada.
    '''
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href =  f'<a href="data:file/txt;base64,{img_str}" download="{filename}">{text}</a>'
    return href


@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_query_results(sql):
    '''
    Recibe un sentecia SQL, se conecta a la base de datos y luego retorna el resultado de la sentencia SQL como un
    objecto de tipo DataFrame
    '''

    # Connect to the PostgreSQL database server
    with pg2.connect(host=host,
                          port='5432',
                          database=database,
                          user=user,
                          password=password) as conn:

        # Execute query and return results as a pandas dataframe
        df = pd.read_sql(sql, conn, index_col=None)
    return df



def download_link(object_to_download, download_filename, download_link_text):
    '''
    Retorna un link para descargar la información procesada en formato csv.
    '''
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

#-------- Porción de código dedicado a la barra lateral del DashBoard-----#
####                                                                #####
#--------------------------------------------------------------------------#


with st.sidebar: ### Columna lateral de control
    title_image= load_image('LOGO_IGAC.png')  ## Carga el logo del Dash
    width,hei= title_image.size
    title_image=title_image.resize((int(width),int(hei/1.5)))
    st.image(title_image)
    st.title('Seleccione una fuente')
    option = st.selectbox('',('Chaparral', 'Open Street Maps', 'Text Detection')) # Se selecciona uno de los 3 principales procesos
    st.write('Usted seleccionó:', option)

    #Se seleccionó la extración de topónimos de una imágen
    if option == 'Text Detection':
        image_file = st.file_uploader("", type=['png', 'jpeg', 'jpg']) ## Carga la imagen a la cual se aplicará el OCR
        flight_input = st.text_input("Ingrese el número de vuelo", 'C-1857')## Get the flight number from the user
        photo_input = st.text_input("Ingrese el número de la foto", '202') ### Get the photo number from the user
        iniciar_proceso_OCR = st.sidebar.button(label='Compute')  ## Boton para iniciar el proceso OCR.

    #Se seleccionó la opción Chaparral, por lo que toda la información exclusiva de Chaparral es obtenida pare efectos de filtrado
    if option == 'Chaparral':
        ##Sentencia SQL para obtener toda la información contenida en la tabla chaparralocr
        sql_ocr = '''select * from chaparralocr'''
        ##Sentencia SQL para obtener toda la información contenida en la tabla chaparralquadrants
        sql_cuadrante='''select * from chaparralquadrants'''

        image_file=None
        iniciar_proceso_OCR=False
        st.write('Conectando con la base de datos...')
        photo_ids='An error occured'
    #    cursor= db_connection.connect_db(database=database,host=host,user=user,password=password)
        igacocr_df=get_query_results(sql_ocr) ## Contiene toda la info OCR de chaparral

        igacocr_df.columns = ['Photo-id', 'Toponimo', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'Long', 'Lat','Clase',
                          'Vereda',
                          'point']  ## Renombra cada una de las columnas de la tabla chaparralocr ahora convertida a dataframe

        #El dataframe anterior contiene elementos nulos,los cuales son elementos no categorizados.
        igacocr_df.fillna('SIN CATEGORÍA', inplace=True)

        #Se obtiene cada una de las veredas ordendas alfabeticámente, las cuales se usaran posteriormente como filtro.
        veredas = igacocr_df[['Vereda']].sort_values(by='Vereda')['Vereda'].unique()

        veredas_df= Chaparral.leer_veredas_chaparral()  ### Contiene cada uno de los puntos de las veredas de Chaparral
        cuadrants_dir_df= get_query_results(sql_cuadrante)
        st.markdown('---')
        st.write('Si el siguiente checkbox es seleccionado, usted podrá filtrar toda la información de chaparral por clases.'
                'En caso contrario la información será filtrada a través de la selección de una vereda y su respectiva foto.')
        all_info = st.checkbox('Mostrar toda la información')

        ##Diferentes filtros para trabajar sobre la información de Chaparral.
        st.markdown('# Filtros')
        if all_info:
            seleted_class = st.selectbox('Seleccione una clase', clases[1:])
        else:
            seleted_second_division = st.selectbox('Seleccione una vereda',
                                                   veredas)
            photo_ids = igacocr_df.loc[igacocr_df['Vereda'] == seleted_second_division, ['Photo-id']][
                'Photo-id'].unique()
            photo_id = st.selectbox('Seleccione una foto', photo_ids)

    #Se seleccionó la opción que extrae toda la información de Chaparral obtenida por medio de Open Street Maps
    if option == 'Open Street Maps':  ### Acciones para la pestaña OSM
        sql_osm='''select * from chaparralosm'''
        image_file = None
        iniciar_proceso_OCR = False
        st.write('Conectando con la base de datos...')
  #      cursor = db_connection.connect_db(database=database, host=host, user=user, password=password)
        st.markdown('---')
        st.markdown('# Filtros')
        chaparralosm= get_query_results(sql_osm)
        clases=np.array(chaparralosm.iloc[:, 37].value_counts().index)
        seleted_class = st.selectbox('Seleccione una clase', clases[1:])


st.title('GEOTEXT DASHBOARD') ## DashBoard title
col1, col2= st.columns((1,0.9)) ### Dashboard layout ( two columns: one for showing the map and the another for showing images)


### ----------- -------------Text Detection---------------------------------------------------------------
#--------------------------------------------------------------------------------------------
if iniciar_proceso_OCR and image_file is not None and option == 'Text Detection' and photo_input.isnumeric():

    ## Inicializa el proceso OCR a través de la API Read de Azure y retorna un DataFrame con los topónimos dectectados y sus respectivos puntos
    # que conforman la bounding box
    df, status, rectangles = azure_process(image_file)

    # Se le aplica a los topónimos detectados una serie de pasos con el propósito de obtener la información más relevante
    df = text_cleance.limpieza_text_detected(df)

    ## Se lee el archivo que contiene los números de vuelos, número de foto y las respectivas coordenadas abarcadas por la foto cargada
    all_country = gpd.read_file("Cob_Clasificacion_Analoga.json", driver="GeoJSON")

    vuelo = flight_input  # all_country['No_Vuelo']
    foto = int(photo_input)  # all_country['No_foto']
    geoj = all_country
    im = load_image(image_file)
    w = im.width
    h = im.height

    #Se obtienen las coordenadas aproximadas de cada uno de los topónimos identificados previamente. También se obtiene el poligono que da forma al
    # territorio de Chaparral
    info_DF,lat,long,poligono= getting_coordenates.get_coordenates(df, vuelo, foto, geoj, w, h)
    info_DF ['ID-Photo']=image_file.name
    info_DF .drop(['0','1'],axis=1,inplace=True)
    st.markdown('---')
    st.subheader('Tabla con los topónimos detectados y sus coordenadas.')
    st.table(info_DF)

    ## Las siguientes cinco líneas de código están relacionadas con la preparación de la información para su posterior descargue
    name_csv=image_file.name.split('.')[0]
    name_df =f'{name_csv}.csv'
    tmp_download_link = download_link(info_DF, name_df, 'Click here to download your data!')
    st.markdown('---')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

    m=mapa(lat,long,width=580,height=500)
    folium.GeoJson(poligono,name='chaparral_photo').add_to(m) ## Se adiciona el poligono de chaparral al folium

    # Agrega marcadores al mapa, los cuales se ubican en la posición en la que fue detectado el topónimo. Cada marcador contiene el topónimo identificado,
    # así como sus respectivas coordenadas
    for row in info_DF.index:
        lat=info_DF.loc[row,'lat_text']
        long=info_DF.loc[row,'lon_text']
        pop_up=info_DF.loc[row,'Toponym']
        text_marker=f'Topónimo: {pop_up}\nLat: {lat}\nLong: {long}'
        folium.Marker(
            location=[lat, long],
            popup=text_marker,
            icon=folium.Icon(color="green"),
        ).add_to(m)

    # Se muestra el mapa en la columna 1.
    with col1:
        st.write('Visualización de datos en fuentes colaborativas')
        folium_static(m)

    ## En la columna 2 se muestra la imágen cargada con cada uno de los topónimos identificados rodeados por rectángulos rojos
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

    ## Las siguientes tres líneas de código tienen que ver con el proceso para descargar la imágen ya procesada
    name_img=nname_image
    tmp_download_link_im = get_image_download_link(fig, name_img, 'Click here to download your image!')
    st.markdown(tmp_download_link_im, unsafe_allow_html=True)

## No inicia el proceso OCR porque no se ha cargado una imágen o el número de vuelo ingresado no es de tipo entero
else:
    st.sidebar.write('Revise si ha cargado una imágen ó si el número de la foto  es de tipo entero.')


### ----------- Chaparral-------------------
#------------------------------------------------
if option =='Chaparral' and  not all_info:
    dir_photo=''# df.loc[df['photo-name']==photo_id,'s3-dir'].values[0]
    polygon_chaparral= Chaparral.leer_chaparral_polygon() # Retorna el poligono de Chaparral
    f = veredas_df.loc[veredas_df['Veredas'] == seleted_second_division, :]### Contiene las coordenadas de la vereda seleccionada
    polygon_vereda= Chaparral.polygon_vereda_seleccionada(f)  ## Retorna el poligono que delimita el territorio de la vereda seleccionada
    mapa_chaparral = mapa(3.7728555555591194, -75.57493008952609, width=580, height=500) ## Crea un nuevo mapa centrado en Chaparral

    ## Se carga la imagen desde AWS S3 correspondiente al nombre de la foto seleccionado, así como su información más importante
    im_s3,mapa_chaparral,info_impo=getting_coordenates.dibujar_bounding_boxes(ocr_df=igacocr_df,dir_df=cuadrants_dir_df,photo_id=photo_id,mapa=mapa_chaparral)

    ## Se muestra el mapa en la columna 1, el cual contiene el poligono de Chaparral, el poligono de la veredad seleccionada y cada uno de los marcadores
    ## correspodientes a los topónimos identificados en la respectiva imágen.
    with col1:
        st.write('Visualización de datos en fuentes colaborativas')

        folium.GeoJson(polygon_chaparral,
                       name='chaparral'
                       ).add_to(mapa_chaparral)
        folium.GeoJson(polygon_vereda,
                       name='chaparral',style_function=lambda x:style1
                       ).add_to(mapa_chaparral)
        folium_static(mapa_chaparral)

    ## Muestra la imágen que se extrajo de S3
    with col2:
        st.write(f'Image from S3: {photo_id}')
        st.image(im_s3)

    ## Descargar la información en formato csv. Descargar la imágen procesada.
    name_df = f'{photo_id}.csv'
    name_photo=f'{photo_id}.png'
    tmp_download_link = download_link(info_impo, name_df, 'Click here to download your data!')
    tmp_download_link_photo = get_image_download_link(im_s3, name_photo, 'Click here to download your photo!')
    st.markdown('---')
    st.table(info_impo)
    st.markdown('---')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

    st.markdown(tmp_download_link_photo, unsafe_allow_html=True)


## Se dispone de toda la información  de Chaparral, con el propósito de ser filtrada en base a las clases identificadas (quebrada, paramo, vereda...)
elif option =='Chaparral' and   all_info:
    polygon_chaparral = Chaparral.leer_chaparral_polygon()

    mapa_chaparral = mapa(3.7728555555591194, -75.57493008952609, width='100%', height='100%')
    folium.GeoJson(polygon_chaparral,
                   name='chaparral'
                   ).add_to(mapa_chaparral)
    mapa_chaparral,info_impo=getting_coordenates.get_all_info(mapa_chaparral,igacocr_df,seleted_class)
    folium_static(mapa_chaparral)
    name_df=f'{seleted_class}.csv'
    tmp_download_link = download_link(info_impo, name_df, 'Click here to download your data!')
    st.markdown('---')
    st.table(info_impo)
    st.markdown('---')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

### ----------- Open Street Maps-------------------
#--------------------------------------------------

if option == 'Open Street Maps':
    polygon_chaparral = Chaparral.leer_chaparral_polygon()  ## Poligono de Chaparral

    mapa_chaparral = mapa(3.7728555555591194, -75.57493008952609, width='100%', height='100%')

    folium.GeoJson(polygon_chaparral,
                   name='chaparral'
                   ).add_to(mapa_chaparral)

    ## Retorna el mapa de chaparral con los marcadores correspondientes a la clase selecionada. También retorna un DataFrame con toda esta información
    ## para luego ser descargada en formato csv.
    mapa_chaparral, info_impo = getting_coordenates.get_info_osm(mapa_chaparral, chaparralosm, seleted_class)

    st.write('Visualización de datos en fuentes colaborativas')
    name_df = f'{seleted_class}.csv'
    tmp_download_link = download_link(info_impo, name_df, 'Click here to download your data!')
    folium_static(mapa_chaparral)
    st.markdown('---')
    st.table(info_impo)
    st.markdown('---')
    st.markdown(tmp_download_link, unsafe_allow_html=True)
