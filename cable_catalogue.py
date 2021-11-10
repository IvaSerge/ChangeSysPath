# ================ Python imports
import math


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
cab_lst.append(["3x(1x150)", 105, 3.396])
cab_lst.append(["3x(1x240)", 117, 4.434])
cab_lst.append(["2x3(1x150)", 210, 6.792])
cab_lst.append(["3-#120, 1-#70", 44, 4.78])
cab_lst.append(["2 runs of 3-#120, 1-#70", 62.23, 9.56])
cab_lst.append(["3 runs of 3-#120, 1-#70", 76.21, 14.34])
cab_lst.append(["4 runs of 3-#120, 1-#70", 88, 19.12])
cab_lst.append(["3-#120, 1-#120 mm, 1-#70", 50, 6.74])
cab_lst.append(["2 runs of 3-#120, 1-#120 mm, 1-#70", 70.71, 13])
cab_lst.append(["3 runs of 3-#120, 1-#120 mm, 1-#70", 86.6, 20.22])
cab_lst.append(["4 runs of 3-#120, 1-#120 mm, 1-#70", 100, 26.96])
cab_lst.append(["5 runs of 3-#120, 1-#120 mm, 1-#70", 111.8, 33.7])
cab_lst.append(["6 runs of 3-#120, 1-#120 mm, 1-#70", 122.47, 40.44])
cab_lst.append(["3-#150, 1-#70", 48.5, 5.87])
cab_lst.append(["2 runs of 3-#150, 1-#70", 68.6, 11.74])
cab_lst.append(["5 runs of 3-#150, 1-#70", 108.5, 29.35])
cab_lst.append(["6 runs of 3-#150, 1-#70", 118.8, 35.22])
cab_lst.append(["3-#150, 1-#150 mm, 1-#70", 56, 7.99])
cab_lst.append(["2 runs of 3-#150, 1-#150 mm, 1-#70", 79.2, 15.98])
cab_lst.append(["4 runs of 3-#150, 1-#150 mm, 1-#70", 97, 31.96])
cab_lst.append(["5 runs of 3-#150, 1-#150 mm, 1-#70", 125.2, 39.95])
cab_lst.append(["6 runs of 3-#150, 1-#150 mm, 1-#70", 137.2, 47.94])
cab_lst.append(["7 runs of 3-#150, 1-#150 mm, 1-#70", 148.2, 55.93])
cab_lst.append(["8 runs of 3-#150, 1-#150 mm, 1-#70", 158.4, 63.92])


def get_cable(section):
	"""
	get cable by type and cross-section

	args:
		section (str): cross-section of cable`
	"""
	global cab_lst
	cable = [x for x in cab_lst if section in x[0]][0]
	try:
		return cable
	except:
		raise ValueError(
			"Cable not in catalogue \n %s" % section)
