# IGAC DASHBOARD

La finalidad de este proyecto es proporcionar una forma concisa de interactuar con la información (DashBoard) obtenida por medio de diferentes fuentes. Por la naturaleza de los 
datos, la parte visual juega un papel muy importante en el correcto entendimiento de los mismos, por lo que la aplicación hace especial enfásis en la parte visual.

El DashBoard está compuesto por tres funcionalidades básicas: extracción de texto de una imagen, manipulación de la  información del caso de estudio (municipio de Chaparral) y 
manipulación de la iformación obtenida de terceros (Open Street Maps). A continuación se discuten cada una de estas tres funcionalidades en más detalle.

### Extracción de texto.
En la barra lateral de la aplicación, en la sección de "Seleccione una fuente" seleccione la opción "Text Detection". Para ello deberá cargar la imágen de interés.
Adicionalmente deberá ingresar manualmente el número de vuelo y el número de la foto. Usualmente el nombre de la imágen contendrá toda esta información. Paso siguiente es 
presionar el botón "Compute" y esperar por los resultados. La información se mostrará en el mapa, en la imágen misma y en una tabla. Si se desea, puede descargar tanto la imagen
como la información en formato csv.

### Caso de estudio.

En la barra lateral de la aplicación, en la sección de "Seleccione una fuente" seleccione la opción "Chaparral".
Esta funcionalidad está enfocada en la manipulación exclusiva de la información procesada del municipio de Chaparral-Tolima. La infomación se puede filtrar a partir de la 
selección de una vereda del municipio y la imágen de interés perteneciente a dicha vereda. Por otro lado, también es posible filtrar la información solamente por clases 
(e.g. alto,arroyo,caserío, etc).

### Fuentes externas.
En la barra lateral de la aplicación, en la sección de "Seleccione una fuente" seleccione la opción "Open Street Maps".
Esta funcionalidad es muy parecida a la anterior, solamente difieren en la fuente de la información, en donde en este último caso la información es obtenida por medio de la API 
de Open Street Maps.


Todos los requerimientos para la correcta funcionalidad de la apliación están listados en el archivo requirements.txt. En la carpeta del proyecto ejecute el siguiente comando
para instalar todas las librerías y dependencias: **pip install -r requirements.txt**

La aplicación se ecuentra alojada en AWS y se puede ingresar a ella por medio del siguiente [link](http://geotext.ddns.net/).

Un especial agradeciemiento a : Santiago Andrés Hurtado Avella, Daniela Velásquez Ciro, Cristhian Londoño, Iván Alejandro Ortiz Cardona y Josefina Zakzuk quienes hicieron este 
proyecto posible.
