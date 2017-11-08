from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput

class FormNumeric(GridLayout):
    def __init__(self,input_dict,*args):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 55
        self.width = 200
        self.input_dict = input_dict
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=25,color=(0,0,0,1),
                            valign="middle",font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.num_input = TextInput(size_hint=(None,None),height=30,multiline=False)
        self.add_widget(input_label)
        self.add_widget(self.num_input)

    def get_val(self):
        try:
            val = float(self.num_input.text)
        except ValueError:
            raise ValueError("{} should be numeric".format(self.input_dict["visible_name"]))
        return val
