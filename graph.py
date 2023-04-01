
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

# ================ Python imports
import collections
from collections import defaultdict


class Graph():
	def __init__(self, nodes):
		"""
		self.edges is a dict of all possible next nodes
		e.g. {'X': ['A', 'B', 'C', 'E'], ...}
		self.weights has all the weights between two nodes,
		with the two nodes as a tuple as the key
		e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
		"""
		self.edges = defaultdict(list)
		self.weights = {}
		self.add_edges(nodes)

	def add_edges(self, nodes):
		for nod in nodes:
			self.add_edge(nod[0], nod[1], 1)

	def add_edge(self, from_node, to_node, weight):
		# Note: assumes edges are bi-directional
		self.edges[from_node].append(to_node)
		self.weights[(from_node, to_node)] = weight

	def dijsktra(self, initial, end):
		# shortest paths is a dict of nodes
		# whose value is a tuple of (previous node, weight)
		shortest_paths = {initial: (None, 0)}
		current_node = initial
		visited = set()

		while current_node != end:
			visited.add(current_node)
			destinations = self.edges[current_node]
			weight_to_current_node = shortest_paths[current_node][1]

			for next_node in destinations:
				weight = self.weights[(current_node, next_node)] + weight_to_current_node
				if next_node not in shortest_paths:
					shortest_paths[next_node] = (current_node, weight)
				else:
					current_shortest_weight = shortest_paths[next_node][1]
					if current_shortest_weight > weight:
						shortest_paths[next_node] = (current_node, weight)

			next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
			if not next_destinations:
				return "Route Not Possible"
			# next node is the destination with the lowest weight
			current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

		# Work back through destinations in shortest path
		path = []
		while current_node is not None:
			path.append(current_node)
			next_node = shortest_paths[current_node][0]
			current_node = next_node
		# Reverse path
		path = path[::-1]
		return path


global doc
