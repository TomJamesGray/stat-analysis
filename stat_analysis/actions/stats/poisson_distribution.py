import logging
import os.path
import numpy as np
import math
import matplotlib.pyplot as plt
from collections import OrderedDict
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)


class PoissonDistribution(BaseAction):
    type = "stats.poisson_distribution"
    view_name = "Poisson Distribution"
    saveable = True

    def __init__(self,output_widget):
        self.user_name = "XYZ"
        self.status = "OK"
        self.form = [
            {
                "group_name":"Data",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "data_type":"dataset",
                        "required":True,
                        "form_name":"dataset",
                        "visible_name":"Data set",
                        "on_change":lambda x,val:x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type":"combo_box",
                        "data_type":"column_numeric",
                        "get_cols_from":lambda x:x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required":True,
                        "form_name":"col",
                        "visible_name":"Column"
                    }
                ]
            },
            {
                "group_name":"Distribution options",
                "inputs":[
                    {
                        "input_type":"check_box",
                        "form_name":"show_bars",
                        "visible_name":"Show data bars",
                        "required":True
                    },
                    {
                        "input_type":"numeric",
                        "required":False,
                        "allow_comma_separated":True,
                        "form_name":"predict_on",
                        "visible_name":"Get probability for values",
                        "tip":"For multiple values input them with commas separating them"
                    }
                ]
            },
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

    def run(self, validate=True, quiet=False, use_cached=False, **kwargs):
        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        # Get data set from the users input
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        col_data = []
        # Get index of column in data set
        col_pos = list(dataset.get_header_structure().keys()).index(vals["col"])

        for row in dataset.get_data():
            # Get column data in separate list
            col_data.append(row[col_pos])
        # Calculate the mean, this is the only input for the Poisson distribution
        mean = np.mean(col_data)

        if not quiet:
            self.result_output.clear_outputs()
            # Poisson distribution function
            y_func = lambda x:(np.e ** - mean)*((mean**x)/math.factorial(x))

            # Get x values for the line and use the poisson function on them
            x_line = list(range(min(col_data),max(col_data)+1,1))
            y_line = [y_func(x) for x in x_line]

            if vals["predict_on"] != None:
                # Get probabilities for user given values
                predicted_vals = [str("{:.3g}".format(y_func(value))) for value in vals["predict_on"]]
                self.result_output.add_widget(BorderedTable(
                    headers=[vals["col"], "Probability"], data=[[str(x) for x in vals["predict_on"]], predicted_vals],
                    row_default_height=40, row_force_default=True, orientation="vertical", size_hint_y=None,
                    for_scroller=True
                ))
            # Create graph and subplot
            fig = plt.figure()
            axis = plt.subplot(111)
            # Plot the poisson function
            axis.plot(x_line,y_line,color=App.get_running_app().graph_colors[0])

            if vals["show_bars"]:
                # Show the relative frequency bars for the actual data
                x_vals = set(col_data)
                # Dictionary to store the amount of occurences of x values
                x_counts = {}
                for val in col_data:
                    if val in x_counts.keys():
                        # Value already exists in the x count so increment it
                        x_counts[val] += 1
                    else:
                        # Value doesn't already exist in the x count so create the key
                        x_counts[val] = 1
                # Sort the x data into amending order so it matches the poisson line
                x_counts = OrderedDict(sorted(x_counts.items(),key=lambda x:x[0]))

                x_relative_freq = [x/len(col_data) for x in x_counts.values()]
                # Plot the relative frequency bars
                axis.bar(list(x_vals),x_relative_freq,color=App.get_running_app().graph_colors[1])
            # Set the axis labels
            axis.set_xlabel(vals["col"])
            axis.set_ylabel("Probability Density")

            axis.legend()
            # Make the path for the graph image and save it
            path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
            fig.savefig(path)
            # Show the graph
            self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))
