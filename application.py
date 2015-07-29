version = '0.1'
devel = False
compress = False
add_to_site = []
update_url = ''

import wx, os, json
from confmanager import ConfManager
name = 'oht'
url = 'None'
description = 'Oht (One-Handed Typing) is an app which allows you to type using only one hand.\n\nGreat for lazy people, smokers, alcoholics and people with limited physical movement.'
vendor_name = 'Software Metropolis'
developers = ['Chris Norman']

info = wx.AboutDialogInfo()
info.SetName(name)
info.SetDescription(description)
info.SetVersion(version)
info.SetDevelopers(developers)

directory = os.path.join(os.path.expanduser('~'), '.%s' % name)
if not os.path.isdir(directory):
 os.mkdir(directory)

special_keys = {
 u'?': u'/',
 u'!': u'1',
 u'"': u'2',
 u'$': u'4',
 u'%': u'5',
 u'^': u'6',
 u'&': u'7',
 u'*': u'8',
 u'(': u'9',
 u')': u'0',
 u'|': u'\\',
 u'@': u'`',
 u'~': u"'",
 u'<': u',',
 u'>': u'.',
 u'{': u'[',
 u'}': u']',
 u'+': u'=',
 u'_': u'-',
 u':': u';',
}

class App(wx.App):
 """Overrides MainLoop to save the configuration."""
 def MainLoop(self, *args, **kwargs):
  l = super(App, self).MainLoop(*args, **kwargs)
  j = {}
  j['config'] = config.get_dump()
  j['modes'] = {}
  for m in modes.operation_modes:
   if not modes.system_mode(m) and config.has_section(m.name):
    j['modes'][m.name] = []
    for key, value in m.keys.items():
     j['modes'][m.name].append([key, value])
  j['special_keys'] = special_keys
  with open(config_file, 'w') as f:
   json.dump(j, f, indent = 1)
  return l

app = App(False)
app.SetAppDisplayName('%s (v %s)' % (name, version))
app.SetAppName(name)
app.SetVendorName(vendor_name)
app.SetVendorDisplayName(vendor_name)

from collections import OrderedDict
keys = OrderedDict()
keys['numpad1'] = ur".,'/;-=\`"
keys['numpad2'] = u'abc'
keys['numpad3'] = u'def'
keys['numpad4'] = u'ghi'
keys['numpad5'] = u'jkl'
keys['numpad6'] = u'mno'
keys['numpad7'] = u'pqrs'
keys['numpad8'] = u'tuv'
keys['numpad9'] = u'wxyz'
keys['numpad0'] = u' 1234567890'

config = ConfManager('%s Config' % name)
config.add_section('keys', 'Standard Keys')
for k, v in keys.items():
 config.set('keys', k, v, title = 'The keys which can be press with %s' % k, validate = lambda value: None if len(value) else 'Keys cannot be unassigned. To quit the program, press Numpad Minus.')

import modes
from gui import Choice, Frame
import press

config.add_section('settings', 'General Settings')
config.set('settings', 'shift_mode', modes.shift_modes[0], title = 'Shift mode (available with Numpad Decimal)', control = Choice, kwargs = dict(choices = modes.shift_modes))
config.set('settings', 'operation_mode', modes.operation_modes[0].name, title = 'The current number pad mode (can be changed with Numpad Divide)', control = Choice, kwargs = dict(choices = [x.name for x in modes.operation_modes]))
config.set('settings', 'timeout', 0.5, title = 'The time to wait before sending the desired key', kwargs = dict(digits = 2))
config.set('settings', 'autocapitalise', './1', title = 'The punctuation (without shift) that will trigger autocapitalisation')
config.set('settings', 'reset_mode', True, title = 'Reset the operation mode when the program starts.')

config.add_section('sounds', 'Sound Preferences')
config.set('sounds', 'keyboard', True, title = 'Play a sound when a key is pressed.')
config.set('sounds', 'capslock', True, title = 'Play a sound when a letter or symbol was capitalised')

keys = {}
for n, k in enumerate(config.options('keys') + ['divide', 'multiply', 'subtract', 'add', 'DECIMAL']):
 keys[n] = k

frame = Frame(None, title = '%s Main Frame' % name)

from confmanager.parser import parse_json
config_file = os.path.join(directory, 'config.json')
if os.path.isfile(config_file):
 with open(config_file, 'r') as f:
  try:
   j = json.load(f)
   for k, v in j.get('special_keys', {}).items():
    special_keys[k] = v
   parse_json(config, j['config'])
   for mode_name, mode_keys in j.get('modes', {}).items():
    actual_mode_keys = OrderedDict()
    for key_name, key_value in mode_keys:
     actual_mode_keys[key_name] = key_value
    modes.operation_modes.append(modes.Mode(mode_name, actual_mode_keys, add = True))
  except MemoryError as e:
   wx.MessageBox('While loading the configuration file %s: %s. Continuing with application defaults.' % (config_file, e.message), 'Error in Configuration')
config.set('settings', 'operation_mode', modes.operation_modes[0].name if config.get('settings', 'reset_mode') else config.get('settings', 'operation_mode'))

if __name__ == '__main__':
 config.get_gui().Show(True)
 app.MainLoop()
