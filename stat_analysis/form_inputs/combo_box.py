import logging
from kivy.uix.dropdown import DropDown
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from stat_analysis.generic_widgets.bordered import BorderedButton
from stat_analysis.actions import base_action
from kivy.graphics import Rectangle,Color

logger = logging.getLogger(__name__)

class FormDropDown(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.parent_action = parent_action
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

        main_btn_text = ""
        self.main_btn = BorderedButton(text=main_btn_text, size_hint=(1,None), height=30, background_normal="",
                                       color=(0,0,0,1),background_color=(1,1,1,1),halign="left",valign="middle",
                                       padding=(5,5))
        self.main_btn.bind(size=self.main_btn.setter("text_size"))
        self.add_widget(self.main_btn)
        # Get the dropdown options
        if type(input_dict["data_type"]) == list:
            dropdown_options = input_dict["data"]
        elif input_dict["data_type"] == "dataset":
            dropdown_options = [x.save_name for x in App.get_running_app().datasets]
        elif input_dict["data_type"] == "column_numeric":
            dropdown_options = ["1","2","3"]
            if "get_cols_from" not in input_dict.keys():
                raise ValueError("To use column_numeric data type get_cols_from must be set")
            elif isinstance(input_dict["get_cols_from"],base_action.BaseAction):
                raise ValueError("get_cols_from {} is not an action".format(input_dict["get_cols_from"]))

            self.main_btn.bind(on_release=self.try_populate_dropdown)
            logger.info("Not adding dropdown as first one so no data set will be selected")
            main_btn_text = "Select data set first"
            dropdown_options = None
        else:
            raise ValueError("Unrecognised data type {} in form layout".format(input_dict["data_type"]))


        self.main_btn.text = main_btn_text
        # If dropdown options hasn't been set, ie if data set needs to be selected don't
        # create dropdown
        if dropdown_options != None:
            self.dropdown = DropDown()
            for i in dropdown_options:
                btn = ButtonDropDown(text=i)
                btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
                self.dropdown.add_widget(btn)
                self.main_btn.bind(on_release=self.dropdown.open)
                # Support for on_change attribute in input_dict
                if "on_change" in input_dict.keys():
                    self.dropdown.bind(on_select=lambda instance,y:[setattr(self.main_btn,'text',y),
                                                                    input_dict["on_change"](self,y)])
                self.dropdown.bind(on_select=lambda instance,y:setattr(self.main_btn,'text',y))
        elif dropdown_options == None:
            print("No dropdown options")

    def try_populate_dropdown(self,*args):
        if self.input_dict["get_cols_from"](self) == None:
            logger.debug("get_cols_from property is still none, not populating dropdown")
            return True
        else:
            dataset = self.input_dict["get_cols_from"](self)
            logger.debug("Populating dropdown with data set {}".format(dataset))


    def get_val(self):
        return self.main_btn.text


class ButtonDropDown(BorderedButton):
    b_width = NumericProperty(1)