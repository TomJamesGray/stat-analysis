import logging
from kivy.app import App
import csv
from stat_analysis.actions import base_action
from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.d_types.get_d_type import guess_d_type
from stat_analysis.d_types.setup import types
from collections import OrderedDict
from stat_analysis.actions.data.import_set_col_types import ImportSetColTypes
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

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

    def run(self,validate=True,quiet=False):
        # Set the maximum sample length for the guess_d_type function.
        # Bigger samples will increase accuracy, but slow the program down
        max_sample_length = 50

        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))
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
        smpl_data = {}
        for header in self.headers:
            smpl_data[header] = []
        # Set the sample rate for the d_type sample
        smpl_rate = int(len(data)/max_sample_length)
        # Smpl_rate should be larger than 2 or 1
        if smpl_rate < 2:
            smpl_rate = 1

        add_to_smpl = False
        for x,item in enumerate(data):
            if x % smpl_rate == 0 and len(smpl_data) < max_sample_length:
                # Add the columns to the smpl_data
                for i in range(0,len(item)):
                    # TODO Add handling if there are more columns than expected
                    smpl_data[self.headers[i]].append(item[i])

        col_d_types = OrderedDict()
        for col_name,col_data in smpl_data.items():
            col_d_types[col_name] = guess_d_type(col_data)

        logger.debug("Guessed d_types: {}".format(col_d_types))

        # Set stored data property to be used in get_data method
        self.stored_data = data
        # Set the columns property, this is an OrderedDict, eg
        # {"col_name":("d_type_name", function to convert string to useful data type}
        # At this point this is only a suggestion and as such the data shouldn't be
        # modified to to reflect this as it'll be confirmed at the next step
        self.cols_structure = col_d_types
        # Set the save name that will be shown to user in the saved actions grid on the home screen
        self.save_name = vals["save_name"]
        try:
            # Add action to data sets
            App.get_running_app().add_dataset(self)
        except ValueError:
            logger.error("Dataset with name '{}' already exists, please choose a different name".format(self.save_name))
            return False

        if not quiet:
            self.output_widget.parent.refresh(ImportSetColTypes,dataset_name=vals["save_name"])



    def get_data(self):
        return self.stored_data

    def get_headers(self):
        return list(self.cols_structure.keys())

    def get_header_structure(self):
        return self.cols_structure

    def set_header_structure(self,struct):
        self.cols_structure = struct
        # Get converter functions in a list
        converters = []
        for _,x in self.cols_structure.items():
            converters.append(x[1])

        for row in range(0,len(self.stored_data)):
            for col in range(0,len(self.stored_data[0])):
                self.stored_data[row][col] = converters[col](self.stored_data[row][col])

    @property
    def records(self):
        return len(self.stored_data)

    @property
    def columns(self):
        return len(self.stored_data[0])

    def serialize(self):
        # Get rid of the converter functions in cols structure
        col_struct = OrderedDict()
        for key,value in self.cols_structure.items():
            col_struct[key] = value[0]

        return {
            "form_outputs":self.form_outputs,
            "header_structure":col_struct,
            "type":self.type
        }

    def load(self,state):
        self.form_outputs = state["form_outputs"]
        self.run(validate=False,quiet=True)
        # Add back the converter functions to header strucure
        header_struct = OrderedDict()
        for key,value in state["header_structure"].items():
            header_struct[key] = (value,types[value]["convert"])
        self.set_header_structure(header_struct)