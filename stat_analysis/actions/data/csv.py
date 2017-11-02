from stat_analysis.actions import base_action


class ImportCSV(base_action.BaseAction):
    type = "data.import_csv"
    view_name = "CSV Import"

    def __init__(self,output_widget):
        self.user_name = "XYZ"
        self.status = "OK"
        self.form = [
            {
                "group_name":"File",
                "inputs":[
                    {
                        "input_type":"file",
                        "required":True,
                        "form_name":"file",
                        "visible_name":"File"
                    }
                ]
            },
            {
                "group_name":"File Info",
                "inputs":[
                    {
                        "input_type":"check_box",
                        "visible_name":"Use headers",
                        "form_name":"use_headers",
                        "required":True
                    },
                    {
                        "input_type": "numeric",
                        "default": 1,
                        "step": 1,
                        "min": 1,
                        "max": 10,
                        "required": True,
                        "name": "start_line",
                        "visible_name": "Start reading at line:"
                    }
                ]
            }
        ]
        self.output_widget = output_widget