from time import time

import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

# 19.5.2021
# 18.5.2021
# df = pd.read_csv(r'D:\Users\Technion\Sagi Dalyot - AchituvCohen\post_doc\scooter\csv_files\points_in_clip.csv')
# links_list = df['line_id'].unique()
# print(len(links_list))

# 12.5.2021
# def count_complexity(to, via):
#     if via > to:
#         return to + via
#     else:
#         return via + to
#
#
# t1 = time()
# df = pd.read_csv(
#     r'D:\Users\Technion\Sagi Dalyot - AchituvCohen\post_doc\scooter\csv_files\dates\test\2020_06_01\file_with_link_clean.csv')
# for index, row in df.iterrows():
#     if row['VIA'] > row['TO']:
#         df.at[index, 'via_to'] = row['TO'] + row['VIA']
#
# df['via_to'] = df.apply(
#     lambda x: count_complexity(x['TO'], x['VIA']), axis=1)
#     df.where(df['VIA'] > df['TO'], df['TO'] + df['VIA'], inplace=True)
# print(time() - t1)
# 11.5.2021
# os.chdir(os.path.realpath('..'))
# df = pd.read_csv('csv_files/dates/test/2020_05_31/file2020_05_31.csv', nrows=10)
# print(df)
# df['gmt'] = pd.DatetimeIndex(df['time']).tz_localize(tz='Israel').tz_convert('GMT')
# df['timestamp'] = df['gmt'].map(lambda x: pd.to_datetime(x).timestamp())
#
# df = df.groupby('timestamp').agg(
#     {'gmt': 'first', 'OID_': 'first', 'line_id': 'first', 'POINT_X': 'mean', 'POINT_Y': 'mean', }).reset_index()
# df['duration'] = ''
# df['length'] = ''
# df['speed'] = ''
# print(df)
# file = pd.read_csv('csv_files/points_in_clip.csv')
# hh = 0
# 6.5.2021

# string = 'MyProject10/test/points_in_clip_samples.shp'
# print(str.replace(string,'.shp',""))
# print(os.path.split('MyProject10/test/points_in_clip_samples.shp'))
# os.chdir(os.path.realpath('..'))
# What to run
# what_to_run = [0,]
# # 1 - Clip the input to clip shape file polygon layer of the links area
# if True in what_to_run  or 1 in what_to_run:
#     print ('True')

#
# df = pd.read('MyProject10/test/points_test.csv')
# data_time = pd.DatetimeIndex(df['time'])
# df['date'] = data_time.date
# print(df['date'])
