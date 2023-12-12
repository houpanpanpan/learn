import argparse
import matplotlib.pyplot as plt
import env
import multiprocessing
import sys
from json import dumps
from validate import MultiValidator
import validate.utils as vu
from env.localview import BasicLocalViewMaker
from env.obs import StaticPointsObsManager
from env.utils import choose_start_end_pos
from S57 import Shp_ADAM
from net import *
from net.agent import JustAgent
import json
import pandas as pd
import os
import re
from tkinter import _flatten
#from planner.algors import AStarAlgor

shp_name = "./output/sub_map/hk_sub.shp"
json_file = "./output/test_1210.json"

parser = argparse.ArgumentParser(description="Input dir name & train epochs")
parser.add_argument("-d", type=str, help="Dir name", required=True)
parser.add_argument("-r", type=str, help="Result dir", required=True)
# parser.add_argument("-s", type=int, help="Start epoch (included)", default=10000)
# parser.add_argument("-e", type=int, help="End epoch (not included)", default=110000)
# parser.add_argument("--step", type=int, help="Step for epoch", default=10000)
parser.add_argument("-l", type=int, help="History Layers", default=4)
parser.add_argument("-m", type=str, help="Net model", default="V1")

def normal_reward(
        d1, d2, d3,
):
    #return d3*2000
    return 5000*d3

sys.setrecursionlimit(1000000)

if __name__ == "__main__":
    args = parser.parse_args()
    print("Using args: ")
    print(args.d, args.r, args.s, args.e, args.step)

    result_path = "./output/" + args.r
    dir_path = "./output/" + args.d
    history_layers = args.l
    model = args.m

    if model == "V1":
        #from net import JustNet
        net_cls = JustNet
    else:
        expr = f"net_cls = JustNet{model}"
        exec(expr)

    print("Checking agents: ")
    # print(agents_path)
    print("Will save to: ")
    print(result_path)


    planner_raster_size = 0.002
    #planner_raster_size = 0.002
    dp_threshold = 0.001
    local_view_rst_cnt = 51
    local_view_los = 0.01 / 50 * 51
    agent_speed = 0.01 / 50
    tolerance = 2
    epsilon = 0.1

    multiprocessing.set_start_method("spawn")

    s57_obj = Shp_ADAM(
            shp_name,
    )

    hk_env = env.JustEnv(
        s57_map=s57_obj,
        lv_maker=BasicLocalViewMaker,
        lv_params={
            "end_point_grey": 0.5,
            "obs_grey": 1,
            "ground_grey": 1,
            "show_agent": True,
        },
        obs_manager=StaticPointsObsManager,
        obs_params={
            "point_num": 50,
            "point_size": 2e-4,
        },
        #planner_cls=AStarAlgor,
        planner_raster_size=planner_raster_size,
        agent_speed=agent_speed,
        dp_threshold=dp_threshold,
        #planner_config_file_name=planner_path,
        max_vanish=2,
        history_layer=history_layers,
        map_pre_params={
            "clip_size": 0,
            "border_size": 0,
        },
    )
    hk_env.set_reward(
            normal_reward_func=normal_reward,
            collision_reward=-5,
            vanish_reward=-5,
            target_reward=5,
    )

    paths = []
    agents_path = {}
    agents = []
    reached_cnt = []
    agent_dist = []
    target_dist = []
    r_agent_dist = []
    r_target_dist = []
    total_reward = []

    torch_files = os.listdir(dir_path)
    num_torch = len(torch_files)
    with open(json_file) as fd:
            data = json.loads(fd.read())

    for j in range(num_torch-1):
        agents_path[torch_files[j+1]] = "./output/" + args.d + "/" + torch_files[j+1]

    for label in agents_path:
        path = agents_path[label]
        paths.append(path)
        agents.append(
                JustAgent(path, epsilon, history_layer=history_layers, net_cls=net_cls)
        )
    # print(len(agents_path))
    # print(len(agents))

    for i in range(int(num_torch/10)):
        validator = MultiValidator(
                env=hk_env,
                agents=agents[i*10:i*10+10],
                tolerance=tolerance,
        )

        print("Start validation")
        result = validator.validate_models(
            data=data,  
        )
        reached_cnt.append(result[0])
        agent_dist.append(result[1])
        target_dist.append(result[2])
        r_agent_dist.append(result[3])
        r_target_dist.append(result[4])
        for i in range(len(result[5])):
            total_reward.append(result[5][i])

        validator.end_validation()


    index = []
    task_num = [data["task_num"]]*(num_torch-2)
    for file in torch_files[1:-1]:
        index.append(int(re.split(r'[_.]', file)[-2]))
        index = sorted(index)

    validate_result = {
        "index": index,
        "task_num": task_num,
        "reached_cnt": list(_flatten(reached_cnt)),
        "agent_dist": list(_flatten(agent_dist)),
        "target_dist": list(_flatten(target_dist)),
        "r_agent_dist": list(_flatten(r_agent_dist)),
        "r_target_dist": list(_flatten(r_target_dist)),
        "total_reward": total_reward,
    }
    df_result = pd.DataFrame(validate_result)
    df_result = df_result.set_index("index", drop=True)
    # print(df_result)
    df_result.to_csv(result_path)

    print(f"Result saved to: {result_path}")