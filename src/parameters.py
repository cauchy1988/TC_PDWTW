#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/3 15:39
# @Author  : Tang Chao
# @File    : parameters.py
# @Software: PyCharm
import copy


class Parameters(object):
    def __init__(self, **kwargs):
        self._params = {
            "alpha": 1.0,
            "beta": 1.0,
            "gama": 1000000000.0,
            "shaw_param_1": 9.0,
            "shaw_param_2": 3.0,
            "shaw_param_3": 3.0,
            "shaw_param_4": 5.0,
            "p": 6,
            "p_worst": 3,
            "w": 0.05,
            "annealing_p": 0.5,
            "c": 0.99975,
            "r": 0.1,
            "reward_adds": [33, 9, 13],
            "eta": 0.025,
            "initial_weight": 1,
            "iteration_num": 25000,
            "ep_tion": 0.4,
            "segment_num": 100,
            "unlimited_float": 10000000000000000.0,
            "unlimited_float_bound": 10000000000000000.0 + 100.0,
            "theta": 25000,
            "tau": 2000
        }
        self._params.update(kwargs)
        self._original_params = copy.deepcopy(self._params)  # Store original parameters for reset
        
    def reset(self):
        self._params = copy.deepcopy(self._original_params)
    
    def __getattr__(self, name):
        if name in self._params:
            return self._params[name]
        raise AttributeError(f"'Parameters' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name == "_params":
            super().__setattr__(name, value)
        elif "_params" in self.__dict__ and name in self._params:
            self._params[name] = value
        else:
            super().__setattr__(name, value)

    def to_dict(self):
        return dict(self._params)
