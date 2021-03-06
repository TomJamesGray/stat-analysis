from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from stat_analysis.generic_widgets.form_inputs import FormInputLabel


class FormNumeric(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        if "allow_comma_separated" not in input_dict.keys():
            input_dict["allow_comma_separated"] = False

        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 55
        self.width = 200
        self.input_dict = input_dict

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        self.num_input = TextInput(size_hint=(None,None),height=30,multiline=False)

        if "default" in input_dict.keys():
            if input_dict["default"] != None:
                if input_dict["allow_comma_separated"]:
                    self.num_input.text = ",".join([str(x) for x in input_dict["default"]])
                else:
                    self.num_input.text = str(input_dict["default"])

        self.add_widget(input_label)
        self.add_widget(self.num_input)

    def get_val(self):
        def __get_val(x):
            # Gets the value from a section of the input if comma separated, or the whole input if not
            try:
                val = float(x)
            except ValueError:
                raise ValueError("{} should be numeric".format(self.input_dict["visible_name"]))
            return val
        # Input is empty so return None
        if self.num_input.text == "":
            return None

        if self.input_dict["allow_comma_separated"]:
            out = []
            # If comma separated return a list of numbers
            for x in self.num_input.text.split(","):
                out.append(__get_val(x))
            return out
        else:
            return __get_val(self.num_input.text)
