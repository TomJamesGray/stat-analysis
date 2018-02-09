import logging
import os
import numpy
import matplotlib.pyplot as plt
from stat_analysis.actions import base_action
from kivy.app import App
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)

class Regression(base_action.BaseAction):
    type = "stats.regression"
    view_name = "Regression"
    help_text = \
"""[size=16][b]Linear and polynomial regression[/b][/size]

This action performs a regression of the given degree for the given dataset

[b]Outputs[/b]

The formula for the output line is given as well as a graph containing a scatter plot of the dataset and the regression line generated. This graph can be modified by pressing the "graph options" button where you can customise the axis labels and the minimum and maximum x and y values.

"""


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
                        "visible_name":"Data Set",
                        "on_change":lambda x,val:x.parent_action.set_tmp_dataset(val)
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column_numeric",
                        "get_cols_from":lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener":lambda x:x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "x_var",
                        "visible_name": "X Variable"
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column_numeric",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener":lambda x:x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "y_var",
                        "visible_name": "Y Variable"
                    }]
            },
            {
                "group_name":"Regression",
                "inputs":[
                    {
                        "input_type": "numeric_bounded",
                        "default": 1,
                        "step":1,
                        "min":1,
                        "max":10,
                        "int_only": True,
                        "required": "false",
                        "form_name": "regression_degree",
                        "visible_name": "Regression Degree"
                    },
                    {
                        "input_type": "numeric_bounded",
                        "default": 2,
                        "step":1,
                        "min":0,
                        "max":10,
                        "int_only":True,
                        "required": "false",
                        "form_name": "regression_out_precision",
                        "visible_name": "Output Precision",
                        "tip":"This controls the amount of decimal points to be shown in the output for"
                              "the regression line"
                    }]
            },
            {
                "group_name": "Save",
                "inputs": [
                    {
                        "input_type": "check_box",
                        "required": True,
                        "form_name": "save_action",
                        "visible_name": "Save action"
                    },
                    {
                        "input_type": "string",
                        "required": False,
                        "visible_name": "Action save name",
                        "form_name": "action_save_name",
                        "required_if": [lambda x: x["save_action"] == True]
                    }
                ]
            }

        ]
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []
        self.stored_coeffs = None

    def set_tmp_dataset(self,val):
        self.tmp_dataset = val
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self,val):
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False,preloaded=False,use_cached=False,*args):
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

        # Get the data set for x and y in seperate lists
        x,y = [],[]
        x_parse = dataset.get_header_structure()[vals["x_var"]][1]
        y_parse = dataset.get_header_structure()[vals["y_var"]][1]
        # Get's the position in each row for the desired columns
        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        y_pos = list(dataset.get_header_structure().keys()).index(vals["y_var"])
        for row in dataset.get_data():
            x.append(x_parse(row[x_pos]))
            y.append(y_parse(row[y_pos]))

        if use_cached and self.stored_coeffs != None:
            logger.debug("Using cached model for type {} save name {}".format(self.type, self.save_name))
            coeffs = self.stored_coeffs
        else:
            coeffs = numpy.polyfit(x,y,vals["regression_degree"])


        if not quiet:
            logger.info("Coeffs generated: {}".format(coeffs))
            # Generate x and y values for the regression line to be displayed
            x_line = numpy.linspace(min(x),max(x)+0.5,500)
            # Get the y values from the coefficients generated by polyfit
            y_line = [sum([x*(y**(len(coeffs)-i-1)) for i,x in enumerate(coeffs)]) for y in x_line]
            # Get a representaion of the function for the output
            func = ""
            deg = len(coeffs)-1
            for coeff in coeffs:
                if func != "" and coeff > 0:
                    func += "+"
                rnd_coeff = numpy.around(coeff,int(vals["regression_out_precision"]))
                if deg > 1:
                    func += "{}x[sup]{}[/sup]".format(rnd_coeff,deg)
                elif deg == 1:
                    func += "{}x".format(rnd_coeff)
                else:
                    func += "{}".format(rnd_coeff)
                deg -= 1

            fig = plt.figure()
            axis = plt.subplot(111)
            axis.scatter(x,y,color=App.get_running_app().graph_colors[1])
            axis.plot(x_line,y_line,color=App.get_running_app().graph_colors[0])

            # Set axis labels
            axis.set_xlabel(vals["x_var"])
            axis.set_ylabel(vals["y_var"])

            axis.legend()
            path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
            fig.savefig(path)

            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(
                headers=["Function"],data=[[func]],row_default_height=30,row_force_default=True,
                orientation="horizontal",size_hint_y=None,size_hint_x=1,for_scroller=True,markup=True
            ))

            self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))
        if vals["save_action"] and not preloaded:
            # Save the action
            self.save_name = vals["action_save_name"]
            try:
                App.get_running_app().add_action(self)
            except ValueError:
                logger.error("Dataset with that name already exists")


