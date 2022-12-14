
from typing import Union, List
import math

import NonoBlock


#################################################################################
# definition of dataclass dcBlock  #ffff00
#################################################################################
class dcBlock:
   def __init__(self, minLeftPos, maxRightPos, curPos, length, hasSucc = True):
      self.__minLeftPos = minLeftPos    
      """Minimal allowed left position of block regarding first blockelement.
      Depends on the current position of the block left to myself   
      """
      self.maxRightPos = maxRightPos 
      """ Maximal allowed right position of block regarding first blockelement. 
      Depends on the current position of the block right to myself      
      """
      self.curPos = curPos            #: current position of first blockelement
      self.length = length            #: length of block
      self.hasSucc = hasSucc
      self.allowedPos = set ()
      """ All allowed positions of block (regarding first blockelement) within the complete line
      """
      self.posSet = set ([i for i in range (self.curPos, self.curPos+self.length)])
      """A set of position indices of the blocks"""

   def SetAllowedPositionsOfBlock (self, allowedPos = set(), *, posMin = 0, posMax = 1):
      if allowedPos: self.allowedPos = allowedPos
      else: self.allowedPos = {*range (posMin, posMax+1+self.length)}

   def RemoveAllowedPositions (self, posToRemove: Union[int, set]):
      if isinstance (posToRemove, int): 
         self.allowedPos = self.allowedPos - {posToRemove}
      else:
        self.allowedPos = self.allowedPos - posToRemove

      
   def StepRight (self):
      i = self.curPos + 1
      #s = {*range(i, i+self.length)}.issubset (self.allowedPos)
      while i <= self.maxRightPos and not {*range(i, i+self.length)}.issubset (self.allowedPos): i += 1
      if i <= self.maxRightPos:
         self.posSet = {*range(i, i+self.length)}
         self.curPos = i
         return True
      else: return False  # we couldn't perform a step

   # TODO: remove
   def _StepRight (self):
      if self.curPos < self.maxRightPos:
         self.posSet.remove (self.curPos)
         self.posSet.add (self.curPos+self.length)
         self.curPos += 1
         return True
      else: return False  # we couldn't perform a step

   def ResetLeft (self):
      # Set all positions to the initial values
      if self.hasSucc: self.maxRightPos = self.__minLeftPos
      else: pass    # the max position was never changed
      self.curPos = self.__minLeftPos
      self.posSet = {*range (self.curPos, self.curPos+self.length)}
#################################################################################
# end of dataclass dcBlock
#################################################################################


#################################################################################
# definition of dataclass dcRowBlocks  #ff00ff
#################################################################################
class dcRowBlocks:

   def __init__(self, blockList : List[NonoBlock.ClBlock], noFields: int, lockedPos = set()):
      # Create all blocks of row index self.iRow.  All blocks on the left side is the starting configuration
      # Get the preset block values from nonogram input out of rowBlocks
      self.noFields = noFields 
      """The length of the line""" 
      self.blocksInLine = []
      """A list of dcBlocks in the line"""
      self.posOfAllBlocks = set ()
      """The null based index of all black fields that are currently set within the line."""
      self.numberPermutations: int
      """The overall number of permutations to distribute all blocks in the line"""
      self.reqNoCrossPerLine: int
      """Defines the required number of crosses which must be set in the line to complete it"""

      iPos = 0  # position index of  block in a row
      for block in blockList:
         #  In init position min, current and max are all the same = iPos
         tmp = dcBlock(iPos, iPos, iPos, block.length)
         self.blocksInLine.append (tmp)
         self.posOfAllBlocks.update(tmp.posSet)
         iPos += block.length + 1

      # The required number of crosses in this line is the length of the line minus the number of required blocks
      self.reqNoCrossPerLine = noFields - len (self.posOfAllBlocks)

      # The last block must get a new max right position and the attribut hasSucc to False 
      self.blocksInLine [-1].maxRightPos = self.noFields - block.length
      self.blocksInLine [-1].hasSucc = False

      # Now we set for each block all the allowed positions considering the positions which are not allowed (lockedPos) .
      self.SetAllowedPosWithinLine (lockedPos)
      self.numberPermutations = self.CalcPermutationsOfRow ()
      
   def CalcPermutations (self, q, k):
      if q <= 1: return 1
      fc = 1
      for i in range (q, q+k): fc *= i
      return int (fc/math.factorial (k))

   def CalcPermutationsOfRow (self):
         k = len (self.blocksInLine)
         q = self.noFields - k + 2 - len (self.posOfAllBlocks) 
         return self.CalcPermutations (q, k)


   def SetAllowedPosWithinLine (self, lockedPos):
      """Sets for each block all the allowed positions. These are all positions (regarding to the first element) the block can
      be placed within its line, from the most left position to the most right position. 
      """
      # When we start, the first block is positioned to the left at position index 0
      posMin = 0
      posMax = self.noFields - sum (block.length + 1 for block in self.blocksInLine) + 1
      for block in self.blocksInLine:
         block.SetAllowedPositionsOfBlock (posMin=posMin, posMax=posMax)
         block.RemoveAllowedPositions (lockedPos)
         posMin += block.length + 1
         posMax += block.length + 1


   def UpdateAllowedPositions (self, lockedPos):
      for block in self.blocksInLine:
         block.RemoveAllowedPositions (lockedPos)

   def EstimateReducedPermutations (self, crossedPos: set, filledPos: set):
      # TODO: here we need an effective algorithm to estimate the numer of permutation
      # with respect to already fix placed crosses and fix placed blocks.
      k = len (self.blocksInLine)
      q = self.noFields - k + 2 - len (self.posOfAllBlocks) - len (crossedPos)
      return self.CalcPermutations (q, k)


   def NextStep (self):
      # When doing a step, we try to move the lowest block first
      for i, block in enumerate (self.blocksInLine):
         if block.StepRight ():
            # after performing a step, all blocks to the left (if there are ones) must be reset to the left
            if i > 0:
               for precBlock in self.blocksInLine [0:i]:
                  precBlock.ResetLeft ()
               # Now we must set the new max right position from the current position of the successor block   
               for j, precBlock in enumerate (self.blocksInLine [0:i]):
                  precBlock.maxRightPos = self.blocksInLine [j+1].curPos - precBlock.length - 1

            # Now lets get all the blocks after step was performed      
            self.posOfAllBlocks = set ()
            for b in self.blocksInLine:
               self.posOfAllBlocks.update (b.posSet)
            return True

      # if we get here, a move was not possible
      return False         

   def ResetLeft (self):
      self.posOfAllBlocks = set ()
      for block in self.blocksInLine:
         block.ResetLeft ()
         self.posOfAllBlocks.update (block.posSet)

#################################################################################
# end of dataclass dcRowBlocks
#################################################################################




if __name__ == "__main__":
   na: list  # only for visualisation of step performing
   s = {3,4,6,7,8,9}
   p = {6,7}
   isIn = p.issubset (s)

   s = {*range(1,9)}
   from Nonogram_Game import NonogramGame as noG
   
   bl = dcBlock (0, 10, 3, 5, True)
   bl.SetAllowedPositionsOfBlock (posMin=2, posMax=6)

   ap = bl.allowedPos

   def helperPrint (posOfAllBlocks, count):
      s = [chr(9608) if i in posOfAllBlocks else '_' for i in range (count)]
      print ("".join([str(i) for i in s]),  end='')



   ret, rB, cB, pF = noG.ReadNonogramFromFile ('Nono_Examples\dive.nob')
   na =  [0] * len(cB)

   dcRowI = dcRowBlocks (rB [10], len(cB))
   helperPrint (dcRowI.posOfAllBlocks, len(cB))
   print (f'{1:>4}')
   i = 2
   while dcRowI.NextStep ():
      helperPrint (dcRowI.posOfAllBlocks, len(cB))
      print (f'{i:>4}')
      i += 1

   pass