import logging
import numpy as np
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from kivy.app import App
from kivy.uix.image import Image
from collections import OrderedDict
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class BarChart(BaseAction):
    type = "graph.bar_chart"
    view_name  = "Bar Chart"

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
                        "tip":"If left blank the count for the x variable is used"
                    },
                    {
                        "input_type":"check_box",
                        "required":True,
                        "form_name":"sort_x",
                        "visible_name":"Sort the data on the X variable"
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

    def run(self):
        logger.debug("Running action {}".format(self.type))
        if self.validate_form():
            logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
            vals = self.form_outputs
            dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])
            # Get's the position in each row for the desired columns
            x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
            raw_data = OrderedDict()

            if vals["y_var"] == None:
                for row in dataset.get_data():
                    if row[x_pos] in raw_data.keys():
                        raw_data[row[x_pos]] += 1
                    else:
                        raw_data[row[x_pos]] = 1
            else:
                y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
                for row in dataset.get_data():
                    if row[x_pos] in raw_data.keys():
                        raw_data[row[x_pos]] += row[y_pos]
                    else:
                        raw_data[row[x_pos]] = row[y_pos]

            x_data = range(len(raw_data))
            if vals["sort_x"]:
                y_data = OrderedDict(sorted(raw_data.items(),key=lambda x:x[1]))
            else:
                y_data = raw_data

            fig = plt.figure()
            axis = plt.subplot(111)
            axis.bar(x_data,y_data.values())
            plt.xticks(x_data,y_data.keys())
            # Set axis labels
            plt.xlabel(vals["x_var"])
            if vals["y_var"] == None:
                plt.ylabel("Count")
            else:
                plt.ylabel(vals["y_var"])

            axis.legend()
            fig.savefig("tmp/plot.png")

            self.result_output.clear_outputs()
            self.result_output.add_widget(Image(source="tmp/plot.png", nocache=True, size_hint_x=1, size_hint_y=None,
                                                height=500))