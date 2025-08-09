#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/28 22:00
# @Author: Tang Chao
# @File: two_stage.py
# @Software: PyCharm
import copy
import random

from solution import PDWTWSolution
from alns import adaptive_large_neighbourhood_search

# two stage algorithm, first to minimize the vehicle num, second to solve the problem
# the vehicles described in the two stage algorithm in the paper should be in a homogeneous fleet
def first_stage_to_limit_vehicle_num_in_homogeneous_fleet(one_solution: PDWTWSolution) -> PDWTWSolution:
	# the first step : cope with every request one by one
		# if one ok, cope with the next request still in the request bank,
		# if not ok, after _add_one_same_vehicle and continue the loop
	# now all the request have been arranged, delete the redundant/useless vehicles, the first step is completed
	# assume that the first step uses 'a' iterations totally
	# then it will continue the second step:
		#1、move away all the requests from the vehicle that has the maximum vehicle id and the vehicle itself from Meta structure and Solution structure
		#2、rearrange the requests in the solution with the remaining vehicles
			# use the modified ALNS algorithm(the total iteration num is set to 2000 transiently) to solve the problem
			# if last 2000 iterations can not arrange all the requests in the request bank, then stop the algorithm loop
			# else preserve the current Solution and goto #1 and repeat the steps
		#total iteration number should be limited to (25000 - 'a')

	requests_in_bank = one_solution.request_bank.copy()
	
	a_iteration_num = 0
	new_vehicle_add_flag = False
	while requests_in_bank:
		a_iteration_num += 1
		
		current_request = requests_in_bank.pop(0)
		if one_solution.insert_one_request_to_any_vehicle_route_optimal(current_request):
			new_vehicle_add_flag = False
			continue
		else:
			# it is impossible that the arrangement of a request is not successful after an insertion of a new vehicle
			assert not new_vehicle_add_flag
			one_solution.add_one_same_vehicle()
			requests_in_bank.append(current_request)
			new_vehicle_add_flag = True

	result_solution = one_solution.copy()
	
	total_iteration_num = a_iteration_num
	while total_iteration_num <= one_solution.meta_obj.parameters.theta:
		one_solution.delete_vehicle_and_its_route(one_solution.max_vehicle_id())
		
		one_solution.meta_obj.parameters.iteration_num = one_solution.meta_obj.parameters.tau
		adaptive_large_neighbourhood_search(one_solution.meta_obj, one_solution, insert_unlimited=True)
		
		if not one_solution.request_bank:
			result_solution = one_solution.copy()
			total_iteration_num += one_solution.meta_obj.parameters.iteration_num
		else:
			break
			
	result_solution.meta_obj.parameters.reset()
	return result_solution

def two_stage_algorithm_in_homogeneous_fleet(initial_solution: PDWTWSolution) -> PDWTWSolution:
	# the first stage
	result_solution = first_stage_to_limit_vehicle_num_in_homogeneous_fleet(initial_solution)
	
	# the second stage
	adaptive_large_neighbourhood_search(result_solution.meta_obj, result_solution, insert_unlimited=True)
	
	return result_solution