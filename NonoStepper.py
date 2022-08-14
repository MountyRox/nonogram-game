
na: list  # only for visualisation of step performing

#################################################################################
# definition of dataclass dcBlock  #ffff00
#################################################################################
class dcBlock:
   global na
   def __init__(self, minLeftPos, maxRightPos, curPos, length, hasSucc = True):
      self.__minLeftPos = minLeftPos    # minimal allowed left position of block regarding first blockelement
      self.maxRightPos = maxRightPos  # maximal allowed right position of block regarding first blockelement
      self.curPos = curPos            # current position of first blockelement
      self.length = length            # length of block
      self.hasSucc = hasSucc
      # A set of position indices of the blocks
      self.posSet = set ([i for i in range (self.curPos, self.curPos+self.length)])

   def StepRight (self):
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
      self.posSet = set ([i for i in range (self.curPos, self.curPos+self.length)])
#################################################################################
# end of dataclass dcBlock
#################################################################################


#################################################################################
# definition of dataclass dcRowBlocks  #ff00ff
#################################################################################
class dcRowBlocks:

   def __init__(self, blockList : list, noFields: int):
      # Create all blocks of row index self.iRow.  All blocks on the left side is the starting configuration
      # Get the preset block values from nonogram input out of rowBlocks
      self.blockList = blockList
      self.noFields = noFields
      self.blocksInLine = []
      self.posOfAllBlocks = set ()
      
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
   from Nonogram_Game import NonogramGame as noG


   def helperPrint (posOfAllBlocks, count):
      s = [chr(9608) if i in posOfAllBlocks else '_' for i in range (count)]
      print ("".join([str(i) for i in s]))



   ret, rB, cB, pF = noG.ReadNonogramFromFile ('Nono_Vogel.nob')
   na =  [0] * len(cB)

   dcRowI = dcRowBlocks (rB [8], len(cB))
   helperPrint (dcRowI.posOfAllBlocks, len(cB))
   while dcRowI.NextStep ():
      helperPrint (dcRowI.posOfAllBlocks, len(cB))

   pass