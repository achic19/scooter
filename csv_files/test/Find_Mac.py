import os

import arcpy
import pandas as pd
import numpy as np
from _datetime import datetime

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


# add unidirectional route to bt
def test_unidirectional():
    bt = pd.read_csv('file2020-06-01.csv')
    bt['via_to'] = bt['VIAUNITC'] + bt['TOUNITC']
    bt['via_to_uni'] = bt['via_to'].where(bt['VIAUNITC'] < bt['TOUNITC'], bt['TOUNITC'] + bt['VIAUNITC'])
    bt.to_csv('file2020-06-01_uni.csv')


def test_filter_mac():
    print('test_filter_mac')
    bt = pd.read_csv('file2020-06-01_uni.csv')
    # Filter the Bt_files to work only with those in gps_scooter file
    links_list = pd.read_csv('file_with_link_clean.csv')['via_to'].unique()
    bt1 = bt[bt['via_to_uni'].isin(links_list)]
    bt2 = bt[~bt['via_to_uni'].isin(links_list)]
    bt1.to_csv('bt_in_gps_scooter.csv')
    bt2.to_csv('bt_not_gps_scooter.csv')


def test_Mac_with_its_via_to(bt_file, file_to_save='mac_df.csv'):
    print('test_Mac_with_its_via_to')
    bt = pd.read_csv(bt_file)
    mac_df = pd.DataFrame(columns=['via_to_list', 'time'], index=bt['MAC'].unique())
    for group_name, group in bt.groupby('MAC'):
        print(group_name)
        group = group.sort_values(by=['LASTDISCOTS']).reset_index(drop=True)
        temp_list = list(group['via_to_uni'])
        # Save only macs that traverse more than four links
        if len(temp_list) > 3:
            mac_df.at[group_name, 'via_to_list'] = temp_list
            mac_df.at[group_name, 'time'] = list(group['LASTDISCOTS'])
    mac_df = mac_df[mac_df['via_to_list'].notna()]
    mac_df.to_csv(file_to_save)


def test_scooter_with_its_via_to():
    print('test_scooter_with_its_via_to')
    gps_scooter_temp = pd.read_csv('file_with_link_clean.csv')
    sco_df = pd.DataFrame(columns=['via_to_list', 'time'], index=gps_scooter_temp['line_id'].unique())
    # The code iterates over the GPS trajectories of each scooter route and
    # saves the "via_to" link when the "via link" changes and average time of timestamp .
    for j, (name_group, group_scooter) in enumerate(gps_scooter_temp.groupby('line_id')):
        print(name_group)
        scooter_id_group_sorted = group_scooter.sort_values(by=['timestamp']).reset_index(drop=True)
        len_group_sorted = scooter_id_group_sorted.shape[0]
        # if scooter users with less than 4 records (GPS points) continue
        if len_group_sorted < 4:
            continue
        via_to_list, time, time_temp = [], [], []
        flag = True
        for index_gps, record_gps in scooter_id_group_sorted.iterrows():
            if flag:
                # if flag is true a new bunch of gps records are initialized
                via_to_list.append(record_gps['via_to'])
                # Edge case when only one gps point is have a certain via_to
                if index_gps == len_group_sorted - 1 or scooter_id_group_sorted['via_to'][index_gps + 1] != \
                        scooter_id_group_sorted['via_to'][index_gps]:
                    time.append(record_gps['timestamp'])
                else:
                    time_temp.append(record_gps['timestamp'])
                    # Edge case when the bunch include only  the last two gps points
                    if index_gps + 1 == len_group_sorted - 1:
                        time_temp.append(scooter_id_group_sorted.iloc[index_gps + 1]['timestamp'])
                        time.append(sum(time_temp) / 2)
                        break
                    flag = False
            else:

                next_rec = scooter_id_group_sorted.iloc[index_gps + 1]
                time_temp.append(record_gps['timestamp'])
                # if the next point with same via to save the time
                if record_gps['via_to'] == next_rec['via_to']:
                    # Edge case when the next point is also the last point in the list
                    if index_gps + 1 == len_group_sorted - 1:
                        time_temp.append(next_rec['timestamp'])
                        time.append(sum(time_temp) / len(time_temp))
                        break
                else:
                    # if the next point is not with the current via to point, close the bunch and start a new one
                    time.append(sum(time_temp) / len(time_temp))
                    time_temp = []
                    flag = True
        if len(via_to_list) > 3:
            sco_df.at[name_group, 'via_to_list'] = via_to_list
            sco_df.at[name_group, 'time'] = time
    sco_df = sco_df[sco_df['via_to_list'].notna()]
    sco_df.to_csv("scooter_and_via_to.csv")


def calculate_similarity_sol_2(x):
    # This solution just calculate the ratio between the intersection and union
    set_x = set(x.strip("[]").replace("'", "").split(', '))
    set_y = set(list_via_to_scooter)
    intersection_length = len(set_x & set_y)
    union_length = float(len(set_x | set_y))
    similarity = intersection_length / union_length * 100
    return similarity


def calculate_similarity3(x):

    # Get the mac links as link
    x = x['via_to_list']
    list_via_to_mac = x.strip("[]").replace("'", "").split(', ')
    # if there are at least four identical links between the user scooter to the mac user run the
    # rest of the code
    if len(set(list_via_to_mac) & set(list_via_to_scooter)) < 4:
        return 0
    else:
        grade = 0
        index = 0
        for link in list_via_to_scooter:
            # in each iteration, it  searches the current link in the  'list_via_to_mac' list (from the specified index to the end).
            # When the link is detected in the 'list_via_to_mac' list, the code updates the grade and  index.
            try:
                index = list_via_to_mac.index(link, index) + 1
                grade += 1
            except ValueError:
                continue
    return grade


def calculate_similarity4(x):
    # input

    via_to_mac = np.array(x['via_to_list'].strip("[]").replace("'", "").split(', '))
    time_mac = np.array(x['time'].strip("[]").split(', ')).astype(float)
    # Length data
    len_mac_list = len(via_to_mac)

    if len(set(via_to_mac) & set(via_to_scooter)) < 3 or not (
            (time_mac[0] - 600) <= time_scooter[0] <= (time_mac[-1] + 600) or ((time_scooter[0] - 600) <= time_mac[0] <=
                                                                               (time_scooter[-1] + 600))):
        return 0
    # Find for each link in the scooters links list the same link's index/dices (if any) in the second(mac link) list
    matching_list = list(
        map(lambda itm: [itm[1], itm[0], list(np.where(np.array(via_to_mac) == itm[1])[0])], enumerate(via_to_scooter)))
    # Remove items with no pair from the second list
    result = [pair for pair in matching_list if len(pair[2]) > 0]
    # Examine all the matching links in the results to find sequences
    # i - control matching links to examine ,
    # min_mac_ind_to_check f-  ensures that the code does not look backward to the detected  sequences
    i = 0
    score = 0
    min_mac_ind_to_check = 0
    while i < len(result):
        time_diff = pd.DataFrame(columns=['mac_ind', 'scooter_ind', 'time_diff'])
        i_result = result[i]
        mac_result = i_result[2]
        scooter_ind_local = i_result[1]
        #  The for loop is intended to handle situations where there are more than one match for a certain link.
        #  In that case, the link with the shortest time difference is selected.
        #  Here the algorithm examines the first link in the sequence.
        for mac_ind in mac_result:
            # In two case - continue
            # 1 - When the tested index is found at the end of the via_to,it cannot be the beginning of the sequence.
            # 2 - When the tested index is prior to the index of the last sequence.
            if mac_ind > len_mac_list - 2 or mac_ind < min_mac_ind_to_check:
                continue
            time_diff_temp = abs(time_scooter[scooter_ind_local] - time_mac[mac_ind])
            if time_diff_temp > 600:
                continue
            time_diff = time_diff.append(
                {'mac_ind': mac_ind, 'scooter_ind': scooter_ind_local, 'time_diff': time_diff_temp},
                ignore_index=True)
        # If no matching scooter link with a difference of less than 10 minutes (600 seconds) is found,
        # move on to the next scooter link.
        if time_diff.empty:
            i += 1
            continue
        best_pair = np.argmin(time_diff['time_diff'])
        temp_grade = 1
        in_loop = True
        # Check the next links in respect to the indices of matching links.
        scooter_ind_local = int(time_diff.loc[best_pair]['scooter_ind'] + 1)
        mac_ind_local = int(time_diff.loc[best_pair]['mac_ind'] + 1)
        while in_loop:
            # cases to stop the while loop -the indices exceed the list bounds, next links are not the same,
            # the time difference exceeds the limit of 600 seconds
            if scooter_ind_local < len_scooter_list and mac_ind_local < len_mac_list and via_to_scooter[
                scooter_ind_local] == via_to_mac[mac_ind_local] and abs(
                time_scooter[scooter_ind_local] - time_mac[mac_ind_local]) < 600:
                temp_grade += 1
                scooter_ind_local += 1
                mac_ind_local += 1
            else:
                if temp_grade > 2:
                    # Sequence is found - There are more than three consecutive links
                    score += temp_grade
                    i += temp_grade
                    min_mac_ind_to_check = mac_ind_local
                else:
                    i += 1
                in_loop = False
    if score > 2:
        print('Mac %s : the score is %i' % (x['MAC'], score))
    return score


def find_Mac_route():
    arcpy.env.workspace = os.getcwd()
    arcpy.env.qualifiedFieldNames = False
    # filter_field = 'line_id' or 'via_to_uni' 'MAC
    filter_field = 'MAC'
    # join_field = "via_to" or 'via_to_uni'
    join_field = "via_to_uni"
    # 'file_with_link_clean.csv'/'bt_in_gps_scooter.csv'
    path_to_file = 'bt_in_gps_scooter.csv'
    link_network = "links_network.shp"

    # Join to the links_network
    arcpy.env.workspace = os.getcwd()

    mac_array = ['017FD035A0F4']
    for mac in mac_array:
        print(mac)
        # if the filter_field  is 'line_id' the filter_id is int
        filter_id = mac
        filtered_network = "macs_test/filtered_network" + str(filter_id) + ".shp"
        filtered_file_name = "macs_test_csv/filtered_file" + str(filter_id) + ".csv"
        # Filter _file
        file = pd.read_csv(path_to_file)
        filtered_file = file[file[filter_field] == filter_id]
        filtered_file = filtered_file[
            ['MAC', 'LASTDISCOTS', 'LASTDISCOTS_GMT', 'via_to_uni']]
        filtered_file['LASTDISCOTS_GMT'] = filtered_file['LASTDISCOTS_GMT'].apply(lambda x: x.replace(" ", "_"))
        filtered_file.to_csv(filtered_file_name)

        res = arcpy.AddJoin_management(link_network, "via_to", filtered_file_name, join_field,
                                       join_type='KEEP_COMMON')
        # Alter the properties of a non nullable, short data type field to become a text field
        if arcpy.Exists(filtered_network):
            arcpy.Delete_management(filtered_network)
        arcpy.CopyFeatures_management(res, filtered_network)


def test_Nordeo_Blv(x):
    # this code finds Macs that go through all the  Nordeo links
    list_via_to_mac = x['via_to_list'].strip("[]").replace("'", "").split(', ')
    try:
        index = list_via_to_mac.index(Nordeo_Blv_links[0])
        list_to_compare = list_via_to_mac[index:index + 6]
        if list_to_compare == Nordeo_Blv_links:
            print(x['MAC'])
    except ValueError:
        return


if __name__ == '__main__':
    what_to_run = {'unidirectional': False, 'filter_mac': False, 'test_Mac_with_its_via_to': False,
                   'test_scooter_with_its_via_to': False, 'calculate_similarity': 'sol 4', 'find_Mac_route': False,
                   'test_Nordeo_Blv': [False, False]}
    if what_to_run['unidirectional']:
        test_unidirectional()
    if what_to_run['filter_mac']:
        test_filter_mac()
    # New data frame For each Mac with its via_to's
    if what_to_run['test_Mac_with_its_via_to']:
        test_Mac_with_its_via_to('bt_in_gps_scooter.csv')
    if what_to_run['test_scooter_with_its_via_to']:
        test_scooter_with_its_via_to()

    # For each Scooter route calculate similarity to each mac
    if what_to_run['calculate_similarity'] == 'sol 1':
        # this code is not complete and lack result file
        # test_filter_mac()
        gps_scooter = pd.read_csv('file_with_link_clean.csv')
        bt = pd.read_csv('bt_in_gps_scooter.csv')
        links_list = bt['MAC'].unique()
        # Results file with line_id and the optional Macs
        results = pd.DataFrame(columns=['line_id', 'optional_Macs', 'num_of_matches'])

        sum_df = pd.DataFrame(index=links_list)
        sum_df['agg'] = 0
        # Go over all the routes
        for i, (name, group) in enumerate(gps_scooter.groupby('line_id')):
            sum_df['agg'] = 0
            group_sorted = group.sort_values(by=['timestamp']).reset_index(drop=True)
            # print(group_sorted.head(10))
            time_0 = group_sorted.at[0, 'timestamp']
            # print(time_0)
            for index, record in group_sorted.iterrows():
                if index == 0:
                    continue
                pre_index = group_sorted.iloc[index - 1]
                # print(pre_index)
                cur_via_to = pre_index['via_to']
                if record['via_to'] == cur_via_to:
                    # print(record['via_to'])
                    continue
                else:
                    # print(record['via_to'])
                    temp_bt = bt[bt['via_to_uni'] == cur_via_to]
                    # print(temp_bt.head(10))
                    lastdiscots = temp_bt['LASTDISCOTS']
                    temp_df = temp_bt[
                        (lastdiscots > time_0 - 60) & (lastdiscots < pre_index['timestamp'] + 60)]
                    for index, row in temp_df.iterrows():
                        sum_df.at[row['MAC'], 'agg'] += 1
                    time_0 = record['timestamp']
            # print(sum_df.sort_values(by=['agg'], ascending=False))
        if (sum_df['agg'] > 3).any():
            print(name)
            print(sum_df[sum_df['agg'] > 3])
    if what_to_run['calculate_similarity'] == 'sol 2':
        mac_df = pd.read_csv('mac_df.csv', header=0, names=['MAC', 'via_to_list'])
        gps_scooter = pd.read_csv("scooter_and_via_to.csv", header=0, names=['line_id', 'via_to_list'])
        gps_scooter['high_similarity_mac'] = ''
        gps_scooter['high_similarity_grade'] = ''
        for index, record in gps_scooter.iterrows():
            line_id = record['line_id']
            print(line_id)
            # Convert 'via_to_list' a list
            list_via_to_scooter = record['via_to_list'].strip("[]").replace("'", "").split(', ')
            mac_df[line_id] = mac_df['via_to_list'].apply(lambda x: calculate_similarity_sol_2(x))
            # Store the highest mac matching and the its grade
            maxi = mac_df[line_id].max()
            gps_scooter.at[index, 'high_similarity_grade'] = maxi
            gps_scooter.at[index, 'high_similarity_mac'] = list(mac_df[mac_df[line_id] == maxi]['MAC'])
            # mac_df.sort_values(by=line_id, ascending=False, inplace=True)
        gps_scooter = gps_scooter[gps_scooter['high_similarity_grade'] > 80]
        mac_df.to_csv('res.csv')
    if what_to_run['calculate_similarity'] == 'sol 3':
        print('calculate_similarity sol 3')
        mac_df = pd.read_csv('mac_df.csv', header=0, names=['MAC', 'via_to_list'])
        gps_scooter = pd.read_csv("scooter_and_via_to.csv", header=0, names=['line_id', 'via_to_list'])
        gps_scooter['high_similarity_mac'] = ''
        gps_scooter['high_similarity_grade'] = 0
        for index, record in gps_scooter.iterrows():
            line_id = record['line_id']
            print(line_id)
            # Convert 'via_to_list' a list
            list_via_to_scooter = record['via_to_list'].strip("[]").replace("'", "").split(', ')
            mac_df[line_id] = mac_df.apply(lambda x: calculate_similarity3(x), axis=1)

            # Store the highest mac matching and the its grade
            maxi = mac_df[line_id].max()
            gps_scooter.at[index, 'high_similarity_grade'] = maxi
            gps_scooter.at[index, 'high_similarity_mac'] = list(mac_df[mac_df[line_id] == maxi]['MAC'])

        gps_scooter = gps_scooter[gps_scooter['high_similarity_grade'] > 4]
        mac_df.to_csv('res.csv')
        gps_scooter.to_csv('res_sco.csv')

    if what_to_run['find_Mac_route']:
        print('find_Mac_route')
        find_Mac_route()
    if what_to_run['test_Nordeo_Blv'][0]:
        print('test_Nordeo_Blv')
        if what_to_run['test_Nordeo_Blv'][1]:
            test_Mac_with_its_via_to('file2020-06-01_uni.csv', 'mac_df_all.csv')
        bt = pd.read_csv('mac_df_all.csv', header=0, names=['MAC', 'via_to_list'])
        Nordeo_Blv_links = ['TA2TA257', 'TA13TA2', 'TA13TA39', 'TA262TA39', 'TA262TA78', 'TA137TA78']
        Nordeo_Blv_links.reverse()
        bt.apply(lambda x: test_Nordeo_Blv(x), axis=1)
    if what_to_run['calculate_similarity'] == 'sol 4':
        print('calculate_similarity sol 4')
        mac_df = pd.read_csv('mac_df.csv', header=0, names=['MAC', 'via_to_list', 'time'])
        gps_scooter = pd.read_csv("scooter_and_via_to.csv", header=0, names=['line_id', 'via_to_list', 'time'])
        gps_scooter['high_similarity_mac'] = ''
        gps_scooter['high_similarity_grade'] = 0
        for index, record in gps_scooter.iterrows():
            print("Progress  {:2.1%}".format(index / gps_scooter.shape[0]))
            line_id = record['line_id']
            # Convert 'via_to_list' a list
            via_to_scooter = np.array(record['via_to_list'].strip("[]").replace("'", "").split(', '))

            if len(via_to_scooter) < 10:
                continue
            print(
                'In {} ,the number of links are {} which start at {}'.format(line_id, len(via_to_scooter),
                                                                             datetime.now()))
            time_scooter = np.array(record['time'].strip("[]").split(', ')).astype(float)
            # The length of list_via_to_scooter will be used in calculate_similarity4 method
            len_scooter_list = len(via_to_scooter)
            mac_df[line_id] = mac_df.apply(calculate_similarity4, axis=1)
            # Store the highest mac matching and the its grade
            maxi = mac_df[line_id].max()
            gps_scooter.at[index, 'high_similarity_grade'] = maxi
            gps_scooter.at[index, 'high_similarity_mac'] = list(mac_df[mac_df[line_id] == maxi]['MAC'])
            # mac_df.sort_values(by=line_id, ascending=False, inplace=True)
        gps_scooter = gps_scooter[gps_scooter['high_similarity_grade'] > 0]
        mac_df.to_csv('res_4.csv')
        gps_scooter.to_csv('res_sco_4.csv')
