# Python 3.8 D:\Users\achituv\anaconda3\envs\ox\python.exe

# שינתי את המקום של הקבצים, יש לשים ךב לכך בזמן הרצת הקובץ בשנית
# from operator import itemgetter
#
# import pandas as pd
# import shapely.wkt
# from geopandas import GeoDataFrame
# from shapely import geometry
#
#
# def convert(row):
#     new_values = row['route'][2:-2].split('] [')
#     pnt_list = []
#     my_index = row['index']
#     for value in new_values:
#         split_value = value.split('"')
#         pnt = shapely.wkt.loads(split_value[1])
#         date = split_value[3]
#         my_pnts['geometry'].append(pnt)
#         my_pnts['time'].append(date)
#         my_pnts['line_id'].append(my_index)
#         pnt_list.append([pnt, date])
#         print(my_index)
#
#     my_linestring = geometry.LineString([[p.x, p.y] for p in list(map(itemgetter(0), pnt_list))])
#     my_lines['geometry'].append(my_linestring)
#     my_lines['time_start'].append(pnt_list[0][1])
#     my_lines['time_end'].append(pnt_list[-1][1])
#
#
# if __name__ == '__main__':
#     # df_pnt = gpd.GeoDataFrame(columns=['geometry', 'time', 'line_id'])
#     # df_lines = gpd.GeoDataFrame(columns=['geometry', 'time_start', 'time_end'])
#     db = pd.read_csv('Tel_aviv_routes_1st_wk_06_2020.csv').reset_index()
#     my_pnts = {'geometry': [], 'time': [], 'line_id': []}
#     my_lines = {'geometry': [], 'time_start': [], 'time_end': []}
#     db.apply(lambda x: convert(x), axis=1)
#     df_pnts = GeoDataFrame(my_pnts, columns=['time', 'line_id','geometry'],
#                            crs='EPSG:4326')
#     df_lines = GeoDataFrame(my_lines, columns=['time_start', 'time_end', 'geometry'],
#                             crs='EPSG:4326')
#     df_pnts.to_file('points.shp')
#     df_lines.to_file('lines.shp')
