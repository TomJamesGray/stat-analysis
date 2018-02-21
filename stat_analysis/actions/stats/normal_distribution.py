import logging
import os.path
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)


class NormalDistribution(BaseAction):
    type = "stats.normal_distribution"
    view_name = "Normal Distribution"
    help_text = \
"""[size=16][b]Normal distribution[/b][/size]

This action creates a normal distribution from a given dataset by calculating the mean [font=res/equation.otf]μ[/font] and the variance [font=res/equation.otf]σ[sup]2[/sup][/font]. Then the probability density function is created using the formula:

[font=res/equation.otf][size=20](1/√2π) · exp(-(x-μ)[sup]2[/sup]/2σ[sup]2[/sup])[/size][/font]

where exp is the exponential function ie [font=res/equation.otf][size=16] e[sup]x[/sup] = exp(x)[/size][/font]

[b]Inputs[/b]

Show data bars displays a bar chart of the probability that a random value would fall into this category.

To get a probability from the generated normal distribution you can input the "x" values to get the corresponding value from the generated probability density function. To get the probabilities for multiple x values you can separate the values with commas.

[b]Example[/b]

A good example dataset is the "heights" example dataset as if you run the normal distribution action with the column "height" and enable "Show data bars" (this displays a bar chart of the data) you can see the data fits the generated probability density function reasonably well.
"""
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
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        col_data = []
        col_pos = list(dataset.get_header_structure().keys()).index(vals["col"])

        for row in dataset.get_data():
            col_data.append(row[col_pos])

        variance = np.var(col_data)
        mean = np.mean(col_data)
        if not quiet:
            self.result_output.clear_outputs()
            # This is the normal distribution function
            y_func = lambda x:(1/(2*np.pi*variance)**0.5) * np.e ** (-(x-mean)**2/(2*variance))

            # Get x values for the line
            x_line = np.linspace(min(col_data),max(col_data),500)
            y_line = [y_func(x) for x in x_line]

            if vals["predict_on"] != None:
                predicted_vals = [str("{:.3g}".format(y_func(value))) for value in vals["predict_on"]]
                self.result_output.add_widget(BorderedTable(
                    headers=[vals["col"], "Probability"], data=[[str(x) for x in vals["predict_on"]], predicted_vals],
                    row_default_height=40, row_force_default=True, orientation="vertical", size_hint_y=None,
                    for_scroller=True
                ))

            fig = plt.figure()
            axis = plt.subplot(111)
            axis.plot(x_line,y_line,color=App.get_running_app().graph_colors[0])

            if vals["show_bars"]:
                # Get the x values
                x_vals = set(col_data)
                x_counts = {}
                for val in col_data:
                    if val in x_counts.keys():
                        x_counts[val] += 1
                    else:
                        x_counts[val] = 1

                x_counts = OrderedDict(sorted(x_counts.items(),key=lambda x:x[0]))

                x_relative_freq = [x/len(col_data) for x in x_counts.values()]
                axis.bar(list(x_vals),x_relative_freq,color=App.get_running_app().graph_colors[1])

            axis.set_xlabel(vals["col"])
            axis.set_ylabel("Probability Density")

            axis.legend()
            path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
            fig.savefig(path)

            self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))