import logging
import os.path
import numpy as np
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
    help_text =\
    """[size=16][b]Logistic Regression[/b][/size]

This action performs a logistic regression, this means it predicts the probability of a binary variable being true, given another parameter.

[b]Outputs[/b]

The formula for the output line, ie the probability density function is:

[font=res/equation.otf][size=20](1+e[sup][size=14]-(a+bx)[/size][/sup])[sup][size=14]-1[/size][/sup][/size][/font]

where a is the constant term and and b is the x coefficient

The percentage accuracy value is a measure of how well the dataset fits the model, so higher percentage values means the dataset fits the model better which means the model is more accurate

[b]Example[/b]

An example of a logistic regression can be found in the "exam passes" dataset. If you do a logistic regression with the binary variable being "pass" and the x variable being the hours of revision done, you can predict the probability that a student will pass the exam given the amount of revision they do.
    """
    saveable = True

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
                    },
                    {
                        "input_type": "numeric",
                        "required": False,
                        "allow_comma_separated": True,
                        "form_name": "inverse_logit",
                        "visible_name": "Get values from probabilities",
                        "tip": "For multiple values input them with commas separating them"
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

    def run(self,validate=True,quiet=False,use_cached=False,**kwargs):
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

        # Note data for x must be in form [[1],[2],...]
        x,y = [],[]
        # Get the position in each row for chosen columns
        x_pos = list(dataset.get_header_structure().keys()).index(vals["x_var"])
        y_pos = list(dataset.get_header_structure().keys()).index(vals["bin_var"])

        for row in dataset.get_data():
            x.append([row[x_pos]])
            y.append(row[y_pos])

        # Make sure the y column is binary, ie only 2 options
        y_options = []
        for val in y:
            if val not in y_options and len(y_options) == 2:
                # This value would be the third in the found options, therefore this column isn't binary :(
                if not quiet:
                    self.make_err_message("Chosen y column is not binary".format(y_options))
                return False
            elif val not in y_options:
                y_options.append(val)

        if self.stored_model != None and use_cached:
            logger.debug("Using cached model for type {} save name {}".format(self.type,self.save_name))
            model = self.stored_model
        else:
            model = LR(fit_intercept=True,C=1e9)
            model.fit(x,y)
            self.stored_model = model

        if not quiet:
            x_coeff = model.coef_[0][0]
            const = model.intercept_[0]
            # Generate an accuracy percentage by feeding the x values back in and comparing
            # them with the corresponding y values
            predicted = model.predict(x)
            percentage_accuracy = metrics.accuracy_score(y, predicted) * 100

            logger.info("Logistic regression done, x coeff {}, constant term {}, % accuracy {}".format(
                x_coeff,const,percentage_accuracy))

            self.result_output.clear_outputs()
            self.result_output.spacing = (0,5)
            self.result_output.add_widget(BorderedTable(
                headers=["X Coefficient","Constant\nterm","Percentage\naccuracy"],data=[[str(x_coeff)],[str(const)],
                ["{}%".format(percentage_accuracy)]],row_default_height=40,row_force_default=True,
                orientation="horizontal",size_hint_y=None,size_hint_x=1,for_scroller=True
            ))

            if vals["predict_on"] != None:
                predicted_vals = [str(np.round(1/(1+np.exp(-(y*x_coeff+const))),3)) for y in vals["predict_on"]]
                self.result_output.add_widget(BorderedTable(
                    headers=[vals["x_var"],"Probability"],data=[[str(x) for x in vals["predict_on"]],predicted_vals],
                    row_default_height=40,row_force_default=True,orientation="vertical",size_hint_y=None,
                    for_scroller=True
                ))

            if vals["inverse_logit"] != None:
                predicted_x = []
                used_p_vals = []
                for val in vals["inverse_logit"]:
                    if not (0 < val <1):
                        logger.warning("Invalid probability {}".format(val))
                        continue

                    predicted_x.append(str(np.round(-1/x_coeff * (np.log(1/val -1)+const),3)))
                    used_p_vals.append(val)

                if len(used_p_vals) != 0:
                    self.result_output.add_widget(BorderedTable(
                        headers=["Probability",vals["x_var"]],data=[used_p_vals,predicted_x],
                        row_default_height=40,row_force_default=True,orientation="vertical",size_hint_y=None,
                        for_scroller=True
                    ))

            if vals["make_graph"]:
                # Generate x and y values for the line
                x_line = np.linspace(min(x,key=lambda a:a[0])[0],max(x,key=lambda a:a[0])[0],500)
                # Function to generate the probability density function is 1/(1+exp(-f(x)))
                # where f(x) is the linear function generated by the Logistic regression function
                y_line = [1/(1+np.exp(-(y*x_coeff+const))) for y in x_line]

                fig = plt.figure()
                axis = plt.subplot(111)
                axis.set_ylim([0,1])
                axis.scatter([a[0] for a in x],y,color=App.get_running_app().graph_colors[1])
                axis.plot(x_line,y_line,color=App.get_running_app().graph_colors[0])

                # Set axis labels
                axis.set_xlabel(vals["x_var"])
                axis.set_ylabel(vals["bin_var"])

                axis.legend()
                path = os.path.join(App.get_running_app().tmp_folder, "plot.png")
                fig.savefig(path)

                self.result_output.add_widget(ExportableGraph(source=path, fig=fig, axis=[axis], nocache=True,
                                                          size_hint_y=None))
