#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/14 12:24
# @Author  : Tang Chao
# @File    : benchmark_reader.py.py
# @Software: PyCharm
from abc import ABC, abstractmethod
from meta import Meta

class BenchmarkReader(ABC):
	def __init__(self):
		pass
	
	@abstractmethod
	def get_meta_obj(self) -> Meta:
		pass
