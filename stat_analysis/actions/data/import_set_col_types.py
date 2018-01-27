from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.actions.data.set_col_types import SetColTypes
from kivy.uix.label import Label
from kivy.app import App
from collections import OrderedDict


class ImportSetColTypes(SetColTypes):
    type = "data.import_set_col_types"
    view_name = "Set Column Data Types"

    def __init__(self,output_widget,**kwargs):
        self.save_name = "XYZ"
        self.status = "OK"
        self.base_form = []
        self.output_widget = output_widget
        self.passed_dataset_name = kwargs["dataset_name"]
        self.form_add_cols(kwargs["dataset_name"],set_dataset_selector=False,re_render=False)
        self.drop_err_cols = kwargs["drop_err_cols"]
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
        self.data_spreadsheet.bind(minimum_width=self.result_output.setter("width"))

        total_errors = 0
        errors_ouptputs = Label(color=(0,0,0,1),size_hint=(None,None),markup=True,font_size="12")
        errors_ouptputs.bind(texture_size=errors_ouptputs.setter("size"))

        columns = App.get_running_app().get_dataset_by_name(self.passed_dataset_name).get_header_structure()

        for col_name,error_vals in self.possible_errors.items():
            if len(error_vals) == 0:
                continue

            guessed_type = columns[col_name][0]
            blanks = 0
            total_errors += len(error_vals)
            outputs = []
            for val in error_vals:
                if val == "":
                    blanks += 1
                    total_errors += 1
                else:
                    outputs.append("• Recommended type {} conflicts with '{}'\n".format(guessed_type,val))
                    total_errors += 1

            errors_ouptputs.text += "\n[size=14]Column '{}' errors:[/size]\n".format(col_name)

            if blanks != 0:
                errors_ouptputs.text += "• {} blank records conflicts with recommended type {}\n".format(
                    blanks,guessed_type)

            for out in outputs:
                errors_ouptputs.text += out

        errors_ouptputs.text = "[size=18]Total potential errors {}[/size]\n".format(total_errors) + \
                               errors_ouptputs.text
        self.result_output.add_widget(errors_ouptputs)