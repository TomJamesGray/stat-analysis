import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty,StringProperty,ListProperty


class FileChooserSaveDialog(BoxLayout):
    text_input = ObjectProperty(None)
    initial_path = os.path.expanduser("~")
    default_file_name = StringProperty("Untitled")
    on_save = None
    on_cancel = None


class FileChooserLoadDialog(BoxLayout):
    initial_path = os.path.expanduser("~")
    on_load = None
    on_cancel = None
    filters = ListProperty()