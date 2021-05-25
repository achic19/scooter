import os

import arcpy
import pandas as pd

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
    mac_df = pd.DataFrame(columns=['via_to_list'], index=bt['MAC'].unique())
    for group_name, group in bt.groupby('MAC'):
        print(group_name)
        temp_list = list(group['via_to_uni'])
        # Save only macs that traverse more than four links
        if len(temp_list) > 3:
            mac_df.at[group_name, 'via_to_list'] = list(group['via_to_uni'])
    mac_df = mac_df[mac_df['via_to_list'].notna()]
    mac_df.to_csv(file_to_save)


def test_scooter_with_its_via_to():
    print('test_scooter_with_its_via_to')
    gps_scooter = pd.read_csv('file_with_link_clean.csv')
    sco_df = pd.DataFrame(columns=['via_to_list'], index=gps_scooter['line_id'].unique())
    # The code iterates over the GPS trajectories of each scooter route and
    # saves the "via_to" link when the "via link" changes.
    for i, (name, group) in enumerate(gps_scooter.groupby('line_id')):
        print(name)
        group_sorted = group.sort_values(by=['timestamp']).reset_index(drop=True)
        via_to_list = []
        for index, record in group_sorted.iterrows():
            if index == 0:
                continue
            pre_index = group_sorted.iloc[index - 1]
            cur_via_to = pre_index['via_to']
            if record['via_to'] == cur_via_to:
                continue
            else:
                via_to_list.append(pre_index['via_to'])

            # A case where the last index is different from the previous one or group with one element.
        if group_sorted['via_to'].size == 1 or group_sorted['via_to'].iloc[-1] != group_sorted['via_to'].iloc[-2]:
            via_to_list.append(group_sorted['via_to'].iloc[-1])

        if len(via_to_list) > 4:
            sco_df.at[name, 'via_to_list'] = via_to_list
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


def calculate_similarity(x):
    # Todo prove the '4' value
    # Get the mac links as link
    mac_name = x['MAC']
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

    mac_array = ['61B0AD47E1DE', '017FD0527EF8']
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
    list_via_to_mac = x.strip("[]").replace("'", "").split(', ')
    try:
        index = list_via_to_mac.index(Nordeo_Blv_links[0])
        list_to_compare = list_via_to_mac[index, ]

    except ValueError:
        return


if __name__ == '__main__':
    what_to_run = {'calculate_similarity': False, 'find_Mac_route': False, 'test_Nordeo_Blv': True}
    # test_unidirectional()
    # input data
    # test_filter_mac()
    # New data frame For each Mac with its via_to's
    # test_Mac_with_its_via_to('bt_in_gps_scooter.csv')
    # test_scooter_with_its_via_to()

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
        print('calculate_similarity')
        mac_df = pd.read_csv('mac_df.csv', header=0, names=['MAC', 'via_to_list'])
        gps_scooter = pd.read_csv("scooter_and_via_to.csv", header=0, names=['line_id', 'via_to_list'])
        gps_scooter['high_similarity_mac'] = ''
        gps_scooter['high_similarity_grade'] = 0
        for index, record in gps_scooter.iterrows():
            line_id = record['line_id']
            print(line_id)
            # Convert 'via_to_list' a list
            list_via_to_scooter = record['via_to_list'].strip("[]").replace("'", "").split(', ')
            mac_df[line_id] = mac_df.apply(lambda x: calculate_similarity(x), axis=1)
            # mac_df[line_id] = mac_df['via_to_list'].apply(lambda x: calculate_similarity(x))
            # Store the highest mac matching and the its grade
            maxi = mac_df[line_id].max()
            gps_scooter.at[index, 'high_similarity_grade'] = maxi
            gps_scooter.at[index, 'high_similarity_mac'] = list(mac_df[mac_df[line_id] == maxi]['MAC'])
            # mac_df.sort_values(by=line_id, ascending=False, inplace=True)
        gps_scooter = gps_scooter[gps_scooter['high_similarity_grade'] > 4]
        mac_df.to_csv('res.csv')
        gps_scooter.to_csv('res_sco.csv')

    if what_to_run['find_Mac_route']:
        print('find_Mac_route')
        find_Mac_route()
    if what_to_run['test_Nordeo_Blv']:
        print('test_Nordeo_Blv')
        test_Mac_with_its_via_to('file2020-06-01_uni.csv', 'mac_df_all.csv')
        bt = pd.read_csv('mac_df_all.csv')
        Nordeo_Blv_links = ['TA2TA257', 'TA13TA2', 'TA13TA39', 'TA262TA39', 'TA262TA78', 'TA137TA78']
        bt.apply(lambda x: test_Nordeo_Blv(x), axis=1)
