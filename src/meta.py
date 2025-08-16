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
		
		# Get reference vehicle (any vehicle since they should all be the same)
		reference_vehicle = next(iter(self.vehicles.values()))
		
		new_vehicle_start_node_id = max(self.nodes.keys()) + 1
		new_vehicle_end_node_id = new_vehicle_start_node_id + 1
		
		random_depot_node = self.nodes[reference_vehicle.start_node_id]
		self.nodes[new_vehicle_start_node_id] = Node(new_vehicle_start_node_id, random_depot_node.x, random_depot_node.y, random_depot_node.earliest_service_time, random_depot_node.latest_service_time, random_depot_node.service_time, random_depot_node.load)
		self.nodes[new_vehicle_end_node_id] = Node(new_vehicle_end_node_id, random_depot_node.x, random_depot_node.y, random_depot_node.earliest_service_time, random_depot_node.latest_service_time, random_depot_node.service_time, random_depot_node.load)

		# Add new vehicle to the Meta structure
		self.vehicles[new_vehicle_id] = Vehicle(
			new_vehicle_id,
			reference_vehicle.capacity,
			reference_vehicle.velocity,
			new_vehicle_start_node_id,
			new_vehicle_end_node_id
		)
		
		# Initialize vehicle_run_between_nodes_time for the new vehicle
		self.vehicle_run_between_nodes_time[new_vehicle_id] = {}
		for from_node_id in self.nodes.keys():
			self.vehicle_run_between_nodes_time[new_vehicle_id][from_node_id] = {}
			for to_node_id in self.nodes.keys():
				if from_node_id == to_node_id:
					self.vehicle_run_between_nodes_time[new_vehicle_id][from_node_id][to_node_id] = 0.0
				else:
					# Calculate travel time = distance / speed
					distance = self.distances.get(from_node_id, {}).get(to_node_id, 0.0)
					travel_time = distance / reference_vehicle.velocity if reference_vehicle.velocity > 0 else distance
					self.vehicle_run_between_nodes_time[new_vehicle_id][from_node_id][to_node_id] = travel_time
		
		# Add the new vehicle to all requests
		for one_request in self.requests.values():
			one_request.vehicle_set.add(new_vehicle_id)
			
		# Update distances
		random_depot_node_id = random_depot_node.node_id
		for from_node_id, to_node_dict in self.distances.items():
			to_node_dict[new_vehicle_start_node_id] = to_node_dict[random_depot_node_id]
			to_node_dict[new_vehicle_end_node_id] = to_node_dict[random_depot_node_id]
		self.distances[new_vehicle_start_node_id] = copy.deepcopy(self.distances[random_depot_node_id])
		self.distances[new_vehicle_start_node_id][new_vehicle_end_node_id] = 0.0
		self.distances[new_vehicle_end_node_id] = copy.deepcopy(self.distances[random_depot_node_id])
		self.distances[new_vehicle_end_node_id][new_vehicle_start_node_id] = 0.0
		
		for vehicle_id, time_dict in self.vehicle_run_between_nodes_time.items():
			for from_node_id, to_node_dict in time_dict.items():
				to_node_dict[new_vehicle_start_node_id] = to_node_dict[random_depot_node_id]
				to_node_dict[new_vehicle_end_node_id] = to_node_dict[random_depot_node_id]
			time_dict[new_vehicle_start_node_id] = copy.deepcopy(time_dict[random_depot_node_id])
			time_dict[new_vehicle_end_node_id] = copy.deepcopy(time_dict[random_depot_node_id])
			time_dict[new_vehicle_start_node_id][new_vehicle_end_node_id] = 0.0
			time_dict[new_vehicle_end_node_id][new_vehicle_start_node_id] = 0.0

		return new_vehicle_id
	
	def delete_vehicle(self, deleted_vehicle_id: int) -> bool:
		if deleted_vehicle_id not in self.vehicles:
			return False  # Return False to indicate nothing was deleted
		
		# Prevent deletion of the last vehicle
		if len(self.vehicles) <= 1:
			raise RuntimeError('Cannot delete the last vehicle! At least one vehicle must remain.')
		
		start_depot_node_id = self.vehicles[deleted_vehicle_id].start_node_id
		end_depot_node_id = self.vehicles[deleted_vehicle_id].end_node_id
		
		# Check if other vehicles are using these nodes - this should never happen if logic is correct
		start_node_in_use = any(veh.start_node_id == start_depot_node_id or veh.end_node_id == start_depot_node_id 
		                        for veh_id, veh in self.vehicles.items() if veh_id != deleted_vehicle_id)
		end_node_in_use = any(veh.start_node_id == end_depot_node_id or veh.end_node_id == end_depot_node_id 
		                      for veh_id, veh in self.vehicles.items() if veh_id != deleted_vehicle_id)
		
		# If nodes are shared, this is a bug - throw exception
		if start_node_in_use or end_node_in_use:
			raise RuntimeError(f"Vehicle {deleted_vehicle_id} has shared nodes with other vehicles: start_node_in_use={start_node_in_use}, end_node_in_use={end_node_in_use}")
		
		# Delete the vehicle from the Meta structure
		del self.vehicles[deleted_vehicle_id]
		
		# Delete from vehicle run time data
		if deleted_vehicle_id in self.vehicle_run_between_nodes_time:
			del self.vehicle_run_between_nodes_time[deleted_vehicle_id]
		
		# Delete nodes and all related data - they should definitely exist and not be shared
		del self.nodes[start_depot_node_id]
		del self.nodes[end_depot_node_id]
		
		# Delete from all time dictionaries
		for vehicle_id, time_dict in self.vehicle_run_between_nodes_time.items():
			for from_node_id, to_node_id_dict in time_dict.items():
				del to_node_id_dict[start_depot_node_id]
				del to_node_id_dict[end_depot_node_id]
			del time_dict[start_depot_node_id]
			del time_dict[end_depot_node_id]

		# Remove vehicle from all requests
		for one_request in self.requests.values():
			one_request.vehicle_set.discard(deleted_vehicle_id)  # discard() won't raise KeyError
		
		# Delete from distances
		for from_node_id, node_id_dict in self.distances.items():
			del node_id_dict[start_depot_node_id]
			del node_id_dict[end_depot_node_id]
		del self.distances[start_depot_node_id]
		del self.distances[end_depot_node_id]

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
	