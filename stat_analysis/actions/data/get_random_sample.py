import logging
import random
import copy
from kivy.app import App
from stat_analysis.actions.base_action import BaseAction
from stat_analysis.generic_widgets.bordered import BorderedTable

logger = logging.getLogger(__name__)

class DataSample(BaseAction):
    type = "data.sample"
    view_name = "Dataset Sample"

    def __init__(self,output_widget):
        self.form = [
            {
                "group_name":"Dataset",
                "inputs":[
                    {
                        "input_type":"combo_box",
                        "required":True,
                        "data_type":"dataset",
                        "form_name":"dataset",
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
                        "form_name":"random_sample",
                        "required":True
                    },
                    {
                        "input_type":"string",
                        "required":True,
                        "form_name":"save_name",
                        "visible_name":"Dataset save name"
                    }
                ]
            }
        ]
        self.output_widget = output_widget
        self.base_dataset,self.cols_structure = None,None

    def run(self, validate=True, quiet=False, preloaded=False, use_cached=False, **kwargs):
        logger.info("Running action {}".format(self.type))
        if validate:
            if not self.validate_form():
                logger.warning("Form not validated, form errors: {}".format(self.form_errors))
                self.make_err_message(self.form_errors)
                return False
            else:
                logger.debug("Form validated, form outputs: {}".format(self.form_outputs))

        vals = self.form_outputs
        self.base_dataset = App.get_running_app().get_dataset_by_name(vals["dataset"])
        # Store a copy of the cols_structure of the base dataset, so modifications to the
        # base dataset don't change this dataset since it should be independent
        self.cols_structure = copy.copy(self.base_dataset.get_header_structure())

        if vals["n_records"] > self.base_dataset.records:
            e = "Number of records desired is greater than number of records in dataset"
            logger.error(e)
            self.make_err_message(e)
            return False

        if vals["n_records"] <= 0:
            e = "Zero or less records desired"
            logger.error(e)
            self.make_err_message(e)
            return False

        self.stored_data = []
        dataset_data = self.base_dataset.get_data()

        if vals["random_sample"]:
            self.stored_data = random.sample(dataset_data,int(vals["n_records"]))
        else:
            smpl_rate = int(self.base_dataset.records/vals["n_records"])
            for i in range(0,self.base_dataset.records):
                if i % smpl_rate == 0 and len(self.stored_data) < vals["n_records"]:
                    self.stored_data.append(dataset_data[i])

        self.save_name = vals["save_name"]
        try:
            # Add action to data sets
            App.get_running_app().add_dataset(self)
        except ValueError:
            logger.error("Dataset with name '{}' already exists, please choose a different name".format(self.save_name))
            return False

        if not quiet:
            self.result_output.clear_outputs()
            self.result_output.add_widget(BorderedTable(
                headers=["Records", "Columns", "Data types"],
                data=[[str(self.records)], [str(self.columns)],
                      [str((", ".join((["{} -> {}".format(x, y[0]) for x, y in self.cols_structure.items()]))))]],
                row_default_height=30, row_force_default=True, orientation="horizontal", for_scroller=True,
                size_hint_x=1, size_hint_y=None))

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
