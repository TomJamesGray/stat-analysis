import logging
import os
from stat_analysis.actions.base_action import BaseAction
from kivy.app import App
from stat_analysis.generic_widgets.form_outputs import ExportableGraph
from collections import OrderedDict
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class BarChart(BaseAction):
    type = "graph.bar_chart"
    view_name  = "Bar Chart"
    saveable = True

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
        """Set temporary data set so it can be accessed by form inputs"""
        self.tmp_dataset = val
        # Update the form inputs that are listening for the data set being changed
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        # Add form input to list of listeners for the data set change
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False,preloaded=False,**kwargs):
        logger.debug("Running action {}".format(self.type))

        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        # Get data set the users input
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        if dataset == False:
            # Dataset couldn't be found
            raise ValueError("Dataset {} couldn't be found".format(vals["dataset"]))

        # Get's the position in each row for the desired columns
        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        raw_data = OrderedDict()

        if vals["y_var"] == None:
            # Use the amount of occurences as the height of bars
            for row in dataset.get_data():
                if row[x_pos] in raw_data.keys():
                    # Value already exists, so increment the count
                    raw_data[row[x_pos]] += 1
                else:
                    # Value doesn't exit so add it to the raw_data dict
                    raw_data[row[x_pos]] = 1
        else:
            # Get position of y column
            y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
            for row in dataset.get_data():
                if row[x_pos] in raw_data.keys():
                    # Value already exists, so increment the count
                    raw_data[row[x_pos]] += row[y_pos]
                else:
                    # Value doesn't exit so add it to the raw_data dict
                    raw_data[row[x_pos]] = row[y_pos]

        if vals["sort_x"]:
            # Sort the bars so the x values are in ascending order
            y_data = OrderedDict(sorted(raw_data.items(),key=lambda x:x[1]))
        else:
            y_data = raw_data
        # Create graph figure and subplot
        fig = plt.figure()
        axis = plt.subplot(111)
        # Create bar chart
        axis.bar(y_data.keys(),y_data.values(),color=App.get_running_app().graph_colors[0])

        # Set axis labels
        axis.set_xlabel(vals["x_var"])

        if vals["y_var"] == None:
            axis.set_ylabel("Count")
        else:
            axis.set_ylabel(vals["y_var"])

        axis.legend()
        # Find path to save the graph image and save it
        path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
        fig.savefig(path)

        if not quiet:
            self.result_output.clear_outputs()
            # Show the graph
            self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))


