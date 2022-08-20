import itertools
import operator
import sys
import os
import pathlib
from typing import Any
import pygame as pg
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import *
import QtDialogs
from enum import Enum
#from regex import F
import NonoBlock
import pgButton
import UndoRedo
import ConfigProperties as cfg
import NonogramAssist as nAss



class NonogramGame:
   # define some colors
   BLACK = pg.Color ('black')
   WHITE = pg.Color ('white')
   RED = pg.Color ('red')
   NAVY = pg.Color ('navy')

   MAX_RECENT_LEN = 10   #: the maximum length of the recent file list within the config data


   #: Enum for the position of mouse click: 'COLBLOCKS ROWBLOCKS BOARD INVALID'
   EnField = Enum('self.EnField', 'COLBLOCKS ROWBLOCKS BOARD INVALID')

   enExitCode = Enum ('self.enExitCode', \
      'NONE CANCEL QUIT GET_OPEN_NEW_REQUEST GET_OPEN_REQUEST GET_SAVEAS_REQUEST OPEN_RECENT OPEN_NEW_RECENT')
   """
   Enum for the exit codes after processing user events:
   'NONE CANCEL QUIT GET_OPEN_NEW_REQUEST GET_OPEN_REQUEST GET_SAVEAS_REQUEST OPEN_RECENT OPEN_NEW_RECENT'
   """
   def __init__(self):
      """Defines all instance variables. If no concrete value can be given, the type will be given.  

         Args:
            None.

         Returns:
            None.
      """

      self.minBlockSize = 16  #: The minimum of one nonogram block in pygame self.screen pixel units
      self.rectLineWidth = 3  #: The line width of the rectangle framing the nonogram: MUST BE AN ODD VALUE

      self.rowBlocks: list    #: 2D list: input values of blocks in one row of the nonogram. Each element is a NonoBlock.ClBlock
      self.colBlocks: list    #: 2D list: input values of blocks in one column of the nonogram. Each element is a NonoBlock.ClBlock

      self.nonoAssist: nAss.NonoAssist
      """An instance of class NonogramAssist.NonoAssist providing functions to get permuatation information of the 
      nonogram and to solving the nonogram"""
      
      self.processedFields: dict 
      """
      For each processed field within the nonogram we have an entry in the self.processedFields dictionary
      The key is the tuple (column, row). Col and row are matrix indices for the field.
      (0,0) is the upper left field; (1,0) the one to the right;  (0,1) the one below
      The value is also a dict of: 
         'pos': upper left pixel position of the pygame self.screen, 
         'state': status of block regarding constants of NonoBlock.ClBlock FILLED CROSS UNKNOWN
         'mode': mode of the block regarding constants of NonoBlock.ClBlock NORMAL TRIAL
      """

      self.propertyDict: dict
      """
      Dictionary for loading and storing configuration parameter:  
      {'RecentFiles': [], 'RecentNewFiles': [], 'StartDirOpen': '', 'StartDirOpenNew': '', 'StartDirSaveAs': ''}
      """

      self.localMsgText = cfg.GetLocalMsgText ()
      """
      Dictionary for English or German text for message boxes, Infotext, etc.:  
         PartlySolutionOnly: ['', '']
         NoValidNonoFile:  ['', '']
         NoSolutionFound: ['', '']
         WantToSave: ['', '']
         butOpenNew: ''
         butOpen:''
         butSave: ''
         butSaveAs: ''
         butTrial:''  
         butRtoB:''  
         butRtoW:''  
         butUndo:'' 
         butRedo:''  

      """

      self.cfgFileName = 'RecentFiles'     #: Filename for saving the configuration data (recent file list etc.) 
      self.defaultStartDir = os.getcwd()  #: The default directory for user open file dialogs 

      self.groupButtons: pg.sprite.Group   #: Pygame group for the GUI buttons

      self.buttonOpenNew:       pgButton.clButton
      self.buttonOpen:          pgButton.clButton
      self.buttonSave:          pgButton.clButton
      self.buttonSaveAs:        pgButton.clButton
      self.buttonTrial:         pgButton.clButton
      self.buttonRtoB:          pgButton.clButton
      self.buttonRtoW:          pgButton.clButton
      self.buttonUndo:          pgButton.clButton
      self.buttonRedo:          pgButton.clButton

      self.imgBusy: pg.Surface #00FFFF

      self.noRows: int      #: number of rows of the nonogram
      self.noCols: int      #: number of columns of the nonogram
      self.gameMode: chr    
      """Defines the current mode of the game: 'N' for normal;  'T' for trial. Will be set by the class method "SetGameMode"
      The predefined values "NORMAL" and "TRIAL" of the class ClBlock in module NonoBlock are normally used to set gameMode  
      """
      self.pgBlockRes: int    #: pixel size of one block in the nonogram

      self.maxRowBlocks: int  #: The maximal width in pixel necessary to dispay the block length left of the nonogram array
      self.maxColBlocks: int  #: The maximal height in pixel necessary to dispay the block length above of the nonogram array

      self.minLeftFrameWidth =  250  #: The minimum pixel width of the area left to the nonogram holding the block length values for rows 
      self.minUpperFrameHeight = 100 #: The minimum pixel height of the area above to the nonogram holding the block length values for columns 

      self.leftFrameWidth: int        
      """The pixel width of the area left to the nonogram holding the block length values for rows.
      Min must be self.minLeftFrameWidth
      """
      self.upperFrameHeight: int    
      """The pixel height of the area above to the nonogram holding the block length values for columns.
      Min must be self.minUpperFrameHeight.
      """
      self.nonoWidth: int    #: The width of one nonogram block in pygame self.screen pixel units
      self.nonoHeight: int   #: The height of one nonogram block in pygame self.screen pixel units

      self.lineWidthOffs: int   
      """The pixel offset due to the frame arround the nonogram when converting matrix positions to pixel positions.
      Depending on the constant self.rectLineWidth 
      """

      self.screenWidth: int   #: Pixel width of the pygame self.screen
      self.screenHeight: int  #: Pixel height of the pygame self.screen

      self.rectColBlocks: pg.Rect  #: Pixel rectangle of area (above the nonogram) holding the block length values for columns.  
      self.rectRowBlocks: pg.Rect #: Pixel rectangle of area (left of the nonogram) holding the block length values for rows.  
      self.rectBoard: pg.Rect #: Pixel rectangle of area of the nonogram
      self.rectMenu: pg.Rect #: Pixel rectangle of menu button area 

      self.screen: pg.display      #: pygame main self.screen 
      self.screenBkg:  pg.Surface  #: pygame self.screen for background

      # Create an instance for undo redo actions
      self.undoStack: UndoRedo.clUndo   #: Stack for undo / redo actions
      self.undoLengthAfterSave: int  #: The length of the undo stack after the nonogram was saved

      self.isNewNonogram: bool   #: Is True, if a new nonogram is loaded. In this case the Save button must be disabled
      self.currentFilePath: str  #: The file path of the current game
      self.newRecentFilePath: str  #: A file path entered via Open... which may be the new current file path, if the new filepath is a valid nonogram


   @staticmethod 
   def ReadNonogramFromFile (fileName):
      """Reads the nonogram from file 

         Fills the dictionaries self.rowBlocks, self.colBlocks. If additional data about already processed fields ara available, 
         the dictionary self.processedFields will be filled.
         Data format: Z/S n1 n2 ... Z for row data, S for column data; ni the blocklength 
         Example for a 3 (rows) x 2 (columns) nonogram:
         Z 2
         Z 3 5
         Z 1 1 1
         S 3
         S 1 2

         Args:
            filename (str): Path name of the file to read from.

         Returns:
            bool: The return value. True for success, False otherwise.
            list: List of lists containing NonoBlock.ClBlock elements of the nonogram rows.
                  See instance variable self.rowBlocks.
            list: List of lists containing NonoBlock.ClBlock elements of the nonogram columns.
                  See instance variable self.colBlocks.
            dict: Dictionary equivalent to the instance variable self.processedFields
      """
      rdRowBlocks = []    
      rdColBlocks = []
      rdProcessedFields = {}

      try:    
         with open(fileName) as f:
            for row, line in [rdl for rdl in enumerate (f.read().split('\n'))]:
               if not line: continue
               if line[0].upper () == "Z":
                  # if the input line contains '#' block state /mode are available
                  data = line[2:].split("#")
                  # at least one element (data[0]) must be present 
                  if len (data) == 1:
                     pi = [NonoBlock.ClBlock (int(len)) for len in data[0].strip().split(" ")]
                  elif len (data) >= 4:
                     pi = [NonoBlock.ClBlock (int(len), state = s, mode = m) for len, s, m  in zip (data[0].split(" "), data [1], data [2])]

                     # read the last data block with state/mode of self.processedFields
                     # get every second element, one list starting at 0 the other with 1 and zip both
                     for col, (s, m) in enumerate (list(zip(data[3][0::2], data[3][1::2]))):
                        # only if state is not UNKNOWN we write data to self.processedFields 
                        if s != NonoBlock.ClBlock.UNKNOWN:
                           # since we do not know some pixel based variables we cannot give the right position yet.
                           # we put negative values to mark the position to be invalid. The correct values will be calculated from the key of the dict 
                           rdProcessedFields [(col, row)] = {'pos': (-1, -1), 'state': s, 'mode': m}

                  else: 
                     print ('Falsches Datenformat') 
                     return False

                  rdRowBlocks.append (pi)
                  # if we have more than one element in data it must be the state/mode of the blocklength strings
                  #  and the state/mode of the fields within the nonogram
                  #   for c in data[1]:


               elif line[0].upper() == "S":
                  # if the input line contains '#' block state /mode are available
                  data = line[2:].split("#")
                  # at least one element (data[0]) must be present 
                  if len (data) == 1:
                     pi = [NonoBlock.ClBlock (int(len)) for len in data[0].strip().split(" ")]
                  elif len (data) >= 3:
                     pi = [NonoBlock.ClBlock (int(len), state = s, mode = m) for len, s, m  in zip (data[0].split(" "), data [1], data [2])]
                  else: 
                     print ('Falsches Datenformat') 
                     return False
                  rdColBlocks.append (pi)

               else:  # input line does not start with 'Z' or 'S'
                  return False, None, None, None

            return True, rdRowBlocks, rdColBlocks, rdProcessedFields
      except:
         return False, None, None, None
         

   #ff0000

   # Gets the max text length of the rendered block length numbers
   def GetMaxHorTextLength (self, blockArray):
      """Renders the text to display the blocklength data (left to the nonogram) of each row and returns the maximum width in pixel 

         Args:
            blockArray (list): 2D list. Each element contains a list of NonoBlock.ClBlock elements of one nonogram row. 

         Returns:
            int: The width in pixel to display the longest block length text left to the nonogram 
      """
      maxTxt = 0
      # first get the width of a space
      txtSurface = pg.font.SysFont('consolas', self.minBlockSize).render(' ', False, self.BLACK)
      space = txtSurface.get_width ()
      for blocks in blockArray:
         rowLen = 0
         for block in  (blocks):
            txtSurface = pg.font.SysFont('consolas', self.minBlockSize).render(f'{block.length}', False, self.BLACK)
            rowLen += txtSurface.get_width() + space
         if rowLen > maxTxt: maxTxt = rowLen
      return maxTxt


   # Gets the max text length of the rendered block length numbers at top of nonogram
   def GetMaxVertTextLength (self, blockArray):
      """Renders the text to display the blocklength data (above the nonogram) of each column and returns the maximum height in pixel 

         Args:
            blockArray (list): 2D list. Each element contains a list of NonoBlock.ClBlock elements of one nonogram column. 

         Returns:
            int: The height in pixel to display the longest vertical block length text above the nonogram 
      """
      
      return max ([len (blocks)  for blocks in blockArray]) * self.pgBlockRes

   #FFFFFF
   def InitPygameParameter (self):
      """Initialises parameter necessary to setup the pygame frontend when starting the program without any nonogram loaded 

         Args:
            None 

         Returns:
            None 
      """  
      self.screenWidth = 400
      self.screenHeight = 200

      self.processedFields = {}

      self.propertyDict = cfg.ReadProperties (self.cfgFileName)
      if not self.propertyDict:  # we must use the default values
         self.propertyDict = {
               'RecentFiles': [], 
               'RecentNewFiles': [], 
               'StartDirOpen': self.defaultStartDir, 
               'StartDirOpenNew': self.defaultStartDir, 
               'StartDirSaveAs': self.defaultStartDir}

      # define the field rects of the fields on the board
      self.rectColBlocks = pg.Rect (0, 0, 0, 0)
      self.rectRowBlocks = pg.Rect (0, 0, 0, 0)
      self.rectBoard = pg.Rect (0, 0, 0, 0)
      self.rectMenu = pg.Rect (0, 0, self.minLeftFrameWidth, self.minUpperFrameHeight)

      self.undoLengthAfterSave = 0

      self.screen = pg.display.set_mode([self.screenWidth, self.screenHeight])
      # Screen for background
      self.screenBkg = pg.Surface([self.screenWidth, self.screenHeight])

   def InitGameParameter (self):
      """Initialises parameter necessary to setup the pygame frontend when starting the program without any nonogram loaded 

         Args:
            None 

         Returns:
            None 
      """
      # get zize of nonogram
      self.noRows = len (self.rowBlocks)     # number of rows of the nonogram
      self.noCols = len (self.colBlocks)     # number of columns of the nonogram

      self.pgBlockRes = max (self.minBlockSize, int(150/self.noCols))      # pixel size of one block in the nonogram

      # Get the frame to dispay the block length left and above the nonogram array
      self.maxRowBlocks = max ([len (blocks) for blocks in self.rowBlocks])
      self.maxColBlocks = max ([len (blocks) for blocks in self.colBlocks])

      self.leftFrameWidth = max (self.GetMaxHorTextLength (self.rowBlocks) + 5, self.minLeftFrameWidth)       
      self.upperFrameHeight = max (self.GetMaxVertTextLength (self.colBlocks) + 5, self.minUpperFrameHeight)    

      self.nonoWidth = self.pgBlockRes * self.noCols
      self.nonoHeight = self.pgBlockRes * self.noRows

      self.lineWidthOffs = self.rectLineWidth // 2

      self.screenWidth = self.nonoWidth + self.leftFrameWidth + 2*self.rectLineWidth
      self.screenHeight = self.nonoHeight + self.upperFrameHeight + 2*self.rectLineWidth

      # define the field rects of the fields on the board
      self.rectColBlocks = pg.Rect (self.leftFrameWidth+self.rectLineWidth, 0, self.nonoWidth, self.upperFrameHeight)
      self.rectRowBlocks = pg.Rect (0, self.upperFrameHeight+self.rectLineWidth, self.leftFrameWidth, self.nonoHeight)
      self.rectBoard = pg.Rect (self.leftFrameWidth+self.rectLineWidth+self.lineWidthOffs, self.upperFrameHeight+self.rectLineWidth+self.lineWidthOffs, self.nonoWidth, self.nonoHeight)
      self.rectMenu = pg.Rect (0, 0, self.leftFrameWidth, self.upperFrameHeight)

      self.screen = pg.display.set_mode([self.screenWidth, self.screenHeight])
      # Screen for background
      self.screenBkg = pg.Surface([self.screenWidth, self.screenHeight])

      # Create an instance for undo redo actions
      self.undoStack = UndoRedo.clUndo ()
      self.undoLengthAfterSave = 0

      # Now we create an instance of the nonogram assistant
      self.nonoAssist = nAss.NonoAssist (self.rowBlocks, self.colBlocks)

      # The following print will only be excecuted if nAss.DEBUGMODE is true
      self.nonoAssist.PrintPermutationsOfRowsAndCols()

      #ff00ff

   def CreateButtons (self):

      def LoadImage (FileName):
      #return pg.transform.scale(pg.image.load(dateiname), (abstand, abstand))
         return pg.image.load(FileName)

      imgSaveButton = LoadImage (r'Images\Save-Button_40.png')
      imgSaveButtonDis = LoadImage (r'Images\Save-Button_disable_40.png')
      imgSaveAsButton = LoadImage (r'Images\SaveAs-Button_40.png')
      imgSaveAsButtonDis = LoadImage (r'Images\SaveAs-Button_disable_40.png')
      imgRedoButton = LoadImage (r'Images\Redo-PNG-Photos_40.png')
      imgRedoButtonDis = LoadImage (r'Images\Redo-PNG-Photos_disable_40.png')
      imgUndoButton = LoadImage (r'Images\Undo-PNG-Photos_40.png')
      imgUndoButtonDis = LoadImage (r'Images\Undo-PNG-Photos_disable_40.png')
      imgOpenButton = LoadImage (r'Images\Open_40_V2.png')
      imgOpenNewButton = LoadImage (r'Images\Open_new_40.png')
      imgRtoBButton = LoadImage (r'Images\red_to_black_40.png')
      imgRtoBButtonDis = LoadImage (r'Images\red_to_black_disable_40.png')
      imgRtoWButton = LoadImage (r'Images\red_to_white_40.png')
      imgRtoWButtonDis = LoadImage (r'Images\red_to_white_disable_40.png')
      imgTrialButton = LoadImage (r'Images\Trial_40.png')
      imgNormalButton = LoadImage (r'Images\Normal_40.png')

      self.buttonOpenNew = pgButton.clButton (self.screen, imgOpenNewButton, imgOpenNewButton, 
                                             (2,2), self.localMsgText ['butOpenNew'])
      self.buttonOpen = pgButton.clButton    (self.screen, imgOpenButton, imgOpenButton, 
                                             (79,2), self.localMsgText ['butOpen'])
      self.buttonSave = pgButton.clButton    (self.screen, imgSaveButton, imgSaveButtonDis, 
                                             (153,2), self.localMsgText ['butSave'], False)
      self.buttonSaveAs = pgButton.clButton  (self.screen, imgSaveAsButton, imgSaveAsButtonDis, 
                                             (198,2), self.localMsgText ['butSaveAs'], False)
      self.buttonTrial = pgButton.clButton   (self.screen, imgTrialButton, imgNormalButton, 
                                             (2, 51), self.localMsgText ['butTrial'], False, False)
      self.buttonRtoB = pgButton.clButton    (self.screen, imgRtoBButton, imgRtoBButtonDis, 
                                             (46, 51), self.localMsgText ['butRtoB'], False)
      self.buttonRtoW = pgButton.clButton    (self.screen, imgRtoWButton, imgRtoWButtonDis, 
                                             (101, 51), self.localMsgText ['butRtoW'], False)
      self.buttonUndo = pgButton.clButton    (self.screen, imgUndoButton, imgUndoButtonDis, 
                                             (154, 51), self.localMsgText ['butUndo'], False)
      self.buttonRedo = pgButton.clButton    (self.screen, imgRedoButton, imgRedoButtonDis, 
                                             (200, 51), self.localMsgText ['butRedo'], False)

      self.groupButtons = pg.sprite.Group()
      self.groupButtons.add (self.buttonOpenNew)
      self.groupButtons.add (self.buttonOpen)
      self.groupButtons.add (self.buttonSave)
      self.groupButtons.add (self.buttonSaveAs)
      self.groupButtons.add (self.buttonTrial)
      self.groupButtons.add (self.buttonRtoB)
      self.groupButtons.add (self.buttonRtoW)
      self.groupButtons.add (self.buttonUndo)
      self.groupButtons.add (self.buttonRedo)

   def LoadBusy (self):
      self.imgBusy = pg.image.load (r'Images\busy.png')

   def SaveNonogramToFile (self, filename):
      with open(filename, "w", newline='') as f:
         for row, data in enumerate (self.rowBlocks):
            # First the block length
            f.write ('Z ' + ' '.join(str(bl.length) for bl in data) + '#')
            # Second the text cross status
            f.write (''.join(bl.state for bl in data) + '#')
            # third the text cross mode
            f.write (''.join(bl.mode for bl in data) + '#')
            # fourth the status/mode of the nonogramm fields in each row
            # we must run through all posible columns in the current row
            for col in range (self.noCols):
               # if the current (row, col) is in the self.processedFields dict, we write the state/mode
               # if not we write the default (NORMAL)
               if (col, row) in self.processedFields:
                  field = self.processedFields [(col, row)]
                  f.write (field ['state']+field ['mode'])
               else:
                  f.write (NonoBlock.ClBlock.UNKNOWN + NonoBlock.ClBlock.NORMAL)
            f.write ('\n')

         # now all columns
         for col, data in enumerate (self.colBlocks):
            # First the block length
            f.write ('S ' + ' '.join(str(bl.length) for bl in data) + '#')
            # Second the text cross status
            f.write (''.join(bl.state for bl in data) + '#')
            # Third the text cross mode
            f.write (''.join(bl.mode for bl in data))
            f.write ('\n')
            
   def GetNonogramFieldFromRowCol (self, col, row):
      # get the indices for the nonogram array
      upperLeft = (col * self.pgBlockRes + self.rectBoard.left, row * self.pgBlockRes + self.rectBoard.top)
      return upperLeft

   def CheckForInvalidPositons (self):
      for pos, blockAttr in self.processedFields.items():
         if blockAttr ['pos'][0] <= 0:
            blockAttr ['pos'] = self.GetNonogramFieldFromRowCol (*pos)


   def DrawNonogramBackground (self):
      self.screenBkg.fill(self.WHITE)
      #pg.draw.rect (self.screenBkg, (0, 0, 0), ((self.leftFrameWidth, self.upperFrameHeight), (self.screenWidth, self.screenHeight)), width=self.rectLineWidth)
      pg.draw.rect (self.screenBkg, self.BLACK, ((self.leftFrameWidth+self.lineWidthOffs, self.upperFrameHeight+self.lineWidthOffs), (self.nonoWidth+2*self.lineWidthOffs+2, self.nonoHeight+2*self.lineWidthOffs+2)), 
                  width=self.rectLineWidth, border_radius =-1)

      # All the vertical lines
      for c in range (self.noCols+1):
         x = self.leftFrameWidth + self.rectLineWidth + c * self.pgBlockRes
         pg.draw.line (self.screenBkg, self.BLACK, (x, 0), (x, self.screenHeight), width = 1 if c%5 else 2)

      # All the horizontal lines
      for r in range (self.noRows+1):
         y = self.upperFrameHeight + self.rectLineWidth + r * self.pgBlockRes
         pg.draw.line (self.screenBkg, self.BLACK, (0, y), (self.screenWidth, y), width = 1 if r%5 else 2)

      # the text for horizontal block length
      # first get the width of a space
      txtSurface = pg.font.SysFont('consolas', self.minBlockSize).render(' ', False, self.BLACK)
      space = txtSurface.get_width ()
      for y, blocks in enumerate (self.rowBlocks):
         firstRun = True
         for x, block in enumerate (blocks [::-1]):  # we must start at the end
            txtSurface = pg.font.SysFont('consolas', self.minBlockSize).render(f'{block.length}', False, self.BLACK)
            if firstRun: pos = (self.leftFrameWidth - txtSurface.get_width() - 1, self.upperFrameHeight + self.rectLineWidth + y * self.pgBlockRes + 1)
            else: pos = tuple(map(operator.sub, pos, (txtSurface.get_width(), 0)))
            self.screenBkg.blit(txtSurface, pos)
            # remember the rect of the horizontal block length
            block.rectOnScreen = pg.Rect (pos, txtSurface.get_size())
            block.status = NonoBlock.ClBlock.UNKNOWN
            block.mode = self.gameMode
            firstRun = False
            # now we include a space
            pos = tuple(map(operator.sub, pos, (space, 0)))

      # the text for vertical block length
      for y, blocks in enumerate (self.colBlocks):
         for x, block in enumerate (blocks [::-1]):  # we must start at the end
            s = self.minBlockSize
            txtSurface = pg.font.SysFont('consolas', s).render(f'{block}', False, self.BLACK)
            while txtSurface.get_width() >= self.pgBlockRes-1:
               s -= 1
               txtSurface = pg.font.SysFont('consolas', s).render(f'{block.length}', False, self.BLACK)

            pos = (self.leftFrameWidth + self.rectLineWidth + (y+1) * self.pgBlockRes - txtSurface.get_width(), self.upperFrameHeight - (x+1) * self.pgBlockRes)
            # remember the rects of the vertical block length
            block.rectOnScreen = pg.Rect (pos, txtSurface.get_size())
            block.status = NonoBlock.ClBlock.UNKNOWN
            block.mode = self.gameMode
            self.screenBkg.blit(txtSurface, pos)

   def DrawNonogram (self):
      for blockAttr in self.processedFields.values():
         if blockAttr ['state'] == NonoBlock.ClBlock.UNKNOWN: continue
         col = self.RED if blockAttr ['mode'] == NonoBlock.ClBlock.TRIAL else self.BLACK
         if blockAttr ['state'] == NonoBlock.ClBlock.FILLED: 
            pg.draw.rect (self.screen, col, (blockAttr ['pos'], (self.pgBlockRes-0, self.pgBlockRes-0)), width = 0, border_radius =-1)
         elif blockAttr ['state'] == NonoBlock.ClBlock.CROSS: 
            startPos = blockAttr ['pos']
            endPos = tuple(map(operator.add, blockAttr ['pos'], (self.pgBlockRes, self.pgBlockRes)))
            pg.draw.line (self.screen, col, startPos, endPos)
            startPos = tuple(map(operator.add, blockAttr ['pos'], (self.pgBlockRes, 0)))
            endPos = tuple(map(operator.add, blockAttr ['pos'], (0, self.pgBlockRes)))
            pg.draw.line (self.screen, col, startPos, endPos)

   def MarkProcessedBlocks (self):
      # make a 1D list from 2D self.rowBlocks together with 2D self.colBlocks list
      for block in list( itertools.chain(*self.rowBlocks, *self.colBlocks)):
         if block.state == NonoBlock.ClBlock.UNKNOWN: continue
         if block.state == NonoBlock.ClBlock.FILLED or block.state == NonoBlock.ClBlock.CROSS:
            rect = block.rectOnScreen 
            col = self.RED if block.mode == NonoBlock.ClBlock.TRIAL else self.NAVY
            pg.draw.line (self.screen, col, rect.topleft, rect.bottomright, width = 3) 
            pg.draw.line (self.screen, col, rect.topright, rect.bottomleft, width = 3)

   def GetNonogramFieldFromMousePos (self, pos):
      # make position relative to the upper left corner of the nonogram: subtract upper left corner
      relPos = tuple(map(operator.sub, pos, self.rectBoard.topleft))
      # get the indices for the nonogram array
      # the mouse position: first value increases to the right, second value increases when moving down
      ix = relPos [0] // self.pgBlockRes  # corresponds to the column
      iy = relPos [1] // self.pgBlockRes  # corresponds to the row
      upperLeft = (ix * self.pgBlockRes + self.rectBoard.left, iy * self.pgBlockRes + self.rectBoard.top)
      return [upperLeft, (ix, iy)]

   def SetGameTitle (self, txt = ''):
      if txt:
         pg.display.set_caption(txt)
      else:
         # get the filename without extension from file path
         fileName = pathlib.Path(self.currentFilePath).stem
         pg.display.set_caption(f'{fileName}  Trail Mode' if self.gameMode == NonoBlock.ClBlock.TRIAL else f'{fileName}   Normal Mode')

   def SetGameMode (self, mode):
      self.gameMode = mode
      self.buttonTrial.SetEnabledImage (self.gameMode == NonoBlock.ClBlock.NORMAL)
      self.SetGameTitle ()

   def CheckButtonLeftClick (self):
   
      # some menu actions need a restart of the app. For example, if a new game was loaded
      # Restart will return self.enExitCode....
      retCode = self.enExitCode.NONE
      for member in self.groupButtons:
         if not member.enabled: continue
         # we know that the left mouse button was clicked.
         # If the sprite is hovered it must be a button click
         if member.hovered:
            if member == self.buttonOpenNew:
               retCode = self.enExitCode.GET_OPEN_NEW_REQUEST

            elif member == self.buttonOpen:
               retCode = self.enExitCode.GET_OPEN_REQUEST

            elif member == self.buttonSave:
               self.SaveNonogramToFile (self.currentFilePath)
               self.undoLengthAfterSave = self.undoStack.CanUndo() 

            elif member == self.buttonSaveAs:
               retCode = self.enExitCode.GET_SAVEAS_REQUEST

            elif member == self.buttonTrial:
               self.SetGameMode (NonoBlock.ClBlock.NORMAL if self.gameMode == NonoBlock.ClBlock.TRIAL else NonoBlock.ClBlock.TRIAL)
            
            elif member == self.buttonRtoB:
               if member.enabled: self.RedToBlack ()
            
            elif member == self.buttonRtoW:
               if member.enabled: self.RedToWhite ()
            
            elif member == self.buttonUndo:
               if member.enabled: self.undoStack.Undo ()
            
            elif member == self.buttonRedo:
               if member.enabled: self.undoStack.Redo ()

      return retCode

   def CheckButtonRightClick (self):
      # some menu actions need a restart of the app. For example, if a new game was loaded
      # Restart will return self.enExitCode....
      retCode = self.enExitCode.NONE
      for member in self.groupButtons:
         if not member.enabled: continue
         # we know that the left mouse button was clicked.
         # If the sprite is hovered it must be a button click
         if member.hovered:
            if member == self.buttonOpenNew:
               if self.propertyDict ['RecentNewFiles']:  # if we have entries in the recent file list
                  returnPath = QtDialogs.RecentFilePathContexMenu (self.propertyDict ['RecentNewFiles'])
                  if returnPath:
                     retCode = self.enExitCode.OPEN_NEW_RECENT
                     self.newRecentFilePath = returnPath
               else:
                  # show the empty contex menu and do nothing
                  QtDialogs.RecentFilePathContexMenu (['(empty)'])

            elif member == self.buttonOpen:
               if self.propertyDict ['RecentFiles']:  # if we have entries in the recent file list
                  returnPath = QtDialogs.RecentFilePathContexMenu (self.propertyDict ['RecentFiles'])
                  if returnPath:
                     retCode = self.enExitCode.OPEN_RECENT
                     self.newRecentFilePath = returnPath
               else:
                  # show the empty contex menu and do nothing
                  QtDialogs.RecentFilePathContexMenu (['(empty)'])


      return retCode


   def HandleMouseEvent (self, event):
      # some menu actions need a restart of the app. For example, if a new game was loaded
      returnCode = self.enExitCode.NONE
      if self.rectBoard.collidepoint (event.pos):
         rectPos, nonoPos = self.GetNonogramFieldFromMousePos (event.pos)
         modified = True
         # We need the current state/mode for the undo stack
         # if field on nonogram board was never changed it is not yet in the self.processedFields.
         # In this case the state ist UNKNOWN
         if nonoPos in self.processedFields:
            s, m = (list (self.processedFields [nonoPos].values()))[1:]
         else:
            s = NonoBlock.ClBlock.UNKNOWN
            m = NonoBlock.ClBlock.NORMAL

         if event.button == pg.BUTTON_LEFT:
            # we only do something, if there is any change
            if s == NonoBlock.ClBlock.FILLED and m == self.gameMode: modified = False
            else:
               self.processedFields [nonoPos] = {'pos': rectPos, 'state': NonoBlock.ClBlock.FILLED, 'mode': self.gameMode}
         elif event.button == pg.BUTTON_RIGHT:
            if s == NonoBlock.ClBlock.CROSS and m == self.gameMode: modified = False
            else:
               self.processedFields [nonoPos] = {'pos': rectPos, 'state': NonoBlock.ClBlock.CROSS, 'mode': self.gameMode}
         elif event.button == pg.BUTTON_MIDDLE:
            if s == NonoBlock.ClBlock.UNKNOWN and m == self.gameMode: modified = False
            else:
               self.processedFields [nonoPos] = {'pos': rectPos, 'state': NonoBlock.ClBlock.UNKNOWN, 'mode': self.gameMode}
         else: modified = False
         if modified: 
            self.undoStack.Append (UndoRedo.EnUndoAction.SINGLE, [nonoPos, s, m], self.processedFields)

      elif self.rectColBlocks.collidepoint (event.pos) or self.rectRowBlocks.collidepoint (event.pos):
         if event.button == pg.BUTTON_LEFT:
            # make a 1D list from 2D self.rowBlocks together with 2D self.colBlocks list
            for block in list( itertools.chain(*self.rowBlocks, *self.colBlocks)):
               if block.WasClicked (event.pos):
                  # we only do something, if there is any change
                  if block.state != NonoBlock.ClBlock.CROSS or block.mode != self.gameMode:
                     self.undoStack.Append (UndoRedo.EnUndoAction.CHRMARK, [block.state, block.mode], block)
                     block.state = NonoBlock.ClBlock.CROSS
                     block.mode = self.gameMode
                  break

         elif event.button == pg.BUTTON_RIGHT or event.button == pg.BUTTON_MIDDLE:
            # make a 1D list from 2D self.rowBlocks together with 2D self.colBlocks list
            for block in list( itertools.chain(*self.rowBlocks, *self.colBlocks)):
               if block.WasClicked (event.pos):
                  # we only do something, if there is any change
                  if block.state != NonoBlock.ClBlock.UNKNOWN:
                     self.undoStack.Append (UndoRedo.EnUndoAction.CHRMARK, [block.state, NonoBlock.ClBlock.NORMAL], block)
                     block.state = NonoBlock.ClBlock.UNKNOWN
                  break
               
      elif self.rectMenu.collidepoint (event.pos):
         if event.button == pg.BUTTON_LEFT:
            returnCode = self.CheckButtonLeftClick ()
         elif event.button == pg.BUTTON_RIGHT:
            returnCode = self.CheckButtonRightClick ()
            pass

      return returnCode

   def RedToWhite (self):
      # First all red blocks from Nonogram
      undoData = []
      for pos, blockAttr in self.processedFields.items():
         if blockAttr ['mode'] == NonoBlock.ClBlock.TRIAL:
            s, m = (list (blockAttr.values()))[1:]
            undoData.append ([pos, s, m])
            blockAttr ['state'] = NonoBlock.ClBlock.UNKNOWN
            blockAttr ['mode'] = NonoBlock.ClBlock.NORMAL
      if undoData:
         self.undoStack.Append (UndoRedo.EnUndoAction.RED2BW, undoData, self.processedFields)
         
   def RedToBlack (self):
      # First all red blocks from Nonogram
      undoData = []
      for pos, blockAttr in self.processedFields.items():
         if blockAttr ['mode'] == NonoBlock.ClBlock.TRIAL: 
            s, m = (list (blockAttr.values()))[1:]
            undoData.append ([pos, s, m])
            blockAttr ['state'] = s
            blockAttr ['mode'] = NonoBlock.ClBlock.NORMAL
      if undoData:
         self.undoStack.Append (UndoRedo.EnUndoAction.RED2BW, undoData, self.processedFields)

   def CopyAutoFillDataToNonogram (self, autoFillData: dict):
      undoData = []
      if autoFillData:
         for pos, state in autoFillData.items():
            if pos in self.processedFields:
               s, m = (list (self.processedFields [pos].values()))[1:]
            else:
               s = NonoBlock.ClBlock.UNKNOWN
               m = NonoBlock.ClBlock.NORMAL
            undoData.append ([pos, s, m])
            # the correct pixel positions must be assigned later. To mark them as invalid we use -1
            self.processedFields [pos] = {'pos': (-1, -1), 'state': state, 'mode': self.gameMode}

         # Now we convert the -1 pixel data into the correct ones
         self.CheckForInvalidPositons ()
         self.undoStack.Append (UndoRedo.EnUndoAction.AUTOFILLOBV, undoData, self.processedFields)

   def AutofillObvious (self):
      autoFillData = self.nonoAssist.FillObviousFields()
      self.CopyAutoFillDataToNonogram (autoFillData)

   def AutofillRowWithPresets (self): 
      autoFillData = self.nonoAssist.FillFieldsWithPresets(self.processedFields)
      self.CopyAutoFillDataToNonogram (autoFillData[0])

   def AutofillColWithPresets (self):
      autoFillData = self.nonoAssist.FillFieldsWithPresets (self.processedFields, False)
      self.CopyAutoFillDataToNonogram (autoFillData[0])

   #00FFFF
   def AutoSolve (self):
      isSolved = False
      solver = self.nonoAssist.NonogramSolver ()
      partlySolved = False
      for isSolved, autoFillData in solver:
         if autoFillData: 
            partlySolved = True 
            self.CopyAutoFillDataToNonogram (autoFillData)
            self.screen.blit(self.screenBkg, (0, 0))
            self.screen.blit(self.imgBusy, (50, 0))
            self.DrawNonogram ()
            pg.display.flip()
         else: print ('No Data')

      if not isSolved:  # not solved at all, maybe not unique
         if partlySolved: # seems to be only party solved
            QtDialogs.MessageBox (*self.localMsgText ['PartlySolutionOnly'])
         else: # not solved at all, maybe not unique
            QtDialogs.MessageBox (*self.localMsgText ['NoSolutionFound'])

   def Old_AutoSolve (self):
      isSolved, autoFillData = self.nonoAssist.NonogramSolver ()
      if autoFillData:  
         if not isSolved: # seems to be only party solved
            QtDialogs.MessageBox (*self.localMsgText ['PartlySolutionOnly'])
         self.CopyAutoFillDataToNonogram (autoFillData)
      else:  # not solved at all, maybe not unique
         QtDialogs.MessageBox (*self.localMsgText ['NoSolutionFound'])

   def HasTrialBlocks (self):
      return [NonoBlock.ClBlock.TRIAL] in [(list (blockAttr.values()))[2:] for blockAttr in self.processedFields.values()]

   def checkButtonEnable (self):

      self.buttonUndo.SetEnabled (self.undoStack.CanUndo ())
      self.buttonRedo.SetEnabled (self.undoStack.CanRedo ())
      hasTrialBlocks = self.HasTrialBlocks ()
      self.buttonRtoB.SetEnabled (hasTrialBlocks)
      self.buttonRtoW.SetEnabled (hasTrialBlocks)
      self.buttonSave.SetEnabled (not self.isNewNonogram and self.undoStack.CanUndo() != self.undoLengthAfterSave)
      self.buttonSaveAs.SetEnabled (self.undoStack.CanUndo() != self.undoLengthAfterSave)
      self.buttonTrial.SetEnabled (True)

   def ShowButtonInfoText (self):
      for member in self.groupButtons:
         member.DrawInfoText ()

   def CheckButtonClickedLeftOrRight (self, event):
      for member in self.groupButtons:
         member.WasClicked (event)

   def AskUserToSave (self):
      # only if the SaveAs button is enabled, saving is nesseccary.
      # Checking the Save button for eneabled is not the right way, it can be disabled, because we have opened 
      # a new nonogramm which is not allowed to overwrite 
      if self.buttonSaveAs.enabled:
         ret = QtDialogs.MessageBox (*self.localMsgText ['WantToSave'], \
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
         if ret == QMessageBox.Cancel: return self.enExitCode.CANCEL
         elif ret == QMessageBox.No: return self.enExitCode.NONE
         else:
            if self.isNewNonogram:
               pass
            else:
               self.SaveNonogramToFile (self.currentFilePath)
      return self.enExitCode.NONE

   def RunPygameInitLoop (self):
      clock = pg.time.Clock()
      fps = 20
      exitCode = self.enExitCode.NONE
      goOn = True
      returnCode = 0
      while goOn:
         clock.tick(fps)
         for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
               returnCode = self.HandleMouseEvent (event)
               if returnCode == self.enExitCode.GET_OPEN_REQUEST or returnCode == self.enExitCode.GET_OPEN_NEW_REQUEST or \
                              self.enExitCode.OPEN_RECENT or returnCode == self.enExitCode.OPEN_NEW_RECENT:
                  goOn = False
                  exitCode = returnCode

            if event.type == pg.QUIT:
               goOn = False
               exitCode = self.enExitCode.QUIT
            # the button need to know, if it was clicked.
            # At the moment only necessary to hide ino text when button was clicked (left or right)
            #CheckButtonClickedLeftOrRight (event)

         self.screen.fill((255, 255, 255))
         self.groupButtons.update ()
         self.groupButtons.draw (self.screen)
         self.ShowButtonInfoText ()
         pg.display.flip()

      return exitCode

   def RunPygameMainLoop (self):
      clock = pg.time.Clock()
      fps = 20
      exitCode = self.enExitCode.NONE
      goOn = True
      returnCode = 0
      while goOn:
         clock.tick(fps)
         for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
               returnCode = self.HandleMouseEvent (event)
               if returnCode == self.enExitCode.GET_OPEN_REQUEST or returnCode == self.enExitCode.GET_OPEN_NEW_REQUEST or \
                  returnCode == self.enExitCode.OPEN_RECENT      or returnCode == self.enExitCode.OPEN_NEW_RECENT:
                  goOn = False
                  exitCode = returnCode

               elif returnCode == self.enExitCode.GET_SAVEAS_REQUEST:
                  filePath = QtDialogs.GetSaveFileName (self.propertyDict ['StartDirSaveAs'])
                  # GetSaveFileName should return a null string when user cancels the dialog, but it returns '.'
                  if filePath == '.': filePath = ''
                  if filePath:
                     self.SaveNonogramToFile (filePath)
                     self.propertyDict ['StartDirSaveAs'] = str (pathlib.Path(filePath).parent)
                     self.currentFilePath = filePath
                     self.SetGameTitle ()
                     self.undoLengthAfterSave = self.undoStack.CanUndo()
                     self.isNewNonogram = False

            if event.type == pg.KEYDOWN:
               # chnage game mode NORMAL/TRIAL
               if event.key == pg.K_t: 
                  self.SetGameMode (NonoBlock.ClBlock.TRIAL)
               if event.key == pg.K_n: 
                  self.SetGameMode (NonoBlock.ClBlock.NORMAL)
               # Undo
               if event.key == pg.K_z and event.mod & pg.KMOD_CTRL:
                  self.undoStack.Undo ()
                  
               # Redo
               if event.key == pg.K_y and event.mod & pg.KMOD_CTRL:
                  self.undoStack.Redo ()

               # red blocks to white
               if event.key == pg.K_w and event.mod & pg.KMOD_CTRL:
                  self.RedToWhite ()

               # red blocks to black
               if event.key == pg.K_b and event.mod & pg.KMOD_CTRL:
                  self.RedToBlack ()

               if event.key == pg.K_a and event.mod & pg.KMOD_CTRL:
                  self.AutofillObvious ()

               if event.key == pg.K_r and event.mod & pg.KMOD_CTRL:
                  self.AutofillRowWithPresets ()

               if event.key == pg.K_c and event.mod & pg.KMOD_CTRL:
                  self.AutofillColWithPresets ()

               if event.key == pg.K_s and event.mod & pg.KMOD_CTRL:
                  self.AutoSolve ()

            if event.type == pg.QUIT:
               goOn = False
               exitCode = self.enExitCode.QUIT
            # the button need to know, if it was clicked.
            # At the moment only necessary to hide ino text when button was clicked (left or right)
            #CheckButtonClickedLeftOrRight (event)

         #self.screen.fill((255, 255, 255))
         self.screen.blit(self.screenBkg, (0, 0))
         self.DrawNonogram ()
         self.MarkProcessedBlocks ()
         self.groupButtons.update ()
         #self.groupButtons.clear (self.screen, clear_callback)
         self.groupButtons.draw (self.screen)
         self.ShowButtonInfoText ()
         self.checkButtonEnable ()
         pg.display.flip()

      return exitCode

   def ProcessExitOfLoop (self, exitCode):
      filePath = ''
      if exitCode == self.enExitCode.GET_OPEN_REQUEST:
         filePath = QtDialogs.GetOpenFileName (self.propertyDict ['StartDirOpen'])
         # GetSaveFileName should return a null string when user cancels the dialog, but it returns '.'
         if filePath == '.': filePath = ''
         if filePath:
            self.isNewNonogram = False
            self.propertyDict ['StartDirOpen'] = str (pathlib.Path(filePath).parent)


      elif exitCode == self.enExitCode.GET_OPEN_NEW_REQUEST:      
         filePath = QtDialogs.GetOpenNewFileName (self.propertyDict ['StartDirOpenNew'])
         # GetSaveFileName should return a null string when user cancels the dialog, but it returns '.'
         if filePath == '.': filePath = ''
         if filePath:
            self.isNewNonogram = True
            self.propertyDict ['StartDirOpenNew'] = str (pathlib.Path(filePath).parent)

      elif exitCode == self.enExitCode.OPEN_RECENT:
         filePath = self.newRecentFilePath
         self.isNewNonogram = False

      elif exitCode == self.enExitCode.OPEN_NEW_RECENT:
         filePath = self.newRecentFilePath
         self.isNewNonogram = True

      if filePath:
         if os.path.exists (filePath):  #ff00ff
            success, rB, cB, pF =  self.ReadNonogramFromFile(filePath)
            if not success:
               QtDialogs.MessageBox (*self.localMsgText ['NoValidNonoFile'])
               self.isNewNonogram = False
            else:
               self.rowBlocks = rB
               self.colBlocks = cB
               self.processedFields = pF
               self.currentFilePath = filePath
               # we entered a valid nonogram file, which will be stored into the recent file list
               if self.isNewNonogram: recentFileList = self.propertyDict ['RecentNewFiles']
               else: recentFileList = self.propertyDict ['RecentFiles']
               if not (self.currentFilePath in recentFileList):
                  # insert the newest element at the top
                  recentFileList.insert (0, self.currentFilePath)
                  if len (recentFileList) > self.MAX_RECENT_LEN: del recentFileList [-1]  # remove the latest element
               return True
      
      return False


   def Main (self):
      pg.init()
      # Create an PyQT4 application object.
      qtApp = QApplication(sys.argv)

      self.InitPygameParameter ()
      self.CreateButtons ()
      self.LoadBusy ()
      self.SetGameTitle ('Nonogram Game')   

      while True:
         exitCode = self.RunPygameInitLoop ()
         if exitCode == self.enExitCode.QUIT: break
         if self.ProcessExitOfLoop (exitCode): break
      
      if exitCode != self.enExitCode.QUIT:
         while exitCode != self.enExitCode.QUIT:

            self.InitGameParameter ()

            self.SetGameMode (NonoBlock.ClBlock.NORMAL)
            self.CheckForInvalidPositons ()

            self.DrawNonogramBackground ()
            self.HasTrialBlocks ()


            while True:
               exitCode = self.RunPygameMainLoop ()
               if self.AskUserToSave () == self.enExitCode.CANCEL: continue

               if exitCode == self.enExitCode.QUIT: break
               if self.ProcessExitOfLoop (exitCode): break

      cfg.WriteProperties (self.cfgFileName, self.propertyDict)

      qtApp.quit()
      pg.quit()
      sys.exit()

if __name__ == "__main__":

   Game = NonogramGame ()
   Game.Main ()


