#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/25 11:49
# @Author  : Tang Chao
# @File    : alns.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution

_iteration_num = 25000
_ep_tion = 0.4


def adaptive_large_neighbourhood_search(meta_obj: Meta, initial_solution: PDWTWSolution):
	requests_num = len(meta_obj.requests)
	q_upper_bound = min(100, int(_ep_tion * requests_num))
	q_lower_bound = 4
	
	s_best = initial_solution.copy()
	s = initial_solution.copy()
	
	for i in range(0, _iteration_num):
		pass
	