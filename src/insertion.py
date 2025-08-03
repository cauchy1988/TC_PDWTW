#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/21 21:42
# @Author: Tang Chao
# @File: insertion.py
# @Software: PyCharm
from pkgutil import get_loader
from typing import Dict
from meta import Meta
from solution import PDWTWSolution

# bad design in order not to add fuck logic chain into the functions related to noise, chapter 3.6 in the original paper
global_noise_func = None

_unlimited_float = 10000000000000000.0
_unlimited_float_bound = _unlimited_float + 100.0


def _get_request_vehicle_cost(one_solution: PDWTWSolution) -> Dict[int, Dict[int, float]]:
	request_vehicle_cost: Dict[int, Dict[int, float]] = {}
	vehicles = [vehicle_id for vehicle_id in one_solution.vehicle_bank] + \
	           [vehicle_id for vehicle_id, _ in one_solution.paths]
	for request_id in one_solution.request_bank:
		for vehicle_id in vehicles:
			ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, vehicle_id)
			if not ok:
				cost = _unlimited_float_bound
			if request_id not in request_vehicle_cost:
				request_vehicle_cost[request_id] = {}
			request_vehicle_cost[request_id][vehicle_id] = global_noise_func(cost) if not ok and callable(global_noise_func) else cost
	
	return request_vehicle_cost


def _update_request_vehicle_cost(already_inserted_request_id: int, already_inserted_vehicle_path: int,
                                 request_vehicle_cost: Dict[int, Dict[int, float]], one_solution: PDWTWSolution):
	del request_vehicle_cost[already_inserted_request_id]
	for request_id, vehicle_id_dict in request_vehicle_cost.items():
		ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, already_inserted_vehicle_path)
		if not ok:
			cost = _unlimited_float_bound
		vehicle_id_dict[already_inserted_request_id] = global_noise_func(cost) if not ok and callable(global_noise_func) else cost


def basic_greedy_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	assert meta_obj is not None
	
	qq = min(len(one_solution.request_bank), q)
	request_vehicle_cost = _get_request_vehicle_cost(one_solution)
	while qq > 0:
		minimum_cost = _unlimited_float_bound
		request_id_for_insertion = -1
		vehicle_id_for_insertion = -1
		for request_id, vehicle_id_dict in request_vehicle_cost.items():
			for vehicle_id, cost in vehicle_id_dict:
				if cost < minimum_cost:
					minimum_cost = cost
					request_id_for_insertion = request_id
					vehicle_id_for_insertion = vehicle_id
		
		if minimum_cost > _unlimited_float:
			break
		ok = one_solution.insert_one_request_optimal(request_id_for_insertion, vehicle_id_for_insertion)
		assert ok
		
		_update_request_vehicle_cost(request_id_for_insertion, vehicle_id_for_insertion, request_vehicle_cost,
		                             one_solution)
		qq = qq - 1


def regret_insertion_wrapper(k: int):
	def _regret_k_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
		assert q > 0
		assert k >= 2
		assert meta_obj is not None
		
		total_vehicle_num = len(one_solution.vehicle_bank) + len(one_solution.paths)
		assert k <= total_vehicle_num
		
		qq = min(len(one_solution.request_bank), q)
		request_vehicle_cost = _get_request_vehicle_cost(one_solution)
		while qq > 0:
			request_vehicle_list: Dict[int, list] = {}
			request_k_cost_list = []
			for request_id, cost_dict in request_vehicle_cost.items():
				request_vehicle_list[request_id] = []
				for vehicle_id, cost in cost_dict.items():
					request_vehicle_list[request_id].append((vehicle_id, cost))
				request_vehicle_list[request_id].sort(key=lambda tp: tp[1])
				k_cost_sum = 0.0
				for i in range(1, k):
					k_cost_sum = k_cost_sum + (
							request_vehicle_list[request_id][i] - request_vehicle_list[request_id][i])
				request_k_cost_list.append((request_id, k_cost_sum))
			request_k_cost_list.sort(key=lambda tp: tp[1], reverse=True)
			
			j = 0
			while j < len(request_k_cost_list):
				if request_vehicle_list[request_k_cost_list[j][0]][1] <= _unlimited_float:
					break
				j = j + 1
			
			if j >= len(request_k_cost_list):
				break
			
			request_id_for_insertion = request_k_cost_list[j][0]
			vehicle_id_for_insertion = request_vehicle_list[request_id_for_insertion][0]
			ok = one_solution.insert_one_request_optimal(request_id_for_insertion, vehicle_id_for_insertion)
			assert ok
			
			_update_request_vehicle_cost(request_id_for_insertion, vehicle_id_for_insertion, request_vehicle_cost, one_solution)
			qq = qq - 1
		
		return _regret_k_insertion
