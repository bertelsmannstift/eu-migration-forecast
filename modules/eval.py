from sklearn.model_selection import cross_validate
from sklearn.metrics import get_scorer, make_scorer
from sklearn import metrics
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def r2_mod(y_true, y_pred, *, y_mean=0.0):
    """Modified R2 for OOS evaluation where mean is 0"""

    num = ((y_true - y_pred) ** 2).sum()
    denom = ((y_true - y_mean) ** 2).sum()
    return 1 - num / denom


scorer_mae = make_scorer(metrics.mean_absolute_error, greater_is_better=False)
scorer_rmse = make_scorer(
    metrics.mean_squared_error, greater_is_better=False, squared=False
)

scorer_ev = make_scorer(
    metrics.explained_variance_score, multioutput="variance_weighted"
)
scorer_r2 = make_scorer(metrics.r2_score, multioutput="variance_weighted")
scorer_r2_mod = make_scorer(r2_mod)

DEFAULT_SCORING = {
    "mae": scorer_mae,
    "rmse": scorer_rmse,
    "explained_variance": scorer_ev,
    "r2_mod": scorer_r2_mod,
}


def score_cv(reg, X, y, scoring=DEFAULT_SCORING, **kwargs):
    scores = cross_validate(reg, X=X, y=y, scoring=scoring, **kwargs)
    return pd.DataFrame(scores)


def score_test(reg, X, y, scoring=DEFAULT_SCORING):
    scores = {k: s(reg, X, y) for k, s in scoring.items()}
    return pd.Series(scores)


def score_test_countries(
    reg, X_unstacked, y_unstacked, countries, with_dummies=True, scoring=DEFAULT_SCORING
):
    scores = {}
    for c in countries:
        if with_dummies:
            X_tmp = X_unstacked.xs(c, level=1, axis=1).assign(country=c)
        else:
            X_tmp = X_unstacked.xs(c, level=1, axis=1)
        scores[c] = score_test(reg, X_tmp, y_unstacked[c], scoring=scoring)
    return pd.DataFrame(scores).transpose()


def score_cv_countries(
    reg,
    X_unstacked,
    y_unstacked,
    countries,
    cv,
    with_dummies=True,
    scoring=DEFAULT_SCORING,
):
    scores_all = dict()
    for c in countries:
        scores_country = []
        for i_train, i_test in cv.split(X_unstacked):
            if with_dummies:
                x_test_tmp = (
                    X_unstacked.iloc[i_test].xs(c, level=1, axis=1).assign(country=c)
                )
                x_train_tmp = X_unstacked.iloc[i_train].stack().reset_index(level=1)
            else:
                x_test_tmp = X_unstacked.iloc[i_test].xs(c, level=1, axis=1)
                x_train_tmp = X_unstacked.iloc[i_train].stack().droplevel(level=1)
            y_train_tmp = y_unstacked.iloc[i_train].stack().droplevel(level=1)
            y_test_tmp = y_unstacked.iloc[i_test][c]
            reg_tmp = reg.fit(x_train_tmp, y_train_tmp)
            scores = {k: s(reg_tmp, x_test_tmp, y_test_tmp) for k, s in scoring.items()}
            scores_country.append(scores)
        scores_country = pd.DataFrame(scores_country)
        scores_all[c] = scores_country
    scores_all = pd.concat(scores_all)
    return scores_all


def agg_cv_scores(
    scores_all,
    use_quantiles=False,
    agg_arg=["mean", "std", "sem"],
    quantiles=[0.25, 0.5, 0.75],
    level=None,
):
    if level is None:
        obj = scores_all
    else:
        obj = scores_all.groupby(level=level)

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
    df,
    n_rows=7,
    n_cols=4,
    figsize=(25, 25),
    countries=None,
    global_autoscale=False,
    t_min=None,
    t_max=None,
    y_min=None,
    y_max=None,
    vline=None,
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
        sub_df = df.xs(c, level=1, axis="columns")[t_min:t_max]
        sub_df.plot(ax=ax, ylim=y_lim)
        if vline is not None:
            ymin, ymax = ax.get_ylim()
            ax.vlines(vline, ymin, ymax, color="gray", linestyles="dashed")
        ax.set_title(c)
    fig.tight_layout()
    return fig, axs


def plot_prediction(y_pred: pd.DataFrame, y_true: pd.DataFrame, **kwargs):
    df_pred = pd.concat({"true": y_true, "predicted": y_pred}, axis="columns")
    return plot_panel(df_pred, **kwargs)
