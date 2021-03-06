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
from collections import deque

# ================ local imports
import graph
from graph import *
import vector


def _param_by_cat(_bic, _name):
	"""Get parametr by category and parameter Name

	args:
		_bic (BuiltiInCategory.OST_xxx): category
		_name (str): parameter name
	return:
		Autodesk.Revit.DB.Parameter: parameter
	"""
	# check Type parameter
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# check instance parameter
	# ATTENTION! instance is first in!
	# Be sure that all instances has the parameter.
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsNotElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# Not found
	return None


def category_by_bic_name(_bicString):
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return GetCategory(doc, bic)


class TrayNet():
	"""A class to represent conntected cable tray net"""
	def __init__(self, net_name):
		"""Create TrayNet by name
		args:
			net_name (str):
			The name of the net, that can be found in
			"MC Object Variable 1" parameter
		"""
		self.name = net_name
		self.instances = None
		self.nodes = None

		self.get_tray_relations()
		if self.nodes:
			self.graph = Graph(self.nodes)
		else:
			self.graph = None

	@staticmethod
	def get_connector_points(instance):
		location_str = instance.Location.GetType().Name

		if location_str == "LocationCurve":
			con_manager = instance.ConnectorManager
			con = con_manager.Connectors
			points = [x.Origin for x in con]
			return points

		if location_str == "LocationPoint":
			inst_cat = instance.Category.Id.IntegerValue
			# for not standsrd lighting fixtures for WeWork
			if inst_cat == -2001120:
				con_manager = instance.MEPModel.ConnectorManager
				cons = con_manager.Connectors
				con = [x for x in cons if x.Domain == Domain.DomainElectrical]
				point = [x.Origin for x in con]
				return point
			else:
				return [instance.Location.Point]
		return None

	def _get_first_tray(self):
		"""Get first-in cable tray instance.

		Cable tray will be selected by "MC Object Variable 1" parameter value
		"""

		name = self.name
		# tray system name is in "MC Object Variable 1" parameter
		param = _param_by_cat(
			Autodesk.Revit.DB.BuiltInCategory.OST_CableTray,
			"MC Object Variable 1")

		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(param.Id)
		frule = FilterStringRule(pvp, fnrvStr, name, False)
		filter = ElementParameterFilter(frule)

		elem = FilteredElementCollector(doc).\
			OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			FirstElement()
		return elem

	@staticmethod
	def _get_all_reference(_inst):
		reference_list = list()
		elem = _inst
		category_elem = elem.Category.Id
		category_tray = category_by_bic_name("OST_CableTray").Id
		category_fitting = category_by_bic_name("OST_CableTrayFitting").Id

		# for cable tray
		if category_elem == category_tray:
			elem_con_manager = elem.ConnectorManager

		# for cable tray fitting
		if category_elem == category_fitting:
			elem_mep_model = elem.MEPModel
			elem_con_manager = elem_mep_model.ConnectorManager

		elem_cons = elem_con_manager.Connectors
		for connector in elem_cons:
			elem_ref = connector.AllRefs
			if elem_ref:
				for ref in elem_ref:
					reference_list.append(ref.Owner)
		return reference_list

	def get_tray_relations(self):
		"""Get relations between cable trays and fittings

		Relations are represented as pairs of neighbors.\n
		It is possible more than 1 neighbor.\n
		Example: A-B, A-C means that object A is connected to B and C
		all conections are bi-directional. A-B and B-A would be created

		return:
			relation_list: list of pairs
		"""

		# if it is the only one element - no relations
		inst_first = self._get_first_tray()
		elems_to_ceck = collections.deque([])
		elems_to_ceck.append(inst_first)
		outlist = list()
		elems_checked = list()

		# while elems_to_ceck:
		while elems_to_ceck:
			elem_current = elems_to_ceck.pop()
			# there is no need to check element twice
			# but it need to be removed from the que to
			# avoid closed loop cycle
			if elem_current.Id in elems_checked:
				continue
			elems_checked.append(elem_current.Id)
			elem_refs = self._get_all_reference(elem_current)
			# fill que with new references
			map(lambda x: elems_to_ceck.append(x), elem_refs)
			# create pair of relations
			for elem in elem_refs:
				# filter out self-references
				if elem.Id != elem_current.Id:
					# graph works good with Id and do not work with object
					# that seems to be strange!!!
					# As idea obj1 != obj1 but obj1.Id == obj1.Id
					outlist.append([elem_current.Id, elem.Id])
		self.nodes = outlist
		self.instances = [
			doc.GetElement(x)
			for x in elems_checked]

	@staticmethod
	def get_shortest_distance(inst_from, inst_to):
		inst_from_points = TrayNet.get_connector_points(inst_from)
		inst_to_points = TrayNet.get_connector_points(inst_to)
		min_dist = 1000000
		for from_point in inst_from_points:
			for to_point in inst_to_points:
				distance = from_point.DistanceTo(to_point)
				if distance < min_dist:
					min_dist = distance
					nearest_pnt = from_point
		return min_dist, nearest_pnt

	@staticmethod
	def find_nearest_pnt(current_net, next_net):
		"""Search for nearest instance to the next net

		return:
			nearest_pnt (XYZ): clothest to the next_net point
		"""

		current_instances = current_net.instances
		next_instances = next_net.instances

		min_dist = 1000000
		# not very optimiset all-to-all distances comparasion
		for c_inst in current_instances:
			for n_inst in next_instances:
				distance = TrayNet.get_shortest_distance(c_inst, n_inst)
				if distance[0] < min_dist:
					nearest_pair = c_inst, n_inst
					min_dist = distance[0]
		nearest_pnt = TrayNet.get_shortest_distance(
			nearest_pair[0], nearest_pair[1])
		return nearest_pnt[1]


global doc  # type: ignore
