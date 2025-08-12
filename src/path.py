#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/20 00:05
# @Author: Tang Chao
# @File: path.py
# @Software: PyCharm
from __future__ import annotations
from typing import List, Tuple, Optional
from meta import Meta


class PathError(Exception):
	"""Custom exception for Path operations"""
	pass


class Path:
	def __init__(self, vehicle_id: int, meta_obj: Meta, need_init=True):
		self.meta_obj = meta_obj
		self.vehicle_id = vehicle_id
		
		if need_init:
			# node id route
			start_node_id = self.meta_obj.vehicles[self.vehicle_id].start_node_id
			end_node_id = self.meta_obj.vehicles[self.vehicle_id].end_node_id
			self.route: List[int] = [start_node_id, end_node_id]
			
			# start the service time along the node route
			earliest_time = self.meta_obj.nodes[start_node_id].earliest_service_time
			arrival_time = earliest_time + self.meta_obj.nodes[start_node_id].service_time + self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][start_node_id][end_node_id]
			latest_time = max(arrival_time, self.meta_obj.nodes[end_node_id].earliest_service_time)
			
			if latest_time > self.meta_obj.nodes[end_node_id].latest_service_time:
				raise PathError(f"Time window violation: {latest_time} > {self.meta_obj.nodes[end_node_id].latest_service_time}")
			
			self.start_service_time_line: List[int] = [earliest_time, latest_time]
			
			# capacity load line
			# load after each node in route
			self.load_line = [self.meta_obj.nodes[start_node_id].load,
			                  self.meta_obj.nodes[start_node_id].load + self.meta_obj.nodes[end_node_id].load]
			
			# distance accumulated
			end_distance = self.meta_obj.distances[start_node_id][end_node_id]
			self.distances = [0, end_distance]
			
			# time cost of the whole route
			self.whole_time_cost = self.start_service_time_line[-1] - self.start_service_time_line[0]

	def copy(self):
		new_path = Path(self.vehicle_id, self.meta_obj, False)
		new_path.meta_obj = self.meta_obj
		new_path.vehicle_id = self.vehicle_id
		new_path.route = self.route.copy()
		new_path.start_service_time_line = self.start_service_time_line.copy()
		new_path.load_line = self.load_line.copy()
		new_path.distances = self.distances.copy()
		new_path.whole_time_cost = self.whole_time_cost
		
		return new_path
	
	def is_path_free(self):
		return len(self.route) <= 2

	@property
	def whole_distance_cost(self):
		return self.distances[-1] if self.distances else 0.0

	@classmethod
	def get_path_distance_diff(cls, first_path, second_path):
		if not first_path.distances or not second_path.distances:
			return 0.0
		return second_path.distances[-1] - first_path.distances[-1]
	
	@classmethod
	def get_path_time_cost_diff(cls, first_path, second_path):
		return second_path.whole_time_cost - first_path.whole_time_cost

	def _update_service_times_after_insertion(self, start_idx: int) -> bool:
		"""Update service times after inserting nodes at start_idx"""
		for i in range(start_idx, len(self.start_service_time_line)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			new_start_time = max(self.start_service_time_line[i - 1] +
							    self.meta_obj.nodes[prev_node_id].service_time +
			                    self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][prev_node_id][current_node_id],
			                    self.meta_obj.nodes[current_node_id].earliest_service_time)
			
			if new_start_time > self.meta_obj.nodes[current_node_id].latest_service_time:
				return False
			self.start_service_time_line[i] = new_start_time
		return True

	def _update_loads_after_insertion(self, pick_idx: int, delivery_idx: int) -> bool:
		"""Update loads after inserting pickup and delivery nodes"""
		for i in range(pick_idx, delivery_idx + 1):
			current_node_id = self.route[i]
			new_load = self.load_line[i - 1] + self.meta_obj.nodes[current_node_id].load
			if new_load > self.meta_obj.vehicles[self.vehicle_id].capacity:
				return False
			self.load_line[i] = new_load
		return True

	def _update_distances_after_insertion(self, start_idx: int):
		"""Update distances after inserting nodes at start_idx"""
		for i in range(start_idx, len(self.distances)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			current_distance = self.distances[i - 1] + \
							   self.meta_obj.distances[prev_node_id][current_node_id]
			self.distances[i] = current_distance

	def try_to_insert_request(self, request_id: int, pick_insert_idx: int, delivery_insert_idx: int) -> Tuple[bool, float, float]:
		"""Try to insert a request into the path"""
		if pick_insert_idx >= delivery_insert_idx:
			return False, 0.0, 0.0
			
		pick_node_id = self.meta_obj.requests[request_id].pick_node_id
		delivery_node_id = self.meta_obj.requests[request_id].delivery_node_id
		
		# Insert nodes
		self.route.insert(pick_insert_idx, pick_node_id)
		self.route.insert(delivery_insert_idx, delivery_node_id)
		
		# Insert placeholder values
		self.start_service_time_line.insert(pick_insert_idx, 0)
		self.start_service_time_line.insert(delivery_insert_idx, 0)
		
		# Update service times
		if not self._update_service_times_after_insertion(pick_insert_idx):
			return False, 0.0, 0.0
			
		# Update time cost
		current_whole_time_cost = self.start_service_time_line[-1] - self.start_service_time_line[0]
		time_cost_diff = current_whole_time_cost - self.whole_time_cost
		self.whole_time_cost = current_whole_time_cost
			
		# Insert placeholder loads
		self.load_line.insert(pick_insert_idx, 0.0)
		self.load_line.insert(delivery_insert_idx, 0.0)
		
		# Update loads
		if not self._update_loads_after_insertion(pick_insert_idx, delivery_insert_idx):
			return False, 0.0, 0.0
			
		# Insert placeholder distances
		prev_distance = self.distances[-1] if self.distances else 0.0
		self.distances.insert(pick_insert_idx, 0.0)
		self.distances.insert(delivery_insert_idx, 0.0)
		
		# Update distances
		self._update_distances_after_insertion(pick_insert_idx)
		
		current_distance = self.distances[-1] if self.distances else 0.0
		distance_diff = current_distance - prev_distance
		
		return True, float(distance_diff), float(time_cost_diff)
		
	def try_to_insert_request_optimal(self, request_id: int) -> Tuple[bool, float, float, Optional['Path']]:
		"""Find optimal insertion position for a request"""
		if self.vehicle_id not in self.meta_obj.requests[request_id].vehicle_set:
			return False, 0, 0, None
		
		route_len = len(self.route)
		new_path_list = []
		
		for i in range(1, route_len):
			for j in range(i + 1, route_len + 1):
				new_path = self.copy()
				ok, distance_diff, time_cost_diff = new_path.try_to_insert_request(request_id, i, j)
				if ok:
					new_path_list.append((distance_diff, time_cost_diff, new_path))
				
		if not new_path_list:
			return False, 0, 0, None
		
		# Sort by weighted cost
		new_path_list.sort(key=lambda item: (
			self.meta_obj.parameters.alpha * item[0], 
			self.meta_obj.parameters.beta * item[1]
		))
		
		best_path = new_path_list[0]
		return True, best_path[0], best_path[1], best_path[2]
	
	def _update_service_times_after_removal(self, start_idx: int) -> bool:
		"""Update service times after removing nodes"""
		for i in range(start_idx, len(self.start_service_time_line)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			new_start_time = max(self.start_service_time_line[i - 1] +
			                     self.meta_obj.nodes[prev_node_id].service_time +
			                     self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][prev_node_id][current_node_id],
			                     self.meta_obj.nodes[current_node_id].earliest_service_time)
			
			if new_start_time > self.meta_obj.nodes[current_node_id].latest_service_time:
				return False
			self.start_service_time_line[i] = new_start_time
		return True

	def _update_loads_after_removal(self, pick_idx: int, delivery_idx: int) -> bool:
		"""Update loads after removing pickup and delivery nodes"""
		# Only update loads between pickup and delivery if there are nodes in between
		if pick_idx < delivery_idx - 1:
			for i in range(pick_idx, delivery_idx - 1):
				current_node_id = self.route[i]
				new_load = self.load_line[i - 1] + self.meta_obj.nodes[current_node_id].load
				if new_load > self.meta_obj.vehicles[self.vehicle_id].capacity:
					return False
				self.load_line[i] = new_load
		return True

	def _update_distances_after_removal(self, start_idx: int):
		"""Update distances after removing nodes"""
		for i in range(start_idx, len(self.distances)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			current_distance = self.distances[i - 1] + \
			                   self.meta_obj.distances[prev_node_id][current_node_id]
			self.distances[i] = current_distance

	def try_to_remove_request(self, request_id: int) -> Tuple[float, float]:
		"""Try to remove a request from the path"""
		if self.vehicle_id not in self.meta_obj.requests[request_id].vehicle_set:
			raise PathError(f"Vehicle {self.vehicle_id} not in request {request_id} vehicle set")
			
		pick_node_id = self.meta_obj.requests[request_id].pick_node_id
		delivery_node_id = self.meta_obj.requests[request_id].delivery_node_id
		
		pick_node_idx = self.route.index(pick_node_id)
		delivery_node_idx = self.route.index(delivery_node_id)
		
		if pick_node_idx <= 0 or delivery_node_idx <= 0:
			raise PathError(f"Invalid node indices: pick={pick_node_idx}, delivery={delivery_node_idx}")

		# Remove nodes
		self.route.pop(pick_node_idx)
		self.route.pop(delivery_node_idx - 1)  # Adjust index after first removal

		# Update service times
		prev_whole_time_cost = self.whole_time_cost
		self.start_service_time_line.pop(pick_node_idx)
		self.start_service_time_line.pop(delivery_node_idx - 1)
		
		if not self._update_service_times_after_removal(pick_node_idx):
			raise PathError("Time window violation after removal")
		
		self.whole_time_cost = self.start_service_time_line[-1] - self.start_service_time_line[0]
		time_cost_diff = prev_whole_time_cost - self.whole_time_cost

		# Update loads
		self.load_line.pop(pick_node_idx)
		self.load_line.pop(delivery_node_idx - 1)
		
		if not self._update_loads_after_removal(pick_node_idx, delivery_node_idx):
			raise PathError("Capacity violation after removal")
		
		# Update distances
		prev_distance = self.distances[-1] if self.distances else 0.0
		self.distances.pop(pick_node_idx)
		self.distances.pop(delivery_node_idx - 1)
		
		self._update_distances_after_removal(pick_node_idx)
		
		current_distance = self.distances[-1] if self.distances else 0.0
		distance_diff = prev_distance - current_distance

		return float(distance_diff), float(time_cost_diff)

	def get_node_start_service_time(self, node_id: int) -> int:
		"""Get the start service time for a specific node"""
		if node_id not in self.route:
			raise PathError(f"Node {node_id} not found in route")
		node_idx = self.route.index(node_id)
		return self.start_service_time_line[node_idx]
		