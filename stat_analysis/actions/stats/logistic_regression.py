import logging
import numpy as np
import time
import matplotlib.pyplot as plt
from kivy.app import App
from sklearn.linear_model import LogisticRegression as LR
from sklearn import metrics
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.generic_widgets.form_outputs import ExportableGraph

logger = logging.getLogger(__name__)


class LogisticRegression(BaseAction):
    type = "stats.logistic_regression"
    view_name = "Logistic Regression"

    def __init__(self,output_widget):
        self.status = "OK"
        self.form = [
            {
                "group_name": "Data",
                "inputs": [
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
                        "form_name": "x_var",
                        "visible_name": "X Variable"
                    },
                    {
                        "input_type": "combo_box",
                        "data_type": "column",
                        "get_cols_from": lambda x: x.parent_action.tmp_dataset,
                        "add_dataset_listener": lambda x: x.parent_action.add_dataset_listener(x),
                        "required": True,
                        "form_name": "bin_var",
                        "visible_name": "Binary variable"
                    }]
            },
            {
                "group_name": "Graph",
                "inputs":[
                    {
                        "input_type":"check_box",
                        "required":True,
                        "form_name":"make_graph",
                        "visible_name":"Make graph"
                    }
                ]
            },
            {
                "group_name": "Use model",
                "inputs":[
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
                        "required": True,
                        "visible_name": "Action save name",
                        "form_name": "action_save_name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.tmp_dataset = None
        self.tmp_dataset_listeners = []
        self.stored_model = None

    def set_tmp_dataset(self, val):
        self.tmp_dataset = val
        [form_item.try_populate(quiet=True) for form_item in self.tmp_dataset_listeners]

    def add_dataset_listener(self, val):
        self.tmp_dataset_listeners.append(val)

    def run(self,validate=True,quiet=False,preloaded=False,use_cached=False,**kwargs):
        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])

        # Note data for x must be in form [[1],[2],...]
        x,y = [],[]
        # Get the position in each row for chosen columns
        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        y_pos = list(dataset.get_header_structure().keys()).index(vals["bin_var"])

        for row in dataset.get_data():
            x.append([row[x_pos]])
            y.append(row[y_pos])

        if self.stored_model != None and use_cached:
            logger.debug("Using cached model for type {} save name {}".format(self.type,self.save_name))
            model = self.stored_model
        else:
            model = LR(fit_intercept=True,C=1e9)
            model.fit(x,y)
            self.stored_model = model

        x_coeff = model.coef_[0][0]
        const = model.intercept_[0]
        # Generate an accuracy percentage by feeding the x values back in and comparing
        # them with the corresponding y values
        predicted = model.predict(x)
        percentage_accuracy = metrics.accuracy_score(y, predicted) * 100

        logger.info("Logistic regression done, x coeff {}, constant term {}, % accuracy {}".format(
            x_coeff,const,percentage_accuracy))

        if vals["save_action"] and not preloaded:
            # Save the action
            self.save_name = vals["action_save_name"]
            try:
                App.get_running_app().add_action(self)
            except ValueError:
                logger.error("Dataset with that name already exists")

        if not quiet:
            self.result_output.clear_outputs()
            self.result_output.spacing = (0,5)
            self.result_output.add_widget(BorderedTable(
                headers=["X Coefficient","Constant\nterm","Percentage\naccuracy"],data=[[str(x_coeff)],[str(const)],
                ["{}%".format(percentage_accuracy)]],row_default_height=40,row_force_default=True,
                orientation="horizontal",size_hint_y=None,size_hint_x=1,for_scroller=True
            ))

        if vals["predict_on"] != None:
            predicted_vals = [str(np.round(1/(1+np.exp(-(y*x_coeff+const))),3)) for y in vals["predict_on"]]
            if not quiet:
                self.result_output.add_widget(BorderedTable(
                    headers=[vals["x_var"],"Probability"],data=[[str(x) for x in vals["predict_on"]],predicted_vals],
                    row_default_height=40,row_force_default=True,orientation="vertical",size_hint_y=None,
                    for_scroller=True
                ))

        if vals["make_graph"]:
            # Generate x and y values for the line
            x_line = np.arange(min(x,key=lambda a:a[0])[0],max(x,key=lambda a:a[0])[0],0.25)
            # Function to generate the probability density function is 1/(1+exp(-f(x)))
            # where f(x) is the linear function generated by the Logistic regression function
            y_line = [1/(1+np.exp(-(y*x_coeff+const))) for y in x_line]

            fig = plt.figure()
            axis = plt.subplot(111)
            axis.set_ylim([0,1])
            axis.scatter([a[0] for a in x],y)
            axis.plot(x_line,y_line)

            # Set axis labels
            axis.set_xlabel(vals["x_var"])
            axis.set_ylabel(vals["bin_var"])

            axis.legend()
            fig.savefig("tmp/plot.png")

            if not quiet:
                self.result_output.add_widget(ExportableGraph(source="tmp/plot.png", fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))
