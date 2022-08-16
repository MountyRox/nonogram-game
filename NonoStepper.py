
from typing import Union, List
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
      # A set of position indices of the blocks
      self.posSet = set ([i for i in range (self.curPos, self.curPos+self.length)])

   def SetAllAllowedPositions (self, allowedPos = set(), *, posMin = 0, posMax = 1):
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
      self.blockList = blockList
      """A list of NonoBlock.ClBlock in the line. 
      Each ClBlock element holds the attribute of the block"""
      self.noFields = noFields 
      """The length of the line""" 
      self.blocksInLine = []
      """A list of dcBlocks in the line"""
      self.posOfAllBlocks = set ()
      """The null based index of all black fields in the line with length noFields"""

      iPos = 0  # position index of  block in a row
      for block in self.blockList:
         #  In init position min, current and max are all the same = iPos
         tmp = dcBlock(iPos, iPos, iPos, block.length)
         self.blocksInLine.append (tmp)
         self.posOfAllBlocks.update(tmp.posSet)
         iPos += block.length + 1

      # The last block must get a new max right position and the attribut hasSucc to False 
      self.blocksInLine [-1].maxRightPos = self.noFields - block.length
      self.blocksInLine [-1].hasSucc = False

      # Now we set for each block all the allowed positions.
      self.SetAllowedPositions (lockedPos)
      


   def SetAllowedPositions (self, lockedPos):
      """Sets for each block all the allowed positions. These are all positions (regarding to the first element) the block can
      be placed within its line, from the most left position to the most right position. 
      """
      # When we start, the first block is positioned to the left at position index 0
      posMin = 0
      posMax = self.noFields - sum (block.length + 1 for block in self.blocksInLine) + 1
      for block in self.blocksInLine:
         block.SetAllAllowedPositions (posMin=posMin, posMax=posMax)
         block.RemoveAllowedPositions (lockedPos)
         posMin += block.length + 1
         posMax += block.length + 1

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
   bl.SetAllAllowedPositions (posMin=2, posMax=6)

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