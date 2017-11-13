from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import NumericProperty


class BorderedButton(Button):
    b_width = NumericProperty(1)


class BorderedLabel(Label):
    b_width = NumericProperty(1)