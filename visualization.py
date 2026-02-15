import matplotlib.pyplot as plt
import pandas as pd

def plot_cumulative_returns(prices,cr,ticker):
    cr_pct = cr*100
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(cr.index, cr_pct, label="Portfolio", linewidth=2)
    ax.set_title("Cumulative Returns (%)", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()

