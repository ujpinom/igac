import psycopg2 as pg2
import pandas as pd

photos_ids=('C-1974 F-240.jpg', 'C-2070 F-250.jpg', 'C-2070 F-252.jpg','M-1390 F-42286.jpg', 'M-1390 F-42288.jpg',
            'M-1390 F-42290.jpg','C-2071 F-006.jpg', 'C-2071 F-008.jpg', 'M-1379 F-39718.jpg',
       'M-1379 F-39720.jpg', 'C-2568_F-012.tif', 'C-2568_F-014.tif','C-1974 F-238.jpg', 'C-2407_F-166.tif', 'C-2407_F-168.tif',
       'C-2407_F-170.tif', 'C-2568_F-034.tif', 'C-2568_F-036.tif','C-1256_F-362.tif', 'C-2071_F-010.tif', 'M-1379_F-39722.tif',
       'C-1256_F-360.tif', 'C-2407_F-196.tif', 'M-1379_F-39724.tif', 'C-2465_F-210.tif', 'M-1379_F-39726.tif', 'c-1857 f-198.tif',
       'c-1857 f-200.tif', 'c-2284 f-076.tif', 'c-2284 f-78.tif', 'C-1256_F-328.tif', 'c-1917 f-090.tif', 'c-1917 f-102.tif',
       'm-1359 f-37742.tif', 'c-1857 f-226.tif', 'c-1857 f-230.tif','c-1891 f-074.tif', 'c-1891 f-076.tif', 'c-1891 f-084.tif',
       'c-1917 f-092.tif', 'c-1917 f-100.tif', 'c-2070 f-264.tif','c-1857 f-162.tif', 'c-1857 f-188.tif', 'c-1857 f-208.tif',
       'c-1974 f-142.tif', 'c-1857 f-160.tif', 'c-1857 f-190.tif','c-1857 f-192.tif', 'c-1857 f-204.tif', 'c-1857 f-206.tif',
       'c-1841 f-016.tif', 'c-1891 f-072.tif', 'c-2070 f-262.tif','c-1589 f-076.tif', 'c-1589 f-088.tif', 'c-1857 f-156.tif',
       'c-1857 f-158.tif', 'c-1857 f-194.tif', 'c-1857 f-196.tif','c-1857 f-202.tif', 'c-1857 f-232.tif', 'c-1857 f-234.tif',
       'c-1891 f-086.tif', 'c-1891 f-088.tif', 'c-2556 f-138..tif','C-2284_F-074.tif')

def get_photos_ids():
    return photos_ids

def connect_db(database, host, user, password):
    conexiion = pg2.connect(database=database,
                            host=host, user=user,
                            password=password)
    cursor1 = conexiion.cursor()
    sql = '''select * from resources_info '''
    try:
        cursor1.execute(sql)
        data = cursor1.fetchall()
        df = pd.DataFrame(data, columns=['ID', 'photo-name', 'extension', 's3-dir', 'type'])
        consulta = ['tif', 'jpg']
        photos_ids=tuple(df.loc[(df['extension'].isin(consulta)) & (df['type'] == 'aerofotografia'), ['photo-name']]\
                         .values.ravel())
        return df
    except:
        cursor1.execute("ROLLBACK")
        return None