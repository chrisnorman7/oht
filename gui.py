import wx, win32con, application
from press import press, pressHoldRelease, release
from speech import output
from menu import get_menu
from time import time
from string import letters
from threading import Timer
from systray import TrayIcon
from confmanager import NoSectionError
from sound import Sound

class Choice(wx.Choice):
 def SetHelpText(self, *args, **kwargs):
  """This doesn't seem to work..."""
 
 def GetValue(self):
  return self.GetStringSelection()
 
 def SetValue(self, value):
  return self.SetStringSelection(value)

import modes

class Frame(wx.Frame):
 """The OHT main frame."""
 def __init__(self, *args, **kwargs):
  super(Frame, self).__init__(*args, **kwargs)
  self.index = 0 # Where we're at in the current list of keys.
  self.last_key = None # The last key to be pressed.
  self.key_value = None # The value of the key that was pressed.
  self.autocapitalise = False # Prepare to capitalise.
  self.last_key_time = 0.0 # The time the last key was pressed.
  self.all_keys = [] # The keys which have been pressed.
  self.key_timer = None # The time which will write out the next key unless we stop it.
  self.tray_icon = TrayIcon()
  self.Bind(wx.EVT_HOTKEY, self._handle_hotkey)
  for x, y in application.keys.items():
   self.RegisterHotKey(x, 0, getattr(win32con, 'VK_%s' % y.upper()))
  self.Bind(wx.EVT_CLOSE, self.on_close)
 
 def _handle_hotkey(self, event):
  """Handle the resulting hotkey."""
  self.handle_hotkey(application.keys[event.GetId()])
 
 def handle_hotkey(self, key):
  """Does the actual handling in a platform-independant way."""
  if self.key_timer:
   self.key_timer.cancel()
  key = key.lower()
  mode = modes.operation_modes[[x.name for x in modes.operation_modes].index(application.config.get('settings', 'operation_mode'))]
  if key == 'subtract':
   get_menu()
  elif key in ['divide', 'decimal']:
   modes.switch_mode({'divide': 'operation', 'decimal': 'shift'}[key])
  elif key == 'add':
   if mode == modes.MODE_OPERATION_STANDARD:
    press('backspace')
   else:
    press(application.config.get(mode.name, key, 'alt'))
  elif key == 'multiply':
   self.press_current_key()
  else:
   if mode == modes.MODE_OPERATION_NUMBERS: # Pass numbers straight through.
    press(key[-1])
   elif mode == modes.MODE_OPERATION_STANDARD:
    keys = [] # The keys to send as args to press.press.
    if key == self.last_key:
     self.index += 1
    else:
     self.press_current_key()
     self.index = 0
    possible_keys = application.config.get('keys', key)
    if self.index >= len(possible_keys):
     self.index = 0
    self.key_value = possible_keys[self.index]
    if self.key_value == ' ': # A space must be converted before sending.
     self.key_value = 'spacebar'
    output.output(self.key_value)
   else:
    self.key_value = application.config.get(mode.name, key)
    self.press_current_key()
  self.last_key = key
  t = time()
  self.key_timer = Timer(application.config.get('settings', 'timeout'), self.press_current_key, args = [t])
  self.key_timer.start()
  self.last_key_time = t
 
 def press_current_key(self, t = None):
  """Push the current key."""
  if not t or time() - t >= application.config.get('settings', 'timeout'):
   try:
    k = self.key_value
    self.key_value = None
    self.last_key = None
    self.last_key_time = None
   except wx.PyDeadObjectError:
    return # The frame has been deleted.
   if k:
    if application.config.get('sounds', 'keyboard'):
     s = Sound('type')
     s.Play()
    keys = []
    try:
     shift = modes.shift_modes.index(application.config.get('settings', 'shift_mode'))
    except ValueError: # The value got mangled.
     shift = 0
     application.config.set('settings', 'shift_mode', modes.shift_modes[0])
    if shift != modes.MODE_SHIFT_CAPSLOCK:
     application.config.set('settings', 'shift_mode', modes.shift_modes[0])
    if shift in [modes.MODE_SHIFT_UPPER, modes.MODE_SHIFT_CAPSLOCK] or (self.autocapitalise and k in letters):
     if application.config.get('sounds', 'capslock'):
      s = Sound('capslock')
      s.Play()
     keys.insert(0, 'shift')
    elif shift == modes.MODE_SHIFT_CTRL: # Control key.
     keys.insert(0, 'ctrl')
    elif shift == modes.MODE_SHIFT_ALT:
     keys.insert(0, 'alt')
    keys.append(k)
    if k in application.config.get('settings', 'autocapitalise'):
     self.autocapitalise = True
    elif k == 'spacebar':
     self.autocapitalise = self.autocapitalise
    elif k in application.special_keys:
     keys = ['shift', application.special_keys[k]]
    else:
     self.autocapitalise = False
    self.all_keys += keys
    for item in self.all_keys:
     try:
      release(item)
     except KeyError:
      pass # Invalid character.
    self.all_keys = []
    try:
     pressHoldRelease(*keys)
    except KeyError as e:
     wx.MessageBox('Failed to type character: %s. Consider adding it to special keys.' % e.message, 'Error')
 
 def on_close(self, event):
  """Close and Destroy everything that needs to be gotten rid of."""
  self.tray_icon.Destroy()
  event.Skip()