"""Electrical systems fuctions."""

__author__ = "IvaSerge"
__email__ = "ivaserge@ukr.net"
__status__ = "Development"


def sort_by_distance(el_system, board_inst, list_inst):
	"""Sort families by nearest distance
	args:
		el_system - current electrical system
		board_inst - electrical board instance
		instances - list of instances
	return:
		sort_list - sorted list of instances
	"""
	sorted_list = list()
	sorted_list.append(board_inst)
	unsorted_list = list()
	map(lambda x: unsorted_list.append(x), list_inst)

	while unsorted_list:
		if len(unsorted_list) == 1:
			sorted_list.append(unsorted_list.pop(0))
		else:
			start_inst = sorted_list[-1]
			distances = [get_distance(
				start_inst,
				check_inst,
				el_system)
				for check_inst in unsorted_list]
			temp_list = zip(unsorted_list, distances)
			temp_list.sort(key=operator.itemgetter(1))
			next_pnt = temp_list[0][0]
			pop_index = unsorted_list.index(next_pnt)
			unsorted_list.pop(pop_index)
			sorted_list.append(next_pnt)

	return sorted_list


def get_distance(inst_start, inst_to_check, el_system):
	start_pnt = find_connector_origin(inst_start, el_system)
	next_pnt = find_connector_origin(inst_to_check, el_system)
	distance = start_pnt.DistanceTo(next_pnt)
	return distance


def find_connector_origin(inst, el_system):
	con_set = inst.MEPModel.ConnectorManager.Connectors
	for connector in con_set:
		con_type = connector.ConnectorType
		type_is_logic = con_type == ConnectorType.Logical
		if not(connector.AllRefs.IsEmpty):
			con_allRefs = [x for x in connector.AllRefs]
			el_system_owner = con_allRefs[0].Owner
			check_sys = el_system_owner.Id == el_system.Id
			if check_sys and not(type_is_logic):
				return connector.Origin
			if check_sys and type_is_logic:
				# connector is found
				# but logic connector have no Origin
				# so FamilyInstance coordinate would be taken
				# may lead to mistakes while path creation!!!
				return connector.Owner.Location.Point
	return None


def create_new_path(inst_list, el_system):
	"""Creates list of XYZ that runs through instancees in list.

	args:
		inst_list - list of RVT instances
	return:
		xyz_list - list of points that make path
	"""
	pairs_list = list()
	for i, inst in enumerate(inst_list):
		if i < inst_list.Count - 1:
			pairs_list.append([inst, inst_list[i + 1]])
		else:
			pass
	xyz_list = [
		get_intermadiate_points(x, el_system)
		for x in pairs_list]
	last_pnt = find_connector_origin(inst_list[-1], el_system)
	xyz_list.append(last_pnt)

	return flatten_list(xyz_list)


def get_intermadiate_points(inst_list, el_system):
	start_pnt = find_connector_origin(inst_list[0], el_system)
	end_pnt = find_connector_origin(inst_list[1], el_system)
	# check if Z is equal with the tolerance
	start_check_pnt = XYZ(0, 0, start_pnt.Z)
	end_check_pnt = XYZ(0, 0, end_pnt.Z)

	vert_point = XYZ(
		start_pnt.X,
		start_pnt.Y,
		end_pnt.Z)

	if any([
		start_check_pnt.IsAlmostEqualTo(end_check_pnt),
		vert_point.IsAlmostEqualTo(end_check_pnt)
	]):
		# points are on the same level or above each other
		# no additional vertical point requiered
		return start_pnt
	else:
		# points are not on the same level
		# additional vertical point requiered
		return [start_pnt, vert_point]


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


global doc

# sys_electrical = doc.GetElement(ElementId(elemId))
# sys_board = sys_electrical.BaseEquipment
# if not(sys_electrical.Elements.IsEmpty):
# 	sys_elements = [x for x in sys_electrical.Elements]

# start_tray = getByCatAndStrParam(
# 	_bic,
# 	_bip,
# 	tray_name,
# 	False)

# sys_sorted_elements = sort_by_distance(
# 	sys_electrical,
# 	sys_board,
# 	sys_elements)

# short_path = create_new_path(
# 	sys_sorted_elements,
# 	sys_electrical)

# standard_path = elem.GetCircuitPath()
# short_path = List[XYZ]([
# 	standard_path[0],
# 	standard_path[standard_path.Count - 1]])
