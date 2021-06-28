import pandas as pd

from my_python.gps_trajectory import Gps_trajectories
from my_python.preprocessing import *
from Find_Mac import FindMac, MacByFrequency, BtUsersClassification

# define relative path to the project folder
os.chdir(os.path.realpath('..'))

# What to run
what_to_run = {1: False,
               2: False,
               3: {'run': False, 'create_buffer_around': False},
               4: {'run': False, 'from_scratch': False},
               5: False,
               'months': '07',
               'build csv file of scooter user': True,
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
            find_mac = FindMac('file' + mac_csv_file)
            if what_to_run[4]['from_scratch']:
                find_mac.from_scratch()
            find_mac.calculate_similarity4()
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

if what_to_run['build csv file of scooter user']:
    print('build csv file of scooter user')
    bt_as_scooter_rec = BtUsersClassification()
    for date_csv_file in os.listdir('csv_files/dates'):
        if date_csv_file.split('_')[1] == '07':
            print(date_csv_file)
            data_folder = os.path.join('csv_files/dates', date_csv_file)
            os.chdir(data_folder)
            mac_records_loc = pd.read_csv('bt_in_gps_scooter.csv')
            mac_records_loc.set_index(keys='PK_UID', drop=False, inplace=True)
            pk_ids_loc = pd.read_csv('pk_uid.csv')
            bt_as_scooter_rec.scooter_bt(mac_records=mac_records_loc, pk_ids=pk_ids_loc)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(os.path.realpath('..'))

    bt_as_scooter_rec.export_file('csv_files')
if what_to_run['find_mac_route']:
    print('It finds the route of the specified macs in macs array in the specified date')
    date = '2020_07_05'
    mac = ['5D3BA1A66C57']
    FindMac.find_mac_route(mac, date)
