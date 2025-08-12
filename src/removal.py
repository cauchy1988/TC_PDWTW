#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/21 21:41
# @Author: Tang Chao
# @File: removal.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution, InnerDictForNormalization, generate_normalization_dict
import random

def big_r_function(meta_obj, request_id: int, norm_obj: InnerDictForNormalization):
	
	def _nest_big_r_function(another_request_id: int):
		# critical declaration!
		nonlocal request_id
		
		if request_id > another_request_id:
			request_id, another_request_id = another_request_id, another_request_id
		
		return meta_obj.parameters.shaw_param_1 * (norm_obj.distance_pick_dict[request_id][another_request_id] + norm_obj.distance_delivery_dict[request_id][another_request_id]) + \
				meta_obj.parameters.shaw_param_2 * (norm_obj.start_time_diff_pick_dict[request_id][another_request_id] + norm_obj.start_time_diff_delivery_dict[request_id][another_request_id]) + \
				meta_obj.parameters.shaw_param_3 * norm_obj.load_diff_dict[request_id][another_request_id] + \
				meta_obj.parameters.shaw_param_4 * norm_obj.vehicle_set_diff_dict[request_id][another_request_id]
	
	return _nest_big_r_function


def shaw_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	
	solution_request_list = [request_id for request_id in one_solution.request_id_to_vehicle_id]
	assert q <= len(solution_request_list)
	
	r = random.choice(solution_request_list)
	big_d = {r}
	norm_obj = generate_normalization_dict(meta_obj, one_solution)
	while len(big_d) < q:
		r = random.sample(big_d, 1)[0]
		big_l = list(set(solution_request_list) - big_d)
		big_l.sort(key=big_r_function(meta_obj, r, norm_obj))
		y = random.random()
		big_d = big_d | {big_l[int((y ** meta_obj.parameters.p) * len(big_l))]}
	
	one_solution.remove_requests(big_d)


def random_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	assert meta_obj is not None
	
	solution_request_list = [request_id for request_id in one_solution.request_id_to_vehicle_id]
	assert q <= len(solution_request_list)
	q_request_id_list = random.sample(solution_request_list, q)
	one_solution.remove_requests(q_request_id_list)


def worst_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	assert meta_obj is not None
	
	while q > 0:
		big_l = [request_id for request_id in one_solution.request_id_to_vehicle_id]
		assert len(big_l) > 0
		big_l.sort(key=one_solution.cost_if_remove_request, reverse=True)
		y = random.random()
		r = big_l[int((y ** meta_obj.parameters.p_worst) * len(big_l))]
		one_solution.remove_requests({r})
		q = q - 1
