"""The possible modes."""

operation_modes = []
import application
from press import VK_CODE as VC

allowed_keys = VC.keys()
from collections import OrderedDict
from speech import output
from gui import Choice

def add_to_config(m):
 """Add m to the configuration manager."""
 valid_key = lambda v: None if v in allowed_keys else 'That key is not valid: %s.' % v
 application.config.add_section(m.name)
 for spec, key in m.keys.items():
  application.config.set(m.name, spec, key, title = 'The key to be sent when the %s key is pressed' % spec, control = Choice, kwargs = dict(choices = allowed_keys), validate = valid_key)

class Mode(object):
 """Allows the storage of key sets."""
 def __init__(self, name, keys = None, add = True):
  """
  name - The name of this mode.
  keys - A dictionary of spec:key pairs, where spec is like 'numpad1', or 'add', and key is like 'alt' or 'a'.
  add - If True, this mode will be added to the configuration manager.
  """
  if keys == None:
   keys = operation_modes[-1].keys
  self.name = name
  self.keys = keys
  if add and not application.config.has_section(name):
   add_to_config(self)

operation_modes = [
 Mode('SMS Typing', keys = {}, add = False),
 Mode('Number Entry', keys = {}, add = False)
] # All the possible modes.
MODE_OPERATION_STANDARD = operation_modes[0] # One-handed typing.
MODE_OPERATION_NUMBERS = operation_modes[1] # Effective bypass.

alt_keys = OrderedDict()
alt_keys['numpad1'] = 'end'
alt_keys['numpad2'] = 'down_arrow'
alt_keys['numpad3'] = 'page_down'
alt_keys['numpad4'] = 'left_arrow'
alt_keys['numpad5'] = 'enter'
alt_keys['numpad6'] = 'right_arrow'
alt_keys['numpad7'] = 'home'
alt_keys['numpad8'] = 'up_arrow'
alt_keys['numpad9'] = 'page_up'
alt_keys['numpad0'] = 'esc'
alt_keys['add'] = 'alt'
MODE_OPERATION_TEXT = Mode('Text Editing', alt_keys)
operation_modes.append(MODE_OPERATION_TEXT)

MODE_SHIFT_LOWER = 0 # Lower case.
MODE_SHIFT_UPPER = 1 # Upper case.
MODE_SHIFT_CAPSLOCK = 2 # Capslock
MODE_SHIFT_CTRL = 3 # The control key should be added to the current key.
MODE_SHIFT_ALT = 4 # The alt key should be added to the current key.

shift_modes = [
 'Lower case',
 'Upper case',
 'Capslock',
 'Control on',
 'Alt on'
]

def switch_mode(mode = 'operation'):
 """Switch the mode."""
 modes = globals().get('%s_modes' % mode)
 if mode == 'operation':
  modes = [x.name for x in modes]
 m = modes.index(application.config.get('settings', '%s_mode' % mode)) + 1
 if m == len(modes):
  m = 0
 application.config.set('settings', '%s_mode' % mode, modes[m])
 output.output(modes[m])

def system_mode(mode):
 """Returns True if the given mode was added by the system."""
 return mode in [MODE_OPERATION_STANDARD, MODE_OPERATION_NUMBERS, MODE_OPERATION_TEXT]

def get_current_mode():
 """Returns the current operation mode."""
 return operation_modes[[x.name for x in operation_modes].index(application.config.get('settings', 'operation_mode'))]
