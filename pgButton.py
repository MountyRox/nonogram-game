import pygame as pg

class clButton (pg.sprite.Sprite):
  def __init__(self, screen, imageEnabled, imageDisabled, pos, infoText, enabled = True, changeImageWithEnable = True):
    super().__init__()
    self.screen = screen
    self.image_e = imageEnabled
    self.image_d = imageDisabled
    self.enabled = enabled
    self.changeImageWithEnable = changeImageWithEnable
    self.infoText = infoText
    self.hovered = False
    self.hoverStart = 0
    self.wasClicked = False  # is true as long hovered is true after a mouse click (left or right)
    self.image = self.image_e if enabled else self.image_d
    self.rect = self.image.get_rect()
    self.rect.topleft = pos
    
  def SetEnabled(self, enabled):
    self.enabled = enabled
    if self.changeImageWithEnable:
      self.image = self.image_e if self.enabled else self.image_d 

  def SetEnabledImage(self, setEnabled):
    self.image = self.image_e if setEnabled else self.image_d 

  def WasClicked (self, event):
    if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP:
      self.wasClicked = self.hovered
    if self.wasClicked: print (self.rect.topleft)
    
  def check_hover(self):
    hit = self.rect.collidepoint(pg.mouse.get_pos())
    if not self.hovered and hit: # True if we hit the very first time
      self.hoverStart = pg.time.get_ticks()
    self.hovered = hit
    if not hit: self.wasClicked = False

  def DrawInfoText (self):
    if self.hovered and self.enabled and  (pg.time.get_ticks() - self.hoverStart) > 500 and not self.wasClicked: 
    #if self.hovered and self.enabled and  (pg.time.get_ticks() - self.hoverStart) > 500 and (pg.time.get_ticks() - self.hoverStart) < 1000: 
      txtSurface = pg.font.SysFont('microsoft sans serif', 16).render(self.infoText, True, (0,0,0), pg.Color("white"))
      txtRect = txtSurface.get_rect()
      borderRect = txtSurface.get_rect().inflate (10,10)
      borderRect.topleft = self.rect.midbottom
      #borderRect.move (txtRect.width//2, 0)
      self.screen.fill (pg.Color("white"), borderRect)
      txtRect.center = borderRect.center
      self.screen.blit(txtSurface, txtRect)
      pg.draw.rect(self.screen, pg.Color("black"), borderRect, width=2)

  def update (self):
    self.check_hover ()
    if self.hovered and self.enabled: 
      self.screen.fill (pg.Color ('cadetblue2'), self.rect.inflate(4,4))


