import logging
import numpy as np
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from kivy.app import App
from stat_analysis.generic_widgets.form_outputs import ExportableGraph
from collections import OrderedDict
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ScatterPlot(BaseAction):
    type = "graph.scatter"
    view_name  = "Scatter Plot"

    def __init__(self,output_widget):
        self.save_name = ""
        self.status = "OK"
        self.form = [
            {
                "group_name":"Dataset",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "required":True,
                        "data_type":"dataset",
                        "form_name":"dataset",
                        "visible_name":"Data set",
                        "on_change": lambda x, val: x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "x_var",
                        "visible_name": "X Variable"
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": False,
                        "form_name": "y_var",
                        "visible_name": "Y Variable",
                    }
                ]
            },
            {
                "group_name":"Save",
                "inputs":[
                    {
                        "input_type":"check_box",
                        "required":True,
                        "form_name":"save_action",
                        "visible_name":"Save action"
                    },
                    {
                        "input_type":"string",
                        "required":True,
                        "visible_name":"Action save name",
                        "form_name":"action_save_name"
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

    def run(self,validate=True,quiet=False,preloaded=False,**kwargs):
        logger.debug("Running action {}".format(self.type))

        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        if dataset == False:
            # Dataset couldn't be found
            raise ValueError("Dataset {} couldn't be found".format(vals["dataset"]))

        x,y = [],[]
        # Get's the position in each row for the desired columns
        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
        for row in dataset.get_data():
            x.append(row[x_pos])
            y.append(row[y_pos])

        fig = plt.figure()
        axis = plt.subplot(111)

        axis.scatter(x,y)
        # Set axis labels
        axis.set_xlabel(vals["x_var"])
        axis.set_ylabel(vals["y_var"])

        axis.legend()
        fig.savefig("tmp/plot.png")

        if not quiet:
            self.result_output.clear_outputs()
            self.result_output.add_widget(ExportableGraph(source="tmp/plot.png", fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))

        if vals["save_action"] and not preloaded:
            # Save the action
            self.save_name = vals["action_save_name"]
            try:
                App.get_running_app().add_action(self)
            except ValueError:
                logger.error("Dataset with that name already exists")


