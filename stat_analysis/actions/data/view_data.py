import logging
from kivy.app import App
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable

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
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            cur_set = None
            # From the name selected in the combo box get the actual stored data set
            # TODO: What if the name of data set is repeated?
            for d_set in App.get_running_app().datasets:
                if d_set.save_name == vals["data_set"]:
                    cur_set = d_set
                    break
            if cur_set == None:
                # This should never happen
                logger.error("Data set selected in combo box doesn't exist in app's data_sets")
                raise ValueError("Data set selected in combo box doesn't exist in app's data_sets")
            logger.debug("Using {} as cur_set".format(cur_set))
            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(headers=cur_set.get_headers(),table_data=cur_set.get_data(),
                                                        row_default_height=30,row_force_default=True,for_scroller=True,
                                                        size_hint_x=1,size_hint_y=None))
