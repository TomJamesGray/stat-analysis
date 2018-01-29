from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty,ObjectProperty

class PopupStringInput(GridLayout):
    text_input = ObjectProperty(None)
    submit_btn = ObjectProperty(None)
    label = StringProperty("")