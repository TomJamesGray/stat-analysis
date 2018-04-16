import logging
from kivy.app import App
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.form_outputs import DataSpreadsheet

logger = logging.getLogger(__name__)


class ViewData(base_action.BaseAction):
    type = "data.view_data"
    view_name = "View data"

    def __init__(self,output_widget,**kwargs):
        self.form = [
            {
                "group_name": "Data set",
                "inputs": [
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":"dataset",
                        "form_name": "dataset",
                        "visible_name": "Data set"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.run_after_render = False

        if "dataset" in kwargs:
            # Dataset has been specified as a kwarg so run the action when it is rendered
            self.run_after_render = True
            # Set the form outputs and their defaults to the specified data set
            self.form[0]["inputs"][0]["default"] = kwargs["dataset"]
            self.form_outputs = {"dataset":kwargs["dataset"]}

    def render(self):
        super().render()
        if self.run_after_render:
            self.run(validate=False)

    def run(self,quiet=False,validate=True):
        logger.debug("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
        vals = self.form_outputs
        # Get data set from the name from form outputs
        cur_set = App.get_running_app().get_dataset_by_name(vals["dataset"])
        if cur_set == None:
            # Exit if somehow data set can't be found
            logger.error("Data set selected in combo box doesn't exist in app's data_sets")
            raise ValueError("Data set selected in combo box doesn't exist in app's data_sets")
        logger.debug("Using {} as cur_set".format(cur_set))
        if not quiet:
            # Modify result output area so it works better with the DataSpreadsheet widget
            self.result_output.clear_outputs(all=True)
            self.result_output.size_hint_y = 1
            self.result_output.size_hint_x = None
            self.result_output.padding = (0,0,0,5)
            # Create table to show the data sets data
            sheet = DataSpreadsheet(headers=cur_set.get_headers(),table_data=cur_set.get_data())
            # Make DataSpreadsheet fill up screen
            self.result_output.bind(height=sheet.setter("height"))
            sheet.bind(minimum_width=sheet.setter("width"))
            sheet.bind(minimum_width=self.result_output.setter("width"))

            self.result_output.add_widget(sheet)
