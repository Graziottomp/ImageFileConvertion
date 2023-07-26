#!/usr/bin/env python
# coding: utf-8-----------------------------------------------------------------------------------

# KML2Tiff.py: Rotina para converter arquivos KML e PNG provenientes do grupo ICEYE para imagens GeoTiff seguindo:

# Extração das coordenadas do arquivo KML -> Definição das coordenadas Norte/Sul/LEste/Oeste -> Leitura e Converção do arquivo PNG para raster -> Criação do arquivo GeoTiff

# author = 'Maria Paula Graziotto'

# copyright = "Copyright 2023, Maria Paula Graziotto"

# credits = ['Graziotto, M. P.']

# license = "Public Domain"

# version = "1.0"

# maintainer = "Maria Paula Graziotto"

# email = 'graziotto.mp@outlook.com'
-----------------------------------------------------------------------------------------
#importando bibliotecas

import pathlib
import pathlib as plib
from osgeo import ogr, gdal
import geotable
import numpy as np
import glob
import rasterio as rio
from rasterio.plot import show
------------------------------------------------------------------------------------
#definindo o diretório das imagens e identificando os arquivos
current_dir = plib.Path.cwd()
root_dir = current_dir.parents[]

file= glob.glob('*.kml')
file.sort()
png = glob.glob('*.png')
png.sort()
------------------------------------------------------------------------------------
#extração das coordenadas do arquivo KML--

t = geotable.load(file, drop_z=True)
poly= t.geometries[0].wkt.rsplit(sep=',') #retorna uma lista de strings

#separa as strings do poly para extrair lat e lon
n = 5
splited = []
len_poly = len(poly)
for i in range(n):
    start = int(i*len_poly/n)
    end = int((i+1)*len_poly/n)
    splited.append(poly[start:end])
print(splited)

#separa a lista pelas posições de cada string
splited1 = ' '.join(map(str, splited[0]))
splited2 = ' '.join(map(str, splited[1]))
splited3 = ' '.join(map(str, splited[2]))
splited4 = ' '.join(map(str, splited[3]))
coord1 =  splited1[10:] #retirando a string POLYGON do primeiro splited

#def lat e lon para bbox
lon = [coord1[:18], splited2[1:19], splited3[1:19], splited4[1:19]]
lat = [coord1[19:], splited2[20:], splited3[19:], splited4[20:]]

print ('lon: {}, lat: {}'.format(lon,lat))
------------------------------------------------------------------------------------
#definição das coordenadas Norte/Sul/LEste/Oeste--

#min max do lat e lon 
lon_min = min(lon)
lon_max = max(lon)
lat_min = min(lat)
lat_max = max(lat)


#transf em float para determina crs
south = np.float64(lat_min)
north = np.float64(lat_max)
east = np.float64(lon_min)
west = np.float64(lon_max)

print('sul:', south,'norte:', north,'leste:', east,'oeste:', west)
------------------------------------------------------------------------------------
#leitura e converção do arquivo PNG para raster--

name = file.rsplit(".") #para tirar o .kml do nome do arquivo salvo

with rio.open(png, 'r') as img:
    img = img.read([1])
    img = img.astype('uint16')
    bounds = rio.transform.from_bounds(west, north, east, south, img.shape[2], img.shape[1])
    crs = '+proj=latlong'

#criação do arquivo GeoTiff--
    with rio.open('{}.tiff'.format(name[0]),'w', 
                     driver='GTiff',
                     count=1,
                     height=img.shape[1],
                     width=img.shape[2],
                     dtype=img.dtype,
                     crs=crs,
                     transform= bounds,
                     ) as dst:
            dst.write(img)
-------------------------------------------------------------------------------------