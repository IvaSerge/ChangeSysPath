"""Cable tray fuctions."""

__author__ = "IvaSerge"
__email__ = "ivaserge@ukr.net"
__status__ = "Development"

# ================ system imports
import sys
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
import re
from re import *

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
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, elem.Id)
	if elem_status == CheckoutStatus.OwnedByOtherUser:
		return None

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


def write_tray_sys_link(file_database, el_system):
	"""	Writes link info to data base file
	"""

	# get all connected cable trays for system
	if el_system.run_along_trays:
		tray_ids = set([i.Id.ToString() for i in el_system.run_along_trays if i.Category.Id.ToString() == "-2008130"])
	else:
		return None

	# open file for read/wirte.
	# db structure: TrayId, el_sys.Id[]
	with open(file_database, "r+") as f_db:
		data = f_db.read()
		for tray_id in tray_ids:
			# Search for TrayId
			check_list = re.findall(tray_id, data, flags=DOTALL)
			if check_list:
				# if ID found - add circuit ID to the row
				old_str = check_list[0]
				# dublicates now allowed
				if el_system.rvt_sys.Id.ToString() not in old_str:
					new_str = old_str + "," + el_system.rvt_sys.Id.ToString()
					data = data.replace(old_str, new_str)
			else:
				# if Id not - add new row: TrayId, el_sys.Id
				data = data + "\n" + tray_id + "," + el_system.rvt_sys.Id.ToString()
				f_db.seek(0)
				f_db.write(data)
				f_db.truncate()
		f_db.seek(0)
		f_db.write(data)
		f_db.truncate()

	return tray_ids


def get_tray_sys_link(doc, link_str):
	"""
		Find relation cable tray - electrical system.

		Search how much systems run through this cable tray
		OUT - tray, str(system1, system2...)
	"""

	if "," not in link_str:
		return None

	link_ids = link_str.split(",")
	tray = doc.GetElement(ElementId(int(link_ids.pop(0))))
	systems = [doc.GetElement(ElementId(int(i))) for i in link_ids]

	return tray, systems


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
	for el_sys in el_systems:
		# Only for Power circuits
		if el_sys.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit:
			wire_size = el_sys.WireSizeString
			# try to get wire size from other parameters. Project specific
			if not(wire_size):
				param_list = el_sys.GetParameters("Cable Description_1")
				wire_size = [i for i in param_list if i.Id == ElementId(8961915)][0]
				wire_size = wire_size.AsString()

		else:
			# cables for DATA and
			wire_size = el_sys.LookupParameter("Cable Type").AsString()

		# try to get wire type
		try:
			cab_weight = get_cable(wire_size)[2]
			weight_cables += cab_weight
		except:
			# raise ValueError("Cable not in catalogue: %s" % wire_size)
			cab_weight = 0
			weight_cables += cab_weight

	return tray, str(int(round(weight_cables)))


def get_wire_crossection(el_sys):
	"""Get cable cross-section of the system"""

	# Only for Power circuits
	if el_sys.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit:
		# read system parameter
		# wire_type = el_sys.wire_type
		wire_size = el_sys.WireSizeString
		if not(wire_size):
			param_list = el_sys.GetParameters("Cable Description_1")
			wire_size = [i for i in param_list if i.Id == ElementId(8961915)][0]
			wire_size = wire_size.AsString()

		# get info from catalogue
		try:
			cab_diameter = get_cable(wire_size)[1]
		except:
			cab_diameter = 0
			# raise ValueError(
			# 	"Cable not in catalogue \n %d" % el_sys.Id.IntegerValue)
		return cab_diameter * cab_diameter

	# for other circuits
	else:
		# cables for DATA and
		wire_size = el_sys.LookupParameter("Cable Type").AsString()
		try:
			cab_diameter = get_cable(wire_size)[1]
		except:
			return 0
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
	if not info_list:
		return None
	tray = info_list[0]
	tray_fill = str(info_list[1])
	p_name = "MC Object Variable 1"
	setup_param_value(tray, p_name, tray_fill)


def set_tray_weight(info_list):
	if not info_list:
		return None
	tray = info_list[0]
	tray_weight = str(info_list[1])
	p_name = "MC Object Variable 2"
	setup_param_value(tray, p_name, tray_weight)


def set_tag(info_list):
	if not info_list:
		return None
	tray = info_list[0]
	from_to = info_list[1]
	wire_size = info_list[2]
	setup_param_value(tray, "Multi_Tag_1", wire_size)
	setup_param_value(tray, "Multi_Tag_2", from_to)


def clean_tray_parameters(tray_list):
	"""
		Put \\s symbol to pre-defined parameters
	"""
	try:
		map(lambda x: setup_param_value(x, "MC Object Variable 1", ""), tray_list)
		map(lambda x: setup_param_value(x, "MC Object Variable 2", ""), tray_list)
		map(lambda x: setup_param_value(x, "Multi_Tag_1", ""), tray_list)
		map(lambda x: setup_param_value(x, "Multi_Tag_2", ""), tray_list)
	except:
		pass


def get_tags(link):
	tray = link[0]
	el_systems = link[1]
	# get ElSys info
	from_to = [x.PanelName +
		"->" + x.LoadName
		for x in el_systems]

	get_wire = lambda el_sys: [
		i for i in el_sys.GetParameters("Cable Description_1")
		if i.Id == ElementId(8961915)][0].AsString()

	# cable_sise = [
	# 	x.WireSizeString if x.WireSizeString
	# 	else get_wire(x)
	# 	for x in el_systems]

	cable_sise = list()
	for el_sys in el_systems:
		# for Power circuits
		if el_sys.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit:
			if el_sys.WireSizeString:
				cable_sise.append(el_sys.WireSizeString)
			else:
				cable_sise.append(get_wire(el_sys))

		# for other circuits
		else:
			# TODO: add info for Data circuits
			cable_sise.append("")

	from_to_string = '\r\n'.join(from_to)
	size_string = '\r\n'.join(cable_sise)
	return tray, from_to_string, size_string


global doc  # type: ignore
