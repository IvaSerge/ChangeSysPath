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

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# ================ Python imports
import operator
import math
from operator import itemgetter, attrgetter


def mm_to_ft(mm):
	return 3.2808 * mm / 1000


def ft_to_mm(ft):
	return ft * 304.8


def toPoint(xyz):
	x = ft_to_mm(xyz.X)
	y = ft_to_mm(xyz.Y)
	z = ft_to_mm(xyz.Z)
	return Point.ByCoordinates(x, y, z)


class Vec():
	def __init__(self, start, end):
		"""
		Vector by start-end points all
		"""
		vector_x = end.X - start.X
		vector_y = end.Y - start.Y
		vector_z = end.Z - start.Z

		self.start = start
		self.end = end
		self.coord = XYZ(vector_x, vector_y, vector_z)
		basis = Autodesk.Revit.DB.XYZ.BasisX
		self.direction = basis.AngleTo(self.coord)

	def altitude_foot(self, point):
		# # line start is A, line end is B
		# point - is the C
		# find point X that is the foot of ABC
		pnt_A = self.start
		pnt_B = self.end
		pnt_C = point

		# check if it is a vertical reiser
		basis = Autodesk.Revit.DB.XYZ.BasisZ
		angle_to_Z = round(math.degrees(basis.AngleTo(self.coord)))

		if any([angle_to_Z == 0, angle_to_Z == 180, not angle_to_Z]):
			pnt_ax, pnt_ay, pnt_az = pnt_A.X, pnt_A.Y, point.Z
			pnt_X = XYZ(pnt_ax, pnt_ay, pnt_az)
			return pnt_X

		# check if points are on the same Z
		if pnt_C.Z != pnt_A.Z:
			pnt_cx, pnt_cy, pnt_cz = point.X, point.Y, pnt_A.Z
			pnt_C = XYZ(pnt_cx, pnt_cy, pnt_cz)
		else:
			pnt_C = point

		dist_AB = ft_to_mm(pnt_A.DistanceTo(pnt_B))
		dist_AC = ft_to_mm(pnt_A.DistanceTo(pnt_C))

		vec_ab = self.coord
		vec_ac = Vec(pnt_A, pnt_C).coord
		vec_cb = Vec(pnt_C, pnt_B).coord
		angle_CBA = vec_ab.AngleTo(vec_cb)
		angle_BAC = vec_ab.AngleTo(vec_ac)

		# check if triangle is obtuse
		# no foot for obtuse triange requiered
		if math.degrees(angle_CBA) >= 90:
			return None

		dist_AX = math.cos(angle_BAC) * dist_AC
		# triangle AXC is similar to rectrialngle with site AB
		similarity_ratio = dist_AX / dist_AB
		scalar_multiply = Autodesk.Revit.DB.XYZ.Multiply
		vector_AX = scalar_multiply(self.coord, similarity_ratio)

		pnt_X = XYZ(
			pnt_A.X + vector_AX.X,
			pnt_A.Y + vector_AX.Y,
			pnt_A.Z + vector_AX.Z)

		return pnt_X
