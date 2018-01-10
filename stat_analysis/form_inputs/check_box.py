from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from stat_analysis.generic_widgets.form_inputs import FormInputLabel

class FormCheckBox(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.rows = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.input_dict = input_dict
        self.check = CheckBox(size_hint=(None,None),width=30,height=30,color=(0,0,0,1))
        self.add_widget(self.check)

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            print("Adding tip")
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        self.add_widget(input_label)

    def get_val(self):
        return self.check.active
