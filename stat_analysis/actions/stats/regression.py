from stat_analysis.actions import base_action


class Regression(base_action.BaseAction):
    type = "stats.regression"

    def __init__(self,output_widget):
        self.user_name = "XYZ"
        self.status = "OK"
        self.form = [
            {
                "input_type":"combo_box",
                "data_type":"dataset",
                "required":True,
                "form_name":"dataset",
                "visible_name":"Data Set"
            }
        ]
        self.output_widget = output_widget