import logging
from kivy.uix.dropdown import DropDown
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty,ListProperty,BooleanProperty
from stat_analysis.generic_widgets.bordered import BorderedButton
from kivy.uix.button import Button
from kivy.core.window import Window
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.form_inputs import FormInputLabel
from stat_analysis.d_types.setup import column_d_type_maps

logger = logging.getLogger(__name__)


class FormDropDown(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.parent_action = parent_action
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.bind(minimum_height=self.setter("height"))
        self.width = 200
        self.input_dict = input_dict

        # Add a tooltip if specified
        if "tip" in input_dict.keys():
            input_label = FormInputLabel(text=input_dict["visible_name"],tip=input_dict["tip"])
        else:
            input_label = FormInputLabel(text=input_dict["visible_name"])


        self.add_widget(input_label)
        self.prev_dataset_name = None

        self.main_btn = BorderedButton(size_hint=(1,None), height=30, background_normal="",
                                       color=(0,0,0,1),background_color=(1,1,1,1),halign="left",valign="middle",
                                       padding=(5,5),b_color=(190/255,190/255,190/255,1),background_down="")
        self.main_btn.bind(size=self.main_btn.setter("text_size"))
        self.add_widget(self.main_btn)

        # Add the form item to any specified listeners
        if "add_dataset_listener" in input_dict.keys():
            logger.info("Adding form item to dataset listener group")
            input_dict["add_dataset_listener"](self)

        # Get the dropdown options
        if type(input_dict["data_type"]) == list:
            # Dropdown options is just a set of values in a list
            dropdown_options = input_dict["data_type"]
        elif input_dict["data_type"] == "dataset":
            dropdown_options = [x.save_name for x in App.get_running_app().datasets]

        elif input_dict["data_type"] == "column_numeric" or input_dict["data_type"] == "column":
            # Data type is numeric columns. This data_type relies on a get_cols_from key
            #  being set, so the column names for the dataset can be retrieved
            if "get_cols_from" not in input_dict.keys():
                raise ValueError("To use column data type get_cols_from must be set")
            elif isinstance(input_dict["get_cols_from"],base_action.BaseAction):
                raise ValueError("get_cols_from {} is not an action".format(input_dict["get_cols_from"]))

            self.main_btn.bind(on_release=self.dropdown_open)
            logger.info("Not adding dropdown as first one so no data set will be selected")
            self.main_btn_text = "Select data set first"
            dropdown_options = None
        else:
            raise ValueError("Unrecognised data type {} in form layout".format(input_dict["data_type"]))

        if "default" in input_dict.keys():
            self.main_btn_text = input_dict["default"]
            print(input_dict)
            if "on_change" in input_dict.keys():
                if input_dict.get("run_on_default_set",True):
                    input_dict["on_change"](self, self.main_btn_text)

        else:
            self.main_btn_text = ""

        self.main_btn.text = self.main_btn_text

        # If dropdown options hasn't been set, ie if data set needs to be selected don't
        # create dropdown
        if dropdown_options != None:
            self.mk_dropdown(dropdown_options)

    def try_populate(self,quiet=False,*args):
        """
        Try and populate the dropdown with values from the specified data set.
        The specified data set will be referenced by name in the get_cols_from key
        in the input dict
        """
        dataset_name = self.input_dict["get_cols_from"](self)

        if dataset_name == None:
            logger.info("get_cols_from property is still none, not populating dropdown")
            return True
        elif self.prev_dataset_name != dataset_name:
            # Dataset has been changed so repopulate dropdown
            logger.info("Populating dropdown with data set {}".format(dataset_name))
            dataset = App.get_running_app().get_dataset_by_name(dataset_name)

            # Only get columns for the specified data type
            headers = []
            allowed_types = column_d_type_maps[self.input_dict["data_type"]]

            for name,desc in dataset.get_header_structure().items():
                if desc[0] in allowed_types:
                    headers.append(name)

            self.main_btn.unbind(on_release=self.try_populate)
            logger.info("Populating dropdown with {}".format(headers))
            self.prev_dataset_name = dataset_name
            self.mk_dropdown(headers)
            if not quiet:
                self.dropdown.open(self.main_btn)
            else:
                logger.debug("Parent dataset has been changed, resetting main_btn_text")
                self.main_btn.text = ""
                self.main_btn_text = ""
        else:
            if not quiet:
                # Dataset hasn't been changed so re open dropdown without repopulating
                self.dropdown.open(self.main_btn)

    def dropdown_open(self,*args):
        """
        Generic function to open the dropdown, done so that if the drop down is
        using "get_cols_from" it can try and repopulate the options if the dataset
        changes
        """
        if "get_cols_from" in self.input_dict.keys():
            self.try_populate()
        elif self.input_dict["data_type"] == "dataset":
            # Remake the dropwon with the list of datasets, because this could change
            # if an "example dataset" is imported
            self.mk_dropdown([x.save_name for x in App.get_running_app().datasets])
            self.dropdown.open(self.main_btn)
        else:
            self.dropdown.open(self.main_btn)

    def mk_dropdown(self,dropdown_options):
        self.dropdown = DropDown()
        for i,txt in enumerate(dropdown_options):
            if i == len(dropdown_options)-1:
                btn = ButtonDropDown(text=txt,bottom=True)
            else:
                btn = ButtonDropDown(text=txt)
            Window.bind(mouse_pos=btn.mouse_pos)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))

            self.dropdown.add_widget(btn)
            self.main_btn.bind(on_release=self.dropdown_open)
            # Support for on_change attribute in input_dict
            if "on_change" in self.input_dict.keys():
                self.dropdown.bind(on_select=lambda instance, y: [setattr(self.main_btn, 'text', y),
                                                                  self.input_dict["on_change"](self, y)])
            else:
                self.dropdown.bind(on_select=lambda instance, y: setattr(self.main_btn, 'text', y))

    def get_val(self):
        if self.main_btn_text == self.main_btn.text and "default" not in self.input_dict.keys():
            # Main button hasn't been changed therefore combo box isn't selected
            return None
        return self.main_btn.text


class ButtonDropDown(Button):
    b_width = NumericProperty(1)
    b_color = ListProperty([190/255, 190/255, 190/255, 1])
    hovering = BooleanProperty(False)
    bottom = BooleanProperty(False)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering and collision:
            # Mouse moved within the button
            return
        elif collision and not self.hovering:
            # Mouse enter button
            self.background_color = (210/255,210/255,210/255,1)
        elif self.hovering and not collision:
            # Mouse exit button
            self.background_color = (1,1,1,1)

        self.hovering = collision