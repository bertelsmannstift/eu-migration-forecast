""" Forecast evaluation """

from ctypes import Union
from tkinter import Label
from sklearn import model_selection
from sklearn.model_selection import cross_validate, cross_val_predict
from sklearn.metrics import get_scorer, make_scorer
from sklearn import metrics, base
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import wasserstein_distance
from eumf_data import Labeled, stack_labeled, discretize_labeled
from typing import Optional, Iterable, Tuple, Union
from numpy.typing import ArrayLike


def r2_mod(y_true, y_pred, *arg, y_base=0.0):
    """Modified R2 for OOS evaluation where mean is 0"""

    num = ((y_true - y_pred) ** 2).sum()
    denom = ((y_true - y_base) ** 2).sum()
    return 1 - num / denom


def delta_mae(y_true, y_pred, *arg, y_base=0.0):
    """Modified R2 for OOS evaluation where mean is 0"""

    sae = np.abs(y_true - y_pred)
    sae_base = np.abs(y_true - y_base)
    return (sae_base.sum() - sae.sum()) / len(y_true)


def rmse_weighted(y_true, y_pred, *arg, factor=1.0):
    se = (y_true - y_pred) ** 2
    weights = np.exp(np.abs(y_true * factor))
    return np.sqrt(np.sum(se * weights))


scorer_mae = make_scorer(metrics.mean_absolute_error, greater_is_better=False)
scorer_rmse = make_scorer(
    metrics.mean_squared_error, greater_is_better=False, squared=False
)
scorer_ev = make_scorer(
    metrics.explained_variance_score, multioutput="variance_weighted"
)
scorer_r2 = make_scorer(metrics.r2_score, multioutput="variance_weighted")
scorer_r2_mod = make_scorer(r2_mod)
scorer_delta_mae = make_scorer(delta_mae, greater_is_better=True)

scorer_emd = make_scorer(wasserstein_distance, greater_is_better=False)

DEFAULT_SCORING = {
    "mae": scorer_mae,
    "rmse": scorer_rmse,
    "explained_variance": scorer_ev,
    "r2_mod": scorer_r2_mod,
    "delta_mae": scorer_delta_mae,
}

DEFAULT_SCORING_MULTICLS = ["f1_micro", "f1_macro", "f1_weighted"]


# def score_cv(reg, X, y, scoring=DEFAULT_SCORING, **kwargs):
#     scores = cross_validate(reg, X=X, y=y, scoring=scoring, **kwargs)
#     return pd.DataFrame(scores)

# def score_test(reg, X:pd.DataFrame, y:pd.Series, scoring=DEFAULT_SCORING):
#     if hasattr(scoring, "items"):
#         scores = {k: scorer(reg, X, y) for k, scorer in scoring.items()}
#     else:
#         scores = {k: get_scorer(k)(reg, X, y) for k in scoring}
#     return pd.Series(scores)


class BlockKFold:
    def __init__(self, n_splits: int, margin: Optional[Union[int, float]] = None):
        if isinstance(n_splits, int):
            self.n_splits = n_splits
        else:
            raise ValueError("n_splits must be integer")
        if isinstance(margin, int) or isinstance(margin, float) or margin is None:
            self.margin = margin
        else:
            raise ValueError("margin must me int or float")

    def get_n_splits(self, X, y, groups):
        return self.n_splits

    def split(self, X, y=None, groups=None):
        n_samples = len(X)
        k_fold_size = n_samples // self.n_splits
        indices = list(range(n_samples))

        if self.margin is None:
            margin = 0
        if isinstance(self.margin, int):
            margin = self.margin
        elif isinstance(self.margin, float):
            margin = int(n_samples / self.n_splits * self.margin)

        for i in range(self.n_splits):
            start = i * k_fold_size
            stop = start + k_fold_size

            test = indices[start:stop]
            train1 = indices[:start]
            train2 = (
                indices[stop + margin :] if stop + margin < n_samples else []
            )

            yield train1 + train2, test


def score_cv(est: base.BaseEstimator, data: Labeled, scoring=DEFAULT_SCORING, **kwargs):
    scores = cross_validate(est, X=data.x, y=data.y, scoring=scoring, **kwargs)
    return pd.DataFrame(scores)


def score_test(est: base.BaseEstimator, data: Labeled, scoring=DEFAULT_SCORING):
    if hasattr(scoring, "items"):
        scores = {k: scorer(est, data.x, data.y) for k, scorer in scoring.items()}
    else:
        scores = {k: get_scorer(k)(est, data.x, data.y) for k in scoring}
    return pd.Series(scores)


def score_test_countries(
    est: base.BaseEstimator,
    test: Labeled,
    country_indicators: Optional[ArrayLike] = None,
    countries: Optional[Iterable] = None,
    scoring=DEFAULT_SCORING,
):
    scores = {}

    if country_indicators is None:
        country_indicators = test.index.get_level_values(1)

    if countries is None:
        countries = pd.unique(country_indicators)

    for c in countries:
        scores[c] = score_test(est, test[country_indicators == c], scoring=scoring)
    return pd.DataFrame(scores).transpose()


# def score_cv_countries(
#     reg,
#     X_unstacked,
#     y_unstacked,
#     countries,
#     cv,
#     with_dummies=True,
#     scoring=DEFAULT_SCORING,
# ):
#     scores_all = dict()
#     for c in countries:
#         scores_country = []
#         for i_train, i_test in cv.split(X_unstacked):
#             if with_dummies:
#                 x_test_tmp = (
#                     X_unstacked.iloc[i_test].xs(c, level=1, axis=1).assign(country=c)
#                 )
#                 x_train_tmp = X_unstacked.iloc[i_train].stack().reset_index(level=1)
#             else:
#                 x_test_tmp = X_unstacked.iloc[i_test].xs(c, level=1, axis=1)
#                 x_train_tmp = X_unstacked.iloc[i_train].stack().droplevel(level=1)
#             y_train_tmp = y_unstacked.iloc[i_train].stack().droplevel(level=1)
#             y_test_tmp = y_unstacked.iloc[i_test][c]
#             reg_tmp = reg.fit(x_train_tmp, y_train_tmp)
#             scores = {k: s(reg_tmp, x_test_tmp, y_test_tmp) for k, s in scoring.items()}
#             scores_country.append(scores)
#         scores_country = pd.DataFrame(scores_country)
#         scores_all[c] = scores_country
#     scores_all = pd.concat(scores_all)
#     return scores_all


def score_cv_countries(
    est: base.BaseEstimator,
    data_unstacked: Labeled,
    cv: model_selection.BaseCrossValidator,
    countries: Optional[Iterable] = None,
    scoring=DEFAULT_SCORING,
):

    if countries is None:
        countries = data_unstacked.y.columns

    scores_all = {}
    for c in countries:
        scores_all[c] = []

    for i_train, i_test in cv.split(data_unstacked.x):
        x_train_tmp = data_unstacked.x.iloc[i_train]
        y_train_tmp = data_unstacked.y.iloc[i_train]
        train_tmp = Labeled(x_train_tmp, y_train_tmp)
        train_stacked_tmp = stack_labeled(train_tmp)
        est_tmp = est.fit(train_stacked_tmp.x, train_stacked_tmp.y)
        for c in countries:
            x_test_tmp = data_unstacked.x.iloc[i_test].xs(
                c, level=1, axis=1, drop_level=False
            )
            y_test_tmp = data_unstacked.y.iloc[i_test][[c]]
            test_tmp = Labeled(x_test_tmp, y_test_tmp)
            test_stacked_tmp = stack_labeled(test_tmp)
            scores = {
                k: s(est_tmp, test_stacked_tmp.x, test_stacked_tmp.y)
                for k, s in scoring.items()
            }
            scores_all[c].append(scores)

    for c in countries:
        scores_all[c] = pd.DataFrame(scores_all[c])

    return pd.concat(scores_all)


def score_cv_countries_cls(
    est: base.BaseEstimator,
    data_unstacked: Labeled,
    cv: model_selection.BaseCrossValidator,
    bins: Iterable[float],
    classes: Iterable,
    countries: Optional[Iterable] = None,
    scoring: Union[Iterable, dict] = ["accuracy"],
):

    if countries is None:
        countries = data_unstacked.y.columns

    scores_all = {}
    for c in countries:
        scores_all[c] = []

    if not isinstance(scoring, dict):
        scoring = {s: get_scorer(s) for s in scoring}

    for i_train, i_test in cv.split(data_unstacked.x):
        x_train_tmp = data_unstacked.x.iloc[i_train]
        y_train_tmp = data_unstacked.y.iloc[i_train]
        train_tmp = Labeled(x_train_tmp, y_train_tmp)
        train_stacked_tmp = stack_labeled(train_tmp)
        train_cls_tmp = discretize_labeled(train_stacked_tmp, bins, classes)
        est_tmp = est.fit(train_cls_tmp.x, train_cls_tmp.y)
        for c in countries:
            x_test_tmp = data_unstacked.x.iloc[i_test].xs(
                c, level=1, axis=1, drop_level=False
            )
            y_test_tmp = data_unstacked.y.iloc[i_test][[c]]
            test_tmp = Labeled(x_test_tmp, y_test_tmp)
            test_stacked_tmp = stack_labeled(test_tmp)
            test_cls_tmp = discretize_labeled(test_stacked_tmp, bins, classes)
            scores = {
                k: s(est_tmp, test_cls_tmp.x, test_cls_tmp.y)
                for k, s in scoring.items()
            }
            scores_all[c].append(scores)

    for c in countries:
        scores_all[c] = pd.DataFrame(scores_all[c])

    return pd.concat(scores_all)


def agg_cv_scores(
    scores_all,
    use_quantiles=False,
    agg_arg=["mean", "std", "sem"],
    quantiles=[0.25, 0.5, 0.75],
    level=None,
    folds=None,
):
    if level is None:
        obj = scores_all
    else:
        obj = scores_all.groupby(level=level)

    if folds is not None:
        obj=obj.iloc[folds]

    if use_quantiles:
        tmp_df = obj.quantile(quantiles).unstack()
        if level is None:
            tmp_df = tmp_df.unstack()
    else:
        tmp_df = obj.agg(agg_arg)
        if level is None:
            tmp_df = tmp_df.transpose()

    return tmp_df


def plot_panel(
    df: pd.DataFrame,
    n_rows: int = 7,
    n_cols: int = 4,
    figsize=(20, 20),
    countries=None,
    global_autoscale=False,
    t_min=None,
    t_max=None,
    y_min=None,
    y_max=None,
    vline=None,
    vspan: Optional[Iterable] = None,
    **kwargs,
):
    if countries is None:
        countries = df.columns.levels[1].to_list()
    fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize)
    y_lim = None
    if global_autoscale:
        y_lim = (min(df.min()) * 1.2, max(df.max()) * 1.2)
    if y_min is not None and y_max is not None:
        y_lim = (y_min, y_max)
    for c, ax in zip(countries, axs.flatten()):
        sub_df = df.xs(c, level=1, axis="columns")[t_min:t_max].dropna()
        # sub_df.plot(ax=ax, ylim=y_lim, **kwargs)
        sns.lineplot(sub_df, ax=ax, **kwargs)
        if vline is not None:
            ymin, ymax = ax.get_ylim()
            ax.vlines(vline, ymin, ymax, color="gray", linestyles="dashed")
        if vspan is not None:
            ax.axvspan(vspan[0], vspan[1], color="lightgray")
        ax.set_title(c)
    fig.tight_layout()
    return fig, axs


def plot_prediction(y_pred: pd.DataFrame, y_true: pd.DataFrame, **kwargs):
    df_pred = pd.concat({"true": y_true, "predicted": y_pred}, axis="columns")
    return plot_panel(df_pred, **kwargs)


def plot_predictions(y_preds: dict[pd.DataFrame], y_true: pd.DataFrame, **kwargs):
    df_pred = pd.concat({**{"true": y_true}, **y_preds}, axis="columns")
    return plot_panel(df_pred, **kwargs)


def agg_multiple_cv_scores(scores: list, labels: list, **kwargs):
    return pd.concat(
        {
            str(label): agg_cv_scores(score, **kwargs).stack()
            for label, score in zip(labels, scores)
        },
        axis=1,
    ).transpose()


def agg_multiple_test_scores(scores: list, labels: list):
    return pd.concat(
        {str(label): score for label, score in zip(labels, scores)}, axis=1,
    ).transpose()


def cv_performance_plot(
    cv_scores: list[pd.DataFrame],
    metric: str,
    indices: Optional[Iterable[int]] = None,
    fold_labels: Optional[Iterable] = None,
    run_labels: Optional[Iterable] = None,
    plot_labels: Optional[Iterable[str]] = None,
    test_scores: Optional[Iterable[pd.DataFrame]] = None,
    test_pos: Optional[int] = None,
    test_vspan: bool = True,
    benchmark_indices: Iterable[int] = [],
    y_label=None,
    **kwargs,
) -> plt.Axes:

    if indices == None:
        indices == range(len(cv_scores))

    if run_labels is None:
        run_labels = indices

    for k, i in enumerate(indices):
        if test_scores is not None:
            if test_pos is None:
                test_pos = len(cv_scores[i])
            df_tmp = pd.concat(
                [
                    cv_scores[i]["test_" + metric][:test_pos],
                    pd.Series(test_scores[i][metric]),
                    cv_scores[i]["test_" + metric][test_pos:],
                ]
            ).reset_index(drop=True)
        else:
            df_tmp = cv_scores[i]["test_" + metric]

        label = (
            plot_labels[k]
            if plot_labels is not None
            else str(run_labels[i])
            if run_labels is not None
            else None
        )

        ax = df_tmp.plot(
            label=label,
            marker="o" if i not in benchmark_indices else "",
            linestyle="-" if i not in benchmark_indices else ":",
            **kwargs,
        )

        if test_vspan and test_scores is not None:
            ax.axvspan(test_pos - 0.5, test_pos + 0.5, color="lightgrey")

    if y_label is not None:
        plt.ylabel(y_label)
    else:
        plt.ylabel(metric)
    plt.legend()
    if fold_labels is not None:
        plt.xticks(range(len(df_tmp)), fold_labels)

    return plt.gca()


def predict_all(
    reg,
    train_stacked: Labeled,
    test_stacked: Labeled,
    cv,
    # t_test_min=None,
    # t_test_max=None,
) -> pd.DataFrame:

    pred_arr_test = reg.predict(test_stacked.x)
    y_pred_stacked_test = pd.Series(pred_arr_test, index=test_stacked.x.index)
    y_pred_trans_test = y_pred_stacked_test.unstack()

    # y predicted over cv
    pred_arr_cv = cross_val_predict(reg, train_stacked.x, train_stacked.y, cv=cv)
    y_pred_stacked_cv = pd.Series(pred_arr_cv, index=train_stacked.y.index)
    y_pred_trans_cv = y_pred_stacked_cv.unstack()

    y_pred_all = pd.concat([y_pred_trans_cv, y_pred_trans_test])

    return y_pred_all.sort_index()
