from my_python.gps_trajectory import Gps_trajectories
from my_python.preprocessing import *
from Find_Mac import FindMac

# define relative path to the project folder
os.chdir(os.path.realpath('..'))

# Parameters
# Mode (test or data)
code_mode = 'data'
print(code_mode)
# What to run
what_to_run = [4]

# 1 - Clip the input to clip shape file polygon layer of the links area
if True in what_to_run or 1 in what_to_run:
    print('Clip the input to clip shape file polygon layer of the links area')
    clip(my_input='MyProject10/points.shp', my_clip='MyProject10/clip_file.shp',
         where_to_save='MyProject10/points_in_clip.shp')

# 2 - Davide by day
if True in what_to_run or 2 in what_to_run:
    print('Davide by day')
    divide_by_day(shp_file='MyProject10/points_in_clip.shp',
                  csv_file='csv_files/points_in_clip.csv')

# 3 - Connect GPS trajectories to links

if True in what_to_run or 3 in what_to_run:
    print('Map matching')
    # Create buffer around the links network

    Gps_trajectories.create_buffer_around(network_links_gis='MyProject10/links_network.shp')
    if code_mode == 'test':
        for date_csv_file in os.listdir('csv_files/dates/test'):
            print(date_csv_file)
            csv_file_path = os.path.join('csv_files/dates/test', date_csv_file, 'file' + date_csv_file + '.csv')
            GPS_obj = Gps_trajectories(csv_file_path=csv_file_path)
            GPS_obj.add_link_information(links_file_folder=os.getcwd() + '/MyProject10')

    else:
        for date_csv_file in os.listdir('csv_files/dates'):
            if date_csv_file == 'test':
                continue
            print(date_csv_file)
            csv_file_path = os.path.join('csv_files/dates', date_csv_file, 'file' + date_csv_file + '.csv')
            GPS_obj = Gps_trajectories(csv_file_path=csv_file_path)
            GPS_obj.add_link_information(links_file_folder=os.getcwd() + '/MyProject10')

if True in what_to_run or 4 in what_to_run:
    print('find mac')
    for date_csv_file in os.listdir('csv_files/dates'):
        print(date_csv_file)
        mac_csv_file = date_csv_file.replace('_', '-')
        data_folder = os.path.join('csv_files/dates', date_csv_file)
        os.chdir(data_folder)
        FindMac('file' + mac_csv_file + '.csv')
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(os.path.realpath('..'))
