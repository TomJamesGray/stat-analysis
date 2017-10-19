from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
# from stat_analysis.main import BorderedButton
from stat_analysis import main
class FormDropDown(GridLayout):
    def __init__(self,label,inputs,*args):
        super().__init__(*args)
        self.cols=1
        input_label = Label(text=label,halign="left",size_hint=(1,None),height=20,color=(0,0,0,1))
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)

        self.dropdown = DropDown()
        for i in inputs:
            btn = Button(text=i["u_name"],size_hint_y=None,height=30)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.main_btn = main.BorderedButton(text="VALUE",size_hint=(None,None),background_color=(1,1,1,1),
                               background_normal="",color=(0,0,0,1),height=30,b_width=2)
        self.main_btn.bind(on_release=self.dropdown.open)

        self.dropdown.bind(on_select=lambda instance,x:setattr(self.main_btn,'text',x))
        self.add_widget(self.main_btn)