#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:51
# @Author  : Tang Chao
# @File    : solution.py
# @Software: PyCharm
import abc
from typing import Dict
from meta import Meta
from path import Path


class Solution:
	@abc.abstractmethod
	def __init__(self, meta_obj: Meta):
		pass
	
	
class PDWTWSolution(Solution):
	def __init__(self, meta_obj: Meta):
		self._metaObj = meta_obj
		# vehicle_id -> Path
		self._paths: Dict[int, Path] = {}
		self._requestBank = set([request_id for request_id, _ in meta_obj.requests])
		self._requestIdToVehicleId: Dict[int, int] = {}
		self._nodeIdToVehicleId: Dict[int, int] = {}
		
		self._vehicleBank = set([vehicle_id for vehicle_id, _ in meta_obj.vehicles])
		
	def cost_if_remove_request(self, request_id: int):
		assert request_id in self.request_id_to_vehicle_id
		
		origin_path = self.paths[self.request_id_to_vehicle_id[request_id]].copy()
		assert origin_path is not None
		copied_path = origin_path.copy()
		
		distance_diff, time_diff = copied_path.try_to_remove_request(request_id)
		
		return self.meta_obj.alpha * distance_diff + self.meta_obj.beta * time_diff
	
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
				
	def get_node_start_service_time_in_path(self, node_id: int):
		assert node_id in self.node_id_to_vehicle_id
		vehicle_id = self.node_id_to_vehicle_id[node_id]
		
		assert vehicle_id in self.paths
		path_obj = self.paths[vehicle_id]
		return path_obj.get_node_start_service_time(node_id)
	
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
	
	
	