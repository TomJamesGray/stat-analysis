import logging
from kivy.app import App
from stat_analysis.actions import base_action

logger = logging.getLogger(__name__)


class ViewData(base_action.BaseAction):
    type = "data.view_data"
    view_name = "View data"

    def __init__(self,output_widget):
        self.save_name = "XYZ"
        self.status = "OK"
        self.form = [
            {
                "group_name": "Data set",
                "inputs": [
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":"dataset",
                        "form_name": "data_set",
                        "visible_name": "Data set"
                    }
                ]
            }
        ]
        self.output_widget = output_widget

    def run(self):
        logger.info("Running action {}".format(self.type))
        if self.validate_form():
            logger.info("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            for d_set in App.get_running_app().data_sets:
                if d_set.save_name == vals["data_set"]:
                    cur_set = d_set
                    break
            print(cur_set)