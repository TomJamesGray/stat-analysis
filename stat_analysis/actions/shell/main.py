import logging
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

logger = logging.getLogger(__name__)


class Shell:
    type = "distributions.shell"
    view_name = "Shell"

    def __init__(self,output_widget):
        self.output_widget = output_widget

    def render(self):
        logger.debug("Initialising shell")
        self.output_widget.add_widget(ShellInput(shell=self))


class ShellInput(GridLayout):
    shell = ObjectProperty()
    pass


class ShellInputBox(TextInput):
    def test(self,window,keycode,text,modifiers):
        if keycode[1] == "enter":
            # Evaluate the text
            print("Evaluate")
            print(self.parent.shell)
        super().keyboard_on_key_down(window,keycode,text,modifiers)