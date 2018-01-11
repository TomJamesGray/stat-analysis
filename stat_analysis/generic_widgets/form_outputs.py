import shutil
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from stat_analysis.generic_widgets.files import FileChooserSaveDialog
from kivy.uix.button import Button
from kivy.properties import StringProperty,BooleanProperty
from kivy.core.window import Window


class ExportableImage(GridLayout):
    source = StringProperty("")
    nocache = BooleanProperty(False)

    def save_btn(self):
        self.save_popup = Popup(size_hint=(None, None), size=(400, 400))
        f_chooser = FileChooserSaveDialog(default_file_name="graph.png")
        f_chooser.on_save = self.do_save
        self.save_popup.content = f_chooser
        self.save_popup.open()

    def do_save(self,path,filename):
        self.save_popup.dismiss()
        shutil.copyfile(self.source,os.path.join(path,filename))

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