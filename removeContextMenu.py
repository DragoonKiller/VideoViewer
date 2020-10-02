import os
import sys
from winregistry import WinRegistry as Reg

reg = Reg()
regPath = 'HKEY_CLASSES_ROOT\\*\\shell'
videoViewerPath = regPath + '\\VideoViewer'
commandPath = videoViewerPath + '\\command'
reg.delete_key(commandPath)
reg.delete_key(videoViewerPath)
