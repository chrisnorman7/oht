"""Bind any key."""

import os
from threading import Thread
from winsound import PlaySound

import win32con
import wx

from accessible_output2.outputs.auto import Auto
from attr import attrs, attrib
from keyboard import all_modifiers, send, write
from wx.lib.intctrl import IntCtrl
from wx.lib.sized_controls import SizedFrame
from yaml import load, dump, FullLoader

speech = Auto()


def speak(text):
    """Speak through the default screenreader."""
    return speech.speak(text, interrupt=True)


# Thanks to https://gist.github.com/chriskiehl/2906125 for this code.

vk_codes = {
    'backspace': 0x08,
    'tab': 0x09,
    'clear': 0x0C,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'caps_lock': 0x14,
    'esc': 0x1B,
    'spacebar': 0x20,
    'page_up': 0x21,
    'page_down': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left_arrow': 0x25,
    'up_arrow': 0x26,
    'right_arrow': 0x27,
    'down_arrow': 0x28,
    'select': 0x29,
    'print': 0x2A,
    'execute': 0x2B,
    'print_screen': 0x2C,
    'ins': 0x2D,
    'del': 0x2E,
    'help': 0x2F,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,
    'numpad_0': 0x60,
    'numpad_1': 0x61,
    'numpad_2': 0x62,
    'numpad_3': 0x63,
    'numpad_4': 0x64,
    'numpad_5': 0x65,
    'numpad_6': 0x66,
    'numpad_7': 0x67,
    'numpad_8': 0x68,
    'numpad_9': 0x69,
    'multiply_key': 0x6A,
    'add_key': 0x6B,
    'separator_key': 0x6C,
    'subtract_key': 0x6D,
    'decimal_key': 0x6E,
    'divide_key': 0x6F,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B,
    'F13': 0x7C,
    'F14': 0x7D,
    'F15': 0x7E,
    'F16': 0x7F,
    'F17': 0x80,
    'F18': 0x81,
    'F19': 0x82,
    'F20': 0x83,
    'F21': 0x84,
    'F22': 0x85,
    'F23': 0x86,
    'F24': 0x87,
    'num_lock': 0x90,
    'scroll_lock': 0x91,
    'left_shift': 0xA0,
    'right_shift ': 0xA1,
    'left_control': 0xA2,
    'right_control': 0xA3,
    'left_menu': 0xA4,
    'right_menu': 0xA5,
    'browser_back': 0xA6,
    'browser_forward': 0xA7,
    'browser_refresh': 0xA8,
    'browser_stop': 0xA9,
    'browser_search': 0xAA,
    'browser_favorites': 0xAB,
    'browser_start_and_home': 0xAC,
    'volume_mute': 0xAD,
    'volume_Down': 0xAE,
    'volume_up': 0xAF,
    'next_track': 0xB0,
    'previous_track': 0xB1,
    'stop_media': 0xB2,
    'play/pause_media': 0xB3,
    'start_mail': 0xB4,
    'select_media': 0xB5,
    'start_application_1': 0xB6,
    'start_application_2': 0xB7,
    'attn_key': 0xF6,
    'crsel_key': 0xF7,
    'exsel_key': 0xF8,
    'play_key': 0xFA,
    'zoom_key': 0xFB,
    'clear_key': 0xFE,
    '+': 0xBB,
    ',': 0xBC,
    '-': 0xBD,
    '.': 0xBE,
    '/': 0xBF,
    '`': 0xC0,
    ';': 0xBA,
    '[': 0xDB,
    '\\': 0xDC,
    ']': 0xDD,
    "'": 0xDE,
    '`': 0xC0
}

for x in dir(win32con):
    if x.startswith('VK_'):
        vk_codes[x[3:].replace('_', ' ').lower()] = getattr(win32con, x)


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
modifiers = sorted(all_modifiers)
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
    modifiers = set()


@attrs
class NameMixin:
    name = attrib()


@attrs
class SendMixin:
    send = attrib()


@attrs
class FinishAlternative(NameMixin):
    """Forces the sending of the last alternative."""

    type = 'Finish'


@attrs
class KeyAlternative(SendMixin, NameMixin):
    """Sends a key combination."""

    type = 'Key'


@attrs
class TextAlternative(SendMixin, NameMixin):
    """Sends 1 or more lines of text."""

    type = 'Text'


@attrs
class ModifierAlternative(SendMixin, NameMixin):
    """Toggles a modifier."""

    type = 'Modifier'


def bind(control, event_type, id=wx.ID_ANY):
    """Bind a function to a control, using event_type."""

    def inner(func):
        control.Bind(event_type, func, id=id)
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
for name in ('Type', 'Name', 'Send'):
    alternatives.AppendColumn(name)

add_key_button = wx.Button(panel, label='Add &Key')
add_text_button = wx.Button(panel, label='Add &Text')

add_modifier_button = wx.Button(panel, label='Add &Modifier')
add_finish_button = wx.Button(panel, label='Add &Finish Button')

register_hotkey_button = wx.Button(panel, label='&Register Hotkey')
unregister_hotkey_button = wx.Button(panel, label='&Unregister Hotkey')

wx.StaticText(panel, label='&Interval')
interval = IntCtrl(panel, value=500, min=250, max=5000)

remove_alternative_button = wx.Button(panel, label='&Delete Key')
bypass = wx.CheckBox(panel, label='&Bypass')


down_id = wx.NewIdRef().GetId()
up_id = wx.NewIdRef().GetId()


def move_alternative(event):
    """Move an alternative up or down in the list."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    name = hotkey_names[index]
    index = alternatives.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    if event.GetId() == down_id:
        diff = 1
    else:
        diff = -1
    pos = index + diff
    if pos < 0 or pos >= alternatives.GetItemCount():
        return wx.Bell()
    alternative = hotkey_alternatives[name].pop(index)
    data = [
        alternatives.GetItem(
            index, x
        ).GetText() for x in range(alternatives.GetColumnCount())
    ]
    alternatives.DeleteItem(index)
    for col, string in enumerate(data):
        if not col:
            alternatives.InsertItem(pos, string)
        else:
            alternatives.SetItem(pos, col, string)
    hotkey_alternatives[name].insert(pos, alternative)
    alternatives.Select(index)
    alternatives.Focus(index)


for id in (up_id, down_id):
    bind(alternatives, wx.EVT_MENU, id=id)(move_alternative)

move_modifiers = wx.ACCEL_CTRL | wx.ACCEL_SHIFT

alternatives.SetAcceleratorTable(
    wx.AcceleratorTable(
        (
            wx.AcceleratorEntry(
                flags=move_modifiers, keyCode=wx.WXK_DOWN, cmd=down_id
            ),
            wx.AcceleratorEntry(
                flags=move_modifiers, keyCode=wx.WXK_UP, cmd=up_id
            )
        )
    )
)


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
    alt = state.last_alternative
    state.last_name = None
    state.last_alternative = None
    state.alternative_index = -1
    # FinishAlternative instances do nothing:
    if not isinstance(alt, FinishAlternative):
        string = alt.send
        if isinstance(alt, TextAlternative):
            write(string)
        elif isinstance(alt, KeyAlternative):
            if state.modifiers:
                string = '+'.join(state.modifiers) + '+' + string
            send(string)
        elif isinstance(alt, ModifierAlternative):
            if string in state.modifiers:
                state.modifiers.remove(string)
                speak('%s up.' % string)
            else:
                state.modifiers.add(string)
                speak('%s down' % string)
        else:
            raise RuntimeError('Unknown alternative: %r.' % alt)
    if frame.Shown:  # Don't bind if the window is closed.
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
    name = alternative.name
    if isinstance(alternative, ModifierAlternative):
        if alternative.send in state.modifiers:
            s = ' up'
        else:
            s = ' down'
        name += s
    speak(name)
    if isinstance(alternative, FinishAlternative):
        press_alternative()
    else:
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
    if bypass.GetValue():
        res = True
    else:
        res = frame.RegisterHotKey(id, 0, value)
    if res:
        hotkey_ids[name] = id
        index = hotkeys.Append((name,))
        hotkeys.SetItemData(index, len(hotkey_names))
        hotkey_names.append(name)
    return res


def register_alternative(hotkey, cls, *args):
    """Add an alternative."""
    alt = cls(*args)
    hotkey_alternatives.setdefault(hotkey, []).append(alt)
    return alt


def add_alternative(alt):
    """Add an alternative to the alternatives list."""
    cls = type(alt)
    name = alt.name
    if cls is FinishAlternative:
        send = 'N/A'
    else:
        send = alt.send
    alternatives.Append((cls.type, name, send))


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
        if name in hotkey_names:
            return message('That hotkey is already in use.', 'Error')
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


def on_add_alternative(event):
    """Add an alternative."""
    index = hotkeys.GetFocusedItem()
    if index == -1:
        return wx.Bell()
    obj = event.GetEventObject()
    if obj is add_key_button:
        cls = KeyAlternative
        key = wx.GetTextFromUser('Enter keys to send', 'Keys')
    elif obj is add_modifier_button:
        cls = ModifierAlternative
        with wx.SingleChoiceDialog(
            panel, 'Choose a modifier', 'Modifiers', modifiers
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            key = dlg.GetStringSelection()
    elif obj is add_text_button:
        cls = TextAlternative
        key = wx.GetTextFromUser('Enter the text to send', 'Text')
    elif obj is add_finish_button:
        cls = FinishAlternative
        key = ''
    else:
        raise RuntimeError('Bad coding. Object %r.' % obj)
    name = wx.GetTextFromUser(
        'Enter a name', caption='Key Name', default_value=key
    )
    if not name:
        return
    if not key:
        # The button was add_finish_button.
        args = (name,)
    else:
        args = (key, name)
    hotkey = hotkey_names[index]
    alt = register_alternative(hotkey, cls, *args)
    add_alternative(alt)


for control in (
    add_key_button, add_text_button, add_modifier_button, add_finish_button
):
    bind(control, wx.EVT_BUTTON)(on_add_alternative)


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
                    t = entry.get('type', None)
                    for cls in (
                        FinishAlternative, KeyAlternative, TextAlternative,
                        ModifierAlternative
                    ):
                        if t == cls.type:
                            register_alternative(
                                hotkey, cls, *entry.get('args', [])
                            )
                            break
                    else:
                        raise RuntimeError('Invalid alternative type %r.' % t)
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
            cls = type(a)
            attribute_names = [x.name for x in cls.__attrs_attrs__]
            args = [getattr(a, name) for name in attribute_names]
            data['alternatives'][name].append(dict(type=cls.type, args=args))
    with open(filename, 'w') as f:
        dump(data, stream=f)
