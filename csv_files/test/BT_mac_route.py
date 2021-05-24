# This file will join a specific
import os

import arcpy
import pandas as pd

arcpy.env.workspace = os.getcwd()
# filter_field = 'line_id' or
filter_field = 'line_id'
join_field = "via_to"
# 'file_with_link_clean.csv'/
path_to_file = 'file_with_link_clean.csv'
link_network = "links_network.shp"

filtered_file_name = "filtered_file.csv"

mac_array = ['D92C3D725606','FD49BA06D424','3550DBA1897E','017F25EA85E6']
for mac in mac_array:
    print(mac)
    # if the filter_field  is 'line_id' the filter_id is int
    filter_id = mac
    filtered_network = "filtered_network" + str(filter_id) + ".shp"




    # Filter _file
    file = pd.read_csv(path_to_file)
    filtered_file = file[file[filter_field] == filter_id]
    filtered_file.to_csv(filtered_file_name)

    # Join to the links_network
    arcpy.env.workspace = os.getcwd()

    res = arcpy.AddJoin_management(link_network, "via_to", filtered_file_name, join_field,
                                   join_type='KEEP_COMMON')
    if arcpy.Exists(filtered_network):
        arcpy.Delete_management(filtered_network)
    arcpy.CopyFeatures_management(res, filtered_network)
