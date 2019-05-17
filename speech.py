from accessible_output2.outputs.auto import Auto
output = Auto()


def speak(text):
    return output.speak(text, interrupt=True)
