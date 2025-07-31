#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/21 21:41
# @Author: Tang Chao
# @File: removal.py
# @Software: PyCharm
from meta import Meta
from solution import PDWTWSolution
import random

_shaw_param_1 = 9.0
_shaw_param_2 = 3.0
_shaw_param_3 = 3.0
_shaw_param_4 = 5.0

_p = 6
_p_worst = 3


def big_r_function(meta_obj: Meta, one_solution: PDWTWSolution, request_id: int):
	request_id_obj = meta_obj.requests[request_id]
	request_id_pick_up_node_id = request_id_obj.pick_node_id
	request_id_delivery_node_id = request_id_obj.delivery_node_id
	l_first = meta_obj.requests[request_id].require_capacity
	
	def _nest_big_r_function(another_request_id: int):
		another_request_id_obj = meta_obj.requests[another_request_id]
		pick_node_id = another_request_id_obj.pick_node_id
		delivery_node_id = another_request_id_obj.delivery_node_id
		
		d_pick_up = meta_obj.distances[request_id_pick_up_node_id][pick_node_id]
		d_delivery = meta_obj.distances[request_id_delivery_node_id][delivery_node_id]
		
		t_pick_up_one = one_solution.get_node_start_service_time_in_path(request_id_pick_up_node_id)
		t_delivery_one = one_solution.get_node_start_service_time_in_path(request_id_delivery_node_id)
		t_pick_up_two = one_solution.get_node_start_service_time_in_path(pick_node_id)
		t_delivery_two = one_solution.get_node_start_service_time_in_path(delivery_node_id)
		t_pick_diff = abs(t_pick_up_two - t_pick_up_one)
		t_delivery_diff = abs(t_delivery_two - t_delivery_one)
		
		l_second = meta_obj.requests[another_request_id].require_capacity
		
		big_r_value = _shaw_param_1 * (d_pick_up + d_delivery) + \
		              _shaw_param_2 * (t_pick_diff + t_delivery_diff) + \
		              _shaw_param_3 * abs(l_second - l_first) + \
					  _shaw_param_4 * (1 - len(request_id_obj.vehicle_set & another_request_id_obj.vehicle_set) / min(len(request_id_obj.vehicle_set), len(another_request_id_obj.vehicle_set)))
		
		return big_r_value
	
	return _nest_big_r_function


def shaw_removal(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	
	solution_request_list = [request_id for request_id, _ in one_solution.request_id_to_vehicle_id]
	assert q <= len(solution_request_list)
	
	r = random.choice(solution_request_list)
	big_d = {r}
	while len(big_d) < q:
		r = random.sample(big_d, 1)[0]
		big_l = list(set(solution_request_list) - big_d)
		big_l.sort(key=big_r_function(meta_obj, one_solution, r))
		y = random.random()
		big_d = big_d | {big_l[int((y ** _p) * len(big_l))]}
	
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
		r = big_l[int((y ** _p_worst) * len(big_l))]
		one_solution.remove_requests({r})
		q = q - 1
		
