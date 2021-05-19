import os

import arcpy
import pandas as pd


def clip(my_input: str, my_clip: str, where_to_save: str):
    """
    Clip the input to clip shape file polygon  layer
    :param my_input: path relative to project
    :param my_clip: path path relative to project
    :param where_to_save: path relative to project
    :return:
    """
    arcpy.Clip_analysis(my_input, my_clip, where_to_save)


def divide_by_day(shp_file: str, csv_file: str):
    """
    divide large file to different date files

    :param shp_file: path to shape file that including date field
    :param csv_file: path to store csv file
    :return:
    """
    # Generate the X_Y_Z_ coordinates using Add Geometry Properties tool to the table
    arcpy.env.workspace = os.getcwd()

    # Process: Project
    print("Project to ITM")
    itm_dataset = str.replace(shp_file, '.shp', '_pro.shp')
    arcpy.Project_management(in_dataset=shp_file, out_dataset=itm_dataset,
                             out_coor_system=arcpy.SpatialReference(2039),
                             transform_method="WGS_1984_To_Israel_CoordFrame",
                             in_coor_system=arcpy.SpatialReference(4326),
                             preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")

    # Process: Add Geometry Attributes
    print("Add Geometry Attributes")
    arcpy.AddGeometryAttributes_management(Input_Features=itm_dataset,
                                           Geometry_Properties="POINT_X_Y_Z_M", Length_Unit="METERS", Area_Unit="",
                                           Coordinate_System="")
    # Process: Table To Table
    print("Convert Table To CsvFile")
    csv_file_split = os.path.split(csv_file)
    arcpy.TableToTable_conversion(in_rows=str.replace(itm_dataset, 'shp', 'dbf'), out_path=csv_file_split[0],
                                  out_name=csv_file_split[1])

    # Divide files to dates and create new create a new folder for each data
    print("Divide files to dates and create new create a new folder for each data")
    df = pd.read_csv(csv_file)
    data_time = pd.DatetimeIndex(df['time'])
    df['date'] = data_time.date

    for i, (name, group) in enumerate(df.groupby('date')):
        str_name = str.replace(str(name), '-', '_')
        print(str_name)
        os.makedirs('csv_files/dates/' + str_name)
        group.to_csv('csv_files/dates/' + str_name + '/file{}.csv'.format(str_name))

