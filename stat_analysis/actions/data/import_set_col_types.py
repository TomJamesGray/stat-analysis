from stat_analysis.generic_widgets.bordered import BorderedTable
from stat_analysis.actions.data.set_col_types import SetColTypes


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
