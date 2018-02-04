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
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.file_location = None
        self.input_dict = input_dict
        self.default_path = os.path.expanduser("~")

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        self.file_chooser_btn = Button(text="Select File",height=30,size_hint_y=None)
        self.file_chooser_btn.bind(on_press=self.open_f_selector)

        if "default" in input_dict.keys():
            if input_dict["default"] != None:
                self.file_chooser_btn.text  = os.path.basename(input_dict["default"])
                self.default_path = os.path.dirname(input_dict["default"])

        self.add_widget(input_label)
        self.add_widget(self.file_chooser_btn)

    def open_f_selector(self,*args):
        self.popup = Popup(title="Select file",size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserLoadDialog(filters=self.input_dict.get("filters",[]))
        f_chooser.on_cancel = lambda :self.popup.dismiss()
        f_chooser.on_load = self.f_selector_load
        self.popup.content = f_chooser
        self.popup.open()

    def f_selector_load(self,_,file_location):
        self.popup.dismiss()
        self.file_location = file_location[0]
        self.file_chooser_btn.text = os.path.basename(file_location[0])

    def get_val(self):
        return self.file_location
