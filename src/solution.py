#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:51
# @Author  : Tang Chao
# @File    : solution.py
# @Software: PyCharm
import abc
import meta


class Solution:
	@abc.abstractmethod
	def __init__(self, meta_obj: meta):
		pass
	
	
class PDWTWSolution(Solution):
	def __init__(self, meta_obj: meta):
		self._metaObj = meta_obj
		# vehicle_id -> path
		self._paths = {}
		self._requestBank = set([request_id for request_id, _ in meta_obj.requests])
		self._requestIdToPath = {}
		
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
	def request_id_to_path(self):
		return self._requestIdToPath
	
	