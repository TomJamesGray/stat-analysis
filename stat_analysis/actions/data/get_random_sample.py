from stat_analysis.actions.base_action import BaseAction

class DataSample(BaseAction):
    type = "data.sample"
    view_name = "Dataset Sample"

    def __init__(self,output_widget):
        self.save_name = "XYZ"
        self.status = "OK"
        self.form = [
            {
                "group_name":"",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "required":True,
                        "data_type":"dataset",
                        "form_name":"data_set",
                        "visible_name":"Data set"
                    },
                    {
                        "input_type":"numeric",
                        "required":True,
                        "form_name":"n_records",
                        "visible_name":"Number of records"
                    },
                    {
                        "input_type":"check_box",
                        "visible_name":"Random Sampling",
                        "form_name":"random_sample"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
