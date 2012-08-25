# maya imports
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaRender as OpenMayaRender
import maya.cmds as mc

from FabricEngine.CreationPlatform.SceneImpl import Scene
from FabricEngine.CreationPlatform.Nodes.Parsers.LidarParserImpl import LidarParser
from FabricEngine.CreationPlatform.Nodes.SceneGraphNodeImpl import SceneGraphNode
from FabricEngine.CreationPlatform.Nodes.Rendering.ShaderGroupImpl import ShaderGroup
from FabricEngine.CreationPlatform.Nodes.Rendering.MaterialImpl import Material
from FabricEngine.CreationPlatform.Nodes.Rendering.InstanceImpl import Instance
from FabricEngine.CreationPlatform.Nodes.Kinematics.TransformImpl import Transform

from FabricEngine.CreationPlatform.RT.Math import *

class EmulatedViewport(SceneGraphNode):
  
  __redrawEvent = None
  __window = None
  __camera = None
  
  def __init__(self, scene, **options):
    
    super(EmulatedViewport, self).__init__(scene, **options)
    
    # construct event
    self.__redrawEvent = self.constructDGEvent('Redraw')
    
    # construct handler
    handler = self.constructDGEventHandler('Redraw')
    self.__redrawEvent.appendEventHandler(handler)
    
    # construct dg nodes to store the data
    self.__window = self.constructDGNode('Window')
    self.__camera = self.constructDGNode('Camera')
    
    # connect the dg nodes to the handler
    handler.setScope('window', self.__window)
    handler.setScope('camera', self.__camera)
    
    # create dummy drawing record attributes
    self.__window.addMember('numDrawnVerticies', 'Size')
    self.__window.addMember('numDrawnTriangles', 'Size')
    self.__window.addMember('numDrawnGeometries', 'Size')
    
    # create the matrix attributes
    self.__camera.addMember('projectionMat44', 'Mat44')
    self.__camera.addMember('cameraMat44', 'Mat44')
    
    # prepare the rendering
    self.bindDGOperator(
      handler.preDescendBindings,
      name = "pushAttribs",
      sourceCode = [
        "use FabricOGL;",
        "operator pushAttribs() {",
        "  glPushAttrib(GL_ALL_ATTRIB_BITS);",
        "}"
      ],
      layout = []
    )

    # end the rendering
    self.bindDGOperator(
      handler.postDescendBindings,
      name = "popAttribs",
      sourceCode = [
        "use FabricOGL;",
        "operator popAttribs() {",
        "  glPopAttrib();",
        "  glUseProgram(0);",
        "}"
      ],
      layout = []
    )
    
    # add reference interfaces
    self.addReferenceInterface("ShaderGroup", "ShaderGroup", True, self.__addShaderGroup)
    
  def __addShaderGroup(self, data):
    node = data['node']
    self.getRedrawDGEventHandler().appendChildEventHandler(node.getRedrawDGEventHandler())
    
  def setMatrices(self, cam, proj):
    invCameraMat44 = Mat44(
      Vec4(cam(0,0), cam(1,0), cam(2,0), cam(3,0)),
      Vec4(cam(0,1), cam(1,1), cam(2,1), cam(3,1)),
      Vec4(cam(0,2), cam(1,2), cam(2,2), cam(3,2)),
      Vec4(cam(0,3), cam(1,3), cam(2,3), 1.0)
    )
    projectionMat44 = Mat44(
      Vec4(proj(0,0), proj(1,0), proj(2,0), proj(3,0)),
      Vec4(proj(0,1), proj(1,1), proj(2,1), proj(3,1)),
      Vec4(proj(0,2), proj(1,2), proj(2,2), proj(3,2)),
      Vec4(proj(0,3), proj(1,3), proj(2,3), 1.0)
    )
    self.__camera.setData('cameraMat44', 0, invCameraMat44)
    self.__camera.setData('projectionMat44', 0, projectionMat44)
    
  def redraw(self):
    return self.__redrawEvent.fire()

class LidarLocator(OpenMayaMPx.MPxLocatorNode):
  
  __fileName = OpenMaya.MObject()
  __fileNameValue = None
  __scene = None
  __viewport = None
  __parser = None
  __instance = None
  
  def __init__(self):
    super(LidarLocator, self).__init__()
    self.__fileNameValue = ""
    self.__scene = Scene(None, exts = {'FabricLIDAR': ''}, guarded = True)
    self.__viewport = EmulatedViewport(self.__scene)
    self.__parser = None
    
  def __del__(self):
    self.__parser = None
    self.__viewport = None
    self.__scene.close()
    self.__scene = None
    
  def draw(self, view, path, style, status):
    fileNameValue = OpenMaya.MPlug(self.thisMObject(), LidarLocator.__fileName).asString()
    if not fileNameValue == self.__fileNameValue:
      self.__fileNameValue = fileNameValue
      
      # todo: proper file checking
      if self.__parser is None:
        self.__parser = LidarParser(self.__scene, url = self.__fileNameValue)
        
        # setup the shader group
        group = ShaderGroup(self.__scene)
        self.__viewport.addShaderGroupNode(group)
        
        # compute the bbox of the points
        points = self.__parser.getPointsNode()
        bbox = points.getBoundingBox()
        center = bbox['min'].add(bbox['max']).multiplyScalar(0.5).negate()
        scale = Vec3(1.0, 1.0, 1.0).multiplyScalar(0.01)
        center = center.multiply(scale)
        
        # create the material
        material = Material(self.__scene, xmlFile='Standard/FlatVertexColor', shaderGroup=group)
        self.__instance = Instance(self.__scene,
          transform = Transform(self.__scene, globalXfo = Xfo(tr = center, sc = scale)),
          geometry = points,
          material = material
        )

      else:
        self.__parser.setUrl(self.__fileNameValue)
      
    # retrieve both the inv camera matrix as well as projection matrix
    cameraDag = OpenMaya.MDagPath()
    view.getCamera(cameraDag)
    invCameraMat = cameraDag.inclusiveMatrix().inverse()
    projectionMat = OpenMaya.MMatrix()
    view.projectionMatrix(projectionMat)
    self.__viewport.setMatrices(invCameraMat, projectionMat)
    
    # render the fabric creation platform content
    self.__viewport.redraw()
    
  @staticmethod
  def creator():
    return OpenMayaMPx.asMPxPtr( LidarLocator() )
  
  @staticmethod
  def initializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    
    LidarLocator.__fileName = tAttr.create("fileName", "fn", OpenMaya.MFnData.kString)
    tAttr.setStorable(1)
    tAttr.setUsedAsFilename(1)
    LidarLocator.addAttribute(LidarLocator.__fileName)
    
    return OpenMaya.MStatus.kSuccess

# initialize the script plug-in
def initializePlugin(mobject):
  """Loads the plugin"""
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
  mplugin.registerNode(
    "LidarLocator",
    OpenMaya.MTypeId(0x0011AE60),
    LidarLocator.creator,
    LidarLocator.initializer,
    OpenMayaMPx.MPxNode.kLocatorNode
  )
  
# uninitialize the script plug-in
def uninitializePlugin(mobject):
  """Unloads the plugin"""
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
  mplugin.deregisterNode(
    OpenMaya.MTypeId(0x0011AE60)
  )
