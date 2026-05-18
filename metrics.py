import pandas as pd


def compute_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "net_pnl": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "expectancy": 0.0,
            "max_drawdown": 0.0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
        }

    pnl = df["pnl"]
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    total = len(pnl)
    win_sum = wins.sum()
    loss_sum = abs(losses.sum())

    profit_factor = (win_sum / loss_sum) if loss_sum > 0 else float("inf")
    win_rate = (len(wins) / total * 100) if total > 0 else 0
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0

    # Expectancy
    wr = win_rate / 100
    expectancy = (wr * avg_win) - ((1 - wr) * avg_loss) if total > 0 else 0

    # Max drawdown
    cumulative = pnl.cumsum()
    running_max = cumulative.cummax()
    drawdown = running_max - cumulative
    max_drawdown = drawdown.max()

    # Consecutive wins/losses
    results = (pnl > 0).astype(int).tolist()
    max_cw = max_cl = cw = cl = 0
    for r in results:
        if r == 1:
            cw += 1; cl = 0
        else:
            cl += 1; cw = 0
        max_cw = max(max_cw, cw)
        max_cl = max(max_cl, cl)

    return {
        "net_pnl": pnl.sum(),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "total_trades": total,
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "best_trade": pnl.max(),
        "worst_trade": pnl.min(),
        "expectancy": expectancy,
        "max_drawdown": max_drawdown,
        "consecutive_wins": max_cw,
        "consecutive_losses": max_cl,
    }


def compute_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    summary = df.groupby("month").agg(
        pnl=("pnl", "sum"),
        trades=("pnl", "count"),
        wins=("pnl", lambda x: (x > 0).sum()),
    ).reset_index()
    summary["win_rate"] = (summary["wins"] / summary["trades"] * 100).round(1)
    summary["month"] = summary["month"].astype(str)
    return summary
