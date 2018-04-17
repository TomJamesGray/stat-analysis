import logging
import os
from stat_analysis.actions.base_action import BaseAction
from kivy.app import App
from stat_analysis.generic_widgets.form_outputs import ExportableGraph
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ScatterPlot(BaseAction):
    type = "graph.scatter"
    view_name  = "Scatter Plot"
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

        if not quiet:
            # Get data set the users input
            dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

            if dataset == False:
                # Dataset couldn't be found
                raise ValueError("Dataset {} couldn't be found".format(vals["dataset"]))

            x,y = [],[]
            # Get's the position in each row for the desired columns
            x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
            y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
            # Create lists of the x and y column data
            for row in dataset.get_data():
                x.append(row[x_pos])
                y.append(row[y_pos])
            # Create graph figure and subplot
            fig = plt.figure()
            axis = plt.subplot(111)
            # Create scatter plot
            axis.scatter(x,y,color=App.get_running_app().graph_colors[0])
            # Set axis labels
            axis.set_xlabel(vals["x_var"])
            axis.set_ylabel(vals["y_var"])

            axis.legend()
            # Find path to save the graph image and save it
            path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
            fig.savefig(path)

            self.result_output.clear_outputs()
            # Show the graph
            self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))


