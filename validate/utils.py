#encoding: utf-8
#author: vectorwang@hotmail.com


CMD_END = 0
CMD_TASK = 1
CMD_RESULT = 2


def send_end(q):
    q.put({
        "cmd": CMD_END,
    })


def batch_send_end(
        qs,
):
    for q in qs:
        send_end(q)


def send_task(
        q,
        start_pos,
        end_pos,
):
    q.put({
        "cmd": CMD_TASK,
        "start_pos": start_pos,
        "end_pos": end_pos,
    })


def batch_send_task(
        qs,
        start_pos,
        end_pos,
):
    for q in qs:
        send_task(q, start_pos, end_pos)


def send_result(
        q,
        worker_id,
        reached,
        path_distance,
        agent_distance,
        cumulative_reward,
):
    q.put({
        "cmd": CMD_RESULT,
        "worker_id": worker_id,
        "reached": reached,
        "path_distance": path_distance,
        "agent_distance": agent_distance,
        "cumulative_reward": cumulative_reward,
    })
