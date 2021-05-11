import os

import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
# 11.5.2021
os.chdir(os.path.realpath('..'))
df = pd.read_csv('csv_files/dates/test/2020_05_31/file2020_05_31.csv', nrows=10)
print(df)
df['gmt'] = pd.DatetimeIndex(df['time']).tz_localize(tz='Israel').tz_convert('GMT')
df['timestamp'] = df['gmt'].map(lambda x: pd.to_datetime(x).timestamp())

df = df.groupby('timestamp').agg(
    {'gmt': 'first', 'OID_': 'first', 'line_id': 'first', 'POINT_X': 'mean', 'POINT_Y': 'mean', }).reset_index()
df['duration'] = ''
df['length'] = ''
df['speed'] = ''
print(df)
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
