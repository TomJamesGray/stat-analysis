import shutil
import os
import logging
import numpy as np
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from stat_analysis.generic_widgets.files import FileChooserSaveDialog
from kivy.uix.button import Button
from kivy.properties import StringProperty,BooleanProperty,Property,ListProperty,ObjectProperty
from kivy.core.window import Window


logger = logging.getLogger(__name__)


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
        self.graph_options_popup = Popup(size_hint=(None,None),size=(400,400))
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
                "prop": lambda x: x.get_xticks()[1] - x.get_xticks()[0],
                "text": "X Step",
                "set": lambda x,val: x.set_xticks(np.arange(x.get_xticks()[0],x.get_xlim()[1],float(val)))
            },
            {
                "prop": lambda x: x.get_yticks()[1] - x.get_yticks()[0],
                "text": "Y Step",
                "set": lambda x, val: x.set_yticks(np.arange(x.get_yticks()[0], x.get_ylim()[1], float(val)))
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
        for i in range(0,len(self.opts_out)):
            for opt in self.opts_out[i]:
                opt["set"](self.axis[i],opt["form"].text)

        self.on_graph_update(self.fig,self.axis)
