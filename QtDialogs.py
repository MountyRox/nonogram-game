import sys
import pathlib

from PySide6.QtGui import *
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox


# Get filename using QFileDialog
def GetOpenFileName (startDir = ''):
   filter = 'Nonogramm (*.nos);;Alle Dateien (*.*)'
   filename = QFileDialog.getOpenFileName (None, 'Gespeichertes Nonogramm laden', startDir, filter)

   return str(pathlib.Path(filename[0]))  # convert to os independent path string

# Get filename using QFileDialog
def GetOpenNewFileName (startDir = ''):
   filter = 'Nonogramm (*.nob);;Alle Dateien (*.*)'
   filename = QFileDialog.getOpenFileName (None, 'Neues Nonogramm laden', startDir, filter)

   return str(pathlib.Path(filename[0]))  # convert to os independent path string

def GetSaveFileName (startDir = ''):
   filter = 'Nonogramm (*.nos);;Alle Dateien (*.*)'
   filename = QFileDialog.getSaveFileName (None, 'Nonogramm speichern', '', filter, startDir)
   
   return str(pathlib.Path(filename[0]))  # convert to os independent path string

def MessageBox (txt, infoTxt='', buttons = QMessageBox.Ok, defaultButton = QMessageBox.Ok):
   msgBox = QMessageBox ()
   msgBox.setText(txt)
   msgBox.setInformativeText(infoTxt)
   msgBox.setStandardButtons(buttons)
   msgBox.setDefaultButton(defaultButton) 
   return msgBox.exec()




def RecentFilePathContexMenu (recentFilePaths: list):
   pathNameDict = {}
   menu = QMenu()
   # we must check for double file names. If there are some they must derive from different pathes
   doubleFound = False
   nameSet = set () # only to check for double names
   for path in recentFilePaths:
      fileName = pathlib.Path(path).stem
      doubleFound = fileName in nameSet
      if doubleFound: break
      nameSet.add (fileName)

   for path in recentFilePaths:
      fileName = pathlib.Path(path).stem
      if doubleFound:
         menuEntry = f'{fileName} ({pathlib.Path(path).parent})'
         menu.addAction (menuEntry)
         pathNameDict [menuEntry] = (pathlib.Path(path).parent, fileName + pathlib.Path(path).suffix)
      else:
         menu.addAction (fileName)
         pathNameDict [fileName] = (pathlib.Path(path).parent, fileName + pathlib.Path(path).suffix)

   ret = menu.exec(QCursor.pos())
   if ret:
      selectedName = ret.text()
      return str (pathlib.Path.joinpath (*pathNameDict[selectedName]))
   else: return None



if __name__ == "__main__":
   qtApp = QApplication(sys.argv)

   #fileName =  GetOpenFileName ()
   
   # ret = MessageBox ('Nonogram has been modified.', 'Want to save', \
   #       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

      # menu = QMenu()
      # menu.addAction ('Action 1')
      # menu.addAction ('Action 2')
      # menu.addAction ('Action 3')
      # print (menu.exec(QCursor.pos()))
   pathlist = [r'e:\Dokuments\Python\Projets\Nonogramm\Nono1.nob', 
            r'e:\Dokuments\Python\Projets\Nonogramm\Nono_test.nob', 
            r'e:\Dokuments\Python\Projets\Nonogramm\Nono_Vogel.nob',
            r'e:\Dokuments\Python\Projets\Nonogramm\Nono_51.nob',
            r'e:\Dokuments\Python\Projets\Nonogramm\Nono_Multi.nob']
   
   print (RecentFilePathContexMenu (pathlist))

   qtApp.quit()
   sys.exit()

