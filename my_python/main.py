import pandas as pd

from my_python.gps_trajectory import Gps_trajectories
from my_python.preprocessing import *
from Find_Mac import FindMac, MacByFrequency

# define relative path to the project folder
os.chdir(os.path.realpath('..'))

# What to run
what_to_run = {1: False,
               2: False,
               3: {'run': False, 'create_buffer_around': False},
               4: {'run': True, 'from_scratch': False},
               5: True,
               'months': '07',
               'find_mac_route': False}
params = {'months': '07'}
# 1 - Clip the input to clip shape file polygon layer of the links area
if what_to_run[1]:
    print('Clip the input to clip shape file polygon layer of the links area')
    clip(my_input='MyProject10/points_july.shp', my_clip='MyProject10/clip_file.shp',
         where_to_save='MyProject10/points_in_clip_july.shp')

# 2 - Davide by day
if what_to_run[2]:
    print('Davide by day')
    divide_by_day(shp_file='MyProject10/points_in_clip_july.shp',
                  csv_file='csv_files/points_in_clip_july.csv')

# 3 - Connect GPS trajectories to links

if what_to_run[3]['run']:

    print('Map matching')
    # Create buffer around the links network
    if what_to_run[3]['create_buffer_around']:
        Gps_trajectories.create_buffer_around(network_links_gis='MyProject10/links_network.shp')

    for date_csv_file in os.listdir('csv_files/dates'):
        if date_csv_file == 'test':
            continue
        if what_to_run['months'] is True or date_csv_file.split('_')[1] == what_to_run['months']:
            print(date_csv_file)
            csv_file_path = os.path.join('csv_files/dates', date_csv_file, 'file' + date_csv_file + '.csv')
            GPS_obj = Gps_trajectories(csv_file_path=csv_file_path, is_speed=True)
            GPS_obj.add_link_information(links_file_folder=os.getcwd() + '/MyProject10')

# Find matching macs and scooter ids by finding sequences of the same links
if what_to_run[4]['run']:
    print('find mac')
    for date_csv_file in os.listdir('csv_files/dates'):
        if what_to_run['months'] is True or date_csv_file.split('_')[1] == what_to_run['months']:
            print(date_csv_file)
            mac_csv_file = date_csv_file.replace('_', '-')
            data_folder = os.path.join('csv_files/dates', date_csv_file)
            os.chdir(data_folder)
            FindMac('file' + mac_csv_file + '.csv', from_scratch=what_to_run[4]['from_scratch'])
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(os.path.realpath('..'))

# find for macs the matching scooter ids and the number of matching links
if what_to_run[5]:
    print('summing by mac')
    mac_frequency = MacByFrequency()
    for date_csv_file in os.listdir('csv_files/dates'):
        date_slip = date_csv_file.split('_')
        if what_to_run['months'] is True or date_slip[1] == what_to_run['months']:
            print(date_csv_file)
            data_folder = os.path.join('csv_files/dates', date_csv_file)
            my_pd = pd.read_csv(data_folder + '/res_sco_4.csv')
            my_pd.apply(lambda x: mac_frequency.count_line_id(x, date=str(date_slip[1]) + str(date_slip[2])), axis=1)

    mac_frequency.from_dic_to_df('csv_files/count_line_id.csv')

if what_to_run['find_mac_route']:
    print('It finds the route of the specified macs in macs array in the specified date')
    date = '2020_07_05'
    mac = ['5D3BA1A66C57']
    FindMac.find_mac_route(mac, date)
