import logging
import numpy as np
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)


class TransformData(BaseAction):
    type = "data.transform_data"
    view_name = "Transform Data"

    def __init__(self,output_widget):
        self.status = "OK"
        # Define the transforms that can be done on columns
        self.simple_transforms = {
            "Square":lambda x:x**2,
            "Cube":lambda x:x**3,
            "Exponent":lambda x:np.exp(x),
            "Natural Log":lambda x:np.log(x),
            "Log (base 10)":lambda x:np.log10(x)
        }
        self.form = [
            {
                "group_name":"Column",
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
                        "input_type": "combo_box",
                        "data_type": "column_numeric",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "transform_col",
                        "visible_name": "Column to transform"
                    },
                ]
            },
            {
                "group_name":"Transformation",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "data_type":list(self.simple_transforms.keys()),
                        "required":True,
                        "form_name":"transform_name",
                        "visible_name":"Transformation"
                    },
                    {
                        "input_type":"string",
                        "required":True,
                        "form_name":"new_col_name",
                        "visible_name":"New Column Name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []

    def set_tmp_dataset(self, val):
        """Set temporary data set so it can be accessed by form inputs"""
        self.tmp_dataset = val
        # Update the form inputs that are listening for the data set being changed
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        # Add form input to list of listeners for the data set change
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False):
        logger.debug("Running action {}".format(self.type))

        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        # Get data set the user chose
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        if dataset == False:
            # Dataset couldn't be found, this is likely happening when loading
            raise ValueError("Dataset {} couldn't be found".format(vals["dataset"]))
        # Get the position in each row for the column
        col_pos = list(dataset.get_header_structure().keys()).index(vals["transform_col"])
        # Get the function that is going to be used to transform the values
        transform_func = self.simple_transforms[vals["transform_name"]]

        # Get the new values and add them as a column to the data set
        new_data = [transform_func(x[col_pos]) for x in dataset.get_data()]
        dataset.add_column(new_data,col_type="float",col_name=vals["new_col_name"])

        # Set save_name to None so this action doesn't appear on the home screen but is still saved
        self.save_name = None
        App.get_running_app().add_action(self)
        if not quiet:
            # Add an output table showing the amount of records, columns and the column -> data type relationships
            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(
                headers=["Records", "Columns", "Data types"],
                data=[[str(dataset.records)], [str(dataset.columns)],
                      [str((", ".join((["{} -> {}".format(x, y[0]) for x, y in dataset.get_header_structure().items()]))))]],
                row_default_height=30, row_force_default=True, orientation="horizontal", for_scroller=True,
                size_hint_x=1, size_hint_y=None))
        return True

    def load(self,state):
        self.form_outputs = state["form_outputs"]
        try:
            success = self.run(validate=False,quiet=True)
        except Exception as e:
            err = "Error in loading transform data\n{}".format(repr(e))
            logger.error(err)
            return err
        return True

