import math
import os

import arcpy
import pandas as pd


class Gps_trajectories:
    def __init__(self, csv_file_path: str, is_speed=False):
        """
        :param csv_file_path: to transform to DBF. The file should contain coordinates
        """
        self.file_folder = os.path.split(csv_file_path)[0]
        self.df = pd.read_csv(csv_file_path)
        arcpy.env.workspace = os.path.join(os.getcwd(), self.file_folder)
        # Add speed data for each GPS point
        if is_speed:
            self.__calc_speed()

    @staticmethod
    def create_buffer_around(network_links_gis: str):
        """
        The method creates buffer of 30 meters around each intersection in the links network
        :param network_links_gis: path to links network gis file
        :return:
        """
        print('create buffer around')
        folder = os.path.split(network_links_gis)[0]
        Gps_trajectories.delete_file([folder + '/links_intersections.shp', folder + '/buffer_intersection.shp'])

        arcpy.Intersect_analysis([network_links_gis], folder + '/links_intersections.shp', output_type='POINT')
        arcpy.Buffer_analysis(folder + '/links_intersections.shp', folder + '/buffer_intersection.shp', 30)

    @staticmethod
    def delete_file(files_to_delete):
        """
        delete the file/s in :param files_to_delete if is exist
        :param files_to_delete:
        :return:
        """
        for file in files_to_delete:
            if arcpy.Exists(file):
                arcpy.Delete_management(file)

    def __calc_speed(self):
        # From Israel time to GMT time and to timestamp
        print('calc speed')
        self.df['gmt'] = pd.DatetimeIndex(self.df['time']).tz_localize(tz='Israel').tz_convert('GMT')
        self.df['timestamp'] = self.df['gmt'].map(lambda x: pd.to_datetime(x).timestamp())
        self.df['duration'] = ''
        self.df['length'] = ''
        self.df['speed'] = ''
        # Calculate speed
        df = ' '
        for i, (name, group) in enumerate(self.df.groupby('line_id')):
            # For each scooter trajectories:
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

    def add_link_information(self, links_file_folder):
        """
        add link information for GPS points that are not near intersection
        :param links_file_folder: Help us to
        :return:
        """

        self.__remove_points_near_intersection(links_file_folder + '/buffer_intersection.shp')
        self.__spatial_join(links_file_folder + '/links_network.shp')

    def __remove_points_near_intersection(self, buffer_file_path):
        """
        Remove GPS points near intersection from :param buffer_file_path
        :param buffer_file_path:
        :return:
        """
        print('remove points near intersection')
        gps_with_speed_shp = 'gps_with_speed.shp'
        Gps_trajectories.delete_file([gps_with_speed_shp, 'point_in_buffer.shp', "symdiff.shp"])

        arcpy.management.XYTableToPoint(in_table='stamp_time.csv',
                                        out_feature_class=gps_with_speed_shp,
                                        x_field="POINT_X", y_field="POINT_Y",
                                        coordinate_system=arcpy.SpatialReference(2039))

        arcpy.Intersect_analysis([buffer_file_path, gps_with_speed_shp], 'point_in_buffer.shp',
                                 output_type='POINT')
        arcpy.SymDiff_analysis(gps_with_speed_shp, 'point_in_buffer.shp', "symdiff.shp")

    def __spatial_join(self, network_links_gis):
        """
        :param network_links_gis:
        :return:
        """
        file_with_link_data = 'file_with_link_data'
        Gps_trajectories.delete_file([file_with_link_data + '.shp', file_with_link_data + '.csv'])
        arcpy.SpatialJoin_analysis("symdiff.shp", network_links_gis, file_with_link_data + '.shp',
                                   join_type='KEEP_COMMON',
                                   match_option='CLOSEST', search_radius=45, distance_field_name='distance')
        arcpy.TableToTable_conversion(file_with_link_data + '.shp', arcpy.env.workspace, file_with_link_data + '.csv')

        # Delete unnecessary columns
        df = pd.read_csv(os.path.join(self.file_folder, file_with_link_data + '.csv'))
        df = df[['OID_', 'timestamp', 'gmt', 'line_id', 'POINT_X', 'POINT_Y', 'duration', 'length', 'speed', 'TO_1',
                 'VIA_1', 'via_to_1', 'Shape_Le_1']]
        df.rename(columns={'TO_1': 'TO', 'VIA_1': 'VIA', 'via_to_1': 'via_to', 'Shape_Le_1': 'Shape_Length', },
                  inplace=True)

        # Make it one directional by change the “via_to” field (if necessary) to smaller first in TB file
        df['via_to'] = df['via_to'].where(df['VIA'] < df['TO'], df['TO'] + df['VIA'])
        df.to_csv(os.path.join(self.file_folder, 'file_with_link_clean' + '.csv'))
