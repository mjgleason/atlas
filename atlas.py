import os
import sys
import shapely
import fiona
import rasterio
import fnmatch
import itertools
import geopandas as gpd
import pandas as pd

def get_shortpath(fullpath, par_dir):
    shortpath = fullpath.split(par_dir)[1]

    return shortpath

# from http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Atlas(object):

    def __init__(self, dir):

        self.dir = dir
        self.all_files = None
        self.geo_files = None
        self.rasters = None
        self.vectors = None
        self.tables = None

        # define extensions by type
        # TODO: add valid extensions to search for
        self._EXTS = {'vector':['*.shp'],
                      'raster':['*.tif'],
                      'table':['*.csv']
                      }

        self.update()


    def update(self):

        self.all_files = self.list_files()
        self.geo_files = self.list_geo_files(self.all_files)
        self.rasters = self.list_rasters(self.all_files)
        self.vectors = self.list_vectors(self.all_files)
        self.tables = self.list_tables(self.all_files)
        self.build_schemas()
        self.create_file_handles()

    def list_files(self):

        walked = os.walk(self.dir)
        all_files = []
        for t in walked:
            pardir = t[0]
            for f in t[2]:
                filepath = os.path.join(pardir, f)
                all_files.append(filepath)

        return all_files


    def filter_files_by_ext(self, file_list, exts):

        filtered_files = []
        for ext in exts:
            filtered_files.extend(fnmatch.filter(file_list, ext))
            filtered_files.extend(fnmatch.filter(file_list, ext.upper()))

        return filtered_files


    def list_geo_files(self, file_list):

        exts = list(itertools.chain(*self._EXTS.values()))
        return self.filter_files_by_ext(file_list, exts)


    def list_rasters(self, file_list):

        exts = self._EXTS['raster']
        return self.filter_files_by_ext(file_list, exts)


    def list_vectors(self, file_list):

        exts = self._EXTS['vector']
        return self.filter_files_by_ext(file_list, exts)


    def list_tables(self, file_list):

        exts = self._EXTS['table']
        return self.filter_files_by_ext(file_list, exts)


    def build_schemas(self):

        folders = []
        for f in self.geo_files:
            folder = os.path.dirname(get_shortpath(f, self.dir))[1:]
            folders.append(folder)

        schemas = list(set(folders))

        for schema in schemas:
            self.__setattr__(schema, Schema(schema))


    def create_file_handles(self):

        for f in self.rasters:
            # get schema
            schema_name = os.path.dirname(get_shortpath(f, self.dir))[1:]
            geodata = GeoData(f, 'raster', self.dir, self)
            if self.__getattribute__(schema_name).__dict__.get(geodata.name) is None:
                self.__getattribute__(schema_name).__setattr__(geodata.name, geodata)


        for f in self.vectors:
            # get schema
            schema_name = os.path.dirname(get_shortpath(f, self.dir))[1:]
            geodata = GeoData(f, 'vector', self.dir, self)
            if self.__getattribute__(schema_name).__dict__.get(geodata.name) is None:
                self.__getattribute__(schema_name).__setattr__(geodata.name, geodata)

        for f in self.tables:
            # get schema
            schema_name = os.path.dirname(get_shortpath(f, self.dir))[1:]
            geodata = GeoData(f, 'table', self.dir, self)
            if self.__getattribute__(schema_name).__dict__.get(geodata.name) is None:
                self.__getattribute__(schema_name).__setattr__(geodata.name, geodata)



class GeoData(object):

    def __init__(self, fullpath, datatype, par_dir, atlas = None):

        self.par_dir = par_dir
        self.datatype = datatype
        self.fullpath = fullpath
        self.atlas = atlas
        self.shortpath = get_shortpath(self.fullpath, self.par_dir)
        self.name = os.path.splitext(os.path.basename(self.fullpath))[0]
        self.data = 'Not loaded yet'

    def get(self):

        if self.datatype == 'raster':
            with rasterio.open(self.fullpath) as src:
                self.data = Raster(src)

        elif self.datatype == 'vector':
            self.data = gpd.read_file(self.fullpath)

        elif self.datatype == 'table':
            self.data = pd.read_csv(self.fullpath)

    def save(self):
        if self.datatype == 'raster':
            with rasterio.open(self.fullpath, "w", **self.data.profile) as dest:
                dest.write(self.data.array)

        elif self.datatype == 'vector':
            self.data.to_file(self.fullpath)

        elif self.datatype == 'table':
            self.data.write_csv(self.fullpath, header = True, index= False)


        if atlas is not None:
            self.atlas.update()

    def save_as(self, filepath):
        if self.datatype == 'raster':
            with rasterio.open(filepath, "w", **self.data.profile) as dest:
                dest.write(self.data.array)

        elif self.datatype == 'vector':
            self.data.to_file(filepath)

        elif self.datatype == 'table':
            self.data.write_csv(filepath, header = True, index= False)

        if self.atlas is not None:
            self.atlas.update()


class Raster(object):

    def __init__(self, src):

        self.array = src.read()
        self.profile = src.profile


class Schema(object):

    def __init__(self, name):

        self.name = name




