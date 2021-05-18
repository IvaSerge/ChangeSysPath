# ================ Python imports
import math


class Cable():
	cable_list = list()

	def __init__(self):
		"""
		Cable parameters
		"""
		self.type = str()
		self.section = str()
		self.diameter = float()
		self.weight = float()
		self.resistance = float()
		self.reactance = float()
		Cable.cable_list.append(self)

	def set_parameters(self, param_list):
		self.type = param_list[0]
		self.section = param_list[1]
		self.diameter = param_list[2]
		self.weight = param_list[3]
		self.resistance = param_list[4]
		inductance = param_list[5]
		omega = 2 * math.pi * 50
		self.reactance = omega * inductance

	@classmethod
	def create_catalogue(cls):
		total_list = list()
		add_to_list = lambda x: total_list.append(x)

		# type | cross-section | D mm | Weight kg/km | R Om/km | L mH/km
		nym = list()
		nym.append(["NYM", "3x1.5", 8.4, 120, 14.5, 0])
		nym.append(["NYM", "3x2.5", 9.6, 170, 8.87, 0])
		nym.append(["NYM", "3x4", 11.3, 250, 5.52, 0])
		nym.append(["NYM", "5x1.5", 9.9, 175, 14.5, 0])
		nym.append(["NYM", "5x2.5", 11.5, 250, 8.87, 0])
		nym.append(["NYM", "5x4", 13.8, 370, 5.52, 0])
		nym.append(["NYM", "5x6", 15.0, 500, 3.69, 0])
		nym.append(["NYM", "5x10", 19.0, 810, 2.19, 0])
		nym.append(["NYM", "5x16", 22.7, 1200, 1.38, 0])
		nym.append(["NYM", "5x25", 27.7, 1800, 0.87, 0])
		map(add_to_list, nym)

		nycwy = list()
		nycwy.append(["NYCWY", "4x25/16", 29, 1800, 0.727, 0.28])
		nycwy.append(["NYCWY", "4x35/16", 30, 2100, 0.524, 0.271])
		nycwy.append(["NYCWY", "4x50/25", 34, 2800, 0.387, 0.271])
		nycwy.append(["NYCWY", "4x70/35", 37, 3800, 0.268, 0.262])
		nycwy.append(["NYCWY", "4x95/50", 43, 5100, 0.193, 0.262])
		nycwy.append(["NYCWY", "4x120/70", 47, 6450, 0.153, 0.256])
		map(add_to_list, nycwy)

		nhxh_e30 = list()
		nhxh_e30.append(["(N)HXH E30", "3x1.5", 11, 160, 12.1, 0])
		nhxh_e30.append(["(N)HXH E30", "3x2.5", 12, 200, 7.4, 0])
		nhxh_e30.append(["(N)HXH E30", "3x4", 13, 270, 4.61, 0])
		nhxh_e30.append(["(N)HXH E30", "3x6", 14, 375, 3.08, 0])
		nhxh_e30.append(["(N)HXH E30", "5x1.5", 13, 225, 12.1, 0])
		nhxh_e30.append(["(N)HXH E30", "5x2.5", 14, 295, 7.4, 0])
		nhxh_e30.append(["(N)HXH E30", "5x4", 15, 390, 4.61, 0])
		nhxh_e30.append(["(N)HXH E30", "5x6", 17, 530, 3.08, 0])
		map(add_to_list, nhxh_e30)

		for cable_info in total_list:
			cab_obj = Cable()
			cab_obj.set_parameters(cable_info)

	@classmethod
	def get_cable(cls, cab_type, section):
		"""
		get cable by type and cross-section

		args:
			cab_type (str): cable type
			section (str): cross-section of cable
		"""
		cables = cls.cable_list
		type_list = [x for x in cables if x.type == cab_type]
		if not type_list:
			return None
		cable = [x for x in type_list if x.section == section]
		if not cable:
			return None
		return cable[0]
