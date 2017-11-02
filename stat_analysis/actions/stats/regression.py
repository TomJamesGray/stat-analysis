from stat_analysis.actions import base_action


class Regression(base_action.BaseAction):
    type = "stats.regression"

    def __init__(self,output_widget):
        self.user_name = "XYZ"
        self.status = "OK"
        self.form = [
            {"group_name":"Data",
             "inputs":[
                {
                    "input_type":"combo_box",
                    "data_type":"dataset",
                    "required":True,
                    "form_name":"dataset",
                    "visible_name":"Data Set"
                },
                {
                    "input_type": "combo_box",
                    "data_type": "column_numeric",
                    "required": True,
                    "form_name": "x_var",
                    "visible_name": "X Variable"
                },
                {
                    "input_type": "combo_box",
                    "data_type": "column_numeric",
                    "required": True,
                    "form_name": "y_var",
                    "visible_name": "Y Variable"
                }]
             },
            {"group_name":"Regression",
            "inputs":[
                {
                    "input_type": "check_box",
                    "required": True,
                    "form_name": "regression",
                    "visible_name": "Regression"
                },
                {
                    "input_type": "numeric_bounded",
                    "default": 1,
                    "step":1,
                    "min":1,
                    "max":10,
                    "required": "false",
                    "name": "regression_degree",
                    "required_if": "regression=True",
                    "visible_name":"Regression Degree:"

                }]
             }
    ]
        self.output_widget = output_widget