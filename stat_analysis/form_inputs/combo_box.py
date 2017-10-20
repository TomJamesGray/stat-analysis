from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from kivy.graphics import Rectangle,Color


class FormDropDown(GridLayout):
    def __init__(self,input_dict,*args):
        super().__init__(*args)
        self.cols=1
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=20,color=(0,0,0,1))
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)

        self.dropdown = DropDown()
        for i in ["1","2","3"]:
            btn = ButtonDropDown(text=i,size_hint=(None,None),b_width=5)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        self.main_btn = BorderedButton(text="VALUE")
        self.main_btn.bind(on_release=self.dropdown.open)

        self.dropdown.bind(on_select=lambda instance,y:setattr(self.main_btn,'text',y))
        self.add_widget(self.main_btn)


class BorderedButton(Button):
    b_width = NumericProperty(1)


class ButtonDropDown(BorderedButton):
    b_width = NumericProperty(1)