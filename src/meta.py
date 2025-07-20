#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:14
# @Author  : Tang Chao
# @File    : meta.py
# @Software: PyCharm


class Meta:
	def __init__(self):
		# first_node_id -> {second_node_id -> distance between them}
		self._distances = {}
		# node_id -> Node
		self._nodes = {}
		# request_id -> Request
		self._requests = {}
		# vehicle_id -> Vehicle
		self._vehicles = {}
		# vehicle_id -> {first_node_id -> {second_node_id -> run_time}}
		self._vehicleRunBetweenNodesTime = {}
		
		self._alpha = 1.0
		self._beta = 1.0

	@property
	def distances(self):
		return self._distances
	
	@property
	def nodes(self):
		return self._nodes
	
	@property
	def requests(self):
		return self._requests
	
	@property
	def vehicles(self):
		return self._vehicles
	
	@property
	def vehicle_run_between_nodes_time(self):
		return self._vehicleRunBetweenNodesTime
	
	@property
	def alpha(self):
		return self._alpha
	
	@property
	def beta(self):
		return self._beta
	
	
	