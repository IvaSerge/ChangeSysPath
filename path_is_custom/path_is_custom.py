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

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def check_circuit(_circuit):
	is_data_circuit = _circuit.SystemType == Electrical.ElectricalSystemType.PowerCircuit
	is_elec_circuit = _circuit.SystemType == Electrical.ElectricalSystemType.Data
	if not any([is_data_circuit, is_elec_circuit]):
		return None
	circuit_mode_custom = _circuit.CircuitPathMode == Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.Custom
	if not circuit_mode_custom:
		return _circuit
	return None


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
csv_data = dir_path + "\\" + IN[2]  # type: ignore
outlist = list()
circuits = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	ToElements()

for circuit in circuits:
	check = check_circuit(circuit)
	if not check:
		continue
	outlist.append(check)

OUT = outlist
