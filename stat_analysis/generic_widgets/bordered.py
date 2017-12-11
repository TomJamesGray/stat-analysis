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
    headers = ListProperty([])
    orientation = StringProperty("vertical")
    data = ListProperty([])
    raw_data = ListProperty([])

    def __init__(self,**kwargs):
        super(BorderedTable,self).__init__(**kwargs)
        # Raw_data is technically given priority
        print(self.raw_data)
        if self.raw_data != []:
            headers = self.raw_data[0].keys()
            if self.orientation == "vertical":
                self.cols = len(headers)
                for header in headers:
                    self.add_widget(BorderedLabel(text=str(header), color=(.5, 0, 0, 1), size_hint_x=None))

                for row in self.raw_data:
                        for _,val in row.items():
                            self.add_widget(BorderedLabel(text=str(val), color=(0, 0, 0, 1), size_hint_x=None,
                                                          height=30))
        elif self.data != []:
            if self.orientation == "vertical":
                self.cols = len(self.data)
                for header in self.headers:
                    self.add_widget(BorderedLabel(text=str(header),color=(.5,0,0,1),size_hint_x=None))

                for x in range(0,len(self.data)):
                    for y in range(0,len(self.data[0])):
                        self.add_widget(BorderedLabel(text=str(self.data[x][y]),color=(0,0,0,1),size_hint_x=None,
                                                      height=30))
            elif self.orientation == "horizontal":
                self.rows = len(self.headers)
                for x in range(0, len(self.data)):
                    self.add_widget(
                        BorderedLabel(text=str(self.headers[x]), color=(.5, 0, 0, 1), size_hint_x=None))

                    for y in range(0, len(self.data[0])):
                        x = BorderedLabel(text=str(self.data[x][y]), color=(0, 0, 0, 1), size_hint_x=1,height=30,
                                          halign="left",valign="middle")
                        x.bind(size=x.setter("text_size"))
                        self.add_widget(x)

        else:
            if len(self.headers) != len(self.data):
                raise ValueError("Length of headers and data aren't equal")

