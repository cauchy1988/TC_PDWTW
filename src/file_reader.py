#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/19 13:18
# @Author: Tang Chao
# @File: file_reader.py
# @Software: PyCharm

import abc
from abc import ABC

from meta import Meta


class FileReader(ABC):
	def __init__(self):
		pass
	
	@abc.abstractmethod
	def read_from_directory(self, directory_path: str, meta_obj: Meta):
		"""
		从一个目录的一系列文件中读取具体模型数据
		"""
