from operator import itemgetter
import pandas as pd
import shapely.wkt
from geopandas import GeoDataFrame
from shapely import geometry
import os


def find_point_index(string_list, str_to_find):
    """"
    Find substring (@param: str_to_find) in string (@param: string_list)
    """
    for string in string_list:
        if str_to_find in string:
            return string
    print('Error')


class ToShapeFile:
    """
        This class transforms GPS trajectories to shape file format
    """

    def __init__(self, bd):
        """
        Initialisation of the class includes dataframe( :param bd) and two dictionaries to
        populate the data in proper format. @skip_over handles problematic rows in the database
        """
        self.db = bd
        self.pnt_list = {'geometry': [], 'time': [], 'line_id': []}
        self.lines = {'geometry': [], 'time_start': [], 'time_end': []}
        self.skip_over = 0

    def convert(self, row):
        """
        convert a specific row/s to right format
        :param row:
        :return:
        """

        my_index = row['index']

        if self.skip_over > 0:
            # In case the row is not a new route and had already been addressed
            print(str(my_index) + ' go to next')
            self.skip_over -= 1
            return
        else:
            print(my_index)
            if row['route'][-2:] != ']]':
                # If the route does not end with ]], it means that the next row is included in this scooter route
                temp_str = row['route'][:row['route'].rindex(']') + 1]
                new_values = temp_str[2:-2].split('] [')
                self.skip_over += 1
                go_to_end_row = False
                temp_index = my_index + 1
                while not go_to_end_row:
                    # As a result of the while loop, all the rows that belong to the same
                    # scooter route are added  to the @new_values list
                    new_row = self.db['route'][temp_index]
                    if new_row[-3:-1] != ']]' and new_row[-2:] != ']]':
                        new_values.extend(new_row[new_row.index('['):new_row.rindex(']') + 1][2:-2].split('] ['))
                        self.skip_over += 1
                        temp_index += 1
                    else:
                        go_to_end_row = True
                        if '[' in new_row:
                            new_values.extend(new_row[new_row.index('['):][2:-2].split('] ['))
            else:
                new_values = row['route'][2:-2].split('] [')

        pnt_list = []

        # Loop over all trajectories in @new_values and add them to pnt_list
        for value in new_values:
            split_value = value.split('"')
            pnt = shapely.wkt.loads(find_point_index(split_value, "POINT"))
            date = find_point_index(split_value, "-")
            self.pnt_list['geometry'].append(pnt)
            self.pnt_list['time'].append(date)
            self.pnt_list['line_id'].append(my_index)
            pnt_list.append([pnt, date])

        # Put pnt_list as a new record in lines
        my_linestring = geometry.LineString([[p.x, p.y] for p in list(map(itemgetter(0), pnt_list))])
        self.lines['geometry'].append(my_linestring)
        self.lines['time_start'].append(pnt_list[0][1])
        self.lines['time_end'].append(pnt_list[-1][1])


if __name__ == '__main__':
    # df_pnt = gpd.GeoDataFrame(columns=['geometry', 'time', 'line_id'])
    # df_lines = gpd.GeoDataFrame(columns=['geometry', 'time_start', 'time_end'])
    raw_data = os.path.split(os.path.realpath('..'))[0] + '/csv_files/TLV_routes_July5-11_2020.csv'
    db = pd.read_csv(raw_data).reset_index()
    new_format = ToShapeFile(db)
    # new_format.convert(new_format.db.loc[10365])
    new_format.db.apply(new_format.convert, axis=1)
    df_pnts = GeoDataFrame(new_format.pnt_list, columns=['time', 'line_id', 'geometry'],
                           crs='EPSG:4326')
    df_lines = GeoDataFrame(new_format.lines, columns=['time_start', 'time_end', 'geometry'],
                            crs='EPSG:4326')
    df_pnts.to_file('points_july.shp')
    df_lines.to_file('lines_july.shp')
