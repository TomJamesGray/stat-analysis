import logging
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)

class GroupData(BaseAction):
    type = "data.group_data"
    view_name  = "Group Data"

    def __init__(self,output_widget):
        self.form_width = 300
        self.save_name = ""
        self.status = "OK"
        self.form = [
            {
                "group_name":"Dataset",
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
                        "form_name":"group_width_column",
                        "visible_name":"Column to group on",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                    },
                    {
                        "input_type":"numeric",
                        "required":False,
                        "form_name":"group_width_start_value",
                        "visible_name":"Starting value for groups(leave blank for lowest value)"
                    },
                    {
                        "input_type":"numeric",
                        "required":False,
                        "form_name":"group_width_width",
                        "visible_name":"Width for the groups"
                    },
                    {
                        "input_type": "check_box",
                        "required": True,
                        "form_name": "group_width_count_col",
                        "visible_name": "Add a count column"
                    },
                    {
                        "input_type":"action_columns",
                        "required":False,
                        "form_name":"group_width_action_cols",
                        "visible_name": "Column actions:",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "column_filters":["column_numeric"],
                        "actions":["Sum","Drop"]
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
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self):
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

            if vals["use_group_on_width"]:
                grouping_col_pos = list(dataset.get_header_structure().keys()).index(vals["group_width_column"])
                raw_data = dataset.get_data()
                if vals["group_width_start_value"] == None:
                    #Group width start value is blank so use the minimum value for the start
                    start_val = min(raw_data,key=lambda x:x[grouping_col_pos])[grouping_col_pos]
                else:
                    start_val = vals["group_width_start_value"]

                max_val = max(raw_data,key=lambda x:x[grouping_col_pos])[grouping_col_pos]
                width = vals["group_width_width"]
                # TODO: What if columns are called start value or width?
                column_headers = ["start_value","width"]
                if vals["group_width_count_col"]:
                    column_headers.append("count")

                col_actions = vals["group_width_action_cols"]
                for col,action in col_actions.items():
                    if action != "Drop":
                        column_headers.append(col)
                # Generate the groups in format start value, width so data in that group, x, will be
                # start < x <= start+width

                logger.info("Start value is {}".format(start_val))

