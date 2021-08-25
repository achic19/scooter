from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_validate
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC

# ML algorithms with hyper parameters to build the grid for hyper parameters optimization
# This code is based on - sklearn:
# https://machinelearningmastery.com/hyperparameters-for-classification-machine-learning-algorithms/
algorithm_dictionary = {'random forest': [RandomForestClassifier(),
                                          dict(n_estimators=[10, 100, 1000], max_features=['sqrt', 'log2'])],
                        'SVM': [SVC(),
                                dict(kernel=['poly', 'rbf', 'sigmoid'], C=[50, 10, 1.0, 0.1, 0.01], gamma=['scale'])],
                        'GB': [GradientBoostingClassifier(),
                               dict(learning_rate=[0.001, 0.01, 0.1], n_estimators=[10, 100, 1000],
                                    subsample=[0.5, 0.7, 1.0], max_depth=[3, 7, 9])],
                        'RidgeClassifier': [
                            RidgeClassifier(), dict(alpha=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])],
                        'LogisticRegression': [LogisticRegression(),
                                               dict(solver=['newton-cg', 'lbfgs', 'liblinear'], penalty=['l2'],
                                                    C=[100, 10, 1.0, 0.1, 0.01])],
                        'BaggingClassifier': [BaggingClassifier(), dict(n_estimators=[10, 100, 1000])],
                        'ANN': [MLPClassifier(), dict(activation=['identity', 'logistic', 'tanh', 'relu'],
                                                      hidden_layer_sizes=[(i, j) for i in range(1, 101, 10) for j in
                                                                          range(1, 101, 10)])]}
which_algorithm_to_run = ['random forest', 'SVM', 'GB', 'RidgeClassifier', 'LogisticRegression', 'BaggingClassifier',
                          'ANN']
