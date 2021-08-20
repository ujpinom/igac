import numpy as np
import re
import pandas as pd

def limpieza_text_detected(df2):
    f_numeros = df2['Toponym'].str.contains('1|2|3|4|5|6|7|8|9|0')  # Filtro para filas que contengan numeros
    df1 = df2.loc[f_numeros == False, :]
    df1['num_caract'] = df1['Toponym'].apply(lambda x: len(x))
    df1 = df1.loc[df1['num_caract'] > 2, :]
    df1['Toponym'] = df1['Toponym'].apply(lambda x: re.sub(r"[^a-zA-Z0-9]", " ", x))
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.lstrip())
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.rstrip())
    df1['num_caract'] = df1['Toponym'].apply(lambda x: len(x))
    df1 = df1.loc[df1['num_caract'] > 2, :]
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.upper())
    f = df1['Toponym'].str.contains('IGAC|PASTO|CAFE|PLACE')
    df1 = df1[~f]
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.replace('  ', ' '))  # 2
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.replace('   ', ' '))  # 3
    df1['Toponym'] = df1['Toponym'].apply(lambda x: x.replace('   ', ' '))  # 4
    df1['Toponym'] = df1['Toponym'].str.split()
    # Eliminación de letras sueltas

    # Lista de letras
    letras = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
              'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ',
              'Z', 'X', 'C', 'V', 'B', 'N', 'M']

    df1['Toponym'] = df1['Toponym'].apply(lambda x: [item for item in x if item not in letras])
    df1['Toponym'] = df1['Toponym'].str.join(',')
    df1['Toponym'] = df1['Toponym'].str.replace(',', ' ')
    # Eliminación de palabras de 3 caracteres o menos

    # Re calculo de caracteres
    df1['num_caract'] = df1['Toponym'].apply(lambda x: len(x))

    df = df1[df1['num_caract'] > 3]

    # Retoque de palabras con caracteres (5)

    # Re calculo de caracteres
    df['num_caract'] = df['Toponym'].apply(lambda x: len(x))

    df = df[df['num_caract'] > 5]

    # Eliminación de otras palabras incorrectas

    f = df['Toponym'].str.contains('KODAK SAFETY FILM|HDA LOS|SELEN MATIC MIS|LINDANAY|SEX CARGADO|CUITIV')
    df = df[~f]

    df.drop('num_caract', axis=1, inplace=True)
    return df