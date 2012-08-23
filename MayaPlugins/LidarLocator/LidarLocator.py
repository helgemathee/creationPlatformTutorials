# maya imports
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaRender as OpenMayaRender
import maya.cmds as mc

class LidarLocator(OpenMayaMPx.MPxLocatorNode):
  
  __fileName = OpenMaya.MObject()
  
  def __init__(self):
    super(LidarLocator, self).__init__()
    
  def __del__(self):
    pass
    
  def compute(self, plug, datablock):
    pass
  
  def draw(self, view, path, style, status):
    pass
  
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
