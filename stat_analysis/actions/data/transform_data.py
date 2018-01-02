import logging
import numpy as np
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)

class TransformData(BaseAction):
    type = "data.transform_data"
    view_name  = "Transform Data"

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
                        "form_name":"new_col_name"
                        "visible_name":"New Column Name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.tmp_dataset = None

    def set_tmp_dataset(self,val):
        self.tmp_dataset = val


    def run(self):
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs