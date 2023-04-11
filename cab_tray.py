"""Cable tray fuctions."""

__author__ = "IvaSerge"
__status__ = "Development"

# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory

# ================ Python imports
import collections
from collections import deque

# ================ local imports
import graph
from graph import *
import vector


def param_by_cat(_bic, _name):
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


def category_by_bic_name(doc, _bicString):
	bic_value = System.Enum.Parse(BuiltInCategory, _bicString)
	return Autodesk.Revit.DB.Category.GetCategory(doc, bic_value)


class TrayNet():
	"""A class to represent conntected cable tray net"""
	def __init__(self, net_name):
		"""Create TrayNet by name
		args:
			net_name (str):
			The name of the net, that can be found in
			"Cable Tray ID" parameter
		"""
		self.name = net_name
		self.instances = None
		self.nodes = None
		self.graph = None
		self.get_tray_relations()

	@staticmethod
	def get_connector_points(instance):
		location_str = instance.Location.GetType().Name

		if location_str == "LocationCurve":
			con_manager = instance.ConnectorManager
			con = con_manager.Connectors
			points = [x.Origin for x in con]

		if location_str == "LocationPoint":
			# make it easy! No connector check. Takes only location point
			# inst_cat = instance.Category.Id.IntegerValue
			# for not cable tray fitting
			# if inst_cat != -2008126:
			# 	con_manager = instance.MEPModel.ConnectorManager
			# 	cons = con_manager.Connectors
			# 	con = [x for x in cons if x.Domain == Domain.DomainElectrical]
			# 					points = [x.Origin for x in con]
			# else:
			# 	# for fitting - location point
			points = [instance.Location.Point]

		if len(points) > 2:
			raise ValueError(
				"More than 3 connectors found: check instanse %s" % instance.Id.ToString())
		return points

	def _get_first_tray(self):
		"""Get first-in cable tray instance.

		Cable tray will be selected by "Cable Tray ID" parameter value
		"""

		name = self.name
		# tray system name is in "Cable Tray ID" parameter
		param = param_by_cat(
			Autodesk.Revit.DB.BuiltInCategory.OST_CableTray,
			"Cable Tray ID")

		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(param.Id)
		frule = FilterStringRule(pvp, fnrvStr, name)
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
		category_elem = elem.Category
		category_tray = category_by_bic_name(elem.Document, "OST_CableTray")
		category_fitting = category_by_bic_name(elem.Document, "OST_CableTrayFitting")

		# for cable tray
		if category_elem.Id == category_tray.Id:
			elem_con_manager = elem.ConnectorManager
		# for cable tray fitting
		elif category_elem.Id == category_fitting.Id:
			elem_mep_model = elem.MEPModel
			elem_con_manager = elem_mep_model.ConnectorManager
		# instance is not tray or fitting
		else:
			inst_Id = str(_inst.Id.IntegerValue)
			error_value = "Elem is not a tray: " + inst_Id
			raise ValueError(error_value)

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
			elems_to_ceck.extend(elem_refs)
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

		if self.nodes:
			self.graph = Graph(self.nodes)
		return elems_checked

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
		# not very optimal all-to-all distances comparasion
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
