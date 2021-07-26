import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import IsolationForest
import math


class BT:
    def __init__(self, df_all: str, users: list, data_columns: list, classifier):
        """
        Apply Machine Learning to BT data according to the :param classifier
        :param df_all: samples file path
        :param users: 1:car, 2:scooter,3:pedestrian
        :param data_columns: helps to eliminate superfluous information
        """
        # for each user divide  data to train, validate and test
        df_all = pd.read_csv(df_all)
        df = df_all[df_all['user'] == users[0]][data_columns]
        train, validate, test = np.split(df.sample(frac=1), [int(.6 * len(df)), int(.8 * len(df))])

        for user in users[1:]:
            df = df_all[df_all['user'] == user][data_columns]
            train_0, validate_0, test_0 = np.split(df.sample(frac=1), [int(.6 * len(df)), int(.8 * len(df))])
            train = train.append(train_0)
            validate = validate.append(validate_0)
            test = test.append(test_0)

        # data for ML
        X = train[data_columns[:-1]].to_numpy()
        y = train[data_columns[-1]].to_numpy()

        # test for ML
        test = validate.append(test)
        X_test = test[data_columns[:-1]].to_numpy()
        y_true = test[data_columns[-1]].to_numpy()

        # ML
        clf = classifier
        clf.fit(X, y)

        # Evaluation
        y_pred = clf.predict(X_test)
        print('confusion_matrix =\n {}'.format(confusion_matrix(y_true, y_pred)))
        print('f1_score micro = {0:.3f}'.format(f1_score(y_true, y_pred, average='micro')))
        print('f1_score  = {}'.format(np.round(f1_score(y_true, y_pred, average=None), 2)))
        print('accuracy_score = {0:.3f}'.format(accuracy_score(y_true, y_pred)))
        if isinstance(classifier, RandomForestClassifier):
            print('feature_importances = {}'.format(np.round(clf.feature_importances_, 2)))

        # print(clf.score(validate[data_columns[:-1]].to_numpy(), validate[data_columns[-1]].to_numpy()))
        # print(clf.score(train[data_columns[:-1]].to_numpy(), train[data_columns[-1]].to_numpy()))


class BtDataToMlData:
    """
    The class prepares  BT data for machine learning models
    """

    def __init__(self, features_columns: list, sensors_file: str, path: str):
        """
        The next parameters are used to initialize the class instance -
        :param features_columns: the features that will be used for the ML model
        :param sensors_file: sensors locations file path
        :param path: output folder path
        """
        self.features_columns = features_columns
        self.sensors = pd.read_csv(sensors_file, index_col='Name')[['POINT_X', 'POINT_Y']]
        self.output_folder = path

    def detect_outliers(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Find outliers in :param features for bt_scooter:
        :param features: features before outliers removal
        :return: features after removing outliers
        """
        # identify outliers in the training dataset of bt scooter
        print('   ' + 'Find outliers in :param features ( based on :param features_columns) for bt_scooter')
        stat_list = []
        # Iteratively identify outliers.
        # The code removes 50% of the data from the remaining records during each iteration.
        for i in [1, 2, 3]:
            print(i)
            X_train = features[self.features_columns]
            stat_list.append(list(X_train.mean()))
            stat_list.append(list(X_train.std()))
            iso = IsolationForest(contamination=0.5)
            features['isoutlayer'] = iso.fit_predict(X_train)
            features = features[features['isoutlayer'] == 1]
            features = features.drop(columns='isoutlayer', axis=1)
        pd.DataFrame(stat_list, columns=self.features_columns).to_csv(self.output_folder + '\stat_outliers.csv')
        return features

    def calculate_azimuth_distance(self, row):
        """
        Calculate azimuth and distance between two sensors.
        :param row: includes the name of the sensors to calculate the distance and azimuth
        """
        via_cor = self.sensors.loc[row['VIAUNITC']]
        to_cor = self.sensors.loc[row['TOUNITC']]
        distance = ((to_cor[0] - via_cor[0]) ** 2 + (to_cor[1] - via_cor[1]) ** 2) ** 0.5
        azimuth = math.degrees(math.atan2(to_cor[0] - via_cor[0], to_cor[1] - via_cor[1]))
        if azimuth < 0:
            azimuth += 360
        return pd.Series([distance, azimuth])

    def bt_files_to_features(self, bt_file: str, features_file: str, user: str):
        """
        Prepare each file separately for later use in ML models
        :param user: on the following: {'car': 1, 'scooter': 2, 'ped': 3}
        :param bt_file: bt file path
        :param features_file: path to output file
        """
        print('   ' + user)
        user_dic = {'car': 1, 'scooter': 2, 'ped': 3}
        # Remove records with incomplete information in fields: 'STDCALC','TOLASTDISCOTS'
        bt_users = pd.read_csv(bt_file)
        bt_users = bt_users[
            (pd.notna(bt_users['STDCALC'])) & (bt_users['TOLASTDISCOTS'] > -1) & (bt_users['OPENTS'] > -1)]

        # For dataframe that  does not include the 'via_to_uni' column
        df_columns = bt_users.columns
        if 'via_to_uni' not in df_columns:
            bt_users['via_to_uni'] = bt_users['via_to'].where(bt_users['VIAUNITC'] < bt_users['TOUNITC'],
                                                              bt_users['TOUNITC'] + bt_users['VIAUNITC'])
        # Update label with numeric values with @user_dic and @user
        bt_users['user'] = user_dic[user]

        # Create new feature based on 'CLOSETS' and 'LASTDISCOTS' columns,

        bt_users['TRIPTIMEab'] = bt_users['LASTDISCOTS'] - bt_users['OPENTS']
        bt_users['TRIPTIMEbc'] = bt_users['CLOSETS'] - bt_users['LASTDISCOTS']
        bt_users['TRIPTIMEcd'] = bt_users['TOLASTDISCOTS'] - bt_users['CLOSETS']

        # create 'Length" and "azimuth" features
        bt_users['Length'], bt_users['Azimuth'] = '', ''
        bt_users[['Length', 'Azimuth']] = bt_users.apply(self.calculate_azimuth_distance, axis=1)
        # for scooter apply outliers algorithm
        if user == 'scooter':
            bt_users = self.detect_outliers(bt_users)
        # Save only relevant columns for the next processing
        bt_users[['PK_UID'] + self.features_columns + ['via_to', 'via_to_uni', 'user']].to_csv(features_file)

    @staticmethod
    def features_file_to_one_file(file_array: list, features_file: str):
        """
        Form one features file out of a list of different files, each with a different user.
        In addition convert 'via_to' name link to numbers
        :param file_array: list of features files to append
        :param features_file: the output file path
        """
        features = pd.read_csv(file_array[0])
        for file in file_array[1:]:
            features = features.append(pd.read_csv(file), ignore_index=True)

        features['via_to_int'] = ''
        # Group_by_via_to_uni
        for index, (group_name, group) in enumerate(features.groupby('via_to_uni')):
            temp_index = index
            for group_name2, grpup_temp in group.groupby('via_to'):
                # The same links and opposite directions will have the same number but with a opposite sign
                features.loc[features['via_to'] == group_name2, 'via_to_int'] = temp_index
                temp_index = -temp_index
        # Clean the dataframe and save it as csv file
        features.drop(columns=['via_to_uni', 'via_to', 'Unnamed: 0']).set_index('PK_UID').to_csv(features_file)

# class MlObjects:
