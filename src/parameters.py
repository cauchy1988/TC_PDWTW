#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/3 15:39
# @Author  : Tang Chao
# @File    : parameters.py
# @Software: PyCharm

class Parameters(object):
	def __init__(self):
		self.alpha = 1.0
		self.beta = 1.0
		self.gama = 1000000000.0
		
		self.shaw_param_1 = 9.0
		self.shaw_param_2 = 3.0
		self.shaw_param_3 = 3.0
		self.shaw_param_4 = 5.0
		
		self.p = 6
		self.p_worst = 3
		
		self.w = 0.05
		self.annealing_p = 0.5
		
		self.c = 0.99975
		self.r = 0.1
		
		self.reward_adds = [33, 9, 13]
		
		self.eta = 0.025
		
		# this parameter seems not to be set in the paper
		self.initial_weight = 1
		
		self.iteration_num = 25000
		self.ep_tion = 0.4
		
		self.segment_num = 100
		
		self.unlimited_float = 10000000000000000.0
		self.unlimited_float_bound = self.unlimited_float + 100.0
		
		self.theta = 25000
		self.tau = 2000