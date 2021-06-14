import numpy as np
import pandas as pd


def count_line_id(x):
    high_similarity_mac = np.array(x['high_similarity_mac'].strip("[]").replace("'", "").split(', '))
    for mac in high_similarity_mac:
        if mac not in new_dic:
            new_dic[mac] = [[], []]
        new_dic[mac][0].append(x['line_id'])
        new_dic[mac][1].append(x['high_similarity_grade'])


my_pd = pd.read_csv('res_sco_4_test.csv')

print(my_pd)
new_dic = {}
my_pd.apply(lambda x: count_line_id(x), axis=1)
new_df = pd.DataFrame(data=new_dic.values(), index=new_dic.keys(), columns=['line_ids', 'grades'])
print(new_df)
