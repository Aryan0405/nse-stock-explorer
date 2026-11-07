"""Chart builders. Each returns a plotly Figure. No global state, no images."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

TEMPLATE = "plotly_white"


def _layout(fig, title=None, height=380):
    fig.update_layout(template=TEMPLATE, paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#222"), title=dict(text=title or ""), height=height,
                      margin=dict(l=10, r=10, t=50 if title else 10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    return fig


def returns_distribution(returns: pd.Series, name: str) -> go.Figure:
    r = returns.dropna()
    mu, sd = r.mean(), r.std()
    x = np.linspace(r.min(), r.max(), 200)
    fig = go.Figure()
    fig.add_histogram(x=r, nbinsx=50, histnorm="probability density",
                      name=f"{name} log returns", marker_color="steelblue", opacity=0.75)
    fig.add_scatter(x=x, y=stats.norm.pdf(x, mu, sd), mode="lines",
                    name="Normal fit", line=dict(color="black", dash="dash"))
    fig.add_vline(x=r.mean(), line=dict(color="orange", dash="dash"), annotation_text="Mean")
    fig.add_vline(x=r.median(), line=dict(color="green", dash="dash"), annotation_text="Median",
                  annotation_position="bottom right")
    return _layout(fig, f"{name} Distribution (Kurtosis: {r.kurt():.2f}, Skew: {r.skew():.2f})")


def normalized_price(close: pd.DataFrame, stocks, benchmark="^NSEI") -> go.Figure:
    fig = go.Figure()
    for s in stocks:
        clean = close[s].dropna()
        if clean.empty:
            continue
        fig.add_scatter(x=close.index, y=close[s] / clean.iloc[0] * 100, mode="lines", name=s)
    if benchmark in close.columns:
        clean = close[benchmark].dropna()
        if not clean.empty:
            fig.add_scatter(x=close.index, y=close[benchmark] / clean.iloc[0] * 100,
                            mode="lines", name="NIFTY50",
                            line=dict(color="black", dash="dash", width=2))
    fig.update_yaxes(title="Normalized price (base 100)")
    return _layout(fig, None, 480)


def rolling_volatility(vol: pd.Series, name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=vol.index, y=vol, mode="lines", name=f"{name} vol",
                    line=dict(color="#e67e22"), fill="tozeroy",
                    fillcolor="rgba(230,126,34,0.2)")
    fig.add_hline(y=vol.mean(), line=dict(color="red", dash="dash"), annotation_text="Mean vol")
    return _layout(fig, f"{name} Volatility")


def drawdown_chart(dd: pd.Series, name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=dd.index, y=dd, mode="lines", name="Drawdown",
                    line=dict(color="#e74c3c"), fill="tozeroy",
                    fillcolor="rgba(231,76,60,0.4)")
    fig.update_yaxes(tickformat=".0%")
    return _layout(fig, f"{name} Drawdown Profile")


def sharpe_chart(sh: pd.Series, name: str) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=sh.index, y=sh, mode="lines", name="Sharpe", line=dict(color="#2ecc71"))
    fig.add_scatter(x=sh.index, y=sh.clip(lower=0), mode="lines", showlegend=False,
                    line=dict(width=0), fill="tozeroy", fillcolor="rgba(46,204,113,0.3)")
    fig.add_hline(y=0, line=dict(color="black", width=1))
    return _layout(fig, f"{name} Sharpe Ratio")


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    mask = np.triu(np.ones(corr.shape, dtype=bool))
    # lower triangle only; drop the all-empty first row and last column
    shown = corr.where(~mask).iloc[1:, :-1]
    fig = px.imshow(shown, text_auto=".2f", zmin=-1, zmax=1,
                    color_continuous_scale="RdYlGn", aspect="auto")
    fig.update_xaxes(side="bottom")
    return _layout(fig, None, 520)
