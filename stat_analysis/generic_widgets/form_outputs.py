import shutil
import os
import logging

try:
    # Try and import pygame to allow cursor to be set but don't crash if a different window provider is used, ie SDL2
    import pygame.cursors
    import pygame.mouse
except:
    pass

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
        print("Mouse up")
        for split in self.width_adjusters:
            split.pressed = False
        for col in self.data_columns:
            col.scroll_bar_active = False
            col.horiz_scroll_bar_active = False

        self.resize_cursor_active = False

    def check_width_adjusters(self,instance,touch,*args):
        # Since the Buttons don't work when near(??) a scrollview this is a custom
        # handler to handle button presses
        for a in self.width_adjusters:
            if a.collide_point(*a.to_widget(*touch.pos)):
                a.pressed = True
                return

    def mouse_move(self,instance,touch,*args):
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
        for split in self.width_adjusters:
            if split.collide_point(*split.to_widget(*pos)) and not self.resize_cursor_active:
                # Set cursor to the column reisizer one, ie "<->"
                try:
                    cursor,mask = pygame.cursors.compile(pygame.cursors.sizer_x_strings,"X",".")
                    cursor_data = ((24,16),(7,11),cursor,mask)
                    pygame.mouse.set_cursor(*cursor_data)
                except:
                    # Cursor can't be changed so change the color of the adjuster
                    split.actual_bg_color = (1, 0, 0, 1)
                return

        if not self.resize_cursor_active:
            try:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)
            except:
                for split in self.width_adjusters:
                    split.actual_bg_color = (0, 0, 0, 1)


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
        print("Scroll start root {} collide {}".format(root,self.collide_with_scroll_bar(touch)))
        if self.scroll_bar_active or (self.bar_width != 0 and touch.button == "left" and root and\
                                              self.collide_with_scroll_bar(touch)):
            print("Collide with bar (on scroll start)")
            self.scroll_bar_active = True
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return
        elif root and self.touch_collide_grid(touch) and not self.collide_with_horiz_scroll_bar(touch):
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
            self.horiz_scroll_bar_active = True
        else:
            super().on_scroll_start(touch,check_children=check_children)

        self.refresh_from_layout()

    def on_touch_move(self, touch):
        if self.scroll_bar_active:
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return

    def on_scroll_move(self, touch, root=True):
        print("On scroll move")
        # super().on_scroll_start(touch)
        # return

        if self.scroll_bar_active:
            for sibling in self.siblings:
                sibling.scroll_bar_scroll(touch)
            return
        elif self.touch_collide_grid(touch) and not self.collide_with_horiz_scroll_bar(touch) and\
                not self.horiz_scroll_bar_active:
            for sibling in self.siblings:
                if sibling is not self:
                    touch.x = sibling.center_x
                    touch.y = sibling.center_y
                    touch.pos = (touch.x, touch.y)
                    sibling.touch_scroll(touch)

            self.touch_scroll(touch)

        self.refresh_from_layout()

    def on_scroll_stop(self, touch, check_children=True):
        print("Scroll STOP")
        super().on_scroll_stop(touch,check_children=check_children)
        return

    def collide_with_scroll_bar(self,touch):
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)
        self.bar_width = 15

        horiz = grid_pos[0] + parent_grid.width - self.bar_width <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + parent_grid.height

        print("{} < {} < {}".format(grid_pos[0] + parent_grid.width - self.bar_width,click_pos[0],grid_pos[0] + parent_grid.width))
        print("Horiz {} vertical {} bar width {}\n".format(horiz,vertical,self.bar_width))
        return horiz and vertical

    def touch_collide_grid(self,touch):
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        horiz = grid_pos[0] <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + parent_grid.height

        return horiz and vertical

    def collide_with_horiz_scroll_bar(self,touch):
        # Width of the horizontal scroll bar for the result output
        scroll_width = 20
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        horiz = grid_pos[0] <= click_pos[0] <= grid_pos[0] + parent_grid.width
        vertical = grid_pos[1] <= click_pos[1] <= grid_pos[1] + scroll_width
        return horiz and vertical

    def touch_scroll(self,touch):
        new_scroll_y = self.scroll_y - self.convert_distance_to_scroll(touch.dx, touch.dy)[1]
        if 0 > new_scroll_y or new_scroll_y > 1:
            # This scroll would be going further than allowed
            return
        self.scroll_y -= self.convert_distance_to_scroll(touch.dx, touch.dy)[1]

    def scroll_bar_scroll(self,touch):
        # Convert the y position of the touch to "scroll_y", 0 is the bottom, 1 is the top
        parent_grid = self.parent
        grid_pos = parent_grid.to_window(*parent_grid.pos)
        click_pos = parent_grid.to_window(*touch.pos)

        new_scroll_y = (click_pos[1]-grid_pos[1])/parent_grid.height
        print("Scroll delta {}".format(new_scroll_y-self.scroll_y))
        # new_scroll_y = self.scroll_y - self.convert_distance_to_scroll(-touch.dx, -touch.dy)[1]
        if 0 > new_scroll_y or new_scroll_y > 1:
            # This scroll would be going further than allowed
            return
        print("New scroll scroll y {}".format(new_scroll_y))
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
            return
        elif collision and not self.hovering:
            # Mouse enter button
            # self.background_color = (210 / 255, 210 / 255, 210 / 255, 1)
            self.background_color = (.6,.6,.6,1)
        elif self.hovering and not collision:
            # Mouse exit button
            self.background_color = (1, 1, 1, 1)

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
