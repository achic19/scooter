import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score
from sklearn.ensemble import IsolationForest
import math
import pickle
import geopandas as gpd
from sklearn.model_selection import cross_val_score

# For last tree visualisation
import os

os.environ["PATH"] += os.pathsep + r'C:\Program Files\graphviz-2.38\release/bin/'


class Analysis:
    """
    Analysis of BT data with users classification.
    """

    def __init__(self, bt_file: str, folder_path: str, links_shp: str):
        """
        :param bt_file: to be  analysed
        :param folder_path: to store the result derived from each action
        :param links_shp: name of the shape file
        """
        self.bt = pd.read_csv(bt_file)
        self.bt['hour'] = pd.to_datetime(self.bt['isr_time']).dt.hour
        self.folder = folder_path
        self.links = gpd.read_file(self.folder + 'shape_files/' + links_shp)

    def number_for_each_users(self):
        print('number_for_each_users')
        results = pd.DataFrame(self.bt.groupby('user').count()['via_to'])
        results.to_csv(self.folder + 'number_for_each_users.csv')

    def number_per_link(self):
        print('number_per_link')
        # Groupby links and users and aggregate for each group.
        # Change the table so that user type become a column in the result file
        results = pd.DataFrame(self.bt.groupby(['via_to_uni', 'user']).count()['via_to']).rename(
            columns={'via_to': ''}).unstack(
            fill_value=0).reset_index()
        # Work with new data frame to dissolve multiplex columns and change the columns names to more meaningful names
        results = pd.DataFrame(data=results.to_numpy(), columns=results.columns.droplevel(0))
        results.rename(columns={'': 'via_to', 1: 'car', 2: 'scooter', 3: 'pedestrian'}, inplace=True)
        results[['car', 'scooter', 'pedestrian']] = results[['car', 'scooter', 'pedestrian']].astype('int')
        results.to_csv(self.folder + 'number_per_link.csv')

        # merge links with new data
        new_shp = self.links.merge(results, on='via_to', how='right')
        new_shp.to_file(self.folder + 'shape_files/' + 'number_per_link.shp')

    def number_per_hour(self):
        print('number_per_hour')
        # Groupby links and users and aggregate for each group.
        # Change the table so that user type become a column in the result file
        results = pd.DataFrame(self.bt.groupby(['hour', 'user']).count()['via_to']).rename(
            columns={'via_to': ''}).unstack(
            fill_value=0).reset_index()
        # Work with new data frame to dissolve multiplex columns and change the columns names to more meaningful names
        results = pd.DataFrame(data=results.to_numpy(), columns=results.columns.droplevel(0))
        results.rename(columns={'': 'hour', 1: 'car', 2: 'scooter', 3: 'pedestrian'}, inplace=True)
        results.to_csv(self.folder + 'number_per_hour.csv')

    def number_per_link_hour(self):
        print('number_per_link_hour')
        # Groupby links and users and hour and aggregate for each group.
        # Change the table so that user type and hour become a columns in the result file
        results = pd.DataFrame(self.bt.groupby(['via_to_uni', 'user', 'hour']).count()['via_to']).rename(
            columns={'via_to': ''}).unstack(
            fill_value=0).unstack(
            fill_value=0).reset_index()

        # Before  exporting the to csv file arrange the columns name
        # (make it with single index rather than multiple indices)
        results_columns = ['via_to']
        results_columns.extend(['_'.join([str(col[1]), str(col[2])]) for col in results.columns.values[1:]])
        results = pd.DataFrame(data=results.to_numpy(), columns=results.columns.droplevel(['hour', 'user']))
        results.columns = results_columns
        # Change the type of the data
        results_columns.remove('via_to')
        results[results_columns] = results[results_columns].astype('int')
        results.to_csv(self.folder + 'number_per_link_hour.csv')
        # merge links with new data
        new_shp = self.links.merge(results, on='via_to', how='right')
        new_shp.to_file(self.folder + 'shape_files/' + 'number_per_link_hour.shp')


class BT:
    """
       The class is responsible for handling the machine learning aspects of BT data -
        training, testing, validation, and predilection.
    """

    def __init__(self, data_columns: list, filename: str):
        """
        :param data_columns: helps to eliminate superfluous information
        :param filename: where to store the ml model
        """
        self.data_columns = data_columns
        self.filename = filename

    def training(self, users: list, df_all: str, classifier, complex_model, is_save_model, is_tree_visualized=False):
        """
        Apply Machine Learning to BT samples data according to the

        :param classifier
        :param df_all: samples file path
        :param users: 1:car, 2:scooter,3:pedestrian
        :param complex_model: not included cross validator and hyper parameters tuning
        :param is_save_model: not always we want to save the model
        :param is_tree_visualized: visualize the tree as pdf file
        """
        df_all = pd.read_csv(df_all)

        # for each user divide  data to train, validate and test
        df = df_all[df_all['user'] == users[0]][self.data_columns]
        train, test = np.split(df.sample(frac=1, random_state=1), [int(.8 * len(df))])
        for user in users[1:]:
            df = df_all[df_all['user'] == user][self.data_columns]
            train_0, test_0 = np.split(df.sample(frac=1, random_state=1), [int(.8 * len(df))])
            train = train.append(train_0)
            test = test.append(test_0)

        # data for ML

        X = train[self.data_columns[:-1]].to_numpy()
        y = train[self.data_columns[-1]].to_numpy()

        # ML
        if complex_model:
            model = classifier[0]
            cv = ShuffleSplit(n_splits=20, test_size=0.25)
            # MLPClassifier should not be run in conjunction with many processes in order to prevent crushing
            # if isinstance(model, MLPClassifier):
            #     grid_search = GridSearchCV(estimator=model, param_grid=classifier[1], cv=cv, scoring='accuracy',
            #                                error_score=0)
            # else:
            grid_search = GridSearchCV(estimator=model, param_grid=classifier[1], n_jobs=-1, cv=cv,
                                       scoring='accuracy',
                                       error_score=0)
            clf = grid_search.fit(X, y)

            # summarize results
            print("Best: %f using %s" % (clf.best_score_, clf.best_params_))
            means = clf.cv_results_['mean_test_score']
            stds = clf.cv_results_['std_test_score']
            params = clf.cv_results_['params']
            for mean, stdev, param in zip(means, stds, params):
                print("%f (%f) with: %r" % (mean, stdev, param))
        else:
            clf = classifier
            cv = ShuffleSplit(n_splits=20, test_size=0.25, random_state=0)
            cross_val_score(clf, X, y, cv=cv)
            clf.fit(X, y)

        # Test the algorithm
        X_test = test[self.data_columns[:-1]].to_numpy()
        y_true = test[self.data_columns[-1]].to_numpy()
        y_pred = clf.predict(X_test)
        print('confusion_matrix =\n {}'.format(confusion_matrix(y_true, y_pred)))
        print('f1_score micro = {0:.3f}'.format(f1_score(y_true, y_pred, average='micro')))
        print('f1_score  = {}'.format(np.round(f1_score(y_true, y_pred, average=None), 2)))
        print('accuracy_score = {0:.3f}'.format(accuracy_score(y_true, y_pred)))

        # Save the model if it is required
        if is_save_model:
            pickle.dump(clf, open(self.filename, 'wb'))

        if is_tree_visualized:
            estimator = clf.estimators_[-1]

            from sklearn.tree import export_graphviz

            # Export as dot file
            export_graphviz(estimator, out_file='road_users.dot',
                            feature_names=self.data_columns[:-1],
                            class_names=["cars", "scooters", "peds"],
                            rounded=True, proportion=False,
                            precision=2, filled=True)

            # Convert to png using system command (requires Graphviz)
            # Convert a .dot file to .png
            from subprocess import call
            call(['dot', '-Tpdf', 'road_users.dot', '-o', 'road_users.pdf'])
        if isinstance(classifier, (RandomForestClassifier, GradientBoostingClassifier)):
            print('feature_importances = {}'.format(np.round(clf.feature_importances_, 2)))

    def prediction(self, data: str, output: str):
        """
        Make prediction on new data
        :param output: path file to store the results
        :param data: new data with model features
        :return:
        """
        # Upload the new data, save only the features and convert it numpy
        new_data = pd.read_csv(data)
        X = new_data[self.data_columns[:-1]].to_numpy()
        # Upload the training model and run the new data with this model to predict user type
        new_data['user'] = pickle.load(open(self.filename, 'rb')).predict(X)
        new_data.to_csv(output)

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
        self.sensors_names = self.sensors.index.tolist()
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
        # Remove records with incomplete information in fields: 'STDCALC','TOLASTDISCOTS'
        bt_users = pd.read_csv(bt_file)
        bt_users = bt_users[
            (pd.notna(bt_users['STDCALC'])) & (bt_users['TOLASTDISCOTS'] > -1) & (bt_users['OPENTS'] > -1)]

        # For dataframe that  does not include the 'via_to_uni' column
        df_columns = bt_users.columns
        if 'via_to'not in df_columns:
            bt_users['via_to'] = bt_users['VIAUNITC'] + bt_users['TOUNITC']

        if 'via_to_uni' not in df_columns:
            bt_users['via_to_uni'] = bt_users['via_to'].where(bt_users['VIAUNITC'] < bt_users['TOUNITC'],
                                                              bt_users['TOUNITC'] + bt_users['VIAUNITC'])

        columns_to_add = ['via_to', 'via_to_uni']
        if user == 'new_data':
            # tasks in case of new data - delete rows with sensors not in sensors name list
            bt_users = bt_users[
                (bt_users['VIAUNITC'].isin(self.sensors_names)) & (bt_users['TOUNITC'].isin(self.sensors_names))]
            columns_to_add.append('isr_time')

        else:
            # tasks in case of samples file - Update label with numeric values with @user_dic and @user
            user_dic = {'car': 1, 'scooter': 2, 'ped': 3}
            bt_users['user'] = user_dic[user]
            columns_to_add.append('user')

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
        bt_users[['PK_UID'] + self.features_columns + columns_to_add].to_csv(features_file)

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

        # Clean the dataframe and save it as csv file
        features.drop(columns=['via_to_uni', 'via_to', 'Unnamed: 0']).set_index('PK_UID').to_csv(features_file)
