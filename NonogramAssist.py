from  NonoBlock import ClBlock
from NonoStepper import dcRowBlocks
import time
import math


class NonoAssist:
   DEBUGMODE=True
   DEBUGMODE=False
   if DEBUGMODE:  import Sec2HumanReadable as s2h

   def __init__(self, rowBlocks: list,  colBlocks: list):
      self.rowBlocks = rowBlocks
      self.colBlocks = colBlocks

      self.stepperRows = [dcRowBlocks (blocks, len (colBlocks)) for blocks in rowBlocks]
      self.stepperCols = [dcRowBlocks (blocks, len (rowBlocks)) for blocks in colBlocks]



   def CalculateNumberPermutationsOfNonogram (self, useRows = True):
      # wether we want to use the rows or the columns for calculating the permutation we define a 
      line = self.stepperRows if useRows else self.stepperCols 
         
      noPossi = 1
      for stepper in line:
         noPossi *= stepper.numberPermutations
      return noPossi


   def PrintPermutationsOfRowsAndCols (self):
      if self.DEBUGMODE: 
         for i, stepper in enumerate (self.stepperRows):
            print (f'{i+1:>3}. row has {stepper.numberPermutations:>10} permutations')

         for i, stepper in enumerate (self.stepperCols):
            print (f'{i+1:>3}. columns has {stepper.numberPermutations:>10} permutations')


   def GetOverlappingFields (self, blocks, rowLen):
      p = -1  # The cross position of the previous block. For the first block it must be -1
      blockSetsLeft = []  # array of sets. Each set contains the indices of one block. 
      # First the positions if we fill the row from left
      for b in blocks:
         blockSet = set ()
         for i in range (b.length):
            blockSet.add (p+i+1)
         blockSetsLeft.append (blockSet)  
         p = p + i + 2
            
      p = -1  
      blockSetsRight = []  
      # Now the positions if we fill the row from left. We must inverse the input
      for b in blocks[::-1]:
         blockSet = set ()
         for i in range (b.length):
            blockSet.add (rowLen - 1 - (p+i+1))
         # we must also reverse the array of sets
         blockSetsRight.insert (0, blockSet)   
         p = p + i + 2

      # Now we take the intersection of each left and right set
      interSets = []
      for sl, sr in zip (blockSetsLeft, blockSetsRight):
         interSets.append (sl.intersection (sr))

      return interSets 


   def FillObviousFields (self):
      data = set ()  # we must use a set to avoid same entries. One from using the rows and the other from the columns
      for row, blocks in enumerate (self.rowBlocks):
         ovlSetArray = self.GetOverlappingFields (blocks, len (self.colBlocks))

         for ovlSet in ovlSetArray:
            if ovlSet:
               for col in ovlSet:  # the indices of the overlapping fields are the column indices
                  data.add ((col, row)) 
      
      # now the same for all columns
      for col, blocks in enumerate (self.colBlocks):
         ovlSetArray = self.GetOverlappingFields (blocks, len (self.rowBlocks))

         for ovlSet in ovlSetArray:
            if ovlSet:
               for row in ovlSet:  # now the indices of the overlapping fields are the row indices
                  data.add ((col, row)) 
      
      return dict ([(pos, ClBlock.FILLED) for pos in data])


   def FillLineWithPresets (self, stepper:  dcRowBlocks, crossIndis: set, filledIndis: set):
      # all position indices are possible
      allPossiblePos = set ([i for i in range (stepper.noFields)])
      commonFilledPos = allPossiblePos.copy ()
      commonCrossPos = allPossiblePos.copy ()
      stepper.ResetLeft ()
      # with the resetted stepper we have all init positions and must check if it is a valid position.
      # It is valid, if all filledIndis is a subset of the current filled position set and
      #  crossIndis is a subset of the current cross position set
      if filledIndis.issubset (stepper.posOfAllBlocks) and crossIndis.issubset (allPossiblePos - stepper.posOfAllBlocks):
         commonFilledPos = stepper.posOfAllBlocks & commonFilledPos  # intersection of both sets
         # we get the positions of the crosses , when taking the difference of all possible positions and the current filled ones
         commonCrossPos  = (allPossiblePos - stepper.posOfAllBlocks) & commonCrossPos

      while stepper.NextStep ():
         posOfAllCross = allPossiblePos - stepper.posOfAllBlocks
         if filledIndis.issubset (stepper.posOfAllBlocks) and crossIndis.issubset (posOfAllCross):
            commonFilledPos = stepper.posOfAllBlocks & commonFilledPos  # intersection of both sets
            commonCrossPos  = posOfAllCross & commonCrossPos

      return commonFilledPos, commonCrossPos



   def FillFieldsWithPresets (self, procField: dict, useRows = True):
      result = {}
      # wether we want to use the rows or the columns for calculating the permutation we define a 
      lineStepper = self.stepperRows if useRows else self.stepperCols 

      for iToTake, stepper in enumerate (lineStepper):
         # Get a set of indices, where a cross and a bock is set, for the line to be under investigation
         crossIndis = set ()
         filledIndis = set ()
         for (col, row), attr in procField.items ():
            i = row if useRows else col
            j = col if useRows else row
            if i != iToTake: continue  # we only get entries in our row (col) we want to analyse. 
            # nb can be a dict of dict, or just a dict of state values:
            if  isinstance (attr, dict): state = attr ['state']
            else: state = attr
            # the column j (row j) is the index of the row i (col i) block array
            if state == ClBlock.FILLED: filledIndis.add (j)
            elif state == ClBlock.CROSS: crossIndis.add (j)
            # if attr ['state'] == ClBlock.FILLED: filledIndis.add (j)
            # elif attr ['state'] == ClBlock.CROSS: crossIndis.add (j)

         # if no crosses and no filled blocks are in the current row/col,
         # we will find no further blocks and crosses and can continue
         if not crossIndis and not filledIndis: continue  
         stepper.UpdateAllowedPositions (crossIndis)
         commonFilledPos, commonCrossPos = self.FillLineWithPresets (stepper, crossIndis, filledIndis)
         # the member of the returned sets are the column (row) position where to fill a cross / block
         # The already known blocks and crosses are also part of the returned sets. These member can be deleted
         for i in (commonFilledPos - filledIndis): 
            pos = (i, iToTake) if useRows else (iToTake, i)
            result [pos] = ClBlock.FILLED
         for i in (commonCrossPos - crossIndis): 
            pos = (i, iToTake) if useRows else (iToTake, i)
            result [pos] = ClBlock.CROSS

         pass

      return result

   #ffff00
   def NonogramSolver (self):
      startTime = time.time ()
      nonoSize = len (self.rowBlocks) * len (self.colBlocks)

      solvedFields = {}  # corresponds to the processedFields dict in Nonogram_Game.py, without 'pos' and without 'mode'
      autoFillData = self.FillObviousFields ()
      # the obvious fields are all filled blocks
      for pos in autoFillData:
         solvedFields [pos] =  ClBlock.FILLED

      if self.DEBUGMODE: 
         print (f'{self.s2h.human_time_duration(time.time ()-startTime)} for filling overlapped; {len (solvedFields)} of {nonoSize}') 
      # the nonogram is solved, when the all fields are processed: length of solvedFields == requiredLength
      requiredLength = len (self.rowBlocks) * len (self.colBlocks)
      # now we call alternating FillFieldsWithPresets, once for the rows and once for the coulumns
      startLen = len (solvedFields)
      while True:
         # get new processed fields using all rows
         autoFillData = self.FillFieldsWithPresets (solvedFields)
         solvedFields.update (autoFillData)
         if self.DEBUGMODE: 
            print (f'{self.s2h.human_time_duration(time.time ()-startTime)} for filling rows; {len (solvedFields)} of {nonoSize}') 

         if len (solvedFields) == requiredLength: break

         # now get new processed fields using all columns
         autoFillData = self.FillFieldsWithPresets (solvedFields, False)
         solvedFields.update (autoFillData)
         if self.DEBUGMODE: 
            print (f'{self.s2h.human_time_duration(time.time ()-startTime)} for filling cols; {len (solvedFields)} of {nonoSize}') 
         if len (solvedFields) == requiredLength: break
         # It may happen, that the nonogram connot be solved. This happens, if after a complete loop the length of the
         # solvedFields has not changed. Then we must exit from the loop
         if len (solvedFields) == startLen: break
         startLen = len (solvedFields)
      print (time.time ()-startTime)
      return len (solvedFields) == requiredLength, solvedFields

               
if __name__ == "__main__":
   from Nonogram_Game import NonogramGame as noG

   ret, rB, cB, pF = noG.ReadNonogramFromFile ('Nono_Vogel.nos')

   
   pass