#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:51
# @Author  : Tang Chao
# @File    : solution.py
# @Software: PyCharm
import abc
from meta import Meta


class Solution:
	@abc.abstractmethod
	def __init__(self, meta_obj: Meta):
		pass
	
	
class PDWTWSolution(Solution):
	def __init__(self, meta_obj: Meta):
		self._metaObj = meta_obj
		# vehicle_id -> Path
		self._paths = {}
		self._requestBank = set([request_id for request_id, _ in meta_obj.requests])
		self._requestIdToVehicleId = {}
		
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
	
	