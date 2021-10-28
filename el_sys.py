"""Electrical systems fuctions."""

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
from Autodesk.Revit.DB.Category import GetCategory

# ================ Python imports
import operator
from operator import itemgetter, attrgetter

# ================ local imports
import cab_tray
from cab_tray import *
import graph
from graph import *
import vector
from vector import *


def process_list(_func, _list):
	return map(
		lambda x: process_list(_func, x)
		if type(x) == list else _func(x), _list)


def flatten_list(data):
	# iterating over the data
	list_in_progress = data
	list_found = True

	while list_found:
		flat_list = list()
		list_found = False
		for i in list_in_progress:
			if isinstance(i, list):
				list_found = True
				map(lambda x: flat_list.append(x), i)
			else:
				flat_list.append(i)
		list_in_progress = [x for x in flat_list]
	return list_in_progress


def sort_list_by_point(start_point, point_list):
	list_len = len(point_list)
	start_pnt_list = [start_point] * list_len
	calc_dist = zip(point_list, start_pnt_list)
	sort_dist = [x[0].DistanceTo(x[1]) for x in calc_dist]
	sort_list = zip(point_list, sort_dist)
	return [x[0] for x in sorted(sort_list, key=itemgetter(1))]


class ElSys():
	def __init__(self, el_sys_id):
		"""
		Extended electrical system class
		"""
		self.Id = el_sys_id
		self.rvt_sys = doc.GetElement(el_sys_id)
		self.rvt_board = self.rvt_sys.BaseEquipment
		unsorted_members = [x for x in self.rvt_sys.Elements]
		unsorted_members.insert(0, self.rvt_board)
		self.rvt_members = self.sort_by_distance(unsorted_members)
		self.run_along_trays = None
		self.path = None
		self.wire_type = self.rvt_sys.get_Parameter(
			BuiltInParameter.RBS_ELEC_CIRCUIT_WIRE_TYPE_PARAM).AsValueString()
		# self.wire_size = self.rvt_sys.LookupParameter("E_CableSize").AsString()

	def sort_by_distance(self, _unsorted):
		"""Sort families by nearest distance

		args:
			instances - list of instances
		return:
			sort_list - sorted list of instances
		"""

		for i in range(len(_unsorted) - 1):
			if i == 0:
				sorted_list = [x for x in _unsorted]
			else:
				sorted_part = sorted_list[:i]
				not_sorted_part = sorted_list[i:]
				start_inst = sorted_part[-1]
				distances = [self._get_distance(
					start_inst,
					check_inst)
					for check_inst in not_sorted_part]
				temp_list = list(zip(not_sorted_part, distances))
				temp_list.sort(key=operator.itemgetter(1))
				filtered_items = [x[0] for x in temp_list]
				sorted_list = sorted_part + filtered_items
		return sorted_list

	def _get_distance(self, inst_start, inst_to_check):
		start_pnt = self._find_connector_origin(inst_start)
		next_pnt = self._find_connector_origin(inst_to_check)
		distance = start_pnt.DistanceTo(next_pnt)
		return distance

	def _find_connector_origin(self, inst):
		el_system = self.rvt_sys
		el_sys_board = el_system.BaseEquipment
		con_set = inst.MEPModel.ConnectorManager.Connectors
		# outlist = list()
		# is it BaseEquipment?
		if el_sys_board.Id == inst.Id:
			# find Electrical connector
			# ATTENTION! Tested only for 1 connector in family

			board_connector = [
				con for con in con_set
				if con.Domain == Domain.DomainElectrical][0]
			return board_connector.Origin

		for connector in con_set:
			# filter out only not logical connectors
			# filter out connectors without references
			con_type = connector.ConnectorType
			type_is_logic = con_type == ConnectorType.Logical
			if not type_is_logic:
				ref_connectors = connector.AllRefs
				if ref_connectors:
					# OST_ElectricalCircuit.Id == -2008037
					owners = [
						x.Owner.Id
						for x in ref_connectors
						if x.Owner.Category.Id == ElementId(-2008037)]
				if el_system.Id in owners:
					# connector is found
					return connector.Origin
				else:
					continue
		return None

	def _get_rout_names(self):
		"""Get name list of cable trays through which cables run
		"""
		# the list should be in correct ORDER at this point!
		# TO DO. Automatical ordering to be done later

		el_sys = self.rvt_sys
		tray_net_str = el_sys.LookupParameter("MC Object Variable 1")
		tray_net_str = tray_net_str.AsString()

		# tray-net names shoud be separated by koma and white space
		# Example: aaaa, bbbb
		if tray_net_str:
			return tray_net_str.split(", ")
		else:
			return None

	def get_in_out(self, tray_net, start, end):
		"""
		For each graph it is necessery to find IN-OUT elements

		args:
			tray_net (TrayNet instance)
			start, end (XYZ) - end points

		return:
			start_tray, end_tray - IN, OUT instances
		"""

		tray_elems = tray_net.instances
		outlist = list()

		for check_point in [start, end]:
			min_distance = 1000000000
			for elem in tray_elems:
				pnts = TrayNet.get_connector_points(elem)
				for pnt in pnts:
					distance = check_point.DistanceTo(pnt)
					if distance < min_distance:
						min_distance = distance
						out_elem = elem
			outlist.append(out_elem)
		return outlist

	def find_trays_run(self):
		"""Find cable trays witin cable runs"""
		el_system_start = self.rvt_members[0]
		el_start = self._find_connector_origin(el_system_start)
		el_system_end = self.rvt_members[1]
		el_end = self._find_connector_origin(el_system_end)

		# find a net in net list
		el_sys_nets = list()
		rout_names = self._get_rout_names()
		if not(rout_names):
			self.run_along_trays = None
			return None
		for rout in rout_names:
			for net in list_of_nets:
				if net.name == rout:
					el_sys_nets.append(net)

		# with cycle check all nets
		i = 0
		net_start = el_start
		outlist = list()
		while i <= len(el_sys_nets) - 1:
			outlist.append([])

			# if it is not the last net - find nearest elem to next net
			# in real life there is only one nearest point
			# but unpredectable crazy situations are possible HERE!!!

			net = el_sys_nets[i]
			if i != len(el_sys_nets) - 1:
				net_end = TrayNet.find_nearest_pnt(
					net, el_sys_nets[i + 1])
			else:
				net_end = el_end

			start_end = self.get_in_out(net, net_start, net_end)
			start, end = start_end[0].Id, start_end[1].Id

			if start == end:
				# it is only one object in net
				outlist[i].append(start)
			else:
				# path need to be calculated using graph
				path = net.graph.dijsktra(start, end)
				map(lambda x: outlist[i].append(x), path)
			net_start = net_end
			i += 1

		outlist = flatten_list(outlist)
		self.run_along_trays = process_list(lambda x: doc.GetElement(x), outlist)		

	@staticmethod
	def get_alt_foot_point(point_A, point_B, point_C):
		triangle_vector = Vec(point_A, point_B)
		point_X = triangle_vector.altitude_foot(point_C)
		if point_X:
			return point_X
		else:
			return None

	def _tray_path(self, pnt_list):
		"""From list of points create ordered path"""
		sorted_points = list()
		test_list = list()
		next_pnt = None
		next_pnt_list = None

		for i, points in enumerate(pnt_list):
			test_list.append([])
			# # cable tray fitting, that have only one point - nothing to sort.
			if len(points) == 1:
				sorted_points.append(points[0])

			# it is cable tray. Points need to be sorted
			elif len(points) == 2:
				previous_pnt = sorted_points[-1]
				points_by_distance = sort_list_by_point(previous_pnt, points)
				tray_start = points_by_distance[0]
				tray_end = points_by_distance[1]

				next_inst = None
				# next point - is instance that is outside tray
				if i == len(pnt_list) - 1:
					next_inst = self.rvt_members[1]
					next_pnt = TrayNet.get_connector_points(next_inst)[0]

				# next point - is the part of cable tray net
				else:
					next_pnt_list = pnt_list[i + 1]
					if len(next_pnt_list) == 1:
						next_pnt = next_pnt_list[0]
					else:
						next_pnt = sort_list_by_point(
							points_by_distance[1], next_pnt_list)[0]

				# check entrance to the cable tray
				in_X = ElSys.get_alt_foot_point(tray_start, tray_end, previous_pnt)
				out_X = ElSys.get_alt_foot_point(tray_start, tray_end, next_pnt)

				if in_X and not(out_X):
					sorted_lst = sort_list_by_point(next_pnt, [tray_start, tray_end, in_X])
					sorted_points.append(sorted_lst[1])
					sorted_points.append(sorted_lst[0])

				elif out_X and not(in_X):
					sorted_lst = sort_list_by_point(previous_pnt, [tray_start, tray_end, out_X])
					sorted_points.append(sorted_lst[0])
					sorted_points.append(sorted_lst[1])

				elif out_X and in_X:
					sorted_lst = sort_list_by_point(previous_pnt, [in_X, out_X])
					sorted_points.append(sorted_lst[0])
					sorted_points.append(sorted_lst[1])
				else:
					sorted_points.append(tray_start)
					sorted_points.append(tray_end)
					pass
			else:
				# not possible situation
				raise ValueError("More than 3 poins in list")

		# sorted_points = ElSys.clear_near_points(sorted_points)
		return sorted_points

	@staticmethod
	def test_points(first_pnt, next_pnt):
		distance = first_pnt.DistanceTo(next_pnt)
		first_z = XYZ(0, 0, first_pnt.Z)
		next_z = XYZ(0, 0, next_pnt.Z)

		# parameters to check
		distance_is_ok = distance > 0.01
		level_is_changed = not(Autodesk.Revit.DB.XYZ.IsAlmostEqualTo(first_z, next_z))
		is_above = all([
			first_pnt.X == next_pnt.X,
			first_pnt.Y == next_pnt.Y])

		# situatioh 1. On the same level. Distance Ok
		if distance_is_ok and not(level_is_changed):
			return [next_pnt]

		# situatioh 2. On the same level. Distance is wrong
		if not(distance_is_ok) and not(level_is_changed):
			return None

		# situation 3. Above. Distance is Ok.
		if level_is_changed and is_above and distance_is_ok:
			return [next_pnt]
			# return 3

		# situation 4. Above. Distance is wrong
		if level_is_changed and is_above and not(distance_is_ok):
			# return None
			return distance > 0.01, distance * 100

		# situation 5. Diagonal. Distance is wrong
		if level_is_changed and not(is_above) and not(distance_is_ok):
			new_pnt = XYZ(next_pnt.X, next_pnt.Y, first_pnt.Z)
			return [new_pnt]

		# situation 5. Diagonal. Distance is Ok
		if level_is_changed and not(is_above) and distance_is_ok:
			new_pnt = XYZ(next_pnt.X, next_pnt.Y, first_pnt.Z)
			# check if new point is close to first point
			if first_pnt.DistanceTo(new_pnt) > 0.01 and next_pnt.DistanceTo(new_pnt) > 0.01:  # Ok
				return new_pnt, next_pnt
			elif first_pnt.DistanceTo(new_pnt) < 0.01 and first_pnt.DistanceTo(new_pnt) < 0.01:
				return None
			elif first_pnt.DistanceTo(new_pnt) > 0.01 and first_pnt.DistanceTo(new_pnt) < 0.01:
				return [new_pnt]
			elif first_pnt.DistanceTo(new_pnt) < 0.01 and first_pnt.DistanceTo(new_pnt) > 0.01:
				return None

	@staticmethod
	def clear_near_points(points):
		# outlist = list()
		checked_list = list()

		for point in points:
			if checked_list:
				first_pnt = checked_list[-1]
				next_pnt = point
				test_list = ElSys.test_points(first_pnt, next_pnt)
				if test_list:
					[checked_list.append(x) for x in test_list]
			# start point
			else:
				first_pnt = points[0]
				next_pnt = points[1]
				test_list = ElSys.test_points(first_pnt, next_pnt)
				checked_list.append(first_pnt)
				if test_list:
					[checked_list.append(x) for x in test_list]

		return checked_list
		# return points, checked_list, \
		# 	ElSys.test_points(checked_list[0:-4][5], checked_list[0:-4][6]), checked_list[0:-4][5].DistanceTo(checked_list[0:-4][6])

	@staticmethod
	def get_exit_point(line_points, check_pnt):
		vec = Vec(line_points[0], line_points[1])
		return vec.altitude_foot(check_pnt)

	@staticmethod
	def add_inst_points(tray_path, sys_inst):
		new_path = list()
		pnt_a = tray_path[-2]
		pnt_b = tray_path[-1]

		inst_points = [TrayNet.get_connector_points(x)[0] for x in sys_inst]
		min_distance = 1000000
		# for each instance find nearest point to the last two points
		# get the nearest instance to tray
		for point in inst_points:
			pnt_c = point
			dist_ac = pnt_c.DistanceTo(pnt_a)
			if dist_ac < min_distance:
				min_distance = dist_ac
				nearest_pnt = pnt_c
				pnt_x = ElSys.get_alt_foot_point(pnt_a, pnt_b, nearest_pnt)

		if pnt_x:
			# Remove last point from tray path
			new_path = tray_path[:-1]
			new_path.append(pnt_x)
		else:
			new_path = tray_path

		# sort instance points according new first instance
		unsorted_inst_points = list(inst_points)
		start_point = nearest_pnt
		i = 0
		while i != len(inst_points):
			start_point = sort_list_by_point(start_point, unsorted_inst_points)[0]
			list_index = unsorted_inst_points.index(start_point)
			unsorted_inst_points.pop(list_index)
			new_path.append(start_point)
			i += 1

		return new_path

	def create_new_path(self):
		# check if trays in parameter exist
		net_names_in_param = self._get_rout_names()
		tray_path = None
		if net_names_in_param:
			net_names = [x.name for x in list_of_nets]
			for name in net_names_in_param:
				if name not in net_names:
					raise ValueError(
						"Tray not found \n check system name \"%s\""
						% self.rvt_sys.LookupParameter(
							"MC Object Variable 1").AsString())

		# trays
		if self.run_along_trays:
			path_instances = list()
			# first instance - is electrical board
			brd_inst = self.rvt_members[0]
			path_instances.append(brd_inst)
			map(lambda x: path_instances.append(x), self.run_along_trays)
			# get path on the tray
			points_list = process_list(lambda x: TrayNet.get_connector_points(x), path_instances)
			tray_path = self._tray_path(points_list)
			# other instances
			sys_inst = self.rvt_members[1:]
			inst_path = ElSys.add_inst_points(tray_path, sys_inst)

		# no trays
		else:
			path_instances = self.rvt_members
			inst_path = flatten_list(
				process_list(
					lambda x: TrayNet.get_connector_points(x),
					path_instances))

		# path_with_Z = self.add_z_points(inst_path)
		self.path = self.clear_near_points(inst_path)
		# self.path = inst_path

	@staticmethod
	def add_z_points(path_points):
		"""Add or remove additional points to path

		new horisontal points to be add when Z changes,
		remove points in reisers, remove dublicates
		"""
		updated_list = list()
		for i, point in enumerate(path_points):
			if i == len(path_points) - 1:
				updated_list.append(point)
				continue

			point_next = path_points[i + 1]
			# no changes in Z
			if point.Z == point_next.Z:
				updated_list.append(point)

			# Z is changed
			# add new point on the same level as current
			if point.Z != point_next.Z:
				point_new = XYZ(
					point_next.X,
					point_next.Y,
					point.Z)
				# check if new point is not the same point as next point
				if point_new.IsAlmostEqualTo(point_next):
					# there is no need to make dublicate of the point
					updated_list.append(point)
				else:
					# new point will be added to list
					updated_list.append(point)
					updated_list.append(point_new)
		return updated_list


global doc
global list_of_nets
