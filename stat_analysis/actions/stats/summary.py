import logging
import statistics
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)


class Summary(BaseAction):
    type = "stats.summary"
    view_name = "Summary statistics"

    def __init__(self,output_widget):
        self.user_name = "XYZ"
        self.status = "OK"
        # Define the methods implemented in this action
        # Note spaces in the action maps will be replaced with a "\n" when displayed
        self.action_maps = {
            "Mean":lambda data:statistics.mean(data),
            "Standard Deviation":lambda data:statistics.stdev(data),
            "Median":lambda data:statistics.median(data)
        }
        self.form = [
            {
                "group_name":"Data",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "data_type":"dataset",
                        "required":True,
                        "form_name":"dataset",
                        "visible_name":"Data set",
                        "on_change":lambda x,val:x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type":"combo_box",
                        "data_type":"column_numeric",
                        "get_cols_from":lambda x:x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required":True,
                        "form_name":"col",
                        "visible_name":"Column"
                    }
                ]
            },
            {
                "group_name":"Action",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "data_type":list(self.action_maps.keys()),
                        "required":True,
                        "form_name":"action",
                        "visible_name":"Data Summary"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []

    def set_tmp_dataset(self, val):
        self.tmp_dataset = val
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self):
        logger.info("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])
            col_vals = []
            row_pos = list(dataset.get_header_structure().keys()).index(vals["col"])
            for row in dataset.get_data():
                col_vals.append(row[row_pos])

            val = self.action_maps[vals["action"]](col_vals)
            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(
                headers=[vals["action"].replace(" ","\n")],data=[[str(round(val,5))]],row_default_height=60,
                row_force_default=True,orientation="horizontal",size_hint_y=None,size_hint_x=1,for_scroller=True
            ))
        else:
            self.make_err_message(self.form_errors)
