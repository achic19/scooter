from operator import itemgetter
import pandas as pd
import shapely.wkt
from geopandas import GeoDataFrame
from shapely import geometry
import os


def find_point_index(string_list, str_to_find):
    for string in string_list:
        if str_to_find in string:
            return string
    print('Error')


def convert(row):
    if row['route'][-1] != ']':
        row['route'] = row['route'][:row['route'].rindex(']') + 1]
    if row['route'][0] != '[':
        row['route'] = row['route'][row['route'].index('['):]

    new_values = row['route'][2:-2].split('] [')
    pnt_list = []
    my_index = row['index']
    print(my_index)
    for value in new_values:
        split_value = value.split('"')
        pnt = shapely.wkt.loads(find_point_index(split_value, "POINT"))
        date = find_point_index(split_value, "-")
        my_pnts['geometry'].append(pnt)
        my_pnts['time'].append(date)
        my_pnts['line_id'].append(my_index)
        pnt_list.append([pnt, date])

    my_linestring = geometry.LineString([[p.x, p.y] for p in list(map(itemgetter(0), pnt_list))])
    my_lines['geometry'].append(my_linestring)
    my_lines['time_start'].append(pnt_list[0][1])
    my_lines['time_end'].append(pnt_list[-1][1])


if __name__ == '__main__':
    # df_pnt = gpd.GeoDataFrame(columns=['geometry', 'time', 'line_id'])
    # df_lines = gpd.GeoDataFrame(columns=['geometry', 'time_start', 'time_end'])
    raw_data = os.path.split(os.path.realpath('..'))[0] + '/csv_files/TLV_routes_July5-11_2020.csv'
    db = pd.read_csv(raw_data).reset_index()
    my_pnts = {'geometry': [], 'time': [], 'line_id': []}
    my_lines = {'geometry': [], 'time_start': [], 'time_end': []}
    db.apply(lambda x: convert(x), axis=1)
    df_pnts = GeoDataFrame(my_pnts, columns=['time', 'line_id', 'geometry'],
                           crs='EPSG:4326')
    df_lines = GeoDataFrame(my_lines, columns=['time_start', 'time_end', 'geometry'],
                            crs='EPSG:4326')
    df_pnts.to_file('points_july.shp')
    df_lines.to_file('lines_july.shp')
