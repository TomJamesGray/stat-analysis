from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.actions.data.set_col_types import SetColTypes
from kivy.uix.label import Label
from collections import OrderedDict


def make_err_lbl(msg):
    lbl = Label(text="• {}".format(msg), color=(0, 0, 0, 1), size_hint=(None, None))
    lbl.bind(texture_size=lbl.setter("size"))
    return lbl


class ImportSetColTypes(SetColTypes):
    type = "data.import_set_col_types"
    view_name = "Set Column Data Types"

    def __init__(self,output_widget,**kwargs):
        self.save_name = "XYZ"
        self.status = "OK"
        self.base_form = []
        self.output_widget = output_widget
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
        errors_ouptputs = OrderedDict()

        # make_err_message = lambda txt: self.result_output.add_widget(
        #     Label(text="• {}".format(txt),color=(0,0,0,1),size_hint=(None,None)))

        for col_name,error_vals in self.possible_errors.items():
            if len(error_vals) == 0:
                continue
            blanks = 0
            total_errors += len(error_vals)
            outputs = []
            for val in error_vals:
                if val == "":
                    blanks += 1
                else:
                    outputs.append(make_err_lbl(val))

            if blanks != 0:
                self.result_output.add_widget(make_err_lbl("{} {} Blanks".format(blanks)))
