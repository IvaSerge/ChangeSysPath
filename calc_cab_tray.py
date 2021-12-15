"""Cable tray fuctions."""

__author__ = "IvaSerge"
__email__ = "ivaserge@ukr.net"
__status__ = "Development"

# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory
from Autodesk.Revit.DB.Category import GetCategory  # type: ignore

# ================ Python imports
import collections
from collections import defaultdict

# ================ local imports
import vector
from vector import *
import cab_tray
from cab_tray import *
import cable_catalogue
from cable_catalogue import *
import tray_catalogue
from tray_catalogue import *


def setup_param_value(elem, name, pValue):
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(get_bip(name)).Set(pValue)
		except:
			pass

	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def category_by_bic_name(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return Category.GetCategory(doc, bic)


def get_tray_sys_link(list_of_systems):
	"""
		Find relation cable tray - electrical system.

		Search how much systems run through this cable tray
		OUT - tray, str(system1, system2...)
	"""
	outlist = list()
	all_used_trays = list()
	for sys in list_of_systems:
		used_trays_fittings = sys.run_along_trays
		# filter out fitting elements. We need cable trays only
		fit_category = category_by_bic_name("OST_CableTrayFitting")
		used_trays = [x for x in used_trays_fittings if x.Category.Id != fit_category.Id]
		add_tray = lambda x: all_used_trays.append(x)
		map(add_tray, used_trays)
	for tray in all_used_trays:
		sys_dependend = list()
		tray_id = tray.Id
		for sys in list_of_systems:
			ids_in_sys = [x.Id for x in sys.run_along_trays]
			if tray_id in ids_in_sys:
				sys_dependend.append(sys.rvt_sys)
		outlist.append([tray, sys_dependend])
	return outlist


def calc_tray_filling(link):
	"""Calculate cable tray filling in % """
	tray = link[0]
	el_systems = link[1]
	tray_size = get_tray_size(tray)
	tray_cross_section = tray_size[0] * tray_size[1]
	# get cable size for system
	cab_cross_section_list = [get_wire_crossection(x) for x in el_systems]
	cab_cross_section_list = [x for x in cab_cross_section_list if x]
	if cab_cross_section_list:
		total_cs = sum(cab_cross_section_list)
		# sum results
		fill_percent = int(round(total_cs / tray_cross_section * 100))
		return tray, str(fill_percent)
	else:
		return None


def calc_tray_weight(link):
	"""Calculate cable tray weight in kg/m """
	tray = link[0]
	el_systems = link[1]
	# try:
	weight_tray = Tray.get_tray_weight(tray)
	# except:
	# 	raise ValueError(
	# 		"Tray %d not in catalogue.\n Check type and size.\n Width: %d, Height: %d"
	# 		% (
	# 			tray.Id.IntegerValue,
	# 			tray_catalogue.ft_to_mm(tray.Width),
	# 			tray_catalogue.ft_to_mm(tray.Height)))

	weight_cables = weight_tray
	for sys in el_systems:
		wire_size = sys.WireSizeString
		# try to get wire size from other parameters. Project specific
		if not(wire_size):
			param_list = sys.GetParameters("Cable Description_1")
			wire_size = [i for i in param_list if i.Id == ElementId(8961915)][0]
			wire_size = wire_size.AsString()

		cab_weight = get_cable(wire_size)[2]
		weight_cables += cab_weight
	return tray, str(int(round(weight_cables)))


def get_wire_crossection(sys):
	"""Get cable cross-section of the system"""
	# read system parameter
	# wire_type = sys.wire_type
	wire_size = sys.WireSizeString
	if not(wire_size):
		param_list = sys.GetParameters("Cable Description_1")
		wire_size = [i for i in param_list if i.Id == ElementId(8961915)][0]
		wire_size = wire_size.AsString()

	# get info from catalogue
	try:
		cab_diameter = get_cable(wire_size)[1]
	except:
		raise ValueError(
			"Cable not in catalogue \n %d" % sys.Id.IntegerValue)

	return cab_diameter * cab_diameter


def get_tray_size(tray):
	"""
	Get size of cable tray or fitting

	args:
		tray (FamilyInstance): tray or fitting
	return:
		width, height
	"""
	t_width_list = list()
	t_height_list = list()
	category_elem = tray.Category.Id
	category_tray = cab_tray.category_by_bic_name("OST_CableTray").Id
	category_fitting = cab_tray.category_by_bic_name("OST_CableTrayFitting").Id

	# for cable tray
	if category_elem == category_tray:
		elem_con_manager = tray.ConnectorManager
	# for cable tray fitting
	if category_elem == category_fitting:
		elem_mep_model = tray.MEPModel
		elem_con_manager = elem_mep_model.ConnectorManager

	elem_cons = elem_con_manager.Connectors
	for con in elem_cons:
		t_width_list.append(con.Width)
		t_height_list.append(con.Height)
	t_width = vector.ft_to_mm(min(t_width_list))
	t_height = vector.ft_to_mm(min(t_height_list))
	return t_width, t_height


def set_tray_size(info_list):
	tray = info_list[0]
	tray_fill = str(info_list[1])
	p_name = "MC Object Variable 1"
	setup_param_value(tray, p_name, tray_fill)


def set_tray_weight(info_list):
	tray = info_list[0]
	tray_weight = str(info_list[1])
	p_name = "MC Object Variable 2"
	setup_param_value(tray, p_name, tray_weight)


def set_tag(info_list):
	tray = info_list[0]
	from_to = info_list[1]
	wire_size = info_list[2]
	setup_param_value(tray, "Multi_Tag_1", wire_size)
	setup_param_value(tray, "Multi_Tag_2", from_to)


def clean_tray_parameters(tray_list):
	"""
		Put \\s symbol to pre-defined parameters
	"""

	map(lambda x: setup_param_value(x, "MC Object Variable 1", ""), tray_list)
	map(lambda x: setup_param_value(x, "MC Object Variable 2", ""), tray_list)
	map(lambda x: setup_param_value(x, "Multi_Tag_1", ""), tray_list)
	map(lambda x: setup_param_value(x, "Multi_Tag_2", ""), tray_list)


def get_tags(link):
	tray = link[0]
	el_systems = link[1]
	# get ElSys info
	from_to = [x.PanelName +
		"->" + x.LoadName
		for x in el_systems]

	get_wire = lambda sys: [
		i for i in sys.GetParameters("Cable Description_1")
		if i.Id == ElementId(8961915)][0].AsString()

	cable_sise = [
		x.WireSizeString if x.WireSizeString
		else get_wire(x)
		for x in el_systems]
	from_to_string = '\r\n'.join(from_to)
	size_string = '\r\n'.join(cable_sise)
	return tray, from_to_string, size_string


global doc  # type: ignore
