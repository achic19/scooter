import math
import os

import arcpy
import pandas as pd


class Gps_trajectories:
    def __init__(self, csv_file_path: str):
        """
        :param csv_file_path: to transform to DBF. The file should contain coordinates
        """
        self.file_folder = os.path.split(csv_file_path)[0]
        self.df = pd.read_csv(csv_file_path, nrows=1000)

    def add_link_information(self, network_links_gis):
        self.__calc_speed()
        self.__remove_points_near_intersection(network_links_gis)

    def __calc_speed(self):
        # From Israel time to GMT time and to timestamp
        self.df['gmt'] = pd.DatetimeIndex(self.df['time']).tz_localize(tz='Israel').tz_convert('GMT')
        self.df['timestamp'] = self.df['gmt'].map(lambda x: pd.to_datetime(x).timestamp())
        self.df['duration'] = ''
        self.df['length'] = ''
        self.df['speed'] = ''
        # Calculate speed
        df = ' '
        for i, (name, group) in enumerate(self.df.groupby('line_id')):
            # For each scooter trajectories:
            print(name)
            # Aggregate (calculate mean) GPS points with same time
            group = group.groupby('timestamp').agg(
                {'gmt': 'first', 'OID_': 'first', 'line_id': 'first', 'POINT_X': 'mean',
                 'POINT_Y': 'mean', }).reset_index()
            # try:
            for index, record in group.iterrows():
                # For each GPS point calculate speed (except the first point)
                if index == 0:
                    continue
                else:
                    lst_index = index - 1
                    dx = record['POINT_X'] - group.at[lst_index, 'POINT_X']
                    dy = record['POINT_Y'] - group.at[lst_index, 'POINT_Y']
                    group.at[index, 'duration'] = record['timestamp'] - group.at[lst_index, 'timestamp']
                    group.at[index, 'length'] = math.sqrt(dx * dx + dy * dy)
                    group.at[index, 'speed'] = group.at[index, 'length'] / group.at[index, 'duration']
            # Save the results to another data frame
            if i == 0:
                df = group
            else:
                df = df.append(group, ignore_index=True)
            # except Exception:
            #     e = sys.exc_info()[1]
            #     print(e.args[0])
            #     pass
        self.df = df
        self.df.to_csv(os.path.join(self.file_folder, r'stamp_time.csv'))

    def __remove_points_near_intersection(self, network_links_gis):
        # TODO - Should be Done only once
        arcpy.env.workspace = os.getcwd()
        # ToDo - Update output
        arcpy.Intersect_analysis([network_links_gis], 'links_intersections', output_type='POINT')
        arcpy.Buffer_analysis('links_intersections', 'buffer_intersection', 30)

        arcpy.management.XYTableToPoint(in_table=os.path.join(self.file_folder, r'stamp_time.csv'),
                                        out_feature_class=os.path.join(self.file_folder, r'points_with_spd.shp'),
                                        x_field="POINT_X", y_field="POINT_Y",
                                        coordinate_system=arcpy.SpatialReference(2039))

        # arcpy.Intersect_analysis(['buffer_intersection', itm_fc_name], 'point_in_buffer', output_type='POINT')
        # arcpy.SymDiff_analysis(itm_fc_name, 'point_in_buffer', "symdiff")
