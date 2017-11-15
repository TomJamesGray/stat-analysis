from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox

class FormCheckBox(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.rows = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 30
        self.width = 200
        self.input_dict = input_dict
        self.check = CheckBox(size_hint=(None,None),width=30,height=30,color=(0,0,0,1))
        self.add_widget(self.check)
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=30,color=(0,0,0,1),
                            valign="middle",font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)

    def get_val(self):
        return self.check.active
