import wx, application, modes
from collections import OrderedDict
class Menu(wx.Menu):
 """The application popup menu."""
 def __init__(self):
  super(Menu, self).__init__()
  items = OrderedDict()
  items[wx.ID_ABOUT] = ['&About', lambda event: wx.AboutBox(application.info)]
  items[wx.ID_PREFERENCES] = ['&Preferences', self.show_config]
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
   self.show_config(event)
 
 def delete_mode(self, event):
  """Delete a mode."""
  _modes = [x for x in modes.operation_modes if not modes.system_mode(x)]
  if not _modes:
   return wx.MessageBox('There are no user-defined modes.', 'No Modes Found')
  else:
   dlg = wx.SingleChoiceDialog(application.frame, 'Select a mode to delete', 'Mode Selection', [x.name for x in _modes])
   if dlg.ShowModal() == wx.ID_OK:
    mode = _modes[dlg.GetSelection()]
    if wx.MessageBox('Are you sure you want to delete the %s mode?' % mode.name, 'Are You Sure', style = wx.YES_NO) == wx.YES:
     if application.config.get('settings', 'operation_mode') == mode:
      application.config.set('settings', 'operation_mode', modes.MODE_OPERATION_STANDARD.name)
     application.config.remove_section(mode.name)
     modes.operation_modes.remove(mode)
   dlg.Destroy()
 
 def show_config(self, value):
  """Show the program configuration."""
  application.config.get_gui().Show(True)

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
