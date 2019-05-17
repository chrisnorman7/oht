import os
import wx


class Sound(wx.Sound):
    def __init__(self, filename):
        """Automatically adds the sounds directory and .wav."""
        super().__init__(os.path.join('sounds', filename + '.wav'))
