import os
import sys
from winregistry import WinRegistry as Reg

absPath = os.path.abspath(__file__)
print('current file path', absPath)
dirPath = os.path.dirname(absPath)
print('computed file path', dirPath)
filePath = os.path.join(dirPath, 'main.py')
print('target file path', filePath)
print('python location', sys.executable)

reg = Reg()
regPath = 'HKEY_CLASSES_ROOT\\*\\shell'
videoViewerPath = regPath + '\\VideoViewer'
reg.create_key(videoViewerPath)
reg.write_value(videoViewerPath, '', data = 'Open by Video Viewer')
commandPath = videoViewerPath + '\\command'
reg.create_key(commandPath)
reg.write_value(commandPath, '', data = '"%s" "%s" "%s"' % (sys.executable, filePath, '%1'))
