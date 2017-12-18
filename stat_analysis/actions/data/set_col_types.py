import logging
from kivy.app import App
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.d_types import types

logger = logging.getLogger(__name__)


class SetColTypes(base_action.BaseAction):
    type = "data.set_types"
    view_name = "Set Column Data Types"

    def __init__(self,output_widget):
        self.save_name = "XYZ"
        self.status = "OK"
        self.base_form = [
            {
                "group_name": "Data set",
                "inputs": [
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":"dataset",
                        "form_name": "data_set",
                        "visible_name": "Data set",
                        "on_change":lambda x,val:x.parent_action.form_add_cols(val)
                    }
                ]
            }
        ]
        self.form = self.base_form
        self.output_widget = output_widget

    def form_add_cols(self,dataset_name):
        dataset = App.get_running_app().get_dataset_by_name(dataset_name)
        # Copy the base_form, don't reference it
        self.form = self.base_form[:]
        # Set the default for the dataset selector to the currently selected dataset
        self.form[0]["inputs"][0]["default"] = dataset_name

        for col_name,col_struc in dataset.get_header_structure().items():
            self.form.append({
                "group_name":"Column: {}".format(col_name),
                "inputs":[
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":list(types.keys()),
                        "form_name": "type_{}".format(col_name),
                        "visible_name": "{} Data Type:".format(col_name),
                        "default":col_struc[0]
                    }
                ]
            })
        self.output_widget.clear_widgets()
        self.render()

    def run(self):
        logger.info("Running action {}".format(self.type))
        if self.validate_form():
            logger.info("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs

