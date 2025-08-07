#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/28 22:00
# @Author: Tang Chao
# @File: two_stage.py
# @Software: PyCharm
import copy
import random

from meta import Meta
from solution import PDWTWSolution
from vehicle import Vehicle


def _add_one_same_vehicle(meta_obj: Meta, one_solution: PDWTWSolution):
	assert meta_obj == one_solution.meta_obj
	
	# random check the similarity of any two vehicles
	values = meta_obj.vehicles.values()
	assert values
	selected_two_values = random.choices(values, k=2)
	assert selected_two_values[0].equals(selected_two_values[1])
	
	max_vehicle_id = max(meta_obj.vehicles.keys())
	new_vehicle_id = max_vehicle_id + 1
	
	#update meta_obj
	meta_obj.vehicles[new_vehicle_id] = Vehicle(new_vehicle_id, selected_two_values[0].capacity, selected_two_values[0].velocity, selected_two_values[0].startNodeId, selected_two_values[0].endNodeId)
	meta_obj.vehicle_run_between_nodes_time[new_vehicle_id] = copy.deepcopy(meta_obj.vehicle_run_between_nodes_time[selected_two_values[0].identity])
	# vehicles of a homogeneous fleet have the same start node and end node, so need not add new node to the Meta structure
	
	#update one_solution
	one_solution.vehicle_bank.add(new_vehicle_id)

# two stage algorithm, first to minimize the vehicle num, second to solve the problem
# the vehicles described in the two stage algorithm in the paper should be in a homogeneous fleet
def first_stage_to_limit_vehicle_num_in_homogeneous_fleet(one_solution: PDWTWSolution):
	# cope with every request one by one
		# if one ok, cope with next,
		# if not ok, after _add_one_same_vehicle and continue the steps
	# now all the request have been arranged, delete the redundant/useless vehicles, the first step is completed
	# it uses a's iterations
	pass
