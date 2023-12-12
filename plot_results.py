import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Union, Dict, Optional, List, Tuple
import pandas as pd


plt.rc('font', family='Times New Roman', size=12, weight='bold')


font_small = {
        'family': 'Times New Roman',
        'weight': 'bold',
        'size': 12,
}

font_big = {
        'family': 'Times New Roman',
        'weight': 'bold',
        'size': 15,
}

colors_orange=[
    "#F9CBB0",
    "#F9A16D",
    "#E66817",
    "#6D2D03",
]

colors_blue=[
    "#A5CCE4",
    "#6BB7E4",
    "#166492",
    "#032D45",
]

def colors():
    candidate_colors = colors_blue + colors_orange
    i = 0
    while True:
        yield candidate_colors[i]
        i += 1
        i %= len(candidate_colors)

def get_data_from_csv(
        file_name,
):
    data = pd.read_csv(file_name)
    return data

def average_reward(
        data: pd.DataFrame,
):
    data['average_reward'] = data['total_reward'].apply(
        lambda x: sum(eval(x)) / len(x)
        )
    av_dict = {'average_reward': data['average_reward']}
    average_reward = pd.DataFrame(av_dict)
    average_reward = average_reward.set_index(data["index"], drop=True)
    # print(average_reward)
    return average_reward

def average_reward_std(
        data: pd.DataFrame,
):
    std = data['average_reward'].std()
    std_dict = {"average_reward_std": [std]*data.shape[0]}
    average_reward_std = pd.DataFrame(std_dict)
    average_reward_std = average_reward_std.set_index(data["index"], drop=True)
    return average_reward_std

def reached_percent(
        data: pd.DataFrame,
):
    data['reached_percent'] = round(
        data['reached_cnt'] / data['task_num'] *100, 1
        )
    # print(data.index)
    rp_dict = {'reached_percent': data['reached_percent']}
    reached_percent = pd.DataFrame(rp_dict)
    reached_percent = reached_percent.set_index(data["index"], drop=True)
    return reached_percent

def pathlen_percent(
        data:pd.DataFrame,
):
    data["pathlen_percent"] = data.apply(
        lambda row: (
            round(row["r_agent_dist"] / row["r_target_dist"]*100,1)
            if row["r_target_dist"] != 0 else 0
            ),
        axis=1,
    )
    pp_dict = {"pathlen_percent": data["pathlen_percent"]}
    pathlen_percent = pd.DataFrame(pp_dict)
    pathlen_percent = pathlen_percent.set_index(data["index"], drop=True)
    return pathlen_percent

def pathlen_percent_std(
        data: pd.DataFrame,
):
    std = data['pathlen_percent'].std()
    std_dict = {"pathlen_percent_std": [std]*data.shape[0]}
    pathlen_percent_std = pd.DataFrame(std_dict)
    pathlen_percent_std = pathlen_percent_std.set_index(data["index"], drop=True)
    return pathlen_percent_std

def cal_std(
        data: pd.DataFrame,
):
    column_name = data.columns[0]
    # print(data_name)
    std = data[column_name].std()
    std_name = column_name + "_std"
    std_dict = {std_name: [std]*data.shape[0]}
    df_std = pd.DataFrame(std_dict)
    # print(df_std)
    df_std = df_std.set_index(data.index, drop=True)
    return df_std


def plot_line_graphs(
        data: pd.DataFrame,
        color: str = None,
        save_path: Optional[str] = None,
        model_name: Optional[str] = None,
        ylabel_name: Optional[str] = None,
):
    fig, ax = plt.subplots(1, 1, figsize=(12,6))
    column_name = data.columns[0]
    # print(type(column_name))
    ax.plot(data.index, data[column_name], label=model_name, color=color, lw=3)
    ax.set_xlabel("Training epochs", font_big)
    ax.set_ylabel(ylabel_name, font_big)
    ax.grid()
    ax.legend(prop=font_small)

    if save_path is not None:
        plt.savefig(save_path)
    else:
        plt.show()

def plot_bar_graphs(
        data: pd.DataFrame,
        std: pd.DataFrame,
        color: str = None,
        save_path: Optional[str] = None,
        model_name: Optional[str] = None,
        ylabel_name: Optional[str] = None,
):
    column_name = data.columns[0]
    std_name = std.columns[0]
    # print(column_name, std_name)
    print(data)
    print(std)
    bar_width = 0.5
    fig, ax = plt.subplots(1, 1, figsize=(12,6))
    # print(data[column_name].values.flatten())
    x = np.arange(data.shape[0])
    ax.bar(
        x,
        height=data[column_name].values.flatten(),
        width=bar_width,
        tick_label=data.index,
        yerr=std[std_name].values.flatten(),
        label=model_name,
        color=color,
        capsize=15,
        )

    ax.set_xlabel("Training epochs", font_big)
    ax.set_ylabel(ylabel_name, font_big)
    ax.grid()
    ax.legend(prop=font_small)

    if save_path is not None:
        plt.savefig(save_path)
    else:
        plt.show()


if __name__ == "__main__":
    csv_dir = "./output/just_shp_1107_test.csv"
    data_dict = get_data_from_csv(csv_dir)
    a1 = average_reward(data_dict)
    a2 = cal_std(a1)
    b = reached_percent(data_dict)
    c1 = pathlen_percent(data_dict)
    c2 = cal_std(c1)
    # print(a1)
    # print(c2)
    str = [
        "average reward",
        "Target Reached percent %",
        "Travel Distance %(compared with optimal path)",
    ]
    # plot_line_graphs(data_dict=data_dict, raw_result=c, ylabel_name=str[0])
    plot_line_graphs(data=b, ylabel_name=str[1])
    plot_bar_graphs(data=a1, std=a2, ylabel_name=str[0])
    plot_bar_graphs(data=c1, std=c2, ylabel_name=str[2])
