import pandas as pd
import numpy as np

def calculalte_contribution_by_stock(stock_returns,weights):
    return stock_returns * weights

def total_contribution_by_stock(stock_returns,weights):
    contri = calculalte_contribution_by_stock(stock_returns,weights)
    total_contri = contri.sum()
    return total_contri

def identify_top_contributors(stock_returns_df, weights, top_n=1):
    total_contrib = total_contribution_by_stock(stock_returns_df, weights)
    return {
        'top_contributor': total_contrib.idxmax(),
        'top_contributor_value': total_contrib.max(),
        'top_dragger': total_contrib.idxmin(),
        'top_dragger_value': total_contrib.min()
    }


def calculate_concentration(weights):
    return max(weights)


def calculate_effective_n_stocks(weights):
    weights_array = np.array(weights)
    return 1 / np.sum(weights_array ** 2)