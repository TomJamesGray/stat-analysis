from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import SpinnerOption
# from stat_analysis.main import BorderedSpinner
from stat_analysis import main


class FormDropDown(GridLayout):
    def __init__(self,label,inputs,*args):
        super().__init__(*args)
        self.cols=1
        input_label = Label(text=label,halign="left",size_hint=(1,None),height=20,color=(0,0,0,1))
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)
        input_vals = tuple([x["u_name"] for x in inputs])

        self.spinner = main.BorderedSpinner(text=label,values=input_vals,size_hint=(None,None),background_color=(1,1,1,1),
                               background_normal="",color=(0,0,0,1),height=20,option_cls=FormDropDownOption)
        self.add_widget(self.spinner)

class FormDropDownOption(SpinnerOption):
    pass