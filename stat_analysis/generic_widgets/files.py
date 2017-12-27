import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty,StringProperty


class FileChooserListViewFormAction(FileChooserListView):
    popup = ObjectProperty(None)
    file_chooser_btn = ObjectProperty(None)
    form_parent = ObjectProperty(None)

    def on_submit(self, selected, touch=None):
        """
        Called when the file is selected. Sets the file_location
        attribute on the parent and text on the file_chooser_btn
        """
        self.popup.dismiss()
        self.form_parent.file_location = selected[0]
        self.file_chooser_btn.text = os.path.basename(selected[0])


class FileChooserSaveDialog(BoxLayout):
    text_input = ObjectProperty(None)
    initial_path = os.path.expanduser("~")
    default_file_name = StringProperty("Untitled")
    on_save = None

class FileChooserLoadDialog(BoxLayout):
    initial_path = os.path.expanduser("~")
    on_load = None
