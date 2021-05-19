import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


# add unidirectional route to bt
def test_unidirectional():
    bt = pd.read_csv('file2020-06-01.csv')
    bt['via_to'] = bt['VIAUNITC'] + bt['TOUNITC']
    bt['via_to_uni'] = bt['via_to'].where(bt['VIAUNITC'] < bt['TOUNITC'], bt['TOUNITC'] + bt['VIAUNITC'])
    bt.to_csv('file2020-06-01_uni.csv')


def test_Mac_with_its_via_to():
    bt = pd.read_csv('bt_in_gps_scooter.csv')
    mac_df = pd.DataFrame(columns=['via_to_list'], index=bt['MAC'].unique())
    for group_name, group in bt.groupby('MAC'):
        mac_df.at[group_name, 'via_to_list'] = list(group['via_to_uni'])
    mac_df.to_csv('mac_df.csv')


def test_scooter_with_its_via_to():
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

        sco_df.at[name, 'via_to_list'] = via_to_list
    sco_df.to_csv("scooter_and_via_to.csv")


if __name__ == '__main__':
    # test_unidirectional()
    # input data
    test_scooter_with_its_via_to()
    # New data frame For each Mac with its via_to's
    # test_Mac_with_its_via_to()

    # For each Scooter route calculate similarity to each mac
    # mac_df = pd.read_csv('mac_df.csv')
    # gps_scooter = pd.read_csv("scooter_and_via_to.csv")
    # for scooter_id, group in gps_scooter.groupby('line_id'):לעדבן
    #     list_via_to_scooter = list(group['via_to'])
    #     print(list_via_to_scooter)
    #     mac_df[scooter_id] = mac_df['via_to_list'].apply(lambda x: len(set(x) & set(list_via_to_scooter)) / float(
    #         len(set(x) | set(list_via_to_scooter))) * 100)
    #     print(mac_df.sort_values(by=scooter_id, ascending=False))
    #     break
