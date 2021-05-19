# This file will join a specific
import arcpy
import os
arcpy.env.workspace = os.getcwd()
arcpy.AddJoin_management( "links_network.shp", "via_to", "vegtable.dbf", "HOLLAND95")
arcpy.CopyFeatures_management( "veg_layer", "Habitat_Analysis.gdb/vegjoin")