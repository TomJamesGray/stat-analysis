import logging
import csv
from stat_analysis.actions import base_action
from collections import OrderedDict

logger = logging.getLogger(__name__)


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
                        "form_name": "start_line",
                        "visible_name": "Start reading at line:",
                    }
                ]
            }
        ]
        self.output_widget = output_widget

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
                headers = data[0]
            else:
                # If user doesn't want headers just use numbers
                headers = list(range(1,len(data[0])+1))
            # Get rid of data before user specified start line
            data = data[int(vals["start_line"])-1:]
            new_data = []
            for item in data:
                tmp = OrderedDict()
                for i in range(0,len(item)):
                    # TODO Add handling if there are more columns than expected
                    tmp[headers[i]] = item[i]
                new_data.append(tmp)
            print(new_data)

        else:
            logger.info("Form not validated, form errors: {}".format(self.form_errors))