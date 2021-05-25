import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
# 25.5.2021

# 20.5.2021
# list_1 = ['TA135TA146', 'TA76TA77', 'TA111TA134', 'TA2TA257', 'TA2TA257', 'TA122TA251', 'TA149TA150', 'TA124TA185',
#           'TA104TA257', 'TA257TA36', 'TA81TA83', 'TA150TA151', 'TA122TA251', 'TA55TA76', 'TA149TA150', 'TA55TA76',
#           'TA104TA257', 'TA257TA36', 'TA124TA185', 'TA193TA36', 'TA104TA257', 'TA193TA6', 'TA55TA76', 'TA83TA85',
#           'TA81TA83', 'TA23TA26', 'TA77TA78', 'TA137TA78', 'TA5TA6', 'TA4TA5', 'TA2TA251', 'TA55TA76', 'TA262TA78',
#           'TA77TA78', 'TA76TA77', 'TA124TA185', 'TA149TA150', 'TA150TA328', 'TA146TA184', 'TA112TA79', 'TA2TA257',
#           'TA2TA257', 'TA104TA257', 'TA124TA185', 'TA149TA150', 'TA150TA151', 'TA149TA150', 'TA26TA81', 'TA105TA26',
#           'TA111TA134', 'TA143TA144', 'TA144TA149', 'TA149TA150', 'TA150TA151', 'TA124TA185', 'TA185TA76', 'TA139TA8',
#           'TA83TA85', 'TA136TA146', 'TA26TA81', 'TA23TA26', 'TA83TA85', 'TA105TA83']
# list_2 = ['TA135TA270', 'TA132TA133', 'TA132TA81', 'TA81TA83', 'TA105TA83', 'TA106TA28', 'TA28TA85', 'TA17TA18',
#           'TA16TA17', 'TA16TA22', 'TA22TA23', 'TA23TA26', 'TA105TA26', 'TA105TA83', 'TA83TA85', 'TA28TA85', 'TA109TA85',
#           'TA83TA85', 'TA81TA83', 'TA132TA81', 'TA111TA134']
#
# intersect = len(set(list_1) & set(list_2))
# union = float(len(set(list_1) | set(list_2)))
# print(intersect)
# print(union)
# print(set(list_1) & set(list_2))
#
# print(intersect / union * 100)
# stringA = "['TA112TA262', 'TA78TA79', 'TA79TA80', 'TA183TA80', 'TA183TA81', 'TA111TA81', 'TA111TA83', 'TA83TA85','TA109TA85']"
# res = stringA.strip("[]").replace("'", "").split(', ')
# print(res)
# list_1 = ['TA112TA262', 'TA78TA79', 'TA79TA80', 'TA183TA80', 'TA183TA81', 'TA111TA81', 'TA111TA83', 'TA83TA85',
#           'TA109TA85']
# print(list_1)
# 19.5.2021
# list_1 = ['TA112TA262', 'TA78TA79', 'TA79TA80', 'TA183TA80', 'TA183TA81', 'TA111TA81', 'TA111TA83', 'TA83TA85',
#           'TA109TA85']
# list_2 = ['TA78TA79', 'TA150TA328']
#
# intersect = len(set(list_1) & set(list_2))
# union = float(len(set(list_1) | set(list_2)))
# print(intersect)
# print(union)
# print(set(list_1) & set(list_2))
#
# print(intersect / union * 100)

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
