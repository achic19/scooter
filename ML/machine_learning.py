from python_class.ml_classes import *

# parameters
parameters = {'bt_files_to_features': False, 'features_file_to_one_file': False,
              'BT': [False, {'samples': False, 'prepare new data': False, 'prediction': False}],
              'analysis': [True, {'number_for_each_users': False, 'number_per_link': True}]}
features_columns = ['STDCALC', 'AVGCALC', 'TRIPTIME', 'TRIPTIMEab', 'TRIPTIMEbc', 'TRIPTIMEcd', 'Length', 'Azimuth']
sensors_file = 'bt_devics.csv'

bt_to_kl = BtDataToMlData(features_columns, sensors_file, 'output_files')
if parameters['bt_files_to_features']:
    print('bt_files_to_features')
    # Prepare each file separately for later use in ML models
    bt_to_kl.bt_files_to_features('_car.csv', 'output_files/feature_car.csv', 'car')
    bt_to_kl.bt_files_to_features('_ped.csv', 'output_files/feature_ped.csv', 'ped')
    bt_to_kl.bt_files_to_features('_scooter.csv', 'output_files/feature_scooter.csv', 'scooter')

if parameters['features_file_to_one_file']:
    print('features_file_to_one_file')
    features_file = ['output_files/feature_car.csv', 'output_files/feature_ped.csv', 'output_files/feature_scooter.csv']
    BtDataToMlData.features_file_to_one_file(features_file, 'output_files/features.csv')

if parameters['BT'][0]:
    print('BT')
    parameters_loc = parameters['BT'][1]
    bt = BT(features_columns + ['user'])

    if parameters_loc['samples']:
        print('  samples')
        bt.training(users=[1, 2, 3], df_all='output_files/features.csv', classifier=RandomForestClassifier())

    if parameters_loc['prepare new data']:
        print('  prepare new data')
        bt_to_kl.bt_files_to_features('file2020-07-11.csv', 'output_files/new_data.csv', 'new_data')

    if parameters_loc['prediction']:
        print('prediction')
        bt.prediction('output_files/new_data.csv', 'output_files/prediction.csv')

if parameters['analysis'][0]:
    analysis = Analysis(bt_file='output_files/prediction.csv', analysis_file='output_files/analysis.xlsx')
    parameters_loc = parameters['analysis'][1]
    if parameters_loc['number_for_each_users']:
        analysis.number_for_each_users()
    if parameters_loc['number_per_link']:
        analysis.number_per_link()
