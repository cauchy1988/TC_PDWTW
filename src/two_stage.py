#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/28 22:00
# @Author: Tang Chao
# @File: two_stage.py
# @Software: PyCharm
import copy
import random

from solution import PDWTWSolution

# two stage algorithm, first to minimize the vehicle num, second to solve the problem
# the vehicles described in the two stage algorithm in the paper should be in a homogeneous fleet
def first_stage_to_limit_vehicle_num_in_homogeneous_fleet(one_solution: PDWTWSolution):
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

	