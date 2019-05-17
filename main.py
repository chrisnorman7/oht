"""Bind any key."""

import os

from functools import partial

import wx

from attr import attrs, attrib
from keyboard import send
from wx.lib.sized_controls import SizedFrame
from yaml import load, dump, FullLoader

from press import vk_codes
from speech import speak

app = wx.App()
filename = os.path.join(wx.GetHomeDir(), 'oht.yaml')
frame = SizedFrame(None, title='Onehanded Typing')
panel = frame.GetContentsPane()
panel.SetSizerType('form')


class state:
    """Application state."""

    id = -1  # The id of the most recently created hotkey.
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

hotkeys_label = wx.StaticText(panel, label='&Hotkeys')
hotkeys = wx.ListCtrl(panel, style=wx.LC_REPORT)
hotkeys.AppendColumn('VK Code')

alternatives_label = wx.StaticText(panel, label='&Alternatives')
alternatives = wx.ListCtrl(panel, style=wx.LC_REPORT)
alternatives.AppendColumn('Friendly Name')
alternatives.AppendColumn('Keys')

add_alternative = wx.Button(panel, label='&New Key')
remove_alternative = wx.Button(panel, label='&Delete Key')

register = wx.Button(panel, label='&Register Hotkey')
unregister = wx.Button(panel, label='&Unregister Hotkey')


def press_alternative(alternative):
    """Press some keys if state hasn't changed."""
    if state.last_alternative is alternative:
        keys = alternative.keys
        send(keys)
        state.last_name = None
        state.alternative_index = -1
        state.last_alternative = None


def on_hotkey(name, event):
    """A hotkey has been pressed."""
    alternatives = hotkey_alternatives[name]
    state.alternative_index += 1
    if state.last_name == name:
        if state.alternative_index >= len(alternatives):
            state.alternative_index = 0
    else:
        if state.last_name is not None:
            press_alternative(state.last_alternative)
        state.last_name = name
        state.alternative_index = 0  # Go back to the start.
    try:
        alternative = alternatives[state.alternative_index]
    except IndexError:
        return wx.Bell()
    speak(alternative.name)
    state.last_alternative = alternative
    wx.CallLater(0.25, press_alternative, alternative)


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


def register_hotkey(name, keys):
    """Given a name and a list of entries, registers a new hotkey."""
    value = vk_codes[name]
    frame.Bind(wx.EVT_HOTKEY, partial(on_hotkey, name), id=state.id)
    res = frame.RegisterHotKey(state.id, 0, value)
    if res:
        index = hotkeys.Append((name,))
        hotkeys.SetItemData(index, len(hotkey_names))
        hotkey_names.append(name)
        hotkey_ids[name] = state.id
        hotkey_alternatives[name] = keys
        state.id -= 1
    return res


def register_alternative(alt):
    """Add an alternative."""
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
        for alternative in hotkey_alternatives[name]:
            register_alternative(alternative)


@bind(register, wx.EVT_BUTTON)
def on_register(event):
    """Register a new hotkey."""
    name = get_key()
    if name is not None:
        if not register_hotkey(name, []):
            message('Failed to register hotkey.', 'Error')


@bind(unregister, wx.EVT_BUTTON)
def on_unregister(event):
    """Unregister a hotkey."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    name = hotkey_names.pop(index)
    id = hotkey_ids.pop(name)
    hotkeys.DeleteItem(index)
    alternatives.DeleteAllItems()
    del hotkey_alternatives[name]
    frame.Unbind(wx.EVT_HOTKEY, id=id)
    if frame.UnregisterHotKey(id):
        message('Hotkey unregistered.', 'Success')
    else:
        message('Failed to unregister hotkey.', 'Error')


@bind(add_alternative, wx.EVT_BUTTON)
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
            alt = Alternative(name, keys)
            hotkey_alternatives[hotkey_names[index]].append(alt)
            register_alternative(alt)


@bind(remove_alternative, wx.EVT_BUTTON)
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
            for name, alts in data['hotkeys'].items():
                register_hotkey(
                    name, list(
                        Alternative(a['name'], a['keys']) for a in alts
                    )
                )
    frame.Show(True)
    frame.Maximize()
    app.MainLoop()
    data = dict(hotkeys={})
    for name, alternatives in hotkey_alternatives.items():
        data['hotkeys'][name] = []
        for a in alternatives:
            data['hotkeys'][name].append(dict(name=a.name, keys=a.keys))
    with open(filename, 'w') as f:
        dump(data, stream=f)
