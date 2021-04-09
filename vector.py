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

# ================ Python imports
import operator
from operator import itemgetter, attrgetter

# ================ local imports
import math


class Vec():
	def __init__(self, start, end):
		"""
		Vector by start-end points all
		"""
		vector_x = end.X - start.X
		vector_y = end.Y - start.Y
		vector_z = end.Z - start.Z

		self.origin = start
		self.coord = XYZ(vector_x, vector_y, vector_z)
		# basis = Autodesk.Revit.DB.XYZ.BasisX
		# self.angle = basis.AngleTo(self.vector)

