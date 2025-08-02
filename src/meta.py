#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:14
# @Author: Tang Chao
# @File: meta.py
# @Software: PyCharm
from typing import Dict
from node import Node
from request import Request
from vehicle import Vehicle


class Meta:
	def __init__(self):
		# first_node_id -> {second_node_id -> distance between them}
		self._distances: Dict[int, Dict[int, float]] = {}
		# node_id -> Node
		self._nodes: Dict[int, Node] = {}
		# request_id -> Request
		self._requests: Dict[int, Request] = {}
		# vehicle_id -> Vehicle
		self._vehicles: Dict[int, Vehicle] = {}
		# vehicle_id -> {first_node_id -> {second_node_id -> run_time}}
		self._vehicleRunBetweenNodesTime: Dict[int, Dict[int, Dict[int, float]]] = {}
		
		self._alpha = 1.0
		self._beta = 1.0
		self._gama = 1000000000.0

	def get_max_distance(self):
		return max((v for d in self.distances.values() for v in d.values()), default=None)
		
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

	@property
	def gama(self):
		return self._gama
	
	