import logging
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner,SpinnerOption
from stat_analysis.generic_widgets.bordered import BorderedSpinner
from stat_analysis.d_types.setup import column_d_type_maps
from collections import OrderedDict

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
                            color=(0, 0, 0, 1),font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.add_widget(input_label)
        self.cols_container = GridLayout(cols=2,row_default_height=30,row_force_default=True,size_hint=(None,None),
                                         spacing=(5,5),width=280)
        self.cols_container.bind(minimum_height=self.cols_container.setter("height"))
        self.add_widget(self.cols_container)
        self.bind(minimum_height=self.setter("height"))
        self.column_actions = OrderedDict()
        # self.height = 400

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
            # Make the column headers
            self.cols_container.add_widget(Label(text="Column",color=App.get_running_app().accent_col,font_size="14"))
            self.cols_container.add_widget(Label(text="Action", color=App.get_running_app().accent_col,font_size="14"))

            dataset = App.get_running_app().get_dataset_by_name(dataset_name)

            if "column_filters" in self.input_dict:
                # Get the allowed headers, ie column types that are in the column_filters
                # Header structure is (Name, (Column data type, converter function))

                all_headers = dataset.get_header_structure()
                allowed_headers = []
                for i,header in enumerate(list(all_headers.items())):
                    col_allowed = True
                    for restraint in self.input_dict["column_filters"]:
                        if header[1][0] not in column_d_type_maps[restraint]:
                            col_allowed = False

                    if col_allowed:
                        allowed_headers.append(header[0])

            else:
                allowed_headers = dataset.get_headers()

            for header in allowed_headers:
                self.cols_container.add_widget(Label(text=header,color=(0,0,0,1),font_size="14"))

                spin = BorderedSpinner(text=self.input_dict["actions"][0],values=self.input_dict["actions"],
                                       sync_height=True,option_cls=CustSpinnerOption,background_normal="",
                                       background_color=(1,1,1,1),color=(0,0,0,1))
                self.column_actions[header] = spin
                self.cols_container.add_widget(spin)

            self.prev_dataset_name = dataset_name

    def get_val(self):
        out = OrderedDict()
        for key,val in self.column_actions.items():
            out[key] = val.text

        return out

class CustSpinnerOption(SpinnerOption):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (229/255,229/255,229/255,1)
        self.color = (0,0,0,1)