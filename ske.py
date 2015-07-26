"""SKE (Special Key Editor)."""

import wx, application, sys, press

class SKEFrame(wx.Frame):
 """Used to edit the special character list."""
 def __init__(self, *args, **kwargs):
  super(SKEFrame, self).__init__(*args, **kwargs)
  self.current_key = None # The current key.
  p = wx.Panel(self)
  s = wx.BoxSizer(wx.VERTICAL)
  self.chars = wx.ListCtrl(p, style = wx.LC_REPORT)
  self.chars.Bind(wx.EVT_LIST_ITEM_SELECTED, self.select_item)
  self.chars.InsertColumn(0, 'Character Name', width = 20)
  self.chars.InsertColumn(1, 'Unshifted Value', width = 20)
  self.init_keys()
  s.Add(self.chars, 1, wx.GROW)
  s1 = wx.BoxSizer(wx.HORIZONTAL)
  s1.Add(wx.StaticText(p, label = 'Key &Name'), 1, wx.GROW)
  self.key_name = wx.TextCtrl(p)
  self.key_name.SetMaxLength(1)
  s1.Add(self.key_name, 0, wx.GROW)
  self.key_value = wx.Choice(p, choices = [x.title() for x in press.VK_CODE])
  s1.Add(self.key_value, 1, wx.GROW)
  s.Add(s1, 0, wx.GROW)
  s2 = wx.BoxSizer(wx.HORIZONTAL)
  a = wx.Button(p, label = '&Apply')
  a.Bind(wx.EVT_BUTTON, self.do_apply)
  s2.Add(a, 1, wx.GROW)
  d = wx.Button(p, label = '&Delete')
  d.Bind(wx.EVT_BUTTON, self.delete_char)
  s2.Add(d, 1, wx.GROW)
  s.Add(s2, 0, wx.GROW)
  s3 = wx.BoxSizer(wx.HORIZONTAL)
  b = wx.Button(p, label = '&Create')
  b.Bind(wx.EVT_BUTTON, self.do_new)
  s3.Add(b, 1, wx.GROW)
  c = wx.Button(p, label = 'Close &Window')
  c.SetDefault()
  c.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
  s3.Add(c, 1, wx.GROW)
  s.Add(s3, 0, wx.GROW)
  p.SetSizerAndFit(s)
  self.Raise()
 
 def init_keys(self):
  """Populate the list."""
  self.chars.DeleteAllItems()
  for x, y in application.special_keys.items():
   self.add_char(x, y)
 
 def add_char(self, x, y):
  """Add a new char to the list."""
  self.chars.Append([x, y])
 
 def select_item(self, event):
  """Edit the currently selected character."""
  try:
   key = application.special_keys.keys()[self.get_current_key()]
  except IndexError:
   key = None # A new key has been created.
  self.current_key = key
  self.key_name.SetValue(key if key else '')
  if key:
   self.key_value.SetStringSelection(application.special_keys[key])
  else:
   self.key_value.SetSelection(0)
 
 def get_current_key(self):
  """Get the currently focused key."""
  if sys.platform == 'darwin':
   return self.chars.GetSelection().GetID() - 1
  else:
   return self.chars.GetFocusedItem()
 
 def do_apply(self, event):
  """Apply the edited char."""
  key = self.current_key
  if key:
   del application.special_keys[key]
  application.special_keys[self.key_name.GetValue()] = self.key_value.GetStringSelection()
  self.init_keys()
 
 def do_new(self, event):
  """Add a new entry to the table."""
  self.init_keys()
  self.add_char('', '')
  pos = len(application.special_keys)
  if sys.platform == 'darwin':
   self.chars.SelectRow(pos)
  else:
   self.chars.Select(pos)
   self.chars.Focus(pos)
  self.select_item(event)
 
 def delete_char(self, event):
  """Delete a char from the table."""
  key = self.get_current_key()
  if key == -1:
   return wx.Bell() # The user hasn't selected a column.
  try:
   try:
    key = application.special_keys.keys()[key]
   except IndexError:
    return self.init_keys()
   if wx.MessageBox('Are you sure you want to remove the %s key?' % key, 'Are You Sure', style = wx.YES_NO) == wx.YES:
    del application.special_keys[key]
    self.init_keys()
  except KeyError:
   return wx.MessageBox('Inexplicably, that key has since vanished...', 'Error')
 