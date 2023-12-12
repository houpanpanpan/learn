# encoding: utf-8
# author: vectorwang@hotmail.com
r"""
            _ _     _       _       
__   ____ _| (_) __| | __ _| |_ ___ 
\ \ / / _` | | |/ _` |/ _` | __/ _ \
 \ V / (_| | | | (_| | (_| | ||  __/
  \_/ \__,_|_|_|\__,_|\__,_|\__\___|
"""
import display
import multiprocessing
#import sys
from tqdm import tqdm
from typing import Optional
from env.utils import choose_start_end_pos
from .utils import send_result, batch_send_end, batch_send_task
from .utils import (
        CMD_END, CMD_TASK, CMD_RESULT,
)
from net.utils import get_state_from_lv


class Validator():
    def __init__(
            self,
            env,
            agent,
            tolerance: float = 2,
    ):
        self.env = env
        self.agent = agent
        self.tolerance = tolerance

    def validate_plan(
            self,
            agent,
            start_pos,
            end_pos,
    ):
        self.env.set_task(start_pos, end_pos)

        #start_node = self.env.raster_graph.get_node_from_gps(start_pos)
        #end_node = self.env.raster_graph.get_node_from_gps(end_pos)
        path_distance = self.env.get_task_path_length(
                start_pos, end_pos,
            )
        action_limit = path_distance * self.tolerance // self.env.agent_speed

        is_terminated = False
        step = 0
        state = self.env.state
        positions = [self.env.agent_pos]

        while not is_terminated:
            step += 1
            if step > action_limit:
                break

            action = agent.select_action(state.np_array)
            transition, is_terminated = self.env.step(action)
            state = transition.next_state

            positions.append(self.env.agent_pos)

        if is_terminated and self.env._reached_target():
            reached = True
        else:
            reached = False

        #agent_distance = step * self.env.agent_speed
        agent_distance = self.env.cur_travel_dist

        return reached, path_distance, agent_distance


class VisualValidator(Validator):
    def __init__(
            self,
            env,
            agent,
            tolerance: float = 2,
            display_fifo_path: Optional = None,
            display_interval: float = 0.1,
    ):
        super().__init__(env, agent, tolerance)

        if display_fifo_path is not None:
            self.fifo = display.init_fifo(display_fifo_path)
        else:
            self.fifo = None
        self.display_interval = display_interval

    def validate_show_path(
            self,
            min_dis: float = 4,
            max_dis: float = 5,
    ):
        start_pos, end_pos = choose_start_end_pos(self.env, min_dis, max_dis)
        self.env.set_task(start_pos, end_pos)

        start_node = self.env.raster_graph.get_node_from_gps(start_pos)
        end_node = self.env.raster_graph.get_node_from_gps(end_pos)
        path_distance = self.env.planner_obj.get_distance(
                start_node, end_node
            ) * self.env.planner_raster_size
        action_limit = path_distance * self.tolerance // self.env.agent_speed

        is_terminated = False
        step = 0
        state = self.env.state
        if type(state) is list or type(state) is tuple:
            display_state = state[-1]
        else:
            display_state = state
        positions = [self.env.agent_pos]

        if self.fifo is not None:
            display.send_localview(display_state, self.fifo, self.display_interval)

        while not is_terminated:
            step += 1
            if step > action_limit:
                break

            #action = self.agent.select_action(state.np_array)
            state_tensor = get_state_from_lv(state)
            action = self.agent.select_action(state_tensor)
            action = action[0][0].item()

            transition, is_terminated = self.env.step(action)
            state = transition.next_state

            if self.fifo is not None:
                display.send_localview(state, self.fifo, self.display_interval)
            positions.append(self.env.agent_pos)

        agent_xs = [x for x, _ in positions]
        agent_ys = [y for _, y in positions]

        return agent_xs, agent_ys


class VisualValidatorUDP(Validator):
    def __init__(
            self,
            env,
            agent,
            tolerance: float = 2,
            display_port: int = 2333,
            display_interval: float = 0.1,
    ):
        super().__init__(env, agent, tolerance)

        self.display_port = display_port
        self.display_interval = display_interval

    def validate_show_path(
            self,
            min_dis: float = 4,
            max_dis: float = 5,
    ):
        start_pos, end_pos = choose_start_end_pos(self.env, min_dis, max_dis)
        self.env.set_task(start_pos, end_pos)

        start_node = self.env.raster_graph.get_node_from_gps(start_pos)
        end_node = self.env.raster_graph.get_node_from_gps(end_pos)
        path_distance = self.env.planner_obj.get_distance(
                start_node, end_node
            ) * self.env.planner_raster_size
        action_limit = path_distance * self.tolerance // self.env.agent_speed

        is_terminated = False
        step = 0
        state = self.env.state
        if type(state) is list or type(state) is tuple:
            display_state = state[-1]
        else:
            display_state = state
        positions = [self.env.agent_pos]

        display.send_display_info_udp(display_state, 0, self.display_port, self.display_interval)

        while not is_terminated:
            step += 1
            if step > action_limit:
                break

            state_tensor = get_state_from_lv(state)
            action = self.agent.select_action(state_tensor)
            #action = action[0][0].item()
            transition, is_terminated = self.env.step(action)
            state = transition.next_state
            if type(state) is list or type(state) is tuple:
                display_state = state[-1]
            else:
                display_state = state
            action = transition.action

            display.send_display_info_udp(display_state, action, self.display_port, self.display_interval)
            positions.append(self.env.agent_pos)

        agent_xs = [x for x, _ in positions]
        agent_ys = [y for _, y in positions]

        return agent_xs, agent_ys


class ValidateWorker(multiprocessing.Process):
    def __init__(
            self,
            worker_id,
            env,
            agent,
            recv_queue: multiprocessing.Queue,
            send_queue: multiprocessing.Queue,
            tolerance: float = 2,

    ):
        super().__init__()
        self.worker_id = worker_id
        self.env = env
        self.agent = agent
        self.tolerance = tolerance
        self.recv_queue = recv_queue
        self.send_queue = send_queue

    def validate_plan(
            self,
            agent,
            start_pos,
            end_pos,
    ):
        self.env.set_task(start_pos, end_pos)

        #start_node = self.env.raster_graph.get_node_from_gps(start_pos)
        #end_node = self.env.raster_graph.get_node_from_gps(end_pos)
        path_distance = self.env.get_task_path_length(
                start_pos, end_pos,
            )
        action_limit = path_distance * self.tolerance // self.env.agent_speed

        is_terminated = False
        step = 0
        state = self.env.state
        positions = [self.env.agent_pos]
        cumulative_reward = 0

        while not is_terminated:
            step += 1
            if step > action_limit:
                break

            action = agent.select_action(get_state_from_lv(state))
            transition, is_terminated = self.env.step(action)
            state = transition.next_state
            cumulative_reward += transition[-1]

            positions.append(self.env.agent_pos)

        if is_terminated and self.env._reached_target():
            reached = True
        else:
            reached = False

        #agent_distance = step * self.env.agent_speed
        agent_distance = self.env.cur_travel_dist

        return reached, path_distance, agent_distance, cumulative_reward

    def run(self):
        while True:
            msg = self.recv_queue.get()

            if msg["cmd"] == CMD_END:
                break

            elif msg["cmd"] == CMD_TASK:
                start_pos = msg["start_pos"]
                end_pos = msg["end_pos"]
                reached, path_distance, agent_distance, cumulative_reward = self.validate_plan( 
                        self.agent,
                        start_pos=start_pos,
                        end_pos=end_pos,
                )
                send_result(
                        q=self.send_queue,
                        worker_id=self.worker_id,
                        reached=reached,
                        path_distance=path_distance,
                        agent_distance=agent_distance,
                        cumulative_reward=cumulative_reward,
                )

        print("Task ends")


class MultiValidator():
    def __init__(
            self,
            env,
            agents,
            tolerance: float = 2,

    ):
        super().__init__()
        self.env = env
        self.agents = agents
        self.tolerance = tolerance

        self.task_queues = []
        self.workers = []

        self.result_queue = multiprocessing.Queue(100)
        self.agent_cnt = len(self.agents)

        for i in range(self.agent_cnt):
            self.task_queues.append(multiprocessing.Queue(1))

        print(f"Initializing workers, total: {self.agent_cnt}")
        for i, q in tqdm(enumerate(self.task_queues)):
            self.workers.append(ValidateWorker(
                worker_id=i,
                env=self.env,
                agent=agents[i],
                recv_queue=self.task_queues[i],
                send_queue=self.result_queue,
                tolerance=tolerance,
            ))

        for worker in self.workers:
            worker.start()


    def validate_models(
            self,
            data: dict,
    ):
        min_dis = data["min_dist"]
        max_dis = data["max_dist"]
        test_task = data["test_task"]
        task_num = data["task_num"]

        print(f"Validating models, task_num: {task_num}\n\tmin dist: {min_dis}, max_dist: {max_dis}")
        total_agent_dist = [0] * len(self.agents)
        total_target_dist = [0] * len(self.agents)
        total_agent_reached_dist = [0] * len(self.agents)
        total_target_reached_dist = [0] * len(self.agents)
        reached_cnt = [0] * len(self.agents)
        total_reward = [[].copy() for _ in range(len(self.agents))]

        for e in tqdm(range(task_num)):
            start_pos, end_pos = test_task[e]

            batch_send_task(
                    self.task_queues,
                    start_pos=start_pos,
                    end_pos=end_pos,
            )

            for _ in range(len(self.workers)):
                msg = self.result_queue.get()

                i = msg["worker_id"]
                reached = msg["reached"]
                path_dist = msg["path_distance"]
                agent_dist = msg["agent_distance"]
                cumulative_reward = msg["cumulative_reward"]
                total_reward[i].append(cumulative_reward)

                total_agent_dist[i] += agent_dist
                total_target_dist[i] += path_dist
                if reached:
                    reached_cnt[i] += 1
                    total_agent_reached_dist[i] += agent_dist
                    total_target_reached_dist[i] += path_dist

        return (
                reached_cnt,
                total_agent_dist, total_target_dist,
                total_agent_reached_dist, total_target_reached_dist,
                total_reward,
        )
    

    def end_validation(self):
        batch_send_end(self.task_queues)
