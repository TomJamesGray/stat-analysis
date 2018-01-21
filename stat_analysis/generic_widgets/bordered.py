import logging
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty,ListProperty,StringProperty,BooleanProperty

logger = logging.getLogger(__name__)


class BorderedButton(Button):
    b_width = NumericProperty(1)
    b_color = ListProperty([0, 0, 0, 1])
    inside = BooleanProperty(False)


class BorderedLabel(Label):
    b_width = NumericProperty(1)
    b_color = ListProperty([0,0,0,1])


class BorderedTable(GridLayout):
    headers = ListProperty([])
    orientation = StringProperty("vertical")
    markup = BooleanProperty(False)
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
        self.header_col = App.get_running_app().accent_col
        if for_scroller:
            self.bind(minimum_height=self.setter("height"))

        if self.table_data != []:
            if self.orientation == "vertical":
                self.cols = len(self.headers)
                for header in self.headers:
                    self.add_widget(BorderedLabel(text=str(header), color=self.header_col, size_hint_x=None,
                                                  size_hint_y=None,height=30,markup=self.markup))

                for row in self.table_data:
                        for val in row:
                            self.add_widget(BorderedLabel(text=str(val), color=(0, 0, 0, 1), size_hint_x=None,
                                                          size_hint_y=None,height=30,markup=self.markup))
        elif self.data != []:
            if self.orientation == "vertical":
                self.cols = len(self.headers)
                for header in self.headers:
                    self.add_widget(BorderedLabel(text=str(header),color=self.header_col,size_hint_x=None,
                                                  markup=self.markup))

                for y in range(0,len(self.data[0])):
                    for x in range(0, len(self.data)):
                        self.add_widget(BorderedLabel(text=str(self.data[x][y]),color=(0,0,0,1),size_hint_x=None,
                                                      height=30,markup=self.markup))

            elif self.orientation == "horizontal":
                self.rows = len(self.headers)
                for x in range(0, len(self.data)):
                    self.add_widget(
                        BorderedLabel(text=str(self.headers[x]), color=self.header_col, size_hint_x=None,
                                      markup=self.markup))

                    for y in range(0, len(self.data[0])):
                        x = BorderedLabel(text=str(self.data[x][y]), color=(0, 0, 0, 1), size_hint_x=1,height=30,
                                          halign="left",valign="middle",markup=self.markup)
                        x.bind(size=x.setter("text_size"))
                        self.add_widget(x)

        else:
            if len(self.headers) != len(self.data):
                raise ValueError("Length of headers and data aren't equal")


class BorderedSpinner(Spinner):
    b_width = NumericProperty(1)


class BorderedHoverButton(Button):
    b_width = NumericProperty(1)
    b_color = ListProperty([150/255, 150/255, 150/255, 1])
    bg_color = ListProperty([60 / 255, 60 / 255, 60 / 255, 1])
    bg_color_hover = ListProperty([30/255,30/255,30/255,1])
    hovering = BooleanProperty(False)
    bottom = BooleanProperty(False)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering and collision:
            # Mouse moved within the button
            return
        elif collision and not self.hovering:
            # Mouse enter button
            self.background_color = self.bg_color_hover
        elif self.hovering and not collision:
            # Mouse exit button
            self.background_color = self.bg_color

        self.hovering = collision