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

# ================ Dynamo imports
clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript as ds
from ds.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

# ================ Python imports
import operator
from operator import itemgetter, attrgetter

# ================ local imports
import math


def processList(_func, _list):
	return map(
		lambda x: ProcessList(_func, x)
		if type(x) == list else _func(x), _list)


def unwrap(item):
	return UnwrapElement(item)


def get_orig(item):
	return item.Origin.ToPoint()


def get_lenght(pointList):
	return pointList[0].DistanceTo(pointList[1])
