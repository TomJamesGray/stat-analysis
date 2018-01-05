import logging
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)

class GroupData(BaseAction):
    type = "data.group_data"
    view_name  = "Group Data"

    def __init__(self,output_widget):
        self.save_name = ""
        self.status = "OK"
        self.form = [
            {
                "group_name":"",
                "inputs":[
                    {
                        "input_type": "combo_box",
                        "data_type": "dataset",
                        "required": True,
                        "form_name": "dataset",
                        "visible_name": "Data Set",
                        "on_change": lambda x, val: x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type":"string",
                        "required":True,
                        "form_name":"new_dataset_name",
                        "visible_name":"New dataset name"
                    }
                ]
            },
            {
                "group_name":"Group on width",
                "inputs":[
                    {
                        "input_type":"check_box",
                        "required":True,
                        "form_name":"use_group_on_width",
                        "visible_name":"Use Group on width"
                    },
                    {
                        "input_type":"combo_box",
                        "data_type":"column_numeric",
                        "required":False,
                        "form_name":"width_column",
                        "visible_name":"Column to group on",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                    },
                    {
                        "input_type":"string",
                        "required":False,
                        "form_name":"group_width_start_value",
                        "visible_name":"Starting value for groups(leave blank for lowest value)"
                    },
                    {
                        "input_type":"numeric",
                        "required":False,
                        "form_name":"group_width",
                        "visible_name":"Width for the groups"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []

    def set_tmp_dataset(self, val):
        self.tmp_dataset = val
        [form_item.try_populate_dropdown(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self):
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])
