from collections import deque, namedtuple
from enum import Enum

EnUndoAction = Enum ('EnUndoAction', 'SINGLE RED2BW CHRMARK AUTOFILLOBV')

class clUndo ():
   Entry = namedtuple ('Entry', 'action data dataStruct')
   UndoData = namedtuple ('UndoData', 'pos oldState')

   def __init__(self) -> None:
      self.undo = deque ()
      self.redo = deque ()


   def Append (self, action, data, dataStruct):
      self.undo.append (self.Entry (action, data, dataStruct))


   def _un_redo (self, fromStack, toStack):
      action, data, dataStruct = fromStack.pop ()
      if action == EnUndoAction.SINGLE:
         pos, state, mode = data
         s, m = (list (dataStruct [pos].values()))[1:]
         toStack.append (self.Entry (action, [pos, s, m], dataStruct))
         (dataStruct [pos])['state'] = state
         (dataStruct [pos])['mode'] = mode

      elif action == EnUndoAction.RED2BW:
         redoData = []
         for pos, state, mode in data:
            s, m = (list (dataStruct [pos].values()))[1:]
            redoData.append ([pos, s, m])
            (dataStruct [pos])['state'] = state
            (dataStruct [pos])['mode'] = mode
         toStack.append (self.Entry (action, redoData, dataStruct))
            
      elif action == EnUndoAction.AUTOFILLOBV:
         redoData = []
         for pos, state, mode in data:
            s, m = (list (dataStruct [pos].values()))[1:]
            redoData.append ([pos, s, m])
            (dataStruct [pos])['state'] = state
            (dataStruct [pos])['mode'] = mode
         toStack.append (self.Entry (action, redoData, dataStruct))
            
      elif action == EnUndoAction.CHRMARK:
         state, mode = data
         toStack.append (self.Entry (action, [dataStruct.state, dataStruct.mode], dataStruct))
         dataStruct.state = state
         dataStruct.mode = mode

      else:
         print (f'Fehler: Unbekannter Action Typ bei Undo: action = {action}')
         return False

      return True

   def Undo (self):
      if len (self.undo) == 0: return False
      return (self._un_redo (self.undo, self.redo))   
      
   def Redo (self):
      if len (self.redo) == 0: return False
      return (self._un_redo (self.redo, self.undo))

   def CanUndo (self):
      return len (self.undo)   
      
   def CanRedo (self):
      return len (self.redo)