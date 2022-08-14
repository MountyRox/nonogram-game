import pygame

class ClBlock:
   FILLED = 'F' 
   CROSS = 'C'
   UNKNOWN = 'U'
   NORMAL = 'N'
   TRIAL = 'T'

   def __init__ (self, length, rectOnScreen = pygame.Rect((0,0), (10,10)), *, state = UNKNOWN, mode = NORMAL):
      self.length = length
      self.rectOnScreen = rectOnScreen
      self.state = state
      self.mode = mode


   def set_state (self, state):
      if state != ClBlock.FILLED and state != ClBlock.CROSS and state != ClBlock.UNKNOWN:
         raise ValueError('The state must be ClBlock.FILLED or ClBlock.CROSS or ClBlock.UNKNOWN')
      self._state = state

   def get_state (self):
      return self._state

   state = property(fget=get_state, fset=set_state)      


   def set_mode (self, mode):
      if mode != ClBlock.NORMAL and mode != ClBlock.TRIAL:
         raise ValueError('The mode must be ClBlock.NORMAL or ClBlock.TRIAL')
      self._mode = mode

   def get_mode (self):
      return self._mode

   mode = property(fget=get_mode, fset=set_mode)  

   def WasClicked (self, pos):
      return self.rectOnScreen.collidepoint (pos)    
