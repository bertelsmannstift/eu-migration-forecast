""" Functions to build the data pipeline for the forecast """


from eumf_data import Labeled
from sklearn import model_selection
import eumf_data
import numpy as np
from typing import Optional, Union
import pandas as pd
from sklearn import compose, preprocessing, ensemble, pipeline

cv_default = model_selection.KFold(n_splits=6, shuffle=False)
cv_stratified = model_selection.KFold(n_splits=6, shuffle=True, random_state=42)

LabeledTuple = tuple[Labeled, Labeled]


def prepare_data(
    panel: pd.DataFrame,
    columns: list = ["19"],
    lags=[1, 2, 3, 4],
    t_min="2011",
    t_max="2019",
) -> Labeled:

    panel_lags = eumf_data.create_lags(panel, lags=lags, columns=columns).fillna(
        0.0
    )

    # define x, y; set minimum value
    x = panel_lags.applymap(lambda x: max(x, 0.1))
    y = panel["value"]

    return Labeled(x, y)[t_min:t_max]


def transform_data(data_in: Labeled, delta=4) -> Labeled:
    # transformation: logdiff

    x = np.log(data_in.x) - np.log(data_in.x.shift(delta))
    y = np.log(data_in.y) - np.log(data_in.y.shift(delta))

    return Labeled(x.iloc[delta:], y.iloc[delta:])


def split_data(
    data_in: Labeled, t_test_min="2018-01-01", t_test_max="2019-12-01",
) -> LabeledTuple:

    # t_min = "2012-01-01"
    # t_max = "2019-12-01"
    # t_split_lower = "2017-12-01"
    # t_split_upper = "2018-01-01"

    # train = data_in[t_min:t_split_lower]
    # test = data_in[t_split_upper:t_max]

    test = data_in[t_test_min:t_test_max]
    train = Labeled(data_in.x.drop(test.index), data_in.y.drop(test.index))
    # train = data_in.apply(lambda df: df.drop(test.index))

    return train, test


def stack_data(
    train: Labeled, test: Optional[Labeled] = None
) -> Union[LabeledTuple, Labeled]:
    # stacking
    if test is None:
        train = eumf_data.stack_labeled(train)
        return train
    else:
        train = eumf_data.stack_labeled(train)
        test = eumf_data.stack_labeled(test)
        return train, test


def discretize_labels(
    train: Labeled, test: Optional[Labeled] = None, bins=None, classes=None
) -> Union[LabeledTuple, Labeled]:
    # Note: bins must be set

    train = train.copy()
    train.y = pd.cut(train.y, bins, labels=classes)

    if test is None:
        return train
    else:
        test = test.copy()
        test.y = pd.cut(test.y, bins, labels=classes)

        return train, test


def train_cls_model(
    train: Labeled, cls=None, ct=None, cv=cv_default, params={}, scoring="f1_macro",
) -> model_selection.GridSearchCV:

    if ct is None:
        ct = compose.make_column_transformer(
            (preprocessing.OneHotEncoder(), ["country"]),
            remainder="passthrough",
            sparse_threshold=0,
            verbose_feature_names_out=False,
        )

    if cls is None:
        cls = ensemble.RandomForestClassifier(random_state=1)

    model = pipeline.make_pipeline(ct, cls)

    hptuner = model_selection.GridSearchCV(
        model, params, cv=cv, scoring=scoring, n_jobs=-1,
    )
    hptuner.fit(train.x, train.y)

    return hptuner

