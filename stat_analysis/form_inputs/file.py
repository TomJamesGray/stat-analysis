import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from stat_analysis.generic_widgets.files import FileChooserLoadDialog
from stat_analysis.generic_widgets.form_inputs import FormInputLabel


class FormFile(GridLayout):
    def __init__(self,input_dict,*args,**kwargs):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        # Use all available height
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.file_location = None
        self.input_dict = input_dict
        # Set the default path to be the user's home directory
        # this method works on linux and windows
        self.default_path = os.path.expanduser("~")

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])
        # Create button that opens the file selector when pressed
        self.file_chooser_btn = Button(text="Select File",height=30,size_hint_y=None)
        self.file_chooser_btn.bind(on_press=self.open_f_selector)

        if "default" in input_dict.keys():
            # Set default file location if specified
            if input_dict["default"] != None:
                # Set the button text to the filename
                self.file_chooser_btn.text = os.path.basename(input_dict["default"])
                # Set the default path to the path to the file
                self.default_path = os.path.dirname(input_dict["default"])

        self.add_widget(input_label)
        self.add_widget(self.file_chooser_btn)

    def open_f_selector(self,*args):
        """
        Open the file selector
        """
        self.popup = Popup(title="Select file",size_hint=(None,None),size=(400,400))
        # Create the dialog that is used to select files, with the filters option set in the input
        # dict, if this hasn't been specified pass a blank list (nothing). Filters are used to
        # limit the files that can be selected such as only "csv" files
        f_chooser = FileChooserLoadDialog(filters=self.input_dict.get("filters",[]))
        # Close the popup on the cancel event
        f_chooser.on_cancel = lambda :self.popup.dismiss()
        # Run the f_selector_load method on the load event
        f_chooser.on_load = self.f_selector_load
        # Set the popup content to the file chooser
        self.popup.content = f_chooser
        self.popup.open()

    def f_selector_load(self,_,file_location):
        # Close the popup
        self.popup.dismiss()
        # Set the file location ie file name and path
        self.file_location = file_location[0]
        # Set the text of the button to be the file name
        self.file_chooser_btn.text = os.path.basename(file_location[0])

    def get_val(self):
        return self.file_location
