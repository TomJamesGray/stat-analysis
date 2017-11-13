import logging
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty,ListProperty,StringProperty

logger = logging.getLogger(__name__)


class BorderedButton(Button):
    b_width = NumericProperty(1)


class BorderedLabel(Label):
    b_width = NumericProperty(1)


class BorderedTable(GridLayout):
    headers = ListProperty(None)
    orientation = StringProperty("vertical")
    data = ListProperty(None)

    def __init__(self,**kwargs):
        super(BorderedTable,self).__init__(**kwargs)
        if len(self.headers) != len(self.data):
            raise ValueError("Length of headers and data aren't equal")

        if self.orientation == "vertical":
            self.cols = len(self.data)
            for header in self.headers:
                self.add_widget(BorderedLabel(text=str(header),color=(.5,0,0,1),size_hint_x=None))

            for x in range(0,len(self.data)):
                for y in range(0,len(self.data[0])):
                    self.add_widget(BorderedLabel(text=str(self.data[x][y]),color=(0,0,0,1),size_hint_x=None,height=30))