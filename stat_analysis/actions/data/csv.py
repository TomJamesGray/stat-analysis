import logging
from kivy.app import App
import csv
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable
from collections import OrderedDict

logger = logging.getLogger(__name__)


class ImportCSV(base_action.BaseAction):
    type = "data.import_csv"
    view_name = "CSV Import"

    def __init__(self,output_widget):
        self.save_name = "XYZ"
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
                        "form_name": "start_line",
                        "visible_name": "Start reading at line:",
                    }
                ]
            },
            {
                "group_name":"Save",
                "inputs":[
                    {
                        "input_type":"string",
                        "required":True,
                        "form_name":"save_name",
                        "visible_name":"Action save name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.stored_data = None

    def run(self):
        logger.info("Running action {}".format(self.type))
        if self.validate_form():
            logger.info("Form validated, form outputs: {}".format(self.form_outputs))
            # Get the values from the form validation
            vals = self.form_outputs
            with open(vals["file"]) as f:
                reader = csv.reader(f)
                data = []
                for row in reader:
                    data.append(row)
            logger.info("All data read in, total initial records {}".format(len(data)))

            if vals["use_headers"]:
                # Get the header values from the first row if headers are being used
                self.headers = data[0]
            else:
                # If user doesn't want headers just use numbers
                self.headers = list(range(1,len(data[0])+1))
            # Get rid of data before user specified start line
            data = data[int(vals["start_line"])-1:]
            new_data = []
            for item in data:
                tmp = OrderedDict()
                for i in range(0,len(item)):
                    # TODO Add handling if there are more columns than expected
                    tmp[self.headers[i]] = item[i]
                new_data.append(tmp)
            # Set stored data property to be used in get_data method
            self.stored_data = new_data
            # Set the save name that will be shown to user in the saved actions grid on the home screen
            self.save_name = vals["save_name"]
            # Add action to saved_actions and to data sets
            App.get_running_app().saved_actions.append(self)
            App.get_running_app().datasets.append(self)

            self.result_output.add_widget(BorderedTable(headers=["Records","Columns"],data=[[len(data)],[len(data[0])]],
                                                        row_default_height=30, row_force_default=True))
        else:
            logger.info("Form not validated, form errors: {}".format(self.form_errors))

    def get_data(self):
        return self.stored_data

    def get_headers(self):
        return self.headers