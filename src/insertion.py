#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/21 21:42
# @Author: Tang Chao
# @File: insertion.py
# @Software: PyCharm
import copy
from typing import Dict
from meta import Meta
from solution import PDWTWSolution


def _get_request_vehicle_cost(meta_obj: Meta, one_solution: PDWTWSolution, noise_func) -> Dict[int, Dict[int, float]]:
	request_vehicle_cost: Dict[int, Dict[int, float]] = {}
	vehicles = [vehicle_id for vehicle_id in one_solution.vehicle_bank] + \
	           [vehicle_id for vehicle_id, _ in one_solution.paths]
	if len(set(vehicles)) != len(vehicles):
		raise ValueError("Vehicle IDs must all be unique in one solution's vehicle bank and paths!")
	for request_id in one_solution.request_bank:
		for vehicle_id in vehicles:
			ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, vehicle_id)
			if not ok:
				cost = float(meta_obj.parameters.unlimited_float_bound)
			if request_id not in request_vehicle_cost:
				request_vehicle_cost[request_id] = {}
			request_vehicle_cost[request_id][vehicle_id] = noise_func(cost) if ok and noise_func and callable(noise_func) else cost
	
	return request_vehicle_cost


def _update_request_vehicle_cost(meta_obj: Meta, already_inserted_path_vehicle_id: int,
                                 request_vehicle_cost: Dict[int, Dict[int, float]], one_solution: PDWTWSolution,
                                 already_inserted_request_id: int, noise_func) -> Dict[int, Dict[int, float]]:
	if already_inserted_request_id not in request_vehicle_cost:
		raise KeyError(f'Request vehicle {already_inserted_request_id} does not exist in {request_vehicle_cost}')
	new_request_vehicle_cost = copy.deepcopy(request_vehicle_cost)
	del new_request_vehicle_cost[already_inserted_request_id]
	for request_id, vehicle_id_dict in new_request_vehicle_cost.items():
		ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, already_inserted_path_vehicle_id)
		if not ok:
			cost = meta_obj.parameters.unlimited_float_bound
		vehicle_id_dict[already_inserted_path_vehicle_id] = noise_func(cost) if ok and noise_func and callable(noise_func) else cost
	
	return new_request_vehicle_cost


def basic_greedy_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int, insert_unlimited: bool, noise_func) -> None:
	assert q > 0
	assert meta_obj is not None
	
	qq = min(len(one_solution.request_bank), q)
	request_vehicle_cost = _get_request_vehicle_cost(meta_obj, one_solution, noise_func)
	iteration_num = 0
	while insert_unlimited or iteration_num < qq:
		if iteration_num > len(one_solution.request_bank) + len(one_solution.request_id_to_vehicle_id):
			break
			
		minimum_cost = meta_obj.parameters.unlimited_float_bound
		request_id_for_insertion = None
		vehicle_id_for_insertion = None
		for request_id, vehicle_id_dict in request_vehicle_cost.items():
			for vehicle_id, cost in vehicle_id_dict.items():
				if cost < minimum_cost:
					minimum_cost = cost
					request_id_for_insertion = request_id
					vehicle_id_for_insertion = vehicle_id
		
		if minimum_cost > meta_obj.parameters.unlimited_float:
			break
		ok = one_solution.insert_one_request_to_one_vehicle_route_optimal(request_id_for_insertion, vehicle_id_for_insertion)
		assert ok
		if not ok:
			raise RuntimeError(f'Insertion failed for vehicle {vehicle_id_for_insertion}!')
		
		_update_request_vehicle_cost(meta_obj, vehicle_id_for_insertion, request_vehicle_cost, one_solution,
		                             request_id_for_insertion, noise_func)
		iteration_num += 1


def regret_insertion_wrapper(k: int):
	def _regret_k_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int, insert_unlimited: bool, noise_func) -> None:
		assert q > 0
		assert k >= 2
		assert meta_obj is not None
		
		total_vehicle_num = len(one_solution.vehicle_bank) + len(one_solution.paths)
		assert k <= total_vehicle_num
		
		qq = min(len(one_solution.request_bank), q)
		request_vehicle_cost = _get_request_vehicle_cost(meta_obj, one_solution, noise_func)
		iteration_num = 0
		while insert_unlimited or iteration_num < qq:
			if iteration_num > len(one_solution.request_bank) + len(one_solution.request_id_to_vehicle_id):
				break
			
			request_vehicle_list: Dict[int, list] = {}
			request_k_cost_list = []
			for request_id, cost_dict in request_vehicle_cost.items():
				request_vehicle_list[request_id] = []
				for vehicle_id, cost in cost_dict.items():
					request_vehicle_list[request_id].append((vehicle_id, cost))
				request_vehicle_list[request_id].sort(key=lambda tp: tp[1])
				k_cost_sum = 0.0
				if  len(request_vehicle_list[request_id]) < k:
					raise ValueError("len(request_vehicle_list[request_id]) < k!")
				for i in range(0, k):
					k_cost_sum = k_cost_sum + (
							request_vehicle_list[request_id][i][1] - request_vehicle_list[request_id][0][1])
				request_k_cost_list.append((request_id, k_cost_sum))
			request_k_cost_list.sort(key=lambda tp: tp[1], reverse=True)
			
			j = 0
			while j < len(request_k_cost_list):
				if request_vehicle_list[request_k_cost_list[j][0]][0][1] <= meta_obj.parameters.unlimited_float:
					break
				j = j + 1
			
			if j >= len(request_k_cost_list):
				break
			
			request_id_for_insertion = request_k_cost_list[j][0]
			vehicle_id_for_insertion = request_vehicle_list[request_id_for_insertion][0][0]
			ok = one_solution.insert_one_request_to_one_vehicle_route_optimal(request_id_for_insertion, vehicle_id_for_insertion)
			if not ok:
				raise RuntimeError(f'Insertion failed for vehicle {vehicle_id_for_insertion}!')
			
			request_vehicle_cost = _update_request_vehicle_cost(meta_obj, vehicle_id_for_insertion, request_vehicle_cost, one_solution,
			                             request_id_for_insertion, noise_func)
			iteration_num += 1
			
	return _regret_k_insertion
