import numpy as np

CONFIG = {}

# configure joint limits
max_effort_1_2_3 = 12
max_velocity_1_2_3 = 0.5
max_effort_4_5_6 = 3
max_velocity_4_5_6 = 1.0

joint_limits = {
    "joint1": {
        "lower": -2.7475,
        "upper": 2.7475,
        "effort": max_effort_1_2_3,
        "velocity": max_velocity_1_2_3,
    },
    "joint2": {
        "lower": -2.9656,
        "upper": 0.1744,
        "effort": max_effort_1_2_3,
        "velocity": max_velocity_1_2_3,
    },
    "joint3": {
        "lower": -0.08722,
        "upper": np.pi,
        "effort": max_effort_1_2_3,
        "velocity": max_velocity_1_2_3,
    },
    "joint4": {
        "lower": -3.01,
        "upper": 3.01,
        "effort": max_effort_4_5_6,
        "velocity": max_velocity_4_5_6,
    },
    "joint5": {
        "lower": -1.76,
        "upper": 1.76,
        "effort": max_effort_4_5_6,
        "velocity": max_velocity_4_5_6,
    },
    "joint6": {
        "lower": -0.5,
        "upper": 0.5,
        "effort": max_effort_4_5_6,
        "velocity": max_velocity_4_5_6,
    },
}

CONFIG["joint_limits"] = joint_limits
