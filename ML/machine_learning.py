from python_class.ml_classes import *

# parameters
parameters = {'bt_files_to_features': True, 'features_file_to_one_file': False, 'BT': False}
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

if parameters['BT']:
    print('BT')
    bt = BT('output_files/features.csv', [1, 2, 3], features_columns + ['user'], RandomForestClassifier())
