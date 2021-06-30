import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest


def create_features():
    from scipy import stats
    bt_scooter = pd.read_csv('bt_scooter.csv')
    print(bt_scooter.shape[0])
    bt_scooter = bt_scooter[(pd.notna(bt_scooter['STDCALC'])) & (bt_scooter['TOLASTDISCOTS'] > -1)]
    print(bt_scooter.shape[0])
    print(bt_scooter.columns)
    features = bt_scooter[['PK_UID', 'LASTDISCOTS', 'STDCALC', 'AVGCALC', 'TRIPTIME', 'via_to', 'via_to_uni']]
    features = features.assign(TRIPTIME2=bt_scooter['CLOSETS'] - bt_scooter['LASTDISCOTS'])
    features['via_to_int'] = ''
    for index, (group_name, group) in enumerate(features.groupby('via_to_uni')):
        temp_index = index
        for group_name2, grpup_temp in group.groupby('via_to'):
            features.loc[features['via_to'] == group_name2, 'via_to_int'] = temp_index
            temp_index = -temp_index
    features.to_csv('features.csv')


def detect_outliers():
    # identify outliers in the training dataset
    features = pd.read_csv('features.csv').drop(columns=['via_to_uni', 'via_to'])
    X_train = features.loc[:, features.columns[1:]].to_numpy()
    iso = IsolationForest(contamination=0.1)
    features['isoutlayer'] = iso.fit_predict(X_train)
    print(features[features['isoutlayer'] == -1].shape[0])
    features.to_csv('detect_outliers.csv')


if __name__ == '__main__':
    params = {'create_features': False, 'detect_outliers': True}
    if params['create_features']:
        print("create features file")
        create_features()

    if params['detect_outliers']:
        print('detect outliers')
        detect_outliers()
