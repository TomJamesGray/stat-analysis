import os
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from stat_analysis.generic_widgets.files import FileChooserListViewFormAction
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

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        self.file_chooser_btn = Button(text="Select File",height=30,size_hint_y=None)
        self.file_chooser_btn.bind(on_press=self.open_f_selector)

        self.add_widget(input_label)
        self.add_widget(self.file_chooser_btn)

    def open_f_selector(self,*args):
        self.popup = Popup(title="Select file",size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserListViewFormAction(popup=self.popup,file_chooser_btn=self.file_chooser_btn,
                                                  filters=[lambda _,filename: filename.endswith(".csv")],
                                                  path=os.path.expanduser("~"),form_parent=self)
        self.popup.content = f_chooser
        self.popup.open()

    def get_val(self):
        return self.file_location


