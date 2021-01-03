"""
Examples for a feature class and its view provider.
(c) 2009 Werner Mayer LGPL
"""

__author__ = "Werner Mayer <wmayer@users.sourceforge.net>"

import FreeCAD, Part, math
from FreeCAD import Base
from pivy import coin
import Draft, DraftTools

class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self

class Box(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		''' Add some custom properties to our box feature '''
		obj.addProperty("App::PropertyLength","Length","Box","Length of the box").Length=20.0
		obj.addProperty("App::PropertyLength","Width","Box","Width of the box").Width=20.0
		obj.addProperty("App::PropertyLength","Height","Box", "Height of the box").Height=2.0
		
		obj.addProperty("App::PropertyLength","Radius","Bolt","Radius of the inner circle").Radius=2.0

	def onChanged(self, fp, prop):
		''' Print the name of the property that has changed '''
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

	def execute(self, fp):
		''' Print a short message when doing a recomputation, this method is mandatory '''
		FreeCAD.Console.PrintMessage("Recompute Python Box feature\n")

		length = fp.Length
		width = fp.Width
		height = fp.Height
		radius = fp.Radius

		# create container box solid
		container = Part.makeBox(length,width,height)

		# create exagon solid
		polygon = []
		edges = 6
		m=Base.Matrix()

		m.rotateZ(math.radians(360.0/edges))
		v=Base.Vector(radius,0,0)

		for i in range(edges):
			polygon.append(v)
			v = m.multiply(v)

		polygon.append(v)
		exa = Part.makePolygon(polygon)

		# move to the center of the container box		
		exa.translate(Base.Vector(length/2, width/2, 0))

		exa2 = exa.copy()
		exa2.translate(Base.Vector(length/3, width/3, 0))
	
		# create a face to be extrude
		face=Part.Face([exa ,exa2])

		extrudedHexagon = face.extrude(Base.Vector(0,0,height))

		# cut the container with the array
		honeycomb = container.cut(extrudedHexagon)

		fp.Shape = honeycomb
		#fp.Shape = extrudedHexagon

class ViewProviderBox:
	def __init__(self, obj):
		''' Set this object to the proxy object of the actual view provider '''
		obj.Proxy = self

	def attach(self, obj):
		''' Setup the scene sub-graph of the view provider, this method is mandatory '''
		return

	def updateData(self, fp, prop):
		''' If a property of the handled feature has changed we have the chance to handle this here '''
		return

	def getDisplayModes(self,obj):
		''' Return a list of display modes. '''
		modes=[]
		return modes

	def getDefaultDisplayMode(self):
		''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
		return "Shaded"

	def setDisplayMode(self,mode):
		''' Map the display mode defined in attach with those defined in getDisplayModes.
		Since they have the same names nothing needs to be done. This method is optional.
		'''
		return mode

	def onChanged(self, vp, prop):
		''' Print the name of the property that has changed '''
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

	def getIcon(self):
		''' Return the icon in XMP format which will appear in the tree view. This method is optional
		and if not defined a default icon is shown.
		'''
		return """
			/* XPM */
			static const char * ViewProviderBox_xpm[] = {
			"16 16 6 1",
			" 	c None",
			".	c #141010",
			"+	c #615BD2",
			"@	c #C39D55",
			"#	c #000000",
			"$	c #57C355",
			"        ........",
			"   ......++..+..",
			"   .@@@@.++..++.",
			"   .@@@@.++..++.",
			"   .@@  .++++++.",
			"  ..@@  .++..++.",
			"###@@@@ .++..++.",
			"##$.@@$#.++++++.",
			"#$#$.$$$........",
			"#$$#######      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			"#$$#$$$$$#      ",
			" #$#$$$$$#      ",
			"  ##$$$$$#      ",
			"   #######      "};
			"""

	def __getstate__(self):
		''' When saving the document this object gets stored using Python's cPickle module.
		Since we have some un-pickable here -- the Coin stuff -- we must define this method
		to return a tuple of all pickable objects or None.
		'''
		return None

	def __setstate__(self,state):
		''' When restoring the pickled object from document we have the chance to set some
		internals here. Since no data were pickled nothing needs to be done here.
		'''
		return None


def makeBox():
	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Box")
	Box(a)
	ViewProviderBox(a.ViewObject)
	#○doc.recompute()

makeBox()