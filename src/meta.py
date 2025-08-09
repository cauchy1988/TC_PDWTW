#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:14
# @Author: Tang Chao
# @File: meta.py
# @Software: PyCharm
import copy
import random
from typing import Dict
from parameters import Parameters
from node import Node
from request import Request
from vehicle import Vehicle


class Meta:
	def __init__(self, parameters: Parameters):
		# running parameters
		self.parameters = parameters
		
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
	
	# this interface only use for problems with homogeneous fleet
	def add_one_same_vehicle(self, new_vehicle_id: int):
		if new_vehicle_id is None:
			max_vehicle_id = max(self.vehicles.keys())
			new_vehicle_id = max_vehicle_id + 1
		
		# random check the similarity of any two vehicles
		values = list(self.vehicles.values())
		assert values
		selected_two_values = random.choices(values, k=2)
		assert selected_two_values[0].equals(selected_two_values[1])
		
		# update meta_obj
		# add a new vehicle to the Meta structure
		self.vehicles[new_vehicle_id] = Vehicle(new_vehicle_id, selected_two_values[0].capacity,
		                                            selected_two_values[0].velocity, selected_two_values[0].startNodeId,
		                                            selected_two_values[0].endNodeId)
		self.vehicle_run_between_nodes_time[new_vehicle_id] = copy.deepcopy(
			self.vehicle_run_between_nodes_time[selected_two_values[0].identity])
		# add the new vehicle to the Meta structure's requests
		for one_request in self.requests.values():
			one_request.vehicle_set.add(new_vehicle_id)
		# vehicles of a homogeneous fleet have the same start node and end node, so need not add new node to the Meta structure
	
	def delete_vehicle(self, deleted_vehicle_id: int):
		if deleted_vehicle_id not in self.vehicles:
			return
		
		# delete the vehicle from the Meta structure
		del self.vehicles[deleted_vehicle_id]
		del self.vehicle_run_between_nodes_time[deleted_vehicle_id]
		
		# delete the vehicle from the requests
		for one_request in self.requests.values():
			if deleted_vehicle_id in one_request.vehicle_set:
				one_request.vehicle_set.remove(deleted_vehicle_id)
		# vehicles of a homogeneous fleet have the same start node and end node, so need not add new node to the Meta structure
		
		# at least one vehicle should be left in the Meta structure
		assert self.vehicles

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
	