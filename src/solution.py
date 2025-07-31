#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:51
# @Author: Tang Chao
# @File: solution.py
# @Software: PyCharm
import abc
import hashlib
from abc import ABC
from typing import Dict
from meta import Meta
from path import Path

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
		self._nodeIdToVehicleId: Dict[int, int] = {}
		
		self._vehicleBank = set([vehicle_id for vehicle_id in meta_obj.vehicles])
		
		self._distanceCost = 0.0
		self._timeCost = 0.0

		self._fingerPrint = generate_solution_finger_print(self._paths)

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
		
		return self.meta_obj.alpha * distance_diff + self.meta_obj.beta * time_diff
	
	def cost_if_insert_request_to_vehicle_path(self, request_id: int, vehicle_id: int) -> (bool, float):
		assert request_id in self.request_bank and (vehicle_id in self.vehicle_bank or vehicle_id in self.paths)
		
		if vehicle_id in self.paths:
			the_path = self.paths[vehicle_id].copy()
		else:
			the_path = Path(vehicle_id, self.meta_obj)
			
		ok, distance_diff, time_diff = the_path.try_to_insert_request_optimal(request_id)
		
		if not ok:
			return False, 0.0
		
		return True, self.meta_obj.alpha * distance_diff + self.meta_obj.beta * time_diff
	
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
		return self.meta_obj.alpha * self._distanceCost + self.meta_obj.beta * self._timeCost +  self.meta_obj.gama * len(self.request_bank)
	
	@property
	def objective_cost_without_request_bank(self):
		return self.meta_obj.alpha * self.distance_cost + self.meta_obj.beta * self.time_cost
	