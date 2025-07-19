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
		self.metaObj = meta_obj
		# vehicle_id -> path
		self.paths = {}
		self.request_bank = set([request_id for request_id, _ in meta_obj.requests])
