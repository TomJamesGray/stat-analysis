import logging
from kivy.app import App
import csv
from kivy.resources import resource_find
from stat_analysis.actions import base_action
from stat_analysis.d_types.get_d_type import guess_d_type
from stat_analysis.d_types.setup import types
from stat_analysis.generic_widgets.form_outputs import DataSpreadsheet
from collections import OrderedDict
from stat_analysis.actions.data.import_set_col_types import ImportSetColTypes

logger = logging.getLogger(__name__)


class ImportCSV(base_action.BaseAction):
    type = "data.import_csv"
    view_name = "CSV Import"

    def __init__(self,output_widget):
        self.form = [
            {
                "group_name":"File",
                "inputs":[
                    {
                        "input_type":"file",
                        "required":True,
                        "form_name":"file",
                        "visible_name":"File",
                        "filters":[lambda _,filename: filename.endswith(".csv")]
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
                        "visible_name": "Start reading at line:"
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
        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        # Get the values from the form validation
        vals = self.form_outputs
        with open(vals["file"],"r") as f:
            # Read in the data all as strings
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
            self.headers = [str(x) for x in range(1,len(data[0])+1)]

        # Get rid of data before user specified start line
        start_line = int(vals["start_line"])
        if start_line <= 0 or start_line-1 >= len(data):
            # Make error message to tell the user their start line is wrong
            self.make_err_message("Invalid start line {}".format(vals["start_line"]))
            return False
        else:
            # Trim the input data to go from the start line to the end (-1 is because the list is zero indexed
            # but line numbers aren't
            data = data[int(vals["start_line"])-1:]


        # Arrange the data into columns and run the guess_d_type function
        # This returns: ((data_type_name, converter function),[Possible errors caused by this choice])
        col_d_types = OrderedDict()
        possible_col_errors = OrderedDict()
        for x in range(len(data[0])):
            # Temporary list for the columns data
            tmp_col_data = []
            for y in range(len(data)):
                # Append data value to the list
                tmp_col_data.append(data[y][x])
            # Set col data type and errors with return data from guess_d_type function
            col_d_types[self.headers[x]],possible_col_errors[self.headers[x]] = guess_d_type(tmp_col_data)


        logger.debug("Guessed d_types: {}".format(col_d_types))
        logger.debug("Possible errors: {}".format(possible_col_errors))

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
            # Create DataSpreadsheet widget that is used in ImportSetColTypes action to show a sample of the data
            tbl = DataSpreadsheet(table_data=self.stored_data[:5],headers=self.headers,height=155)
            tbl.bind(minimum_width=tbl.setter("width"))
            # Redraw output screen with ImportSetColTypes action
            self.output_widget.parent.refresh(ImportSetColTypes,dataset_name=vals["save_name"],
                                              spreadsheet=tbl,possible_errors=possible_col_errors)

    def get_data(self):
        """Get the data of the data set"""
        return self.stored_data

    def get_headers(self):
        """Get the header names of the data set"""
        return list(self.cols_structure.keys())

    def get_header_structure(self):
        """Get the header structure of the data set"""
        return self.cols_structure

    def set_header_structure(self,struct,drop_err_cols=True):
        """
        Sets the header structure, and changes the data types of the items to match
        """
        self.cols_structure = struct
        # Get converter functions in a list
        converters = []
        for _,x in self.cols_structure.items():
            converters.append(x[1])
        # Create list to store data temporarily while data is being converted and list
        # that stores indexes of rows that are to be dropped
        tmp_data = []
        to_drop = []
        for row in range(0,len(self.stored_data)):
            # Append blank list to tmp_data for this row of data
            tmp_data.append([])
            for col in range(0,len(self.stored_data[0])):
                try:
                    tmp_data[row].append(converters[col](self.stored_data[row][col]))
                except Exception:
                    # This data item causes an error, like interpreting a string as an int so drop the row
                    to_drop.append(row)

        if to_drop != []:
            # Remove rows that have been flagged to be dropped
            dropped_cols = 0
            for row_no in to_drop:
                # Must subtract dropped cols from the row number since columns that have already been
                # dropped will affect the index of the initially desired row
                del tmp_data[row_no-dropped_cols]
                dropped_cols += 1

        self.stored_data = tmp_data

    def add_column(self,col_data,col_type,col_name):
        if len(col_data) != self.records:
            raise ValueError("Length of additional column is not equal to length of existing data")
        for i in range(0,self.records):
            # Add the new data to the row in the saved data
            self.stored_data[i].append(col_data[i])
        # Update the column structure
        self.cols_structure[col_name] = (col_type,types[col_type]["convert"])

    def set_data(self,data):
        self.stored_data = data

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
            "type":self.type,
            "save_name": self.save_name
        }

    def load(self,state,**kwargs):
        self.form_outputs = state["form_outputs"]
        if "override_dataset_name" in kwargs:
            self.form_outputs["save_name"] = kwargs["override_dataset_name"]
        # Using resource find means that relative paths to datasets like res/example_datasets/...
        # can be loaded easily while still maintaining absolute paths like "/home/tom/..."
        # Resource find also returns None if the file doesn't exist
        file_location = resource_find(self.form_outputs["file"])
        if file_location == None:
            return "Error in loading file {} after `resource_find`, file not found".format(file_location)
        # Update the file attribute in the form outputs
        self.form_outputs["file"] = file_location
        try:
            self.run(validate=False,quiet=True)
        except FileNotFoundError as e:
            err = "Error in loading file {}, file not found\n{}".format(self.form_outputs["file"],e)
            logger.error(err)
            return err
        # Add back the converter functions to header structure
        header_struct = OrderedDict()
        for key,value in state["header_structure"].items():
            header_struct[key] = (value,types[value]["convert"])
        self.set_header_structure(header_struct)

        return True