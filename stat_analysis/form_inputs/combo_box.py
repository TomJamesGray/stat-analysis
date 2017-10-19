from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

class FormDropDown(GridLayout):
    def __init__(self,label,inputs,*args):
        super().__init__(*args)
        self.cols=1
        self.add_widget(Label(text=label,size_hint=(None,None),height=20,color=(0,0,0,1)))
        self.dropdown = DropDown()
        for i in inputs:
            btn = Button(text=i["u_name"],size_hint_y=None,height=30)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.main_btn = Button(text="VALUE",size_hint=(None,None),height=30)
        self.main_btn.bind(on_release=self.dropdown.open)

        self.dropdown.bind(on_select=lambda instance,x:setattr(self.main_btn,'text',x))
        self.add_widget(self.main_btn)