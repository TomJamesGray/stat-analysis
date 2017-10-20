from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import SpinnerOption
# from stat_analysis.main import BorderedSpinner
from stat_analysis import main
from kivy.properties import NumericProperty
from kivy.graphics import Rectangle,Color


class FormDropDown(GridLayout):
    def __init__(self,input_dict,*args):
        super().__init__(*args)
        self.cols = 1
        self.height = 40
        self.size_hint_y = None
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=20,color=(0,0,0,1))
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)
        # TODO Add actual handler for the different data types that can be entered
        input_vals = ("A","B","C","D")

        self.spinner = main.BorderedSpinner(text=input_dict["visible_name"],values=input_vals,size_hint=(None,None),
                                            background_color=(1,1,1,1),background_normal="",color=(0,0,0,1),height=20,
                                            option_cls=FormDropDownOption,width=160)
        self.add_widget(self.spinner)

    def make_border_options(self,*args):
        with self.spinner.canvas.after:
            Color(1,0,0,1)
            Rectangle(pos=(self.x-1,self.y-1),size=(self.width+2,self.height+2+80))

class FormDropDownOption(SpinnerOption):
    b_width = NumericProperty(1)