# ================ system imports
import clr

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import re


def ft_to_mm(ft):
	mm = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits(
		ft, Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS)
	return mm


class Tray():
	tray_list = list()

	# type | W mm | H mm | Weight kg/m |
	tray_list.append(["WSL", 100, 110, 2.65])
	tray_list.append(["WSL", 200, 110, 6.05])
	tray_list.append(["WSL", 200, 150, 12.85])
	tray_list.append(["WSL", 300, 100, 12.1])
	tray_list.append(["WSL", 300, 110, 6.19])
	tray_list.append(["WSL", 300, 150, 12.99])
	tray_list.append(["WSL", 400, 110, 6.68])
	tray_list.append(["WSL", 400, 150, 13.48])
	tray_list.append(["WSL", 500, 110, 6.96])
	tray_list.append(["WSL", 500, 150, 13.76])
	tray_list.append(["WSL", 600, 110, 7.21])
	tray_list.append(["WSL", 600, 150, 14.01])

	tray_list.append(["WSC", 200, 110, 7.56])
	tray_list.append(["WSC", 300, 110, 8.56])
	tray_list.append(["WSC", 400, 110, 9.36])
	tray_list.append(["WSC", 500, 110, 10.26])
	tray_list.append(["WSC", 600, 110, 11.16])
	tray_list.append(["WSC", 200, 150, 13.32])
	tray_list.append(["WSC", 300, 150, 14.22])
	tray_list.append(["WSC", 400, 150, 15.12])
	tray_list.append(["WSC", 500, 150, 16.02])
	tray_list.append(["WSC", 600, 150, 16.92])

	tray_list.append(["CTM", 50, 60, 0.98])
	tray_list.append(["CTM", 100, 60, 1.17])
	tray_list.append(["CTM", 150, 60, 1.43])
	tray_list.append(["CTM", 200, 60, 1.63])
	tray_list.append(["CTM", 300, 60, 2.23])
	tray_list.append(["CTM", 400, 60, 2.6])
	tray_list.append(["CTM", 500, 60, 3.1])
	tray_list.append(["CTM", 600, 60, 3.58])
	tray_list.append(["CTH", 300, 85, 4.17])

	@staticmethod
	def get_tray_weight(tray):
		"""Calculate cable tray weight in kg/m """

		# filter out short name
		regexp = re.compile(r"(\w+)")
		short_type = regexp.match(tray.Name).group(1)

		# filter by type, width, height
		filter_by_type = [x for x in Tray.tray_list if x[0] == short_type]
		filter_by_width = [x for x in filter_by_type if x[1] == round(ft_to_mm(tray.Width))]
		filter_by_height = [x for x in filter_by_width if x[2] == round(ft_to_mm(tray.Height))]

		try:
			weight_tray = filter_by_height[0][3]
			return weight_tray
		except:
			raise ValueError(
				"Tray not found \n check tray \"%s, %d, %d \""
				% (tray.Name, ft_to_mm(tray.Width), ft_to_mm(tray.Height)))
