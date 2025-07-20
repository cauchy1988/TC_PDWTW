#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/20 00:05
# @Author  : Tang Chao
# @File    : path.py
# @Software: PyCharm
import meta


class Path:
	def __init__(self, vehicle_id: int, meta_obj: meta, need_init = True):
		self._metaObj = meta_obj
		self._vehicleId = vehicle_id
		
		if need_init:
			# node id route
			start_node_id = self._metaObj.vehicles[self._vehicleId].start_node_id
			end_node_id = self._metaObj.vehicles[self._vehicleId].end_node_id
			self._route = [start_node_id, end_node_id]
			
			# start the service time alone the node route
			earliest_time = self._metaObj.nodes[start_node_id].earliest_service_time
			arrival_time = earliest_time + self._metaObj.nodes[start_node_id].service_time + self._metaObj.vehicle_run_between_nodes_time[self._vehicleId][start_node_id][end_node_id]
			latest_time = max(arrival_time, self._metaObj.nodes[end_node_id].earliest_service_time)
			assert(latest_time <= self._metaObj.nodes[end_node_id].latest_service_time)
			self._startServiceTimeLine = [earliest_time, latest_time]
			
			# capacity load line
			# load after each node in _route
			self._loadLine = [self._metaObj.nodes[start_node_id].load,
							  self._metaObj.nodes[start_node_id].load + self._metaObj.nodes[end_node_id].load]
			
			# distance accumulated
			end_distance = self._metaObj.distances[start_node_id][end_node_id]
			self._distances = [0, end_distance]
			
			# time cost of the whole route
			self._wholeTimeCost = self._startServiceTimeLine[len(self._startServiceTimeLine) - 1] - self._startServiceTimeLine[0]

	def copy(self):
		new_path = Path(self._vehicleId, self._metaObj, False)
		new_path._metaObj = self._metaObj
		new_path._vehicleId = self._vehicleId
		new_path.route = [item for item in self._route]
		new_path._startServiceTimeLine = [item for item in self._startServiceTimeLine]
		new_path._loadLine = [item for item in self._loadLine]
		
		return new_path
	
	def try_to_insert_request_optimal(self, request_id: int):
		pass
	