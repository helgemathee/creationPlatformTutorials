# maya imports
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaRender as OpenMayaRender
import maya.cmds as mc

from FabricEngine.CreationPlatform.SceneImpl import Scene
from FabricEngine.CreationPlatform.Nodes.Parsers.LidarParserImpl import LidarParser

class LidarLocator(OpenMayaMPx.MPxLocatorNode):
  
  __fileName = OpenMaya.MObject()
  __fileNameValue = None
  __scene = None
  __parser = None
  
  def __init__(self):
    super(LidarLocator, self).__init__()
    self.__fileNameValue = ""
    self.__scene = Scene(None, exts = {'FabricLIDAR': ''}, guarded = True)
    self.__parser = None
    
  def __del__(self):
    self.__parser = None
    self.__scene.close()
    self.__scene = None
    
  def draw(self, view, path, style, status):
    fileNameValue = OpenMaya.MPlug(self.thisMObject(), LidarLocator.__fileName).asString()
    if not fileNameValue == self.__fileNameValue:
      self.__fileNameValue = fileNameValue
      
      # todo: proper file checking
      if self.__parser is None:
        self.__parser = LidarParser(self.__scene, url = self.__fileNameValue)
        
        # todo: create the rendering pipeline for the points
      else:
        self.__parser.setUrl(self.__fileNameValue)
      
      print fileNameValue
    
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
