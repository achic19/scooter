from python_class.ml_classes import *
from python_class.algorithm_dictionary import algorithm_dictionary, which_algorithm_to_run
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier


# my parameters
# samples = complex\simple - if the selected method for training is simple,
# you should send the name of the model with its hyper parameters
parameters = {'bt_files_to_features': False, 'features_file_to_one_file': False,
              'BT': [True,
                     {'samples': [True, {
                         'simple': RandomForestClassifier(n_estimators=100, max_features='log2')}],
                      'prepare new data': False, 'prediction': False}],
              'analysis': [False, {'number_for_each_users': True, 'number_per_link': True, 'number_per_hour': True,
                                   'number_per_link_hour': True}]}
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
    bt = BT(features_columns + ['user'], 'output_files/ml.sav')

    if parameters_loc['samples'][0]:
        print('  samples')
        if list(parameters_loc['samples'][1].keys())[0] == 'complex':
            for alg in which_algorithm_to_run:
                item = algorithm_dictionary[alg]
                print(item[0])
                bt.training(users=[1, 2, 3], df_all='output_files/features.csv', classifier=item,
                            complex_model=True,
                            is_save_model=False)

        else:
            print(parameters_loc['samples'][1].values())
            bt.training(users=[1, 2, 3], df_all='output_files/features.csv',
                        classifier=list(parameters_loc['samples'][1].values())[0],
                        complex_model=False,
                        is_save_model=True,
                        is_tree_visualized=True)

    if parameters_loc['prepare new data']:
        print('  prepare new data')
        bt_to_kl.bt_files_to_features('file2020-07-08.csv', 'output_files/new_data.csv', 'new_data')

    if parameters_loc['prediction']:
        print('  prediction')
        bt.prediction('output_files/new_data.csv', 'output_files/prediction.csv')

if parameters['analysis'][0]:
    analysis = Analysis(bt_file='output_files/prediction.csv', folder_path='output_files/analysis/',
                        links_shp='links.shp')
    parameters_loc = parameters['analysis'][1]
    if parameters_loc['number_for_each_users']:
        analysis.number_for_each_users()
    if parameters_loc['number_per_link']:
        analysis.number_per_link()
    if parameters_loc['number_per_hour']:
        analysis.number_per_hour()
    if parameters_loc['number_per_link_hour']:
        analysis.number_per_link_hour()
