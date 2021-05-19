# def join_data(self):
#
#     # path to csv files and feature class
#
#     # from feature class to dataframe format
#     via_to = list()
#     shape_length = list()
#     cursor = arcpy.da.SearchCursor(self.network_links_gis, ['via_to', 'Shape_Length'])
#     for row in cursor:
#         via_to.append(row[0])
#         shape_length.append(row[1])
#     df_network = pd.DataFrame({'via_to': [], 'Shape_Length': []})
#     df_network['via_to'] = via_to
#     df_network['Shape_Length'] = shape_length
#     # print(df_network)
#
#     # Merge feature class and csv file
#     all_bt_file = pd.read_csv(self.bt_file_path)
#     all_bt_file['via_to'] = all_bt_file['VIAUNITC'] + all_bt_file['TOUNITC']
#     df = pd.merge(all_bt_file, df_network, on=['via_to'], how='inner')
#     df.to_csv(os.path.join(self.workspace_csv_progress, 'join' + self.date + '.csv'))