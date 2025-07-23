#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/21 21:42
# @Author  : Tang Chao
# @File    : insertion.py
# @Software: PyCharm
from typing import Dict
from meta import Meta
from solution import PDWTWSolution

_unlimited_float = 10000000000000000.0
_unlimited_float_bound = _unlimited_float + 100.0


def basic_greedy_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int):
	assert q > 0
	assert meta_obj is not None
	
	qq = min(len(one_solution.request_bank), q)
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
			request_vehicle_cost[request_id][vehicle_id] = cost
	while qq > 0:
		minimum_cost = _unlimited_float_bound
		request_id_for_insertion = -1
		vehicle_id_for_insertion = -1
		for request_id, vehicle_id_dict in request_vehicle_cost:
			for vehicle_id, cost in vehicle_id_dict:
				if cost < minimum_cost:
					minimum_cost = cost
					request_id_for_insertion = request_id
					vehicle_id_for_insertion = vehicle_id
					
		if minimum_cost > _unlimited_float:
			break
		ok = one_solution.insert_one_request_optimal(request_id_for_insertion, vehicle_id_for_insertion)
		assert ok
		
		# update
		del request_vehicle_cost[request_id_for_insertion]
		for request_id, vehicle_id_dict in request_vehicle_cost:
			ok, cost = one_solution.cost_if_insert_request_to_vehicle_path(request_id, vehicle_id_for_insertion)
			if not ok:
				cost = _unlimited_float_bound
			vehicle_id_dict[vehicle_id_for_insertion] = cost

		qq = qq - 1


def regret_k_insertion(meta_obj: Meta, one_solution: PDWTWSolution, q: int, k: int):
	assert q > 0
	assert k >= 2
	assert meta_obj is not None
