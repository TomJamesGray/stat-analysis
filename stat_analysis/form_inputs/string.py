from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from stat_analysis.generic_widgets.form_inputs import FormInputLabel

class FormString(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        # Use all available height
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.input_dict = input_dict

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])
        # Create the text input
        self.str_input = TextInput(size_hint=(1,None),height=30,multiline=False)

        if "default" in input_dict.keys():
            if input_dict["default"] != None:
                # Set the default value
                self.str_input.text = input_dict["default"]

        self.add_widget(input_label)
        self.add_widget(self.str_input)

    def get_val(self):
        if self.str_input.text == "":
            # Input is empty so return None
            return None
        else:
            return self.str_input.text
