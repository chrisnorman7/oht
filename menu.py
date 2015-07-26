import wx, application
from collections import OrderedDict
import modes
class Menu(wx.Menu):
 """The application popup menu."""
 def __init__(self):
  super(Menu, self).__init__()
  items = OrderedDict()
  items[wx.ID_ABOUT] = ['&About', lambda event: wx.AboutBox(application.info)]
  items[wx.ID_PREFERENCES] = ['&Preferences', lambda event: application.config.get_gui().Show(True)]
  items[wx.NewId()] = ['Add A &Mode', self.add_mode]
  items[wx.NewId()] = ['&Delete A Mode', self.delete_mode]
  items[wx.ID_EXIT] = ['&Quit', lambda event: application.frame.Close(True)]
  for id, (title, func) in items.items():
   self.Bind(wx.EVT_MENU, func, self.Append(id, title))
 
 def add_mode(self, event):
  """Create a new mode."""
  dlg = wx.TextEntryDialog(application.frame, 'Enter a name for your new mode', 'Create A Mode')
  if dlg.ShowModal() == wx.ID_OK:
   name = dlg.GetValue()
   modes.operation_modes.append(modes.Mode(name))
   dlg.Destroy()
 
 def delete_mode(self, event):
  """Delete a mode."""
  pass

def get_menu():
 """Get the menu."""
 f = wx.PopupWindow(application.frame)
 f.Show(True)
 m = Menu()
 f.PopupMenu(m)
 f.Close(True)
 f.Destroy()
 m.Destroy()
 application.frame.Show(False)
