import logging
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

logger = logging.getLogger(__name__)

class ActionColumns(GridLayout):
    def __init__(self,input_dict,parent_action,*args):
        super().__init__(*args)
        self.parent_action = parent_action
        self.cols = 1
        self.size_hint = (None,None)
        self.width = 300
        self.input_dict = input_dict
        self.prev_dataset_name = None
        input_label = Label(text=input_dict["visible_name"], halign="left", size_hint=(1, None), height=20,
                            color=(0, 0, 0, 1),
                            font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)
        self.cols_container = GridLayout(cols=2,row_default_height=30,row_force_default=True)
        self.add_widget(self.cols_container)

        logger.info("Adding form item to dataset listener group")
        input_dict["add_dataset_listener"](self)

    def try_populate(self,quiet=False):
        dataset_name = self.input_dict["get_cols_from"](self)

        if dataset_name == None:
            logger.info("get_cols_from property is still none, not populating dropdown")
            return True
        elif self.prev_dataset_name != dataset_name:
            # Dataset has been changed so repopulate dropdown
            logger.info("Populating dropdown with data set {}".format(dataset_name))
            dataset = App.get_running_app().get_dataset_by_name(dataset_name)
            for header in dataset.get_headers():
                self.cols_container.add_widget(Label(text=header,color=(0,0,0,1)))
                self.cols_container.add_widget(
                    Spinner(text=self.input_dict["actions"][0],values=self.input_dict["actions"]))

            self.prev_dataset_name = dataset_name