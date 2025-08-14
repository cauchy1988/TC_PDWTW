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


from __future__ import annotations

import abc
import copy
import hashlib
from abc import ABC
from typing import Dict
from meta import Meta
from path import Path


class InnerDictForNormalization:
	"""Container for normalized difference values between requests"""
	
	def __init__(self) -> None:
		# smaller request_id -> {bigger request_id -> normalized value}
		self.distance_pick_dict: Dict[int, Dict[int, float]] = {}
		self.distance_delivery_dict: Dict[int, Dict[int, float]] = {}
		self.start_time_diff_pick_dict: Dict[int, Dict[int, float]] = {}
		self.start_time_diff_delivery_dict: Dict[int, Dict[int, float]] = {}
		self.load_diff_dict: Dict[int, Dict[int, float]] = {}
		self.vehicle_set_diff_dict: Dict[int, Dict[int, float]] = {}
	
	def copy(self) -> InnerDictForNormalization:
		new_obj = InnerDictForNormalization()
		
		new_obj.distance_pick_dict = copy.deepcopy(self.distance_pick_dict)
		new_obj.distance_delivery_dict = copy.deepcopy(self.distance_delivery_dict)
		new_obj.start_time_diff_pick_dict = copy.deepcopy(self.start_time_diff_pick_dict)
		new_obj.start_time_diff_delivery_dict = copy.deepcopy(self.start_time_diff_delivery_dict)
		new_obj.load_diff_dict = copy.deepcopy(self.load_diff_dict)
		new_obj.vehicle_set_diff_dict = copy.deepcopy(self.vehicle_set_diff_dict)
		
		return new_obj


def _normalize_dict(nested_dict: Dict, epsilon: float = 1e-6) -> Dict:
	"""
	Normalize values in a nested dictionary to [0, 1] range
	
	Args:
		nested_dict: Dictionary to normalize
		epsilon: Threshold for considering values equal
		
	Returns:
		Normalized dictionary with values in [0, 1] range
	"""
	all_values = []
	for outer_key, inner_dict in nested_dict.items():
		for inner_key, value in inner_dict.items():
			all_values.append(value)
	
	if not all_values:
		return nested_dict
	
	min_value = min(all_values)
	max_value = max(all_values)
	
	if abs(max_value - min_value) < epsilon:
		normalized_dict = {}
		for outer_key, inner_dict in nested_dict.items():
			normalized_inner_dict = {}
			for inner_key, value in inner_dict.items():
				normalized_inner_dict[inner_key] = 0.0  # All values normalized to 0.0
			normalized_dict[outer_key] = normalized_inner_dict
	else:
		normalized_dict = {}
		for outer_key, inner_dict in nested_dict.items():
			normalized_inner_dict = {}
			for inner_key, value in inner_dict.items():
				normalized_value = (value - min_value) / (max_value - min_value)
				normalized_inner_dict[inner_key] = normalized_value
			normalized_dict[outer_key] = normalized_inner_dict
	
	return normalized_dict


def generate_normalization_dict(meta_obj: Meta, one_solution: PDWTWSolution) -> InnerDictForNormalization:
	"""
	Generate normalized difference values between all requests in a solution
	
	Args:
		meta_obj: Meta object containing problem data
		one_solution: Solution to analyze
		
	Returns:
		Normalized difference values container
	"""
	# init difference's dict
	distance_pic_dict = {}
	distance_delivery_dict = {}
	start_time_diff_pick_dict = {}
	start_time_diff_delivery_dict = {}
	load_diff_dict = {}
	vehicle_set_diff = {}
	
	request_id_list = [request_id for request_id in one_solution.request_id_to_vehicle_id]
	request_id_list.sort()
	for i in range(len(request_id_list)):
		distance_pic_dict[request_id_list[i]] = {}
		distance_delivery_dict[request_id_list[i]] = {}
		start_time_diff_pick_dict[request_id_list[i]] = {}
		start_time_diff_delivery_dict[request_id_list[i]] = {}
		load_diff_dict[request_id_list[i]] = {}
		vehicle_set_diff[request_id_list[i]] = {}
		
		first_pick_node_id = meta_obj.requests[request_id_list[i]].pick_node_id
		first_delivery_node_id = meta_obj.requests[request_id_list[i]].delivery_node_id
		
		first_pick_node_start_time = one_solution.get_node_start_service_time_in_path(first_pick_node_id)
		first_delivery_node_start_time = one_solution.get_node_start_service_time_in_path(first_delivery_node_id)
		for j in range(i + 1, len(request_id_list)):
			second_pick_node_id = meta_obj.requests[request_id_list[j]].pick_node_id
			second_delivery_node_id = meta_obj.requests[request_id_list[j]].delivery_node_id
			
			second_pick_node_start_time = one_solution.get_node_start_service_time_in_path(second_pick_node_id)
			second_delivery_node_start_time = one_solution.get_node_start_service_time_in_path(second_delivery_node_id)
			
			# update dicts
			distance_pic_dict[request_id_list[i]][request_id_list[j]] = meta_obj.distances[first_pick_node_id][
				second_pick_node_id]
			distance_delivery_dict[request_id_list[i]][request_id_list[j]] = meta_obj.distances[first_delivery_node_id][
				second_delivery_node_id]
			
			start_time_diff_pick_dict[request_id_list[i]][request_id_list[j]] = abs(
				first_pick_node_start_time - second_pick_node_start_time)
			start_time_diff_delivery_dict[request_id_list[i]][request_id_list[j]] = abs(
				first_delivery_node_start_time - second_delivery_node_start_time)
			
			load_diff_dict[request_id_list[i]][request_id_list[j]] = abs(
				meta_obj.requests[request_id_list[i]].require_capacity - meta_obj.requests[
					request_id_list[j]].require_capacity)
			
			vehicle_set_diff[request_id_list[i]][request_id_list[j]] = (1 - len(
				meta_obj.requests[request_id_list[i]].vehicle_set & meta_obj.requests[
					request_id_list[j]].vehicle_set) / min(len(meta_obj.requests[request_id_list[i]].vehicle_set),
			                                               len(meta_obj.requests[request_id_list[j]].vehicle_set)))
	
	# normalize first five dict value
	normalization_obj = InnerDictForNormalization()
	normalization_obj.distance_pick_dict = _normalize_dict(distance_pic_dict)
	normalization_obj.distance_delivery_dict = _normalize_dict(distance_delivery_dict)
	normalization_obj.start_time_diff_pick_dict = _normalize_dict(start_time_diff_pick_dict)
	normalization_obj.start_time_diff_delivery_dict = _normalize_dict(start_time_diff_delivery_dict)
	normalization_obj.load_diff_dict = _normalize_dict(load_diff_dict)
	
	# need not be normalized
	normalization_obj.vehicle_set_diff_dict = vehicle_set_diff
	
	return normalization_obj


def generate_solution_finger_print(paths: Dict[int, Path]) -> str:
	"""Generate a robust fingerprint for the solution based on paths.
	
	Uses a more reliable approach than string conversion by directly hashing
	the structured route data to avoid string representation instabilities.
	
	Args:
		paths: Dictionary mapping vehicle IDs to their paths
		
	Returns:
		Hexadecimal fingerprint string
		
	Raises:
		ValueError: If paths is None or contains None values
	"""
	if paths is None:
		raise ValueError("paths cannot be None")
	
	# Create a deterministic representation using sorted tuples
	route_data = []
	for vehicle_id in sorted(paths.keys()):
		path = paths[vehicle_id]
		if path is None:
			raise ValueError(f"Path for vehicle {vehicle_id} is None")
		if path.route is None:
			raise ValueError(f"Route for vehicle {vehicle_id} is None")
		
		# Create tuple of (vehicle_id, tuple_of_route_nodes)
		route_tuple = (vehicle_id, tuple(path.route))
		route_data.append(route_tuple)
	
	# Convert to bytes in a deterministic way
	fingerprint_data = str(tuple(route_data)).encode('utf-8')
	
	# Use a faster hash function for better performance
	import hashlib
	return hashlib.blake2b(fingerprint_data, digest_size=16).hexdigest()


class Solution(ABC):
	@abc.abstractmethod
	def __init__(self, meta_obj: Meta):
		pass


class PDWTWSolution(Solution):
	"""Solution class for Pickup and Delivery Problem with Time Windows (PDWTW)"""
	
	def __init__(self, meta_obj: Meta):
		"""
		Initialize a PDWTW solution
		
		Args:
			meta_obj: Meta object containing problem data
		"""
		self.meta_obj = meta_obj
		# vehicle_id -> Path
		self.paths: Dict[int, Path] = {}
		self.request_bank = set([request_id for request_id in meta_obj.requests])
		self.request_id_to_vehicle_id: Dict[int, int] = {}
		
		# only preserve pickup and delivery node id map
		self.node_id_to_vehicle_id: Dict[int, int] = {}
		
		self.vehicle_bank = set([vehicle_id for vehicle_id in meta_obj.vehicles])
		
		self.distance_cost = 0.0
		self.time_cost = 0.0
		
		self.finger_print = generate_solution_finger_print(self.paths)
	
	# this interface only use for problems with homogeneous fleet
	def add_one_same_vehicle(self, one_vehicle_id: int = None) -> int:
		"""Add one more vehicle of the same type to the solution"""
		new_vehicle_id = self.meta_obj.add_one_same_vehicle(one_vehicle_id)
		# update one_solution
		self.vehicle_bank.add(new_vehicle_id)
		return new_vehicle_id
	
	# this interface only use for problems with homogeneous fleet
	def delete_vehicle_and_its_route(self, delete_vehicle_id: int):
		"""Delete a vehicle and its associated route"""
		if delete_vehicle_id not in self.paths and delete_vehicle_id not in self.vehicle_bank:
			raise ValueError(f"Vehicle {delete_vehicle_id} not found in solution")
		
		deleted_requests = set([request_id for request_id, vehicle_id in self.request_id_to_vehicle_id if delete_vehicle_id == vehicle_id])
		self.remove_requests(deleted_requests)
		self.vehicle_bank.remove(delete_vehicle_id)
		
		self.meta_obj.delete_vehicle(delete_vehicle_id)
	
	def copy(self):
		"""Create a deep copy of the solution"""
		new_obj = PDWTWSolution(self.meta_obj)
		for vehicle_id, the_path in self.paths.items():
			new_obj.paths[vehicle_id] = the_path.copy()
		new_obj.request_bank = self.request_bank.copy()
		new_obj.request_id_to_vehicle_id = self.request_id_to_vehicle_id.copy()
		new_obj.node_id_to_vehicle_id = self.node_id_to_vehicle_id.copy()
		new_obj.vehicle_bank = self.vehicle_bank.copy()
		
		new_obj.distance_cost = self.distance_cost
		new_obj.time_cost = self.time_cost
		
		new_obj.finger_print = self.finger_print
		
		return new_obj
	
	def cost_if_remove_request(self, request_id: int) -> float:
		"""Calculate the cost if a request is removed from the solution"""
		if request_id not in self.request_id_to_vehicle_id:
			raise ValueError(f"Request {request_id} not found in solution")
		
		vehicle_id = self.request_id_to_vehicle_id[request_id]
		if vehicle_id not in self.paths:
			raise RuntimeError(f"Vehicle {vehicle_id} not found in paths")
		
		origin_path = self.paths[vehicle_id].copy()
		if origin_path is None:
			raise RuntimeError(f"Path for vehicle {vehicle_id} is None")
		
		copied_path = origin_path.copy()
		distance_diff, time_diff = copied_path.try_to_remove_request(request_id)
		
		return self.meta_obj.parameters.alpha * distance_diff + self.meta_obj.parameters.beta * time_diff
	
	def cost_if_insert_request_to_vehicle_path(self, request_id: int, vehicle_id: int) -> tuple[bool, float]:
		"""Calculate the cost if a request is inserted into a specific vehicle path"""
		if request_id not in self.request_bank:
			raise ValueError(f"Request {request_id} not in request bank")
		
		if vehicle_id not in self.vehicle_bank and vehicle_id not in self.paths:
			raise ValueError(f"Vehicle {vehicle_id} not found in solution")
		
		if vehicle_id not in self.meta_obj.requests[request_id].vehicle_set:
			return False, 0.0
		
		if vehicle_id in self.paths:
			the_path = self.paths[vehicle_id].copy()
		else:
			the_path = Path(vehicle_id, self.meta_obj)
		
		ok, distance_diff, time_diff = the_path.try_to_insert_request_optimal(request_id)
		
		if not ok:
			return False, 0.0
		
		return True, self.meta_obj.parameters.alpha * distance_diff + self.meta_obj.parameters.beta * time_diff
	
	def remove_requests(self, request_id_set):
		"""Remove multiple requests from the solution"""
		for request_id in request_id_set:
			if request_id not in self.request_id_to_vehicle_id:
				raise ValueError(f"Request {request_id} not found in solution")
			
			vehicle_id = self.request_id_to_vehicle_id[request_id]
			if vehicle_id not in self.paths:
				raise RuntimeError(f"Vehicle {vehicle_id} not found in paths")
			
			path_obj = self.paths[vehicle_id]
			_, __ = path_obj.try_to_remove_request(request_id)
			
			# update Solution's inner data structure
			self.request_bank.add(request_id)
			del self.request_id_to_vehicle_id[request_id]
			request_obj = self.meta_obj.requests[request_id]
			pick_node_id = request_obj.pick_node_id
			delivery_node_id = request_obj.delivery_node_id
			del self.node_id_to_vehicle_id[pick_node_id]
			del self.node_id_to_vehicle_id[delivery_node_id]
			if path_obj.is_path_free():
				del self.paths[vehicle_id]
				self.vehicle_bank.add(vehicle_id)
			
			self._update_objective_cost_all()
			self.finger_print = generate_solution_finger_print(self.paths)
	
	def insert_one_request_to_one_vehicle_route_optimal(self, request_id: int, vehicle_id: int) -> bool:
		"""Insert a request into a specific vehicle route optimally"""
		if request_id not in self.request_bank:
			raise ValueError(f"Request {request_id} not in request bank")
		
		if vehicle_id not in self.meta_obj.requests[request_id].vehicle_set:
			return False
		
		if vehicle_id in self.vehicle_bank:
			the_path = Path(vehicle_id, self.meta_obj)
		else:
			if vehicle_id not in self.paths:
				raise ValueError(f"Vehicle {vehicle_id} not found in paths")
			the_path = self.paths[vehicle_id]
		
		ok, _, __ = the_path.try_to_insert_request_optimal(request_id)
		if ok:
			self.request_bank.remove(request_id)
			self.request_id_to_vehicle_id[request_id] = vehicle_id
			request_obj = self.meta_obj.requests[request_id]
			self.node_id_to_vehicle_id[request_obj.pick_node_id] = vehicle_id
			self.node_id_to_vehicle_id[request_obj.delivery_node_id] = vehicle_id
			if vehicle_id in self.vehicle_bank:
				self.vehicle_bank.remove(vehicle_id)
				self.paths[vehicle_id] = the_path
			self._update_objective_cost_all()
			self.finger_print = generate_solution_finger_print(self.paths)
		return ok
	
	def insert_one_request_to_any_vehicle_route_optimal(self, request_id: int) -> bool:
		"""Insert a request into any available vehicle route optimally"""
		if request_id not in self.request_bank:
			raise ValueError(f"Request {request_id} not in request bank")
		
		vehicle_id_list = list(self.meta_obj.requests[request_id].vehicle_set & (self.vehicle_bank | list(self.paths.keys())))
		
		for vehicle_id in vehicle_id_list:
			if self.insert_one_request_to_one_vehicle_route_optimal(request_id, vehicle_id):
				return True
		
		return False
	
	def get_node_start_service_time_in_path(self, node_id: int) -> float:
		"""Get the start service time for a node in the solution"""
		if node_id not in self.node_id_to_vehicle_id:
			raise ValueError(f"Node {node_id} not found in solution")
		
		vehicle_id = self.node_id_to_vehicle_id[node_id]
		if vehicle_id not in self.paths:
			raise RuntimeError(f"Vehicle {vehicle_id} not found in paths")
		
		path_obj = self.paths[vehicle_id]
		return path_obj.get_node_start_service_time(node_id)
	
	def _update_objective_cost_all(self) -> None:
		"""Update the total distance and time costs for all paths"""
		self.distance_cost = 0.0
		self.time_cost = 0.0
		for vehicle_id in self.paths:
			self.distance_cost += self.paths[vehicle_id].whole_distance_cost
			self.time_cost += self.paths[vehicle_id].whole_time_cost
			
	def max_vehicle_id(self):
		"""Get the maximum vehicle ID in the solution"""
		if not self.paths and not self.vehicle_bank:
			return None
		
		paths_max = max(self.paths.keys()) if self.paths else 0
		bank_max = max(self.vehicle_bank) if self.vehicle_bank else 0
		max_vehicle_id = max(paths_max, bank_max)
		
		if hasattr(self.meta_obj, 'max_vehicle_id'):
			if max_vehicle_id != self.meta_obj.max_vehicle_id:
				raise RuntimeError(f"Vehicle ID mismatch: {max_vehicle_id} != {self.meta_obj.max_vehicle_id}")
		
		return max_vehicle_id
	
	@property
	def objective_cost(self):
		return self.meta_obj.parameters.alpha * self.distance_cost + self.meta_obj.parameters.beta * self.time_cost + self.meta_obj.parameters.gama * len(
			self.request_bank)
	
	@property
	def objective_cost_without_request_bank(self):
		return self.meta_obj.parameters.alpha * self.distance_cost + self.meta_obj.parameters.beta * self.time_cost
