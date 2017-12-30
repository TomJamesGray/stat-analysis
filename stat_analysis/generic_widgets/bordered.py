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
    # Using this as an example:
    # Col1     Col2     Col3
    #   1        2        3
    #   4        5        6
    #   7        8        9
    # Structure for data to produce this table would be [[1,4,7],[2,5,8],[3,6,9]
    data = ListProperty([])
    # Structure for table_data would be [[1,2,3],[4,5,6],[7,8,9]]
    table_data = ListProperty([])

    def __init__(self,for_scroller=False,**kwargs):
        super(BorderedTable,self).__init__(**kwargs)
        if for_scroller:
            self.bind(minimum_height=self.setter("height"))

        if self.table_data != []:
            if self.orientation == "vertical":
                self.cols = len(self.headers)
                for header in self.headers:
                    self.add_widget(BorderedLabel(text=str(header), color=(.5, 0, 0, 1), size_hint_x=None,size_hint_y=None,height=30))

                for row in self.table_data:
                        for val in row:
                            self.add_widget(BorderedLabel(text=str(val), color=(0, 0, 0, 1), size_hint_x=None,size_hint_y=None,
                                                          height=30))
        elif self.data != []:
            if self.orientation == "vertical":
                self.cols = len(self.headers)
                for header in self.headers:
                    self.add_widget(BorderedLabel(text=str(header),color=(.5,0,0,1),size_hint_x=None))

                for y in range(0,len(self.data[0])):
                    for x in range(0, len(self.data)):
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

