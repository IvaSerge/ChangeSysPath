import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import importlib
from importlib import reload

import csv
import re


def check_circuit(_circuit):
	is_data_circuit = _circuit.SystemType == Electrical.ElectricalSystemType.PowerCircuit
	is_elec_circuit = _circuit.SystemType == Electrical.ElectricalSystemType.Data
	if not any([is_data_circuit, is_elec_circuit]):
		return None
	circuit_mode_custom = _circuit.CircuitPathMode == Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.Custom
	if not circuit_mode_custom:
		return _circuit
	return None


def get_circuit_info(_circuit):
	if _circuit.SystemType == Electrical.ElectricalSystemType.PowerCircuit:
		circuit_system_type = "PowerCircuit"
	elif _circuit.SystemType == Electrical.ElectricalSystemType.Data:
		circuit_system_type = "Data"
	else:
		circuit_system_type = "None"

	circuit_info = list()
	circuit_id = str(_circuit.Id)
	circuit_panel = _circuit.PanelName
	circuit_number = str(_circuit.CircuitNumber)
	circuit_member_id = str([i for i in _circuit.Elements][0].Id)

	circuit_info.append(circuit_system_type)
	circuit_info.append(circuit_id)
	circuit_info.append(circuit_panel)
	circuit_info.append(circuit_number)
	circuit_info.append(circuit_member_id)
	return circuit_info


def write_csv(_file_name, _info):
	open(_file_name, 'w').close()  # clean file
	with open(_file_name, 'w', newline='', encoding='utf-8') as csvfile:
		# creating a csv writer object
		fields = ['System Type', 'Circuit Id', 'Panel', 'Circuit Number', 'Circuit Element']
		csvwriter = csv.writer(csvfile, dialect='excel')
		csvwriter.writerow(fields)
		csvwriter.writerows(_info)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
csv_data = dir_path + "\\" + IN[2]  # type: ignore
circuits_info = list()
circuits = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	ToElements()

for circuit in circuits:
	check = check_circuit(circuit)
	if not check:
		continue
	circuit_info = get_circuit_info(circuit)
	circuits_info.append(circuit_info)

write_csv(csv_data, circuits_info)


OUT = circuits_info
