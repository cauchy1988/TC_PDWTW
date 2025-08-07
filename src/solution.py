#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:51
# @Author: Tang Chao
# @File: solution.py
# @Software: PyCharm
from __future__ import annotations

import abc
import copy
import hashlib
from abc import ABC
from typing import Dict
from meta import Meta
from path import Path


class InnerDictForNormalization:
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


def _normalize_dict(nested_dict, epsilon=1e-6):
	all_values = []
	for outer_key, inner_dict in nested_dict.items():
		for inner_key, value in inner_dict.items():
			all_values.append(value)
	
	min_value = min(all_values)
	max_value = max(all_values)
	
	if abs(max_value - min_value) < epsilon:
		normalized_dict = {}
		for outer_key, inner_dict in nested_dict.items():
			normalized_inner_dict = {}
			for inner_key, value in inner_dict.items():
				normalized_inner_dict[inner_key] = 0.0  # 所有值归一化为 0.0
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
	assert paths is not None
	
	gen_list = []
	for key, value in sorted(paths.items(), key=lambda x: x[0]):
		assert paths[key] is not None
		gen_list.append((key, paths[key].route))
	
	return hashlib.sha256(str(gen_list).encode()).hexdigest()


class Solution(ABC):
	@abc.abstractmethod
	def __init__(self, meta_obj: Meta):
		pass


class PDWTWSolution(Solution):
	def __init__(self, meta_obj: Meta):
		self._metaObj = meta_obj
		# vehicle_id -> Path
		self._paths: Dict[int, Path] = {}
		self._requestBank = set([request_id for request_id in meta_obj.requests])
		self._requestIdToVehicleId: Dict[int, int] = {}
		
		# only preserve pickup and delivery node id map
		self._nodeIdToVehicleId: Dict[int, int] = {}
		
		self._vehicleBank = set([vehicle_id for vehicle_id in meta_obj.vehicles])
		
		self._distanceCost = 0.0
		self._timeCost = 0.0
		
		self._fingerPrint = generate_solution_finger_print(self._paths)
		
	def delete_vehicle_and_its_route(self, delete_vehicle_id: int):
		assert delete_vehicle_id in self.paths or delete_vehicle_id in self.vehicle_bank
		deleted_requests = set([request_id for request_id, vehicle_id in self.request_id_to_vehicle_id if delete_vehicle_id == vehicle_id])
		self.remove_requests(deleted_requests)
		self.vehicle_bank.remove(delete_vehicle_id)
	
	def copy(self):
		new_obj = PDWTWSolution(self.meta_obj)
		for vehicle_id, the_path in self.paths.items():
			new_obj.paths[vehicle_id] = the_path.copy()
		new_obj._requestBank = self.request_bank.copy()
		new_obj._requestIdToVehicleId = self.request_id_to_vehicle_id.copy()
		new_obj._nodeIdToVehicleId = self.node_id_to_vehicle_id.copy()
		new_obj._vehicleBank = self.vehicle_bank.copy()
		
		new_obj._distanceCost = self._distanceCost
		new_obj._timeCost = self._timeCost
		
		new_obj._fingerPrint = self._fingerPrint
		
		return new_obj
	
	def cost_if_remove_request(self, request_id: int):
		assert request_id in self.request_id_to_vehicle_id
		
		origin_path = self.paths[self.request_id_to_vehicle_id[request_id]].copy()
		assert origin_path is not None
		copied_path = origin_path.copy()
		
		distance_diff, time_diff = copied_path.try_to_remove_request(request_id)
		
		return self.meta_obj.parameters.alpha * distance_diff + self.meta_obj.parameters.beta * time_diff
	
	def cost_if_insert_request_to_vehicle_path(self, request_id: int, vehicle_id: int) -> (bool, float):
		assert request_id in self.request_bank and (vehicle_id in self.vehicle_bank or vehicle_id in self.paths)
		
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
		for request_id in request_id_set:
			assert request_id in self.request_id_to_vehicle_id
			vehicle_id = self.request_id_to_vehicle_id[request_id]
			assert vehicle_id in self.paths
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
			self._fingerPrint = generate_solution_finger_print(self._paths)
	
	def insert_one_request_optimal(self, request_id: int, vehicle_id: int) -> bool:
		assert request_id in self.request_bank
		
		if request_id not in self.meta_obj.requests[request_id].vehicle_set:
			return False
		
		if vehicle_id in self.vehicle_bank:
			the_path = Path(vehicle_id, self.meta_obj)
		else:
			assert vehicle_id in self.paths
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
			self._fingerPrint = generate_solution_finger_print(self._paths)
		return ok
	
	def get_node_start_service_time_in_path(self, node_id: int):
		assert node_id in self.node_id_to_vehicle_id
		vehicle_id = self.node_id_to_vehicle_id[node_id]
		
		assert vehicle_id in self.paths
		path_obj = self.paths[vehicle_id]
		return path_obj.get_node_start_service_time(node_id)
	
	def _update_objective_cost_all(self):
		self._distanceCost = 0.0
		self._timeCost = 0.0
		for vehicle_id in self.paths:
			self._distanceCost += self.paths[vehicle_id].whole_distance_cost
			self._timeCost += self.paths[vehicle_id].whole_time_cost
	
	@property
	def meta_obj(self):
		return self._metaObj
	
	@property
	def paths(self):
		return self._paths
	
	@property
	def request_bank(self):
		return self._requestBank
	
	@property
	def request_id_to_vehicle_id(self):
		return self._requestIdToVehicleId
	
	@property
	def node_id_to_vehicle_id(self):
		return self._nodeIdToVehicleId
	
	@property
	def vehicle_bank(self):
		return self._vehicleBank
	
	@property
	def distance_cost(self):
		return self._distanceCost
	
	@property
	def time_cost(self):
		return self._timeCost
	
	@property
	def finger_print(self):
		return self._fingerPrint
	
	@property
	def objective_cost(self):
		return self.meta_obj.parameters.alpha * self._distanceCost + self.meta_obj.parameters.beta * self._timeCost + self.meta_obj.parameters.gama * len(
			self.request_bank)
	
	@property
	def objective_cost_without_request_bank(self):
		return self.meta_obj.parameters.alpha * self.distance_cost + self.meta_obj.parameters.beta * self.time_cost
