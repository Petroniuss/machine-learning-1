import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import interp
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, roc_curve, accuracy_score, recall_score, precision_score
from sklearn.model_selection import KFold, RepeatedKFold
from tabulate import tabulate
from sklearn.neighbors import KNeighborsClassifier

from matplotlib import pyplot

menu_dataset_dir = 'datasets/covid.csv'
goal_column = 'If a vaccine to prevent COVID-19 was offered to you today, would you choose to be vaccinated?'


def load_dataset(dataset_dir):
    print('Entire dataset')
    df = pd.read_csv(dataset_dir)

    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

    column_names_to_pop = [
        'Timestamp',
        'CITY',
        'Country',
        'STATE',
        'Are you above 18 Years of Age. ',

        'Would you be more likely or less likely to have a COVID-19 vaccination if it was recommended to you by each '
        'of the following: [WHO]',

        'Would you be more likely or less likely to have a COVID-19 vaccination if it was recommended to you by each '
        'of the following: [Politicians]',

        'Would you be more likely or less likely to have a COVID-19 vaccination if it was recommended to you by each '
        'of the following: [Government Health Officials]',

        'Would you be more likely or less likely to have a COVID-19 vaccination if it was recommended to you by each '
        'of the following: [Doctors & Healthcare Staff ]',

        'Would you be more likely or less likely to have a COVID-19 vaccination if it was recommended to you by each '
        'of the following: [Friends and Fa,ily]',

        'How concerned are you that you would experience a side effect from a COVID-19 vaccination?',
    ]

    for name in column_names_to_pop:
        df.pop(name)

    def normalize_goal_column(v):
        if v.startswith("Yes"):
            return 1.0
        else:
            return 0.0

    df[goal_column] = df[goal_column].apply(normalize_goal_column)

    print('After filtering')
    print(tabulate(df.head(), headers='keys', tablefmt='psql'))
    print('Goal values')
    print(df[goal_column].value_counts())

    return df


def clean_df(df: pd.DataFrame):
    cleanup_yes_no = {
        "YES": 1.0,
        "Yes": 1.0,
        "No": 0.0,
        "NO": 0.0,
        "Maybe": 0.0
    }

    yes_no_columns = [
        'EYE PAIN',
        'CHEST PAIN',
        'SOAR THROAT',
        'STUFFY/RUNNY NOSE',
        'WEAKNESS FATIGUE',
        'Aches/ Muscle Pain',
        'Headache',
        'Cough',
        'Difficulty in Breathing',
        'Change in Sleep Cycle',

        'Do you personally know anyone in your local community who is ill with a fever and either a cough or '
        'difficulty breathing?',

        'Have you ever been tested for coronavirus (COVID-19)?',
        'Have you been tested for coronavirus (COVID-19) in the last 14 days?',

        'If you have been tested, did this test find that you had coronavirus (COVID-19)?',

        'Did you have to pay anything for this test yourself?',

        'In the last 24 hours, have you done any of the following? [Have gone to work outside that place where you '
        'live]',

        'In the last 24 hours, have you done any of the following? [Gone to Supermarket or Pharmacy]',

        'In the last 24 hours, have you done any of the following? [Gone to Restaurant/CAFE/Shopping Center]',

        'In the last 24 hours, have you done any of the following? [Spent time with someone who is currently not '
        'staying with you.]',

        'In the last 24 hours, have you done any of the following? [Attended public meet with more than 10 people]',

        'In the last 24 hours, have you done any of the following? [You were present in the crowded place of more '
        'than 7 people]',

        'In the last 24 hours, have you done any of the following? [Have used Public Transport]',

        'In the last 24 hours, have you done any of the following? [You were at Home.]',

        'In the last 24 hours, have you done any of the following? [None of the above]',

        'DO YOU SMOKE ?',

        'Do you access to Sanitizer/Hand wash at workplace',

        'Do you access to Sanitizer/Hand wash at Home'
    ]

    cleanup_dict = {col_name: cleanup_yes_no for col_name in yes_no_columns}

    df.pop('For how many days have you had at least one of these symptoms?')
    df.replace(cleanup_dict, inplace=True)

    disease_col = 'HAVE YOU EVER BEEN SUFFERED WITH THE BELOW MENTIONED DISEASES (OR) ARE YOU SUFFURING FROM ANY OF ' \
                  'THE DISEASES BELOW.'

    df[disease_col] = df[disease_col].apply(lambda x: str(x).replace(', ', ','))

    one_hot_df = df[disease_col].str.get_dummies(sep=',')
    one_hot_df.pop('nan')
    one_hot_df.pop('NONE OF THE ABOVE')

    df.pop(disease_col)
    df = pd.concat([df, one_hot_df], axis=1)

    mask_freq_col = 'In last 24 Hours When Ever you stepped outside your personal premises, How often have you used ' \
                    'mask/face cover.'
    freq_dict = {
        'Always': 4.0,
        'Often': 3.0,
        'Sometimes': 2.0,
        'Rarely': 1.0,
        'Never': 0.0
    }

    age_column = 'AGE BAND'
    age_dict = {
        "18-25": 0.0,
        "26-32": 1.0,
        "41-45": 2.0,
        "33-40": 3.0,
        "46-55": 4.0,
        ">60": 5.0
    }

    gender_column = 'GENDER'
    gender_dict = {
        'Male': 0.0,
        'Female': 1.0,
        'Prefer not to say': 0.5
    }

    alcohol_col = 'ALCHOHOL CONSUMPTION'
    alcohol_dict = {
        'NEVER': 0.0,
        'SOCIALLY': 1.0,
        'ONE OR TWICE1 A WEEK': 2.0
    }

    avoid_contact = 'How often are you intentionally avoiding contact with other people?'
    avoid_contact_dict = {
        'All the time': 3.0,
        'Most of the time': 2.0,
        'Some of the time': 1.0,
        'None of the time': 0.0,
        'Option 2': 1.0
    }

    df.replace({
        age_column: age_dict,
        mask_freq_col: freq_dict,
        gender_column: gender_dict,
        alcohol_col: alcohol_dict,
        avoid_contact: avoid_contact_dict
    }, inplace=True)

    df.fillna(0, inplace=True)
    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

    return df


def k_fold(repeats=10):
    return RepeatedKFold(n_splits=5, n_repeats=repeats)


def knn_classifier():
    return KNeighborsClassifier(n_neighbors=5)


def rf_default_classifier():
    return RandomForestClassifier(n_estimators=100)


def rf_all_traits_classifier():
    return RandomForestClassifier(n_estimators=100, bootstrap=False, max_features=None)


def plot_roc_curve(fpr, tpr, clf_name):
    plt.plot([0, 1], [0, 1], 'k--')
    plt.plot(fpr, tpr, label='Knn')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'{clf_name} - ROC curve')
    plt.show()


def eval_clf(X, y, clf, clf_name, repeats=5, show_importance=False, df=None):
    tprs = []
    accuracy = []
    recalls = []
    precisions = []

    base_fpr = np.linspace(0, 1, 101)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot()

    # print mean score
    model = None
    for train, test in k_fold(repeats).split(X, y):
        model = clf.fit(X[train], y[train])
        y_score = model.predict_proba(X[test])

        y_predicted_labels = model.predict(X[test])

        score = accuracy_score(y[test], y_predicted_labels)
        recall = recall_score(y[test], y_predicted_labels)
        precision = precision_score(y[test], y_predicted_labels)

        fpr, tpr, _ = roc_curve(y[test], y_score[:, 1])

        plt.plot(fpr, tpr, 'b', alpha=0.05)
        tpr = interp(base_fpr, fpr, tpr)
        tpr[0] = 0.0
        fpr[0] = 0.0
        tprs.append(tpr)

        accuracy.append(score)
        precisions.append(precision)
        recalls.append(recall)

    tprs = np.array(tprs)
    accuracy = np.array(accuracy)
    recalls = np.array(recalls)
    precisions = np.array(precisions)

    ax.text(0.95, 0.01, f'Recall: {recalls.mean():.2f}\u00B1{recalls.std():.2f}, '
                        f'Accuracy: {accuracy.mean():.2f}\u00B1{accuracy.std():.2f}, '
                        f'Precision: {precisions.mean():.2f}\u00B1{precisions.std():.2f}',
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes,
            color='green', fontsize=18)

    mean_score = accuracy.mean(axis=0)
    mean_tprs = tprs.mean(axis=0)
    std = tprs.std(axis=0)

    tprs_upper = np.minimum(mean_tprs + std, 1)
    tprs_lower = mean_tprs - std

    plt.plot(base_fpr, mean_tprs, 'b')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.fill_between(base_fpr, tprs_lower, tprs_upper, color='grey', alpha=0.3)

    plt.title(f'{clf_name} - ROC', fontsize=36)
    plt.ylabel('True Positive Rate', fontsize=24)
    plt.xlabel('False Positive Rate', fontsize=24)
    plt.show()

    if show_importance:
        importance = model.feature_importances_
        xs = sorted(enumerate(importance), key=lambda x: x[1], reverse=True)
        values = []
        names = []

        for i, v in xs[:5]:
            name = df.columns[i]
            names.append(name)
            values.append(v)

        data = pd.DataFrame({
            "values": values
        }, index=names)

        data.plot(kind='barh', figsize=(14, 5))
        plt.title('Most important features for RF')
        plt.subplots_adjust(wspace=3.2, left=0.5, right=0.95)
        plt.xlabel('Feature importance')
        plt.ylabel('Features')
        plt.show()


def toNumpy(df):
    X, y = df.drop(columns=[goal_column]), df[goal_column]
    X = np.asarray(X, dtype=np.float64)

    # Let's revert what we're trying to predict :)
    y = 1 - np.asarray(y, dtype=np.float64)

    return X, y


def eval_knn_subset(df):
    cols_subset = \
        ['EYE PAIN',
         'CHEST PAIN',
         'SOAR THROAT',
         'STUFFY/RUNNY NOSE',
         'WEAKNESS FATIGUE',
         'Aches/ Muscle Pain',
         'Headache',
         'Cough',
         'Difficulty in Breathing',
         'Change in Sleep Cycle'
         ] + \
        ['AGE BAND',
         'ASTHAMA',
         'HIGH BLOOD PRESSURE',
         'OBESITY',
         'WEEKEND IMMUNE SYSTEM'
         ] + ['In last 24 Hours When Ever you stepped outside your personal premises, How often have you used '
              'mask/face cover.'] + \
        [goal_column]

    df = df[cols_subset]

    X, y = toNumpy(df)
    knn_clf = knn_classifier()

    eval_clf(X, y, knn_clf, 'kNN - subset')
    pass


def eval_knn_all(df):
    X, y = toNumpy(df)
    knn_clf = knn_classifier()

    eval_clf(X, y, knn_clf, 'kNN - all fields')


def eval_rf_default(df):
    X, y = toNumpy(df)
    rf_clf = rf_default_classifier()

    eval_clf(X, y, rf_clf, 'RF - default ', show_importance=True, df=df)


def eval_rf_all_traits(df):
    X, y = toNumpy(df)
    rf_clf = rf_all_traits_classifier()

    eval_clf(X, y, rf_clf, 'RF - all traits ')


def main():
    df = clean_df(load_dataset(menu_dataset_dir))

    eval_knn_all(df)

    eval_knn_subset(df)

    eval_rf_default(df)

    eval_rf_all_traits(df)


if __name__ == '__main__':
    main()
