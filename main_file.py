import  os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import argrelextrema
import sqlite3
from sqlite3 import Error

shp =       'myFShapeFile'
inFolder=  ['s1b-iw-grd-vh-20190528t151107-20190528t151132-016446-01ef55-002.tiff',
            's1b-iw-grd-vv-20190528t151107-20190528t151132-016446-01ef55-001.tiff']
outFolder=  'crop'

def cut_and_save(shpfile='',len_id =1,piture_cut_name=['1.tiff'],picture_save_name='new'):
    for ind, j in enumerate(piture_cut_name):
        for i in range(len_id):
            try:
                os.system('gdalwarp -cutline {1}.shp -crop_to_cutline -dstnodata -9999 -csql "SELECT * FROM {1} WHERE id = {0}" '
                      '{2} {3}_{0}_{2}'.format(str(i+1), shpfile, j, picture_save_name))
            except Exception as E:
                print(E)

def compute_data(hist_data,name_picture):
    df = pd.DataFrame(np.array(hist_data), columns=['data'])

    n = 1  # дельта (мінімальної відстані між точками)
    # Пошук локальних піків
    df['min'] = df.iloc[argrelextrema(df.data.values, np.less_equal, order=n)[0]]['data']
    df['max'] = df.iloc[argrelextrema(df.data.values, np.greater_equal, order=n)[0]]['data']

    # Границя нижнього діапазону для пошуку локальних піків
    df = df.mask(df < 100, np.nan)

    plt.scatter(df.index, df['min'], c='r')
    plt.scatter(df.index, df['max'], c='g')
    df.data.plot()

    max = df[df['max'].notnull()].data
    min = df[df['min'].notnull()].data
    if min.__len__() <= max.__len__():
        df._set_value(0,'min',0)
        last = df[df['data'].notnull()].data.index.values[-1]
        df._set_value(last, 'min', 0)
        min = df[df['min'].notnull()].data
    ww = max + min
    ww = list(ww.index.values)
    width = []
    for i,v in enumerate(ww):
        if i % 2 == 1:
            width.append(ww[i+1] - ww[i-1])
    ind = max.index.values
    max = max.values
    empPicture = convertToBinaryData('/home/myroslav/PycharmProjects/testForGDAL/' + name_picture)

    return {i+1:{'name':name_picture,'data':max[i],'width':float(width[i]),'color_id':float(ind[i]),'picture':empPicture} for i in range(width.__len__())}
    # return {i + 1: {'name': str(name_picture), 'data': max[i], 'width': float(width[i]), 'color_id': float(ind[i]),
    #                 'picture': 'empPicture'} for i in range(width.__len__())}
    # plt.show()
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_task(conn, task):

    sql = ''' INSERT INTO MapData(name,data,width,color_id,pictures)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def write_in_bd(data_with_parameters,pitures_hist_name):
    database = "/home/myroslav/Desktop/MiraBD.sql"
    # create a database connection
    conn = create_connection(database)

    #################################################
    # import pyodbc
    #
    # server = 'tcp:gis.contour.net'
    # database = 'SIGDB'
    # username = 'sa'
    # password = 'mastdie_6'
    #
    # conn = pyodbc.connect(
    #     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
    #     autocommit=True)
    # cur = conn.cursor()
    #
    # sql = ''' INSERT INTO MapData(name,data,width,color_id,pictures)
    #                   VALUES(?,?,?,?,?) '''
    #################################################
    with conn:
        for data in data_with_parameters:
            for ind, val in enumerate(data):
                create_task(conn, [data[val]['name'], data[val]['data'], data[val]['width'], data[val]['color_id'], data[val]['picture']])
                # cur.execute(sql, [data[val]['name'], data[val]['data'], data[val]['width'], data[val]['color_id'], data[val]['picture']])
def simple_plot(pitures_hist_name):
    import subprocess
    color = ['green','red','blue','yellow','black','orange']
    data_with_parameters = []
    for name in pitures_hist_name:
        data_for_hist = subprocess.getoutput('gdalinfo -stats -hist {}'.format(name))
        step1 = data_for_hist.split('\n')[43].split(' ')
        step2 = filter(lambda x: len(x) > 0, step1)
        step3 = [int(i) for i in step2]
        plt.style.use('ggplot')
        data_with_parameters.append(compute_data(step3,name))
    [print(i) for i in data_with_parameters[:3]]
    write_in_bd(data_with_parameters,pitures_hist_name)
    plt.show()



def stackoverflow_example(data):
    pass

if __name__ == '__main__':
    # cut_and_save(shp,3,inFolder,outFolder)
    # cut_and_save('korablici',3,['s1b-iw-grd-vh-20190528t151107-20190528t151132-016446-01ef55-002.tiff'],'crop_korabliki')
    # stackoverflow_example()
    simple_plot(['11.tiff','12.tiff','13.tiff'])

    pass

