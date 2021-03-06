import os
from feature_normalization import clean_data
from sklearn.model_selection import train_test_split
import hyperparameter_selection as hs
import itertools
import pandas as pd
import common
import json
import time

# contains all the parameter combinations that we want to try
hyperparameters = {
    'min_var': [0.005],  # features' variance in [0,0.015]
    'classifier_type': ['svm'],
    'regularization_parameter': [0.01, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2],  # reg_param > 0
    'kernel': ['rbf', 'poly', 'linear'],
    'poly_degree': [2, 3]
}

# flag for the hyperparameter optimization
optimize_hyperparameters = True

# reading data
dataframe_folder = os.path.join('resources', 'dataframes')
dataframe_path = os.path.join(dataframe_folder, 'extracted_data.csv')
dataframe = pd.read_csv(dataframe_path)

# cleaning the whole dataset
dataframe = clean_data(dataframe)

# separating data
X, y = common.split_Xy(dataframe.values)
X, X_test, y, y_test = train_test_split(X, y)

# this part of the script can be really slow, thus it can
# be turned off with the flag
if optimize_hyperparameters:
    parameters_timer_start = time.time()
    best_parameters = {
        'score': 0
    }

    best_parameters_path = os.path.join('resources', 'parameters', 'best_parameters.json')

    # finds the best parameters
    iteration_counter = 0
    hyperparameters_list = [dict(zip(hyperparameters.keys(), v))
                            for v in itertools.product(*hyperparameters.values())]
    for configuration in hyperparameters_list:
        # console output
        iteration_counter += 1
        print('[[iteration n.' + str(iteration_counter) + ']]')

        # sets the configuration
        # hs.set_configuration(configuration,common.classifier)

        # calculate the score of the configuration
        score = hs.get_configuration_score(configuration, dataframe, X, y)

        if score > best_parameters['score']:
            # updates the best parameters
            best_parameters['score'] = score
            for parameter, value in configuration.items():
                best_parameters[parameter] = value
    print()  # newline

    # stores the best parameters
    with open(best_parameters_path, mode='w') as file:
        json.dump(best_parameters, file)

    # console output
    parameters_execution_time = time.time() - parameters_timer_start
    print('-- parameters optimization completed --',
          'execution time: ' + '{:.2f}'.format(parameters_execution_time) + 's',
          'parameters selected: ',
          best_parameters,
          sep="\n")

# evaluating on validation set
hs.final_test(dataframe, X, y, X_test, y_test)
