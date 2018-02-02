import numpy as np
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.resources import resource_find
from kivy.graphics import Rectangle,Color
from kivy.uix.textinput import TextInput
from stat_analysis.generic_widgets.bordered import BorderedLabel
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
            input_label = FormInputLabel(text=input_dict["visible_name"], tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])

        container = GridLayout(rows=1,height=30,width=200,size_hint=(None,None))

        self.text_readout = Label(size_hint=(None,None),width=30,height=30,text=str(input_dict["default"]),
                                          color=(.3,.3,.3,1))

        slider = Slider(min=input_dict["min"],max=input_dict["max"],value=input_dict["default"],step=input_dict["step"],
                        cursor_height=20,cursor_width=20,cursor_image=resource_find("res/slider_image.png"))

        # Draw the increments on the slider
        with slider.canvas.after:
            Color(1,0,0,1)
            for x in np.arange(0,slider.width,slider.width/input_dict["step"]):
                Rectangle(pos=(x,slider.y+slider.height/2),size=(1,10))

        slider.bind(value=self.on_slider_change)

        if "default" in input_dict.keys():
            if input_dict["default"] != None:
                slider.value = input_dict["default"]

        self.add_widget(input_label)
        container.add_widget(self.text_readout)
        container.add_widget(slider)
        self.add_widget(container)

    def on_slider_change(self,instance,value):
        if "int_only" in self.input_dict.keys():
            if self.input_dict["int_only"]:
                self.text_readout.text = str(int(value))
                return

        self.text_readout.text = str(float(value))

    def get_val(self):
        if "int_only" in self.input_dict.keys():
            if self.input_dict["int_only"]:
                return int(self.text_readout.text)

        return float(self.text_readout.text)
