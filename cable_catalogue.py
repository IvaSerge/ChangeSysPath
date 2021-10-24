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
		# self.type = param_list[0]
		self.section = param_list[0]
		self.diameter = param_list[1]
		self.weight = param_list[2]
		# self.resistance = param_list[4]
		# inductance = param_list[5]
		# omega = 2 * math.pi * 50
		# self.reactance = omega * inductance

	@classmethod
	def create_catalogue(cls):
		cab_lst = list()

		# cross-section | D mm | Weight kg/km | R Om/km | L mH/km
		cab_lst.append(["1-#1.5, 1-#1.5, 1-#1.5", 8.3, 0.12])
		cab_lst.append(["1-#1.5, 1-#1.5 mm, 1-#1.5", 8.3, 0.12])
		cab_lst.append(["1-#2.5, 1-#2.5 mm, 1-#2.5", 9.5, 0.169])
		cab_lst.append(["1-#4, 1-#4 mm, 1-#4", 11, 0.238])
		cab_lst.append(["1-#6, 1-#6 mm, 1-#6", 12.2, 0.315])
		cab_lst.append(["1-#10, 1-#10 mm, 1-#10", 14.8, 0.489])
		cab_lst.append(["1-#16, 1-#16 mm, 1-#16", 17.6, 0.73])
		cab_lst.append(["3-#1.5, 1-#1.5, 1-#1.5", 9.9, 175])
		cab_lst.append(["3-#2.5, 1-#2.5", 10.3, 0.203])
		cab_lst.append(["3-#2.5, 1-#2.5 mm, 1-#2.5", 11.1, 0.244])
		cab_lst.append(["3-#4, 1-#4", 12.3, 0.3])
		cab_lst.append(["3-#4, 1-#4 mm, 1-#4", 13.3, 0.362])
		cab_lst.append(["3-#6, 1-#6", 13.5, 0.393])
		cab_lst.append(["3-#6, 1-#6 mm, 1-#6", 14.6, 0.478])
		cab_lst.append(["3-#10, 1-#10", 16.2, 0.604])
		cab_lst.append(["3-#10, 1-#10 mm, 1-#10", 17.9, 0.751])
		cab_lst.append(["3-#16, 1-#16", 19.3, 0.907])
		cab_lst.append(["3-#16, 1-#16 mm, 1-#16", 21.6, 1.138])
		cab_lst.append(["3-#25, 1-#16", 25.3, 1.294])
		cab_lst.append(["3-#25, 1-#25 mm, 1-#16", 28, 1.71])
		cab_lst.append(["3-#35, 1-#16", 28.3, 1.685])
		cab_lst.append(["3-#35, 1-#35 mm, 1-#16", 31.5, 1.99])
		cab_lst.append(["3-#50, 1-#25", 32, 2.12])
		cab_lst.append(["3-#50, 1-#50 mm, 1-#25", 36.1, 2.69])
		cab_lst.append(["3-#70, 1-#35", 36, 2.94])
		cab_lst.append(["3-#70, 1-#70 mm, 1-#35", 40.6, 3.65])
		cab_lst.append(["3-#95, 1-#50", 40.5, 3.87])
		cab_lst.append(["3-#95, 1-#95 mm, 1-#50", 46, 5.01])
		cab_lst.append(["3-#120, 1-#70", 44, 4.78])
		cab_lst.append(["3-#120, 1-#120 mm, 1-#70", 50, 6.74])
		cab_lst.append(["3-#150, 1-#70", 48.5, 5.87])
		cab_lst.append(["3-#150, 1-#150 mm, 1-#70", 56, 7.99])
		cab_lst.append(["2 runs of 3-#120, 1-#70", 95, 13.48])
		cab_lst.append(["2 runs of 3-#120, 1-#120 mm, 1-#70", 100, 13])
		cab_lst.append(["2 runs of 3-#150, 1-#70", 105, 15.08])
		cab_lst.append(["2 runs of 3-#150, 1-#150 mm, 1-#70", 112, 15.98])
		cab_lst.append(["3 runs of 3-#120, 1-#70", 145, 19])
		cab_lst.append(["3 runs of 3-#120, 1-#120 mm, 1-#70", 150, 20.22])
		cab_lst.append(["4 runs of 3-#120, 1-#120 mm, 1-#70", 200, 26.96])
		cab_lst.append(["4 runs of 3-#120, 1-#70", 176, 19.12])
		cab_lst.append(["4 runs of 3-#150, 1-#150 mm, 1-#70", 224, 31.96])
		cab_lst.append(["5 runs of 3-#120, 1-#120 mm, 1-#70", 250, 26.96])
		cab_lst.append(["5 runs of 3-#150, 1-#150 mm, 1-#70", 280, 39.95])
		cab_lst.append(["5 runs of 3-#150, 1-#70", 242, 38.175])
		cab_lst.append(["6 runs of 3-#120, 1-#120 mm, 1-#70", 300, 40.44])
		cab_lst.append(["6 runs of 3-#150, 1-#150 mm, 1-#70", 336, 47.94])
		cab_lst.append(["6 runs of 3-#150, 1-#70", 291, 35.22])
		cab_lst.append(["7 runs of 3-#150, 1-#150 mm, 1-#70", 392, 55.93])
		cab_lst.append(["8 runs of 3-#150, 1-#150 mm, 1-#70", 448, 63.92])
		cab_lst.append(["3x(1x150), MV", 105, 3.396])
		cab_lst.append(["3x(1x240), MV", 117, 4.434])
		cab_lst.append(["2x3(1x150), MV", 210, 6.792])

		for cable_info in cab_lst:
			cab_obj = Cable()
			cab_obj.set_parameters(cable_info)

	@classmethod
	def get_cable(cls, section):
		"""
		get cable by type and cross-section

		args:
			cab_type (str): cable type
			section (str): cross-section of cable`
		"""
		cables = cls.cable_list
		cable = [x for x in cables if x.section == section]
		try:
			return cable[0]
		except:
			raise ValueError(
				"Cable not in catalogue \n %s" % section)
