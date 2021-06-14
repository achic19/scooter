import pandas as pd

gps_scooter_temp = pd.DataFrame()
gps_scooter_temp['via_to'] = [1, 2, 2, 3, 4, 5, 5]
gps_scooter_temp['timestamp'] = [30, 45, 48, 55, 75, 77, 90]
gps_scooter_temp['line_id'] = 1
sco_df = pd.DataFrame(columns=['via_to_list', 'time'], index=gps_scooter_temp['line_id'].unique())
# The code iterates over the GPS trajectories of each scooter route and
# saves the "via_to" link when the "via link" changes.
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

print(sco_df)
