import logging
import copy
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
                        "on_change":lambda x,val:x.parent_action.form_add_cols(val),
                        # Setting this means an infinite loop of calling on_change and re-rendering doesn't occur
                        "run_on_default_set": False
                    }
                ]
            }
        ]
        self.form = self.base_form
        self.output_widget = output_widget

    def form_add_cols(self,dataset_name,set_dataset_selector=True,re_render=True):
        # Get data set that is being modified
        self.dataset = App.get_running_app().get_dataset_by_name(dataset_name)
        # Copy the base_form, don't reference it
        self.form = self.base_form[:]
        if set_dataset_selector:
            # Set the default for the dataset selector to the currently selected dataset
            self.form[0]["inputs"][0]["default"] = dataset_name

        col_pos = 0
        for col_name,col_struc in self.dataset.get_header_structure().items():
            # Go through each column in the data set and add a form input for it with
            # the column name and a combo box of possible data types
            self.form.append({
                "group_name":"Column {}".format(col_pos),
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
        # Clear the form that is being currently displayed and re-render it with the new inputs
        # for the chosen data set
        self.output_widget.clear_widgets()
        if re_render:
            self.render()

    def run(self):
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            vals = self.form_outputs
            logger.debug("Form validated, form outputs: {}".format(vals))

            # Make copies of the stored data and header structure in case this causes all data to be lost
            stored_data_copy = copy.copy(self.dataset.get_data())
            header_struct_copy = copy.copy(self.dataset.get_header_structure())

            n_cols = len(self.dataset.get_headers())
            header_struct = OrderedDict()
            for i in range(0,n_cols):
                # Get the converter function for the user specified data type
                convert = types[vals["{}_type".format(i)]]["convert"]
                # Create the header structure record with the data type name and converter function
                header_struct[vals["{}_name".format(i)]] = (vals["{}_type".format(i)],convert)

            logger.info("Header structure generated: {}".format(header_struct))
            # Set the header structure of the data set
            self.dataset.set_header_structure(header_struct)
            # Make sure there are more than 0 records
            if self.dataset.records == 0:
                # This set_cols_type has caused all the records to be dropped, so restore dataset
                # to prev state
                self.make_err_message("Generated dataset has length zero. Likely caused by setting a column to a "
                                      "value that would cause errors, ie trying to pass strings as integers. "
                                      "Restoring dataset")
                # Reset data set data
                self.dataset.set_data(stored_data_copy)
                # Reset data set header structure
                self.dataset.set_header_structure(header_struct_copy)
                return

            self.result_output.clear_outputs()
            # Add an output table showing the amount of records, columns and the column -> data type relationships
            self.result_output.add_widget(BorderedTable(
                headers=["Records","Columns","Data types"],data=[[str(self.dataset.records)],[str(self.dataset.columns)],
                [str((", ".join((["{} -> {}".format(x,y[0]) for x,y in header_struct.items()]))))]],
                row_default_height=30, row_force_default=True,orientation="horizontal",for_scroller=True,
                size_hint_x=1,size_hint_y=None))
        else:
            # Create error message with the form errors
            self.make_err_message(self.form_errors)
