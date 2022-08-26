@bbsplugin
class NFSU2Hook:
  def onLoad (self):
    self.makeCall(0x005814E0, self.s_BBS.mainLoopAddr)
