from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
# from stat_analysis.main import BorderedButton
from stat_analysis import main


class FormDropDown(GridLayout):
    def __init__(self,label,inputs,*args):
        super().__init__(*args)
        self.cols=1
        input_label = Label(text=label,halign="left",size_hint=(1,None),height=20,color=(0,0,0,1))
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)
        input_vals = tuple([x["u_name"] for x in inputs])

        self.spinner = Spinner(text=label,values=input_vals,size_hint=(None,None))
        self.add_widget(self.spinner)