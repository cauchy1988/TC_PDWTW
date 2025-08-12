#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/20 00:05
# @Author: Tang Chao
# @File: path.py
# @Software: PyCharm
from __future__ import annotations
from meta import Meta


class Path:
	def __init__(self, vehicle_id: int, meta_obj: Meta, need_init=True):
		self.meta_obj = meta_obj
		self.vehicle_id = vehicle_id
		
		if need_init:
			# node id route
			start_node_id = self.meta_obj.vehicles[self.vehicle_id].start_node_id
			end_node_id = self.meta_obj.vehicles[self.vehicle_id].end_node_id
			self.route = [start_node_id, end_node_id]
			
			# start the service time alone the node route
			earliest_time = self.meta_obj.nodes[start_node_id].earliest_service_time
			arrival_time = earliest_time + self.meta_obj.nodes[start_node_id].service_time + self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][start_node_id][end_node_id]
			latest_time = max(arrival_time, self.meta_obj.nodes[end_node_id].earliest_service_time)
			assert(latest_time <= self.meta_obj.nodes[end_node_id].latest_service_time)
			self.start_service_time_line = [earliest_time, latest_time]
			
			# capacity load line
			# load after each node in _route
			self.load_line = [self.meta_obj.nodes[start_node_id].load,
			                  self.meta_obj.nodes[start_node_id].load + self.meta_obj.nodes[end_node_id].load]
			
			# distance accumulated
			end_distance = self.meta_obj.distances[start_node_id][end_node_id]
			self.distances = [0, end_distance]
			
			# time cost of the whole route
			self.whole_time_cost = self.start_service_time_line[len(self.start_service_time_line) - 1] - self.start_service_time_line[0]

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
		return 2 >= len(self.route)
	
	@property
	def whole_distance_cost(self):
		return self.distances[len(self.distances) - 1]

	@classmethod
	def get_path_distance_diff(cls, first_path, second_path):
		return second_path.distances[len(first_path.distances) - 1] - first_path.distances[len(first_path.distances) - 1]
	
	@classmethod
	def get_path_time_cost_diff(cls, first_path, second_path):
		return second_path.whole_time_cost - first_path.whole_time_cost
	
	def try_to_insert_request(self, request_id:int, pick_insert_idx: int, delivery_insert_idx: int) -> (bool, float, float):
		pick_node_id = self.meta_obj.requests[request_id].pick_node_id
		delivery_node_id = self.meta_obj.requests[request_id].delivery_node_id
		
		self.route.insert(pick_insert_idx, pick_node_id)
		self.route.insert(delivery_insert_idx, delivery_node_id)
		
		self.start_service_time_line.insert(pick_insert_idx, 0.0)
		self.start_service_time_line.insert(delivery_insert_idx, 0.0)
		for i in range(pick_insert_idx, len(self.start_service_time_line)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			new_start_time = max(self.start_service_time_line[i - 1] +
							    self.meta_obj.nodes[prev_node_id].service_time +
			                    self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][prev_node_id][current_node_id],
			                    self.meta_obj.nodes[current_node_id].earliest_service_time)
			
			if new_start_time < self.meta_obj.nodes[current_node_id].earliest_service_time or \
			   new_start_time > self.meta_obj.nodes[current_node_id].latest_service_time:
				return False, 0.0, 0.0
			self.start_service_time_line[i] = new_start_time
			
		current_whole_time_cost = self.start_service_time_line[len(self.start_service_time_line) - 1] - self.start_service_time_line[0]
		time_cost_diff = current_whole_time_cost - self.whole_time_cost
		self.whole_time_cost = current_whole_time_cost
			
		self.load_line.insert(pick_insert_idx, 0.0)
		self.load_line.insert(delivery_insert_idx, 0.0)
		for i in range(pick_insert_idx, delivery_insert_idx + 1):
			current_node_id = self.route[i]
			new_load = self.load_line[i - 1] + self.meta_obj.nodes[current_node_id].load
			if new_load > self.meta_obj.vehicles[self.vehicle_id].capacity:
				return False, 0.0, 0.0
			self.load_line[i] = new_load
			
		prev_distance = self.distances[len(self.distances) - 1]
		self.distances.insert(pick_insert_idx, 0.0)
		self.distances.insert(delivery_insert_idx, 0.0)
		for i in range(pick_insert_idx, len(self.distances)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			current_distance = self.distances[i - 1] + \
							   self.meta_obj.distances[prev_node_id][current_node_id]
			self.distances[i] = current_distance
		
		current_distance = self.distances[len(self.distances) - 1]
		distance_diff = current_distance - prev_distance
		
		return True, float(distance_diff), float(time_cost_diff)
		
	def try_to_insert_request_optimal(self, request_id: int) -> (bool, float, float, Path):
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
				
		if 0 == len(new_path_list):
			return False, 0, 0, None
		
		new_path_list.sort(key=lambda item: (self.meta_obj.parameters.alpha * item[0], self.meta_obj.parameters.beta * item[1]))
		return True, new_path_list[0][0], new_path_list[0][1], new_path_list[0][2]
	
	def try_to_remove_request(self, request_id: int) -> (float, float):
		if self.vehicle_id not in self.meta_obj.requests[request_id].vehicle_set:
			assert False
			
		pick_node_id = self.meta_obj.requests[request_id].pick_node_id
		delivery_node_id = self.meta_obj.requests[request_id].delivery_node_id
		
		pick_node_idx = self.route.index(pick_node_id)
		delivery_node_idx = self.route.index(delivery_node_id)
		assert pick_node_idx > 0
		assert delivery_node_idx > 0

		self.route.pop(pick_node_idx)
		self.route.pop(delivery_node_idx)

		prev_whole_time_cost = self.whole_time_cost
		self.start_service_time_line.pop(pick_node_idx)
		self.start_service_time_line.pop(delivery_node_idx - 1)
		for i in range(pick_node_idx, len(self.start_service_time_line)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			new_start_time = max(self.start_service_time_line[i - 1] +
			                     self.meta_obj.nodes[prev_node_id].service_time +
			                     self.meta_obj.vehicle_run_between_nodes_time[self.vehicle_id][prev_node_id][current_node_id],
			                     self.meta_obj.nodes[current_node_id].earliest_service_time)
			
			if new_start_time < self.meta_obj.nodes[current_node_id].earliest_service_time or \
				new_start_time > self.meta_obj.nodes[current_node_id].latest_service_time:
				assert False
		
		self.whole_time_cost = self.start_service_time_line[len(self.start_service_time_line) - 1] - self.start_service_time_line[0]
		time_cost_diff = prev_whole_time_cost - self.whole_time_cost

		self.load_line.pop(pick_node_idx)
		self.load_line.pop(delivery_node_idx)
		for i in range(pick_node_idx, delivery_node_idx - 1):
			current_node_id = self.route[i]
			new_load = self.load_line[i - 1] + self.meta_obj.nodes[current_node_id].load
			if new_load > self.meta_obj.vehicles[self.vehicle_id].capacity:
				assert False
			self.load_line[i] = new_load
		
		prev_distance = self.distances[len(self.distances) - 1]
		self.distances.pop(pick_node_idx)
		self.distances.pop(delivery_node_idx)
		for i in range(pick_node_idx, len(self.distances)):
			prev_node_id = self.route[i - 1]
			current_node_id = self.route[i]
			current_distance = self.distances[i - 1] + \
			                   self.meta_obj.distances[prev_node_id][current_node_id]
			self.distances[i] = current_distance
		
		current_distance = self.distances[len(self.distances) - 1]
		distance_diff = prev_distance - current_distance

		return float(distance_diff), float(time_cost_diff)

	def get_node_start_service_time(self, node_id: int):
		node_idx = self.route.index(node_id)
		return self.start_service_time_line[node_idx]
		