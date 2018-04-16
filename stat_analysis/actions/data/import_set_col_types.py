from stat_analysis.actions.data.set_col_types import SetColTypes
from kivy.uix.label import Label
from kivy.app import App


class ImportSetColTypes(SetColTypes):
    type = "data.import_set_col_types"
    view_name = "Set Column Data Types"

    def __init__(self,output_widget,**kwargs):
        self.status = "OK"
        self.base_form = []
        self.output_widget = output_widget
        # Get the data set name from the kwargs
        self.passed_dataset_name = kwargs["dataset_name"]
        # Modify the form property with the new values
        self.form_add_cols(kwargs["dataset_name"],set_dataset_selector=False,re_render=False)
        # Get the spreadsheet widget from kwargs
        self.data_spreadsheet = kwargs["spreadsheet"]
        self.possible_errors = kwargs["possible_errors"]

    def render(self,**kwargs):
        super().render(**kwargs)
        # Add a sample of the dataset, and display any possible errors
        self.result_output.clear_outputs(all=True)
        self.result_output.size_hint = (None,None)

        lbl = Label(text="Sample of dataset", size_hint=(None, None), height=30, font_size="18",
                    color=(0, 0, 0, 1), halign="left")
        lbl.bind(texture_size=lbl.setter("size"))
        self.result_output.add_widget(lbl)
        self.result_output.add_widget(self.data_spreadsheet)
        # Make the table use up all the width of the output so it can scroll horizontally if needed
        self.data_spreadsheet.bind(minimum_width=self.result_output.setter("width"))

        # Draw the left border on the first column rv and header so the table looks complete
        self.data_spreadsheet.data_columns[0].left_border = True
        self.data_spreadsheet.spreadsheet_header_labels[0].left_border = True

        total_errors = 0
        errors_ouptputs = Label(color=(0,0,0,1),size_hint=(None,None),markup=True,font_size="12")
        # Make error outputs use up all available space
        errors_ouptputs.bind(texture_size=errors_ouptputs.setter("size"))

        columns = App.get_running_app().get_dataset_by_name(self.passed_dataset_name).get_header_structure()

        for col_name,error_vals in self.possible_errors.items():
            if len(error_vals) == 0:
                # Skip this column if there are no detected errors
                continue

            guessed_type = columns[col_name][0]
            blanks = 0
            # Increment total errors with the length of this columns errors
            total_errors += len(error_vals)
            outputs = []
            for val in error_vals:
                if val == "":
                    # Value is blank
                    blanks += 1
                else:
                    outputs.append("• Recommended type {} conflicts with '{}'\n".format(guessed_type,val))
            # Create for column with the amount of errors
            errors_ouptputs.text += "\n[size=14]Column '{}' errors:[/size]\n".format(col_name)

            if blanks != 0:
                # Show the blank records in a separate line, before other errors
                errors_ouptputs.text += "• {} blank records conflicts with recommended type {}\n".format(
                    blanks,guessed_type)

            for out in outputs:
                errors_ouptputs.text += out
        # Add header with total errors for all columns at start of error text
        errors_ouptputs.text = "[size=18]Total potential errors {}[/size]\n".format(total_errors) + \
                               errors_ouptputs.text
        self.result_output.add_widget(errors_ouptputs)