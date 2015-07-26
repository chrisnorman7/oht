import wx, os
class Sound(wx.Sound):
 def __init__(self, filename):
  """Automatically adds the sounds directory and .wav."""
  super(Sound, self).__init__(os.path.join('sounds', filename + '.wav'))
