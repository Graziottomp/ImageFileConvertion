------------------------------------------------------------------------------------
#!/usr/bin/env python
# coding: utf-8

# Rotina para converter arquivos Sentinel 1 em NetCDF para imagens GeoTiff seguindo:

# Leitura do arquivo .nc -> Atributos da imagem para indexar no BD -> Extraindo e georeferenciando as coordenadas dos metadados -> Criação do arquivo GeoTiff

#author = 'Maria Paula Graziotto'
 
# copyright = "Copyright 2023, Maria Paula Graziotto"

# credits = ['Graziotto, M. P.']

# license = "Public Domain"

# version = "3.0"

# maintainer = "Maria Paula Graziotto"

# email = 'graziotto.mp@outlook.com'
------------------------------------------------------------------------------------
#importando bibliotecas

import pathlib as plib
import glob
import numpy as np
import pandas as pd
import xarray as xr 
import rioxarray as rio 
import rasterio as rs
from rasterio.plot import show
from openpyxl import Workbook, load_workbook
from datetime import date, datetime, time
import locale
from pyproj import Proj, CRS, Transformer
from pyproj.transformer import AreaOfInterest
from pyproj.database import query_utm_crs_info
-----------------------------------------------------------------------------------
#definindo diretorio e arquivos
current_dir = plib.Path.cwd()

arquivo_excel = load_workbook('.csv')
nome_arquivos= glob.glob('*.nc')
nome_arquivos.sort()
------------------------------------------------------------------------------------
#extrair infos do nome do arquivo para preencher tabela e conversao para raster
def fsentinel(file2read): 
    try:
      df_S1 = xr.open_dataset(file2read)
    except: 
      print('Erro arquivo:', file2read)
      return False

#extraindo informações de metadado para preencher o BD
    file_Id = 1 
    file_path = str(current_dir)
    file_name = df_S1.metadata.attrs['Abstracted_Metadata:PRODUCT'] 
    file_indexed_by = ('INPE') 
    file_type = ('NetCDF')
    img_projection = df_S1.metadata.attrs['Abstracted_Metadata:geo_ref_system']
    img_bbox1_lat = df_S1.metadata.attrs['Abstracted_Metadata:first_near_lat']
    img_bbox1_lon = df_S1.metadata.attrs['Abstracted_Metadata:first_near_long']
    img_bbox2_lat = df_S1.metadata.attrs['Abstracted_Metadata:first_far_lat']
    img_bbox2_lon = df_S1.metadata.attrs['Abstracted_Metadata:first_far_long']
    img_bbox3_lat = df_S1.metadata.attrs['Abstracted_Metadata:last_near_lat']
    img_bbox3_lon = df_S1.metadata.attrs['Abstracted_Metadata:last_near_long'] 
    img_bbox4_lat = df_S1.metadata.attrs['Abstracted_Metadata:last_far_lat']
    img_bbox4_lon = df_S1.metadata.attrs['Abstracted_Metadata:last_far_long']
    img_res_lat = df_S1.metadata.attrs['Abstracted_Metadata:lat_pixel_res'] 
    img_res_lon = df_S1.metadata.attrs['Abstracted_Metadata:lon_pixel_res']
    img_inc_angle = df_S1.metadata.attrs['Abstracted_Metadata:incidence_near']
    sat_name = df_S1.metadata.attrs['Abstracted_Metadata:MISSION']
    sat_sensor = df_S1.metadata.attrs['Abstracted_Metadata:ACQUISITION_MODE']
    sat_band = ('C')
    sat_orbit = df_S1.metadata.attrs['Abstracted_Metadata:PASS']
    proc_level = df_S1.metadata.attrs['Abstracted_Metadata:SPH_DESCRIPTOR'] 
    sat_proc_level = proc_level[14:25]
    sat_polar1 = df_S1.metadata.attrs['Abstracted_Metadata:mds1_tx_rx_polar']
    sat_polar2 = df_S1.metadata.attrs['Abstracted_Metadata:mds2_tx_rx_polar']
    sat_polar = ('{} + {}'.format(sat_polar1, sat_polar2))
    
#dia e hora
    file_d = file2read[17:25]
    file_t = file2read[26:32]
    ano = file_d[0:4]
    mes = file_d[4:6]
    dia = file_d[6:8]
    data = '%s-%s-%s' %(ano, mes, dia) 
    hora = file_t[0:2]
    mi = file_t[2:4]
    seg = file_t[4:6]
    time = '%s:%s:%s' %(hora, mi, seg) 
    file_dt = '{} {}'.format(data, time)
    locale.setlocale(locale.LC_ALL, 'pt_BR')
    file_date_time = datetime.fromisoformat(file_dt)

#preenchendo a tabela do BD com os atributos: File_Id, file_path, file_name, 
#file_indexed_by, file_date_time, file_type, file_projection,img_bbox (1,2,3 e 4),
#img_res_lat, img_res_lon, sat_name, sat_sensor, sat_band, sat_orbit, sat_proc_level,


#dicionário com todas as variáveis desejadas **Colocar na ordem que a planilha esta

    bd_images = [file_Id, 
                 file_path,
                 file_name, 
                 file_indexed_by, 
                 file_date_time,
                 file_type,
                 img_projection,
                 img_bbox1_lat,
                 img_bbox1_lon,
                 img_bbox2_lat,
                 img_bbox2_lon,
                 img_bbox3_lat,
                 img_bbox3_lon,
                 img_bbox4_lat,
                 img_bbox4_lon,
                 img_res_lat,
                 img_res_lon,
                 img_inc_angle,
                 sat_name, 
                 sat_sensor, 
                 sat_band, 
                 sat_orbit,
                 sat_proc_level,
                 sat_polar]

#abrindo a planilha desejada do worbook
    planilha2 = arquivo_excel.worksheets[1]

#inserindo os dados
    planilha2.append(bd_images)

#salvando a planilha
    arquivo_excel.save(".csv")
        
        
#abrindo a variavel Sigma0 de cada arquivo para conversão
    sig= df_S1['Sigma0_VV']
    lon= df_S1['lon']
    lat= df_S1['lat']

#referenciando o sistema de coordenadas e projeção 
    sig= sig.rio.set_spatial_dims(x_dim='lon', y_dim='lat')
    sig.rio.crs
    sig.rio.write_crs(4326, inplace=True)

#transformando o arquivo com a variavel sigma em raster .tiff
    name = file2read.split(".")     #para tirar o .nc do nome do arquivo salvo
    sig.rio.to_raster("{}.tiff".format(name[0]))

    return True
------------------------------------------------------------------------------------
#leitura de todos os arquivos da pasta

for file2read in nome_arquivos:
    fsentinel(file2read)
------------------------------------------------------------------------------------



