import psycopg2 as pg2
import pandas as pd

photos_ids=('C-1974 F-240', 'C-2070 F-250', 'C-2070 F-252', 'M-1390 F-42286',
       'C-2071 F-006', 'C-2071 F-008', 'M-1379 F-39718', 'M-1379 F-39720',
       'C-2568_F-012', 'C-2568_F-014', 'C-1974 F-238', 'C-2407_F-166',
       'C-2407_F-168', 'C-2407_F-170', 'C-2568_F-034', 'C-2568_F-036',
       'M-1379_F-39722', 'C-2407_F-196', 'M-1379_F-39724', 'C-2071_F-010',
       'm-1359 f-37742', 'C-1256_F-362', 'C-1256_F-328', 'C-1256_F-360',
       'c-1891 f-076', 'C-2465_F-210', 'c-2070 f-264', 'M-1379_F-39726',
       'c-2070 f-262', 'c-1857 f-198', 'c-1857 f-200', 'c-1857 f-196',
       'c-2556 f-138', 'c-1857 f-202', 'c-1857 f-232', 'c-1857 f-234',
       'c-2284 f-076', 'c-2284 f-78', 'C-2284_F-074', 'c-1891 f-072',
       'c-1917 f-090', 'c-1917 f-092', 'c-1917 f-102', 'c-1857 f-226',
       'c-1917 f-100', 'c-1857 f-208', 'c-1857 f-206', 'c-1857 f-230',
       'c-1891 f-084', 'c-1857 f-192', 'c-1857 f-204', 'c-1857 f-158',
       'c-1857 f-194', 'c-1891 f-074', 'c-1891 f-086', 'c-1857 f-162',
       'c-1857 f-188', 'c-1857 f-190', 'c-1857 f-160', 'c-1841 f-016',
       'c-1857 f-156', 'c-1891 f-088')


def get_photos_ids():
    return photos_ids

def connect_db(database, host, user, password):
    conexiion = pg2.connect(database=database,
                            host=host, user=user,
                            password=password)
    cursor1 = conexiion.cursor()
    return cursor1
    # sql = '''select * from resources_info '''
    # try:
    #     cursor1.execute(sql)
    #     data = cursor1.fetchall()
    #     df = pd.DataFrame(data, columns=['ID', 'photo-name', 'extension', 's3-dir', 'type'])
    #     consulta = ['tif', 'jpg']
    #     photos_ids=tuple(df.loc[(df['extension'].isin(consulta)) & (df['type'] == 'aerofotografia'), ['photo-name']]\
    #                      .values.ravel())
    #     return df
    # except:
    #     cursor1.execute("ROLLBACK")
    #     return None

def extract_from_chaparralocr(cursor):
    sql = '''select * from chaparralocr'''
    cursor.execute(sql)
    data = cursor.fetchall()
    ver = pd.DataFrame(data)
    return ver


def extract_dir_cuandrants(cursor):
    sql = '''select * from chaparralquadrants'''
    cursor.execute(sql)
    data = cursor.fetchall()
    ver = pd.DataFrame(data)
    return ver


def extract_from_chaparralosm(cursor):
    sql = '''select * from chaparralosm'''
    cursor.execute(sql)
    data = cursor.fetchall()
    ver = pd.DataFrame(data)
    return ver
