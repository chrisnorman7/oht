"""Bind any key."""

import os
from threading import Thread
from winsound import PlaySound

import wx
from wx.lib.intctrl import IntCtrl

from attr import attrs, attrib
from keyboard import write
from wx.lib.sized_controls import SizedFrame
from yaml import load, dump, FullLoader

from press import vk_codes
from speech import speak


class SoundThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_running = True
        self.sounds = []

    def run(self):
        """Start the thread."""
        while self.app_running:
            if self.sounds:
                PlaySound(self.sounds.pop(-1), 0)

    def queue_sound(self, filename):
        """Queue another sound."""
        self.sounds.append(filename)

    def stop(self):
        """Stop the thread ready for joining."""
        self.app_running = False


app = wx.App()
sounds = SoundThread()
filename = os.path.join(wx.GetHomeDir(), 'oht.yaml')
frame = SizedFrame(None, title='Onehanded Typing')
timer = wx.Timer(frame)
panel = frame.GetContentsPane()
panel.SetSizerType('form')


class state:
    """Application state."""

    last_name = None  # The last hotkey that was pressed.
    last_alternative = None
    alternative_index = -1


@attrs
class Alternative:
    """An alternative to a hotkey."""

    name = attrib()
    keys = attrib()


def bind(control, event_type):
    """Bind a function to a control, using event_type."""

    def inner(func):
        control.Bind(event_type, func)
        return func

    return inner


hotkey_names = []
hotkey_ids = {}
hotkey_alternatives = {}
hotkey_convertions = {}

hotkeys_label = wx.StaticText(panel, label='&Hotkeys')
hotkeys = wx.ListCtrl(panel, style=wx.LC_REPORT)
hotkeys.AppendColumn('VK Code')

alternatives_label = wx.StaticText(panel, label='&Alternatives')
alternatives = wx.ListCtrl(panel, style=wx.LC_REPORT)
alternatives.AppendColumn('Friendly Name')
alternatives.AppendColumn('Keys')

add_alternative_button = wx.Button(panel, label='&New Key')
remove_alternative_button = wx.Button(panel, label='&Delete Key')

register_hotkey_button = wx.Button(panel, label='&Register Hotkey')
unregister_hotkey_button = wx.Button(panel, label='&Unregister Hotkey')
bypass = wx.CheckBox(panel, label='&Bypass')
interval = IntCtrl(panel, value=500, min=250, max=5000)


@bind(frame, wx.EVT_TIMER)
def on_timer(event):
    """The time is up."""
    press_alternative()


@bind(bypass, wx.EVT_CHECKBOX)
def on_bypass(event):
    """Temporarily unbind all hotkeys."""
    if bypass.GetValue():
        # Let's unbind all hotkeys.
        unbind_hotkeys()
    else:
        # Re-bind hotkeys.
        bind_hotkeys()


def unbind_hotkeys():
    """Unbind all hotkeys."""
    for id in hotkey_ids.values():
        frame.UnregisterHotKey(id)


def bind_hotkeys():
    """Bind all hotkeys."""
    for name, id in hotkey_ids.items():
        frame.RegisterHotKey(id, 0, vk_codes[name])


def press_alternative():
    """Press some keys if state hasn't changed."""
    sounds.queue_sound(os.path.join('sounds', 'type.wav'))
    unbind_hotkeys()
    keys = state.last_alternative.keys
    write(keys)
    state.last_name = None
    state.alternative_index = -1
    state.last_alternative = None
    bind_hotkeys()


@bind(frame, wx.EVT_HOTKEY)
def on_hotkey(event):
    """A hotkey has been pressed."""
    name = hotkey_convertions[event.GetRawKeyCode()]
    alternatives = hotkey_alternatives.get(name, None)
    if alternatives is None:
        return wx.Bell()
    if state.last_name == name:
        # Move through the list.
        state.alternative_index += 1
        if state.alternative_index >= len(alternatives):
            state.alternative_index = 0
    else:
        if state.last_name is not None:
            # The user is switching keys.
            timer.Stop()
            press_alternative()
        state.last_name = name
        state.alternative_index = 0  # Go back to the start.
    alternative = alternatives[state.alternative_index]
    state.last_alternative = alternative
    speak(alternative.name)
    timer.Start(interval.GetValue(), oneShot=True)


def message(message, caption):
    """Show a message."""
    return wx.MessageBox(message, caption, style=wx.ICON_EXCLAMATION)


def get_key():
    """Get a key with a dialog."""
    keys = sorted(vk_codes.keys())
    with wx.SingleChoiceDialog(
        panel, 'Select a keycode', 'Keycodes', choices=keys
    ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            index = dlg.GetSelection()
            return keys[index]


def register_hotkey(name):
    """Given a name and a list of entries, registers a new hotkey."""
    value = vk_codes[name]
    hotkey_convertions[value] = name
    id = wx.NewIdRef().GetId()
    res = frame.RegisterHotKey(id, 0, value)
    if res:
        hotkey_ids[name] = id
        index = hotkeys.Append((name,))
        hotkeys.SetItemData(index, len(hotkey_names))
        hotkey_names.append(name)
    return res


def register_alternative(hotkey, name, keys):
    """Add an alternative."""
    alt = Alternative(name, keys)
    hotkey_alternatives.setdefault(hotkey, []).append(alt)
    return alt


def add_alternative(alt):
    """Add an alternative to the alternatives list."""
    alternatives.Append((alt.name, alt.keys))


@bind(hotkeys, wx.EVT_LIST_ITEM_DESELECTED)
def on_hotkey_unselected(event):
    """A hotkey was unselected, clear the alternatives list."""
    alternatives.DeleteAllItems()


@bind(hotkeys, wx.EVT_LIST_ITEM_SELECTED)
def on_hotkey_selected(event):
    """A hotkey was selected, populate the alternatives list."""
    index = hotkeys.GetFocusedItem()
    if index != -1:
        name = hotkey_names[index]
        for alternative in hotkey_alternatives.get(name, []):
            add_alternative(alternative)


@bind(register_hotkey_button, wx.EVT_BUTTON)
def on_register(event):
    """Register a new hotkey."""
    name = get_key()
    if name is not None:
        if not register_hotkey(name):
            message('Failed to register hotkey.', 'Error')


@bind(unregister_hotkey_button, wx.EVT_BUTTON)
def on_unregister(event):
    """Unregister a hotkey."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    name = hotkey_names[index]
    del hotkey_names[index]
    hotkeys.DeleteItem(index)
    alternatives.DeleteAllItems()
    if name in hotkey_alternatives:
        del hotkey_alternatives[name]
    id = hotkey_ids.pop(name)
    if frame.UnregisterHotKey(id):
        message('Hotkey unregistered.', 'Success')
    else:
        message('Failed to unregister hotkey.', 'Error')


@bind(add_alternative_button, wx.EVT_BUTTON)
def on_add_alternative(event):
    """Add an alternative."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    keys = wx.GetTextFromUser('Enter keys to send', 'Keys')
    if keys:
        name = wx.GetTextFromUser(
            'Enter a friendly name for this key', caption='Key Name',
            default_value=keys
        )
        if name:
            hotkey = hotkey_names[index]
            alt = register_alternative(hotkey, name, keys)
            add_alternative(alt)


@bind(remove_alternative_button, wx.EVT_BUTTON)
def on_remove_alternative(event):
    """Remove an alternative."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    name = hotkey_names[index]
    index = alternatives.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    del hotkey_alternatives[name][index]
    alternatives.DeleteItem(index)


if __name__ == '__main__':
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = load(f, Loader=FullLoader)
        if data is not None:
            for hotkey in data.get('hotkeys', []):
                register_hotkey(hotkey)
                for entry in data.get('alternatives', {}).get(hotkey, []):
                    register_alternative(hotkey, entry['name'], entry['keys'])
    frame.Show(True)
    frame.Maximize()
    sounds.start()
    app.MainLoop()
    sounds.stop()
    sounds.join()
    data = dict(hotkeys=[], alternatives={})
    for name in hotkey_names:
        data['hotkeys'].append(name)
        data['alternatives'][name] = []
        for a in hotkey_alternatives.get(name, []):
            data['alternatives'][name].append(dict(name=a.name, keys=a.keys))
    with open(filename, 'w') as f:
        dump(data, stream=f)
