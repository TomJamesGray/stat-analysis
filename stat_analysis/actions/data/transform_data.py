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
        self.save_name = "XYZ"
        self.status = "OK"
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
                    {
                        "input_type": "check_box",
                        "required":True,
                        "form_name":"overwrite_existing_set",
                        "visible_name":"Add column to existing dataset",
                    },
                    {
                        "input_type":"string",
                        "required":False,
                        "form_name":"new_name",
                        "visible_name":"Save name for new dataset",
                        "tip":"Required if existing dataset is not being modified"
                    }
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
        self.tmp_dataset = val
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False):
        logger.debug("Running action {}".format(self.type))

        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
        vals = self.form_outputs
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])
        if dataset == False:
            # Dataset couldn't be found, this is likely happening when loading
            return False
        # Get the position in each row for the column
        col_pos = list(dataset.get_header_structure().keys()).index(vals["transform_col"])
        transform_func = self.simple_transforms[vals["transform_name"]]

        new_data = [transform_func(x[col_pos]) for x in dataset.get_data()]
        dataset.add_column(new_data,col_type="float",col_name=vals["new_col_name"])

        self.save_name = None
        App.get_running_app().add_action(self)
        return True

    def load(self,state):
        self.form_outputs = state["form_outputs"]
        if not self.run(validate=False,quiet=True):
            return False

        return True