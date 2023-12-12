import env
from env.utils import choose_start_end_pos
from env.localview import BasicLocalViewMaker, LayeredLocalView
from env.obs import StaticPointsObsManager
from S57 import Shp_ADAM
from json import dumps


shp_name = "./output/sub_map/hk_sub.shp"
result_path = "./output/test_1211"


def generate_test_task(
        min_dist: int,
        max_dist: int,
        env,
        task_num: int,
):
    test_task = []
    for i in range(task_num):
        test_task.append(choose_start_end_pos(
            env=env,
            min_target_dist=min_dist, 
            max_target_dist=max_dist,
            ))
    return test_task


if __name__ == "__main__":
    s57_obj = Shp_ADAM(
            shp_name,
            #fill_obstacle=True,
    )
    hk_env = env.JustEnv(
        s57_map=s57_obj,
        lv_maker=BasicLocalViewMaker,
        lv_params={
            # since target layer is sperated, end_point can use 1
            "end_point_grey": 1,
            "obs_grey": 1,
            "ground_grey": 1,
            "show_agent": True,
            "localview_cls": LayeredLocalView,
        },
        obs_manager=StaticPointsObsManager,
        obs_params={
            "point_num": 0,
            "point_size": 5e-4,
        },
        #planner_cls=AStarAlgor,
        planner_raster_size=0.001,
        dp_threshold=0.0001,
        max_vanish=1,
        # planner_config_file_name=planner_snapshot,    
        history_layer=1,
        map_pre_params={
            "clip_size": 0,
            "border_size": 0,
        },
    )

    min_dist = 2
    max_dist = 3
    task_num = 1000

    test_task = generate_test_task(
        min_dist=min_dist,
        max_dist=max_dist,
        env=hk_env,
        task_num=task_num,
        )
    
    result = {
        "min_dist": min_dist,
        "max_dist": max_dist,
        "task_num": task_num,
        "test_task": test_task
    }
    with open(result_path, "w") as fd:
        fd.write(dumps(result))
    print(f"Result saved to: {result_path}")