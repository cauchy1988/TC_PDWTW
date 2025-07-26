#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/25 11:49
# @Author  : Tang Chao
# @File    : alns.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution
from removal import *
from insertion import *
import random

_iteration_num = 25000
_ep_tion = 0.4

_w = 0.05
_c = 0.99975
_segment_num = 100
_reward_adds = [33, 9, 13]


def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution):
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(100, int(_ep_tion * requests_num))
	q_lower_bound = 4
	
	w_removal = [_w, _w, _w]
	removal_function_list = [shaw_removal, random_removal, worst_removal]
	
	m = len(initial_solution.paths) + len(initial_solution.vehicle_bank)
	w_insertion = [_w, _w, _w, _w]
	insertion_function_list = [basic_greedy_insertion, regret_insertion_wrapper(2), regret_insertion_wrapper(3),
	                           regret_insertion_wrapper(4), regret_insertion_wrapper(m)]
	
	s_best = initial_solution.copy()
	s = initial_solution.copy()
	for i in range(0, _iteration_num):
		q = random.randint(q_lower_bound, q_upper_bound)
