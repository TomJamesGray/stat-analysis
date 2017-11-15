from kivy.uix.dropdown import DropDown
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from stat_analysis.generic_widgets.bordered import BorderedButton
from kivy.graphics import Rectangle,Color


class FormDropDown(GridLayout):
    def __init__(self,input_dict,*args):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 60
        self.width = 200
        self.input_dict = input_dict
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=20,color=(0,0,0,1),
                            font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)

        # Get the dropdown options
        if type(input_dict["data_type"]) == list:
            dropdown_options = input_dict["data"]
        elif input_dict["data_type"] == "dataset":
            dropdown_options = [x.save_name for x in App.get_running_app().data_sets]
        else:
            raise ValueError("Unrecognised data type {} in form layout".format(input_dict["data_type"]))

        self.dropdown = DropDown()
        for i in dropdown_options:
            btn = ButtonDropDown(text=i)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

        self.main_btn = BorderedButton(text="VALUE", size_hint=(1,None), height=30, background_normal="",
                                       color=(0,0,0,1),background_color=(1,1,1,1),halign="left",valign="middle",padding=(5,5))
        self.main_btn.bind(size=self.main_btn.setter("text_size"))

        self.main_btn.bind(on_release=self.dropdown.open)

        self.dropdown.bind(on_select=lambda instance,y:setattr(self.main_btn,'text',y))
        self.add_widget(self.main_btn)

    def get_val(self):
        return self.main_btn.text


class ButtonDropDown(BorderedButton):
    b_width = NumericProperty(1)