class Cable():
	def __init__(self, start, end):
		"""
		Cable parameters
		"""
		self.type = str()
		self.section = str()
		self.diameter = double()
		self.weight = double()
		self.r = double()
		serf.x = double()


# cores | cross-section | D mm | Weight kg/km | R Om/km | L mH/km
# X[Om] = 2 * pi * f * L[H]
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

nycwy = list()
nycwy.append(["NYCWY", "4x25/16", 29, 1800, 0.727, 0.28])
nycwy.append(["NYCWY", "4x35/16", 30, 2100, 0.524, 0.271])
nycwy.append(["NYCWY", "4x50/25", 34, 2800, 0.387, 0.271])
nycwy.append(["NYCWY", "4x70/35", 37, 3800, 0.268, 0.262])
nycwy.append(["NYCWY", "4x95/50", 43, 5100, 0.193, 0.262])
nycwy.append(["NYCWY", "4x120/70", 47, 6450, 0.153, 0.256])

nhxh_e30 = list()
nhxh_e30.append(["(N)HXH E30", "3x1.5", 11, 160, 12.1, 0])
nhxh_e30.append(["(N)HXH E30", "3x2.5", 12, 200, 7.4, 0])
nhxh_e30.append(["(N)HXH E30", "3x4", 13, 270, 4.61, 0])
nhxh_e30.append(["(N)HXH E30", "3x6", 14, 375, 3.08, 0])
nhxh_e30.append(["(N)HXH E30", "5x1.5", 13, 225, 12.1, 0])
nhxh_e30.append(["(N)HXH E30", "5x2.5", 14, 295, 7.4, 0])
nhxh_e30.append(["(N)HXH E30", "5x4", 15, 390, 4.61, 0])
nhxh_e30.append(["(N)HXH E30", "5x6", 17, 530, 3.08, 0])
