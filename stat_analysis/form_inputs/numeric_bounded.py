from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from stat_analysis.generic_widgets.form_inputs import FormInputLabel


class FormNumericBounded(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.input_dict = input_dict

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            print("Adding tip")
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        container = GridLayout(rows=1,height=30,width=200,size_hint=(None,None))

        self.text_readout = TextInput(size_hint=(None,None),width=40,height=30,multiline=False,disabled=True,
                                      text=str(input_dict["default"]))
        slider = Slider(min=input_dict["min"],max=input_dict["max"],value=input_dict["default"],step=input_dict["step"],
                        cursor_height=20,cursor_width=20)

        slider.bind(value=self.on_slider_change)
        self.add_widget(input_label)
        container.add_widget(self.text_readout)
        container.add_widget(slider)
        self.add_widget(container)

    def on_slider_change(self,instance,value):
        self.text_readout.text = str(value)

    def get_val(self):
        return float(self.text_readout.text)
