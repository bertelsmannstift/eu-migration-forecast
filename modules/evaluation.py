from sklearn.model_selection import cross_validate
from sklearn.metrics import get_scorer
import pandas as pd
import matplotlib.pyplot as plt


def score_cv(
    reg,
    X,
    y,
    scoring=["neg_mean_absolute_percentage_error", "neg_root_mean_squared_error", "r2"],
):
    scores = cross_validate(reg, X=X, y=y, scoring=scoring)
    return pd.DataFrame(scores)


def score_test(
    reg,
    X,
    y,
    scoring=["neg_mean_absolute_percentage_error", "neg_root_mean_squared_error", "r2"],
):
    scores = {s: get_scorer(s)(reg, X, y) for s in scoring}
    return pd.Series(scores)


def plot_panel(
    df, countries=None, n_rows=7, n_cols=4, figsize=(25, 25), autoscale=True
):
    if countries is None:
        countries = df["country"].unique()
    fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize)
    for c, ax in zip(countries, axs.flatten()):
        df_to_plot = df[df["country"] == c].drop(columns="country")
        if autoscale is not None:
            y_max = max([df_to_plot[col].max() for col in df_to_plot.columns])
            y_min = min([df_to_plot[col].min() for col in df_to_plot.columns])
        df_to_plot.plot(ax=ax, ylim=(y_min * 1.2, y_max * 1.2) if autoscale else None)
        ax.set_title(c)
    fig.tight_layout()
    return fig, axs


def plot_prediction(reg, X, countries, t_min=None, t_max=None, **kwargs):
    y_pred = reg.predict(X)
    df_pred = df_panel_1y[["value", "country"]][t_min:t_max].assign(pred=y_pred)
    return plot_panel(df_pred, countries, **kwargs)


def plot_residuals(reg, X, countries=selected_countries, **kwargs):
    y_pred = reg.predict(X)
    df_pred = df_panel_1y[["value", "country"]][t_min:t_max].assign(pred=y_pred)
    df_pred["residuals"] = df_pred["pred"] - df_pred["value"]
    return plot_panel(df_pred[["residuals", "country"]], countries, **kwargs)
