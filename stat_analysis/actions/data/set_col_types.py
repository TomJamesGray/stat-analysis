import logging
from kivy.app import App
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.d_types import types
from collections import OrderedDict

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

    def form_add_cols(self,dataset_name,set_dataset_selector=True,re_render=True):
        self.dataset = App.get_running_app().get_dataset_by_name(dataset_name)
        # Copy the base_form, don't reference it
        self.form = self.base_form[:]
        if set_dataset_selector:
            # Set the default for the dataset selector to the currently selected dataset
            self.form[0]["inputs"][0]["default"] = dataset_name

        col_pos = 0
        for col_name,col_struc in self.dataset.get_header_structure().items():
            self.form.append({
                "group_name":"Column: {}".format(col_pos),
                "inputs":[
                    {
                        "input_type":"string",
                        "required":True,
                        "form_name":"{}_name".format(col_pos),
                        "default":col_name,
                        "visible_name":"Column Name:"
                    },
                    {
                        "input_type": "combo_box",
                        "required": True,
                        "data_type":list(types.keys()),
                        "form_name": "{}_type".format(col_pos),
                        "visible_name": "Data Type:",
                        "default":col_struc[0]
                    }
                ]
            })
            col_pos += 1
        self.output_widget.clear_widgets()
        if re_render:
            self.render()

    def run(self):
        logger.info("Running action {}".format(self.type))
        if self.validate_form():
            vals = self.form_outputs
            logger.info("Form validated, form outputs: {}".format(vals))

            n_cols = len(self.dataset.get_headers())
            header_struct = OrderedDict()
            for i in range(0,n_cols):
                convert = types[vals["{}_type".format(i)]]["convert"]
                header_struct[vals["{}_name".format(i)]] = (vals["{}_type".format(i)],convert)

            logger.info("Header structure generated: {}".format(header_struct))
            self.dataset.set_header_structure(header_struct)
