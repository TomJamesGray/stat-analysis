import shutil
import os
import logging
from kivy.app import App
from stat_analysis.generic_widgets.files import FileChooserSaveDialog
from kivy.effects.scroll import ScrollEffect
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty,BooleanProperty,Property,ListProperty,ObjectProperty
from kivy.core.window import Window


logger = logging.getLogger(__name__)


class DataSpreadsheet(GridLayout):
    headers = ListProperty(None)
    table_data = ListProperty(None)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.size_hint=(None,None)
        self.data_cols = len(self.table_data[0])
        self.col_default_width = 150
        self.col_min_width = 75
        self.adjuster_show_width = 2
        self.adjuster_click_width = 10
        self.width_adjusters = []
        self.data_columns = []
        self.spreadsheet_header_labels = []
        self.resize_cursor_active = False

        self.spreadsheet_headers = GridLayout(rows=1,size_hint=(None,None),height=30,
                                              width=self.col_default_width*self.data_cols+(self.data_cols-1)*
                                                                                          self.adjuster_show_width)

        self.rv_container = GridLayout(rows=1,size_hint=(None,1),
                                       width=self.col_default_width*self.data_cols+(self.data_cols-1)*
                                                                                   self.adjuster_show_width)

        # Transform data so each column is in seperate list
        self.columns = [[] for _ in range(self.data_cols)]
        for y in range(len(self.table_data)):
            for x in range(self.data_cols):
                self.columns[x].append(
                    self.table_data[y][x])

        for i,header in enumerate(self.headers):
            lbl = GridAdjustHeader(text=str(header),width=self.col_default_width)

            data_column = ColumnRV(raw_data=self.columns[i],size_hint=(None,1),
                                   width=self.col_default_width+self.adjuster_show_width)

            self.spreadsheet_headers.bind(height=data_column.setter("height"))
            if i == self.data_cols -1:
                data_column.bar_color = (.7,.7,.7,.9)
                data_column.bar_inactive_color = (.7,.7,.7,.4)
                data_column.bar_width = 15

            split = WidthAdjust(size_hint_x=None,width=self.adjuster_show_width,adjust=[lbl,data_column])

            if i == 0:
                lbl.left_border = True
                data_column.left_border = True

            self.rv_container.add_widget(data_column)
            self.width_adjusters.append(split)
            self.data_columns.append(data_column)
            self.spreadsheet_headers.add_widget(lbl)
            self.spreadsheet_header_labels.append(lbl)
            self.spreadsheet_headers.add_widget(split)

        # Since all the Column RVs are separate, all the RVs need to be aware of each other
        # So the scrolls can be mirrored
        for col in self.data_columns:
            col.siblings = self.data_columns
        Window.bind(on_touch_up=self.mouse_release)
        Window.bind(on_touch_move=self.mouse_move)
        Window.bind(on_touch_down=self.check_width_adjusters)
        Window.bind(mouse_pos=self.set_cursor_hover_adjuster)
        self.add_widget(self.spreadsheet_headers)
        self.add_widget(self.rv_container)

    def mouse_release(self,*args):
        """
        Called when the mouse is released. Resets all the width adjuster states to not pressed. Resets the scroll
        bar and horiz scroll bar active properties on the columns and takes off the resize cursor
        """
        for split in self.width_adjusters:
            split.pressed = False
        for col in self.data_columns:
            col.scroll_bar_active = False
            col.horiz_scroll_bar_active = False

        self.resize_cursor_active = False

    def check_width_adjusters(self,instance,touch,*args):
        """
        Called on touch down and handles the collision detection for the width adjusters
        """
        for a in self.width_adjusters:
            if a.collide_point(*a.to_widget(*touch.pos)):
                a.pressed = True
                # Since only one adjuster can be pressed at once exit
                return

    def mouse_move(self,instance,touch,*args):
        """
        Called when the mouse is moved and a mouse button is pressed down. Handles the resizing of the content
        from the width adjusters.
        """
        for split_no,split in enumerate(self.width_adjusters):
            if split.pressed:
                self.resize_cursor_active = True
                for item in split.adjust:
                    if item.width + touch.dx < self.col_min_width:
                        # This adjustment would make the column too narrow
                        return
                    item.width += touch.dx
                self.spreadsheet_headers.width += touch.dx
                self.rv_container.width += touch.dx
                self.width += touch.dx
                return

    def set_cursor_hover_adjuster(self,instance,pos,*args):
        """
        Called when the mouse is moved. Tries to set the mouse cursor to the resize cursor if the mouse
        is over a "width adjuster" but if it can't, ie the window provider isn't pygame then color the width adjuster
        """
        for split in self.width_adjusters:
            if split.collide_point(*split.to_widget(*pos)) and not self.resize_cursor_active:
                # Set cursor to the column reisizer one, ie "<->"
                App.get_running_app().set_cursor("size_we")
                return

        if not self.resize_cursor_active:
            App.get_running_app().set_cursor("arrow")


class ColumnRV(RecycleView):
    raw_data = ListProperty()
    siblings = ListProperty()
    # This draws a left border down the side of the Column, only really used for import_set_col_types as
    # there is padding so it's visible ColumnRV doesn't normally have a left border
    left_border = BooleanProperty(False)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.data = [{"text":str(x)} for x in self.raw_data]
        self.effect_cls = ScrollEffect
        self.actual_bg_color = (0,0,0,1)
        self.scroll_bar_active = False
        self.horiz_scroll_bar_active = False
        self.scroll_timeout = -1

    def on_scroll_start(self, touch, check_children=True, root=True):
        """
        Handles the start of a scroll event. Determines what kind of scroll is used, ie scroll bar, touch or
        mouse wheel and executes it. This over-rides the default behaviour because all the columns need to scroll
        in sync with each other
        """
        if self.scroll_bar_active or (self.bar_width != 0 and touch.button == "left" and root and\
                                              self.collide_with_scroll_bar(touch)):
            # The scroll bar has been pressed
            self.scroll_bar_active = True
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return

        elif root and self.touch_collide_grid(touch) and not self.collide_with_horiz_scroll_bar(touch):
            # This is the "root" scroller and the touch is within the grid, so scroll the content
            for sibling in self.siblings:
                if sibling is not self:
                    touch.x = sibling.center_x
                    touch.y = sibling.center_y
                    touch.pos = (touch.x,touch.y)
                    if touch.button in ("scrollup","scrolldown"):
                        sibling.on_scroll_start(touch,check_children=check_children,root=False)
                    elif touch.button == "left":
                        sibling.touch_scroll(touch)

            if touch.button in ("scrollup", "scrolldown"):
                super().on_scroll_start(touch,check_children)
            elif touch.button == "left":
                self.touch_scroll(touch)

        elif self.collide_with_horiz_scroll_bar(touch):
            # Touch is on the horizontal scroll bar that doesn't belong to this widget so disable any
            # scrolling until a mouse up event occurs
            self.horiz_scroll_bar_active = True
        else:
            super().on_scroll_start(touch,check_children=check_children)

        self.refresh_from_layout()

    def on_touch_move(self, touch):
        """
        Handles the touch move event, this is only used for the touch bar scrolling when the initial movement is
        minimal
        """
        if self.scroll_bar_active:
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return
        else:
            super().on_scroll_move(touch)

    def on_scroll_move(self, touch, root=True):
        """
        Handles the on scroll move event, this is only used by touch scrolling and the scroll bar
        """

        if self.scroll_bar_active:
            # Vertical scrollbar is active so scroll with that
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return
        elif self.touch_collide_grid(touch) and not self.collide_with_horiz_scroll_bar(touch) and\
                not self.horiz_scroll_bar_active:
            # Touch intersects with the grid and doesn't collide with the horizontal scroll bar and the horizontal
            # scroll bar isn't active so run a "touch scroll"
            for sibling in self.siblings:
                if sibling is not self:
                    touch.x = sibling.center_x
                    touch.y = sibling.center_y
                    touch.pos = (touch.x, touch.y)
                    sibling.touch_scroll(touch)

            self.touch_scroll(touch)

        self.refresh_from_layout()

    def collide_with_scroll_bar(self,touch):
        """
        Determines if the given touch collides with the horizontal scroll bar that is displayed for the final column
        """
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)
        self.bar_width = 15
        # Determine if the touch collides on the x and y axis
        horiz = grid_pos[0] + parent_grid.width - self.bar_width <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + parent_grid.height

        return horiz and vertical

    def touch_collide_grid(self,touch):
        """
        Determines if the given touch collides with the main grid that contains all the column RVs
        """
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        # Determine if the touch collides on the x and y axis
        horiz = grid_pos[0] <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + parent_grid.height

        return horiz and vertical

    def collide_with_horiz_scroll_bar(self,touch):
        """
        Determines if the given touch collides with the horizontal scroll bar that is displayed by the result
        output scrollview.
        """
        # Width of the horizontal scroll bar for the result output
        scroll_width = 20
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        # Determine if the touch collides on the x and y axis
        horiz = grid_pos[0] <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + scroll_width
        return horiz and vertical

    def touch_scroll(self,touch):
        """
        Calculates and sets the amount to scroll the content for touch scrolls based on the change in x and y for the
        given touch
        """
        new_scroll_y = self.scroll_y - self.convert_distance_to_scroll(touch.dx, touch.dy)[1]
        if 0 > new_scroll_y or new_scroll_y > 1:
            # This scroll would be going further than allowed
            return
        self.scroll_y -= self.convert_distance_to_scroll(touch.dx, touch.dy)[1]

    def scroll_bar_scroll(self,touch):
        """
        Calculates and sets the amount to scroll the content based on the y position of the touch, note
        this method doesn't check if the touch intersects with the scroll bar.
        :param touch:
        :return:
        """
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        # Convert the y position of the touch to "scroll_y", 0 is the bottom, 1 is the top
        new_scroll_y = (click_pos[1]-grid_pos[1])/parent_grid.height
        if 0 > new_scroll_y or new_scroll_y > 1:
            # This scroll would be going further than allowed
            return

        self.scroll_y = new_scroll_y


class GridAdjustHeader(Label):
    left_border = BooleanProperty(False)


class WidthAdjust(Button):
    pressed = BooleanProperty(False)
    adjust = ListProperty()
    actual_bg_color = Property((0,0,0,1))


class ExportableGraph(GridLayout):
    source = StringProperty("")
    nocache = BooleanProperty(False)
    image = ObjectProperty(None)
    fig = Property(None)
    axis = ListProperty()

    def save_btn(self):
        self.save_popup = Popup(size_hint=(None, None), size=(400, 400))
        f_chooser = FileChooserSaveDialog(default_file_name="graph.png")
        f_chooser.on_save = self.do_save
        f_chooser.on_cancel = lambda :self.save_popup.dismiss()
        self.save_popup.content = f_chooser
        self.save_popup.open()

    def do_save(self,path,filename):
        self.save_popup.dismiss()
        shutil.copyfile(self.source,os.path.join(path,filename))

    def graph_opts(self):
        self.graph_options_popup = Popup(size_hint=(None,None),size=(400,400),title="Graph Options")
        opts = GraphOptions(fig=self.fig,axis=self.axis)
        opts.on_graph_update = self.update_graph
        self.graph_options_popup.content = opts
        self.graph_options_popup.open()

    def update_graph(self,fig,axis):
        self.graph_options_popup.dismiss()
        self.fig = fig
        self.axis = axis
        self.fig.savefig(self.source)
        self.image.reload()


class ToolBoxButton(Button):
    hovering = BooleanProperty(False)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.mouse_pos)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering and collision:
            # Mouse moved within the button
            if App.get_running_app().current_cursor != "hand":
                App.get_running_app().set_cursor("hand")
            return
        elif collision and not self.hovering:
            # Mouse enter button
            # self.background_color = (210 / 255, 210 / 255, 210 / 255, 1)
            self.background_color = (.6,.6,.6,1)
            App.get_running_app().set_cursor("hand")

        elif self.hovering and not collision:
            # Mouse exit button
            self.background_color = (1, 1, 1, 1)
            App.get_running_app().set_cursor("arrow")

        self.hovering = collision


class GraphOptions(TabbedPanel):
    fig = Property(None)
    axis = ListProperty()
    on_graph_update = Property(None)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.opts_binds = [
            {
                "prop":lambda x:x.get_xlabel(),
                "text":"X Label",
                "set":lambda x,val:x.set_xlabel(val)
            },
            {
                "prop": lambda x: x.get_ylabel(),
                "text": "Y Label",
                "set": lambda x, val: x.set_ylabel(val)
            },
            {
                "prop": lambda x:x.get_xlim()[1],
                "text": "X Upper limit",
                "set": lambda x,val:x.set_xlim(xmax=float(val))
            },
            {
                "prop": lambda x: x.get_xlim()[0],
                "text": "X Lower limit",
                "set": lambda x, val: x.set_xlim(xmin=float(val))
            },
            {
                "prop": lambda x: x.get_ylim()[1],
                "text": "Y Upper limit",
                "set": lambda x, val: x.set_ylim(ymax=float(val))
            },
            {
                "prop": lambda x: x.get_ylim()[0],
                "text": "Y Lower limit",
                "set": lambda x, val: x.set_ylim(ymin=float(val))
            }
        ]

        self.do_default_tab = False
        self.opts_out = []

        for i,axe in enumerate(self.axis):
            self.opts_out.append(self.opts_binds)
            panel = TabbedPanelItem(text="Figure {}".format(i+1))

            if i == 0:
                # Set first axe as default tab
                self.default_tab = panel

            cont = GridLayout(cols=1,size_hint=(1,1))

            grd = GridLayout(cols=2,size_hint=(1,1),row_default_height=30,row_force_default=True)

            for opt in self.opts_out[-1]:
                grd.add_widget(Label(text=opt["text"]))
                opt["form"] = TextInput(text=str(opt["prop"](axe)))
                grd.add_widget(opt["form"])

            cont.add_widget(grd)
            cont.add_widget(Button(text="Update Graph",height=30,size_hint=(1,None),on_press=self.update_graph))

            panel.add_widget(cont)
            self.add_widget(panel)

    def update_graph(self,*args):
        logger.info("Updating graph with opts {}".format(self.opts_out))
        print(self.axis[0].step)
        for i in range(0,len(self.opts_out)):
            for opt in self.opts_out[i]:
                opt["set"](self.axis[i],opt["form"].text)

        self.on_graph_update(self.fig,self.axis)
