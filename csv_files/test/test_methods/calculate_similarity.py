import numpy as np
import pandas as pd

# input
via_to_scooter = np.array([2, 5, 3, 0, 3])
via_to_mac = np.array([2, 5, 3, 0, 3, 2, 5, 8, 10, 11, 15])

time_scooter = np.array([52, 55, 58, 300, 400, 430])
time_mac = np.array([21, 50, 53, 60, 64, 72, 75, 80, 100, 110, 115])
# Length data
len_mac_list = len(via_to_mac)
len_scooter_list = len(via_to_scooter)

# Find for each link in the scooters links list the same link's index/dices (if any) in the second(mac link) list
matching_list = list(
    map(lambda x: [x[1], x[0], list(np.where(np.array(via_to_mac) == x[1])[0])], enumerate(via_to_scooter)))
# Remove items with no pair from the second list
result = [row for row in matching_list if len(row[2]) > 0]
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
    scooter_ind_local = time_diff.loc[best_pair]['scooter_ind'] + 1
    mac_ind_local = time_diff.loc[best_pair]['mac_ind'] + 1
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

print(score)
# for link_mac

# # Driver Code
# print(intersection(list_1, list_to_compare))
# # dict = {key: False for key in inter}
# # print(set(list_1 ).intersection(list_to_compare))
# # for i in range(len(list_1) - 2):
# #     inds_mac = np.where(np.array(list_to_compare) == sub_list[j])[0]
# #     if len(inds_mac) == 0:
# #         not_empty = False
