# maya imports
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaRender as OpenMayaRender
import maya.cmds as mc

# NOTE: USE THIS NODE ID!
# node id = OpenMaya.MTypeId(0x0011AE60),

# initialize the script plug-in
def initializePlugin(mobject):
  """Loads the plugin"""
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
  
# uninitialize the script plug-in
def uninitializePlugin(mobject):
  """Unloads the plugin"""
  mplugin = OpenMayaMPx.MFnPlugin(mobject)
