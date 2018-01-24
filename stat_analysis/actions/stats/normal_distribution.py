import logging
import statistics
import numpy as np
import matplotlib.pyplot as plt
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)


class NormalDistribution(BaseAction):
    type = "stats.normal_distribution"
    view_name = "Normal Distribution"

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

    def run(self, validate=True, quiet=False, preloaded=False, use_cached=False, **kwargs):
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

        variance = statistics.variance(col_data)
        mean = statistics.mean(col_data)

        if not quiet:
            # Get x values for the line
            x_line = np.arange(min(col_data),max(col_data),(max(col_data)-min(col_data))/100)
            y_line = [(1/(2*np.pi*variance)) * np.e ** -((x-mean)**2/2*variance) for x in col_data]

            fig = plt.figure()
            axis = plt.subplot(111)
            axis.plot(x_line,y_line)

            axis.legend()
            fig.savefig("tmp/plot.png")

            self.result_output.add_widget(ExportableGraph(source="tmp/plot.png", fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))