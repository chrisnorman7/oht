import wx, application
from menu import get_menu

class TrayIcon(wx.TaskBarIcon):
 def __init__(self, *args, **kwargs):
  super(TrayIcon, self).__init__()
  self.SetIcon(wx.IconFromBitmap(wx.EmptyBitmap(-1, -1)), application.name)
  self.Bind(wx.EVT_TASKBAR_CLICK, lambda event: get_menu())
