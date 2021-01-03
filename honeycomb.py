"""
Honeycomb solid creator.
(c) 2021 Christian González Di Antonio <christiangda@gmail.com>
"""

__author__ = "Christian González Di Antonio <christiangda@gmail.com>"
__title__ = "HoneycombSolid"
__author__ = "Christian González Di Antonio"
__url__ = "https://github.com/christiangda/freecad-macro-honeycomb"
__Wiki__ = "https://github.com/mwganson/freecad-macro-honeycomb/blob/master/README.md"
__date__ = "2021.01.03" #year.month.date
__version__ = "v1.0.0"

import FreeCAD, Part, math
from FreeCAD import Base
from pivy import coin

class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self

class Honeycomb(PartFeature):
	def __init__(self, obj):
		PartFeature.__init__(self, obj)
		''' Add some custom properties to our Honeycomb feature '''
		obj.addProperty("App::PropertyLength","Length","Honeycomb","Length of the Honeycomb").Length=100.0
		obj.addProperty("App::PropertyLength","Width","Honeycomb","Width of the Honeycomb").Width=100.0
		obj.addProperty("App::PropertyLength","Height","Honeycomb", "Height of the Honeycomb").Height=5.0
		
		obj.addProperty("App::PropertyLength","Circumradius","Polygon","Radius of the inner circle").Circumradius=5.0
        
        #obj.addProperty("App::PropertyLength","Edges","Honeycomb","Poligon number of edges").Radius=6.0

	def onChanged(self, fp, prop):
		''' Print the name of the property that has changed '''
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

	def execute(self, fp):
		''' Print a short message when doing a recomputation, this method is mandatory '''
		FreeCAD.Console.PrintMessage("Recompute Python Honeycomb feature\n")

		length = fp.Length
		width = fp.Width
		height = fp.Height
		radius = fp.Circumradius
        
		#edges = fp.Edges
		edges = 6

        #######################################################################
		# Container box, used to cut the polygon array
		container = Part.makeBox(length,width,height)

        #######################################################################
		# create the first polygon
		figure = []
		m=Base.Matrix()
		edges_angle = math.radians(360.0/edges)
		m.rotateZ(edges_angle)
		v=Base.Vector(radius,0,0)

		for i in range(edges):
			figure.append(v)
			v = m.multiply(v)

		figure.append(v)
		polygon = Part.makePolygon(figure)

		# move it to the center of the container box	
		polygon.translate(Base.Vector(length/2, width/2, 0))

		# create a face for the first polygon
		f1=Part.Face([polygon])

		#######################################################################
		# create copies of poligon using radial pattern

		# calculate how many circunferencias needs to cover the maximun length of the container box
		iters = int(math.floor(math.sqrt(length**2 + width**2)/radius/2)/2 +1)
		FreeCAD.Console.PrintMessage("Iteractions: " + str(iters) + "\n")

		# To store all the poligons face
		e_faces = []
		e_faces.append(f1) # add the first one created before

		# Iterate over each imaginary circle which circunference contains the center of the polygon circle 
		for i in range(1, iters):

			# over each iterations the number of polygons increase the double,
			# the angles are divided by 2 and the imaginary circunferences are the 2*radius multiplied by i
			elements = i*edges
			angle = edges_angle/i
			distance = i*2*radius

			# to relocate each new copy of the polygon
			support_matrix=Base.Matrix()
			
			# different angle to start paste the copies base on iteration
			if i%2 == 0:
				init_angle = 0
			else:
				init_angle = math.radians(30)
            
			# tell the matrix we are working on xy
			support_matrix.rotateZ(angle)

			# calculate the center of the new copy of the polygon at the same imaginary circunference (same distance from x,y,0)
			x_origin =distance*math.cos(init_angle)
			y_origin = distance*math.sin(init_angle)
			v1=Base.Vector(x_origin, y_origin,0)
			
			# create copies and move to the right position
			for j in range(elements):
				polygon_copy = polygon.copy()
				polygon_copy.translate(v1)		
				fn=Part.Face([polygon_copy])
				e_faces.append(fn)
	
				# move to the next angle
				v1 = support_matrix.multiply(v1)

		# join all the faces
		mshell = Part.makeShell(e_faces)
		extruded_polygon = mshell.extrude(Base.Vector(0,0,height))

		# cut the array of solids using the container box
		shape = container.cut(extruded_polygon)

		fp.Shape = shape # comment it to see the array of solids
		#fp.Shape = extruded_polygon # uncomment it to see the array of solids

class ViewProviderHoneycomb:
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
			static const char * ViewProviderHoneycomb_xpm[] = {
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


def makeHoneycomb():
	if FreeCAD.ActiveDocument is None:
		doc=FreeCAD.newDocument()
	else:
		doc = FreeCAD.ActiveDocument

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Honeycomb")
	Honeycomb(a)
	ViewProviderHoneycomb(a.ViewObject)
	doc.recompute()
	Gui.SendMsgToActiveView("ViewFit")


makeHoneycomb()