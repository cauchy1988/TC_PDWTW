#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2024 cauchy1988

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import copy
from typing import Dict, Optional
from parameters import Parameters
from node import Node
from request import Request
from vehicle import Vehicle


class Meta:
	def __init__(self, parameters: Parameters):
		# running parameters
		self.parameters = parameters
		
		# first_node_id -> {second_node_id -> distance between them}
		self.distances: Dict[int, Dict[int, float]] = {}
		# node_id -> Node
		self.nodes: Dict[int, Node] = {}
		# request_id -> Request
		self.requests: Dict[int, Request] = {}
		# vehicle_id -> Vehicle
		self.vehicles: Dict[int, Vehicle] = {}
		# vehicle_id -> {first_node_id -> {second_node_id -> run_time}}
		self.vehicle_run_between_nodes_time: Dict[int, Dict[int, Dict[int, float]]] = {}
	
	def _validate_homogeneous_fleet(self) -> bool:
		"""Validate that all vehicles are identical (proper homogeneity check)."""
		if len(self.vehicles) <= 1:
			return True
		
		vehicles_list = list(self.vehicles.values())
		reference_vehicle = vehicles_list[0]
		
		# Check ALL vehicles against the reference, not just random sampling
		for vehicle in vehicles_list[1:]:
			if not reference_vehicle.equals(vehicle):
				return False
		return True
	
	# this interface only use for problems with homogeneous fleet
	def add_one_same_vehicle(self, new_vehicle_id: Optional[int] = None) -> int :
		if len(self.vehicles) == 0:
			raise RuntimeError('vehicles is empty!')
		
		# Generate new vehicle ID if not provided
		if new_vehicle_id is None:
			max_vehicle_id = max(self.vehicles.keys())
			new_vehicle_id = max_vehicle_id + 1
		
		# Check if vehicle ID already exists
		if new_vehicle_id in self.vehicles:
			raise ValueError(f'Vehicle with ID {new_vehicle_id} already exists!')
		
		# Proper homogeneity check for all vehicles
		if not self._validate_homogeneous_fleet():
			raise RuntimeError('vehicles must have the same value because they belong to homogeneous fleet!')
		
		# Get reference vehicle (any vehicle since they should all be the same)
		reference_vehicle = next(iter(self.vehicles.values()))
		
		# Add new vehicle to the Meta structure
		self.vehicles[new_vehicle_id] = Vehicle(
			new_vehicle_id,
			reference_vehicle.capacity,
			reference_vehicle.velocity,
			reference_vehicle.start_node_id,
			reference_vehicle.end_node_id,
		)
		
		# Safely copy vehicle run time data
		reference_vehicle_id = reference_vehicle.identity
		if reference_vehicle_id in self.vehicle_run_between_nodes_time:
			self.vehicle_run_between_nodes_time[new_vehicle_id] = copy.deepcopy(
				self.vehicle_run_between_nodes_time[reference_vehicle_id])
		else:
			# Initialize empty if reference doesn't exist
			self.vehicle_run_between_nodes_time[new_vehicle_id] = {}
		
		# Add the new vehicle to all requests
		for one_request in self.requests.values():
			one_request.vehicle_set.add(new_vehicle_id)
			
		return new_vehicle_id
	
	def delete_vehicle(self, deleted_vehicle_id: int) -> bool:
		if deleted_vehicle_id not in self.vehicles:
			return False  # Return False to indicate nothing was deleted
		
		# Prevent deletion of the last vehicle
		if len(self.vehicles) <= 1:
			raise RuntimeError('Cannot delete the last vehicle! At least one vehicle must remain.')
		
		# Delete the vehicle from the Meta structure
		del self.vehicles[deleted_vehicle_id]
		
		# Safely delete from vehicle run time data
		if deleted_vehicle_id in self.vehicle_run_between_nodes_time:
			del self.vehicle_run_between_nodes_time[deleted_vehicle_id]
		
		# Remove vehicle from all requests
		for one_request in self.requests.values():
			one_request.vehicle_set.discard(deleted_vehicle_id)  # discard() won't raise KeyError
		
		return True  # Return True to indicate successful deletion
	
	def get_max_distance(self) -> Optional[float]:
		if not self.distances:
			return None
		return float(max((v for d in self.distances.values() for v in d.values()), default=None))
	
	def max_vehicle_id(self) -> Optional[int]:
		if not self.vehicles:
			return None
		return max(self.vehicles.keys())
	
	def get_vehicle_count(self) -> int:
		"""Get the current number of vehicles."""
		return len(self.vehicles)
	
	def is_homogeneous_fleet(self) -> bool:
		"""Check if the current fleet is homogeneous."""
		return self._validate_homogeneous_fleet()