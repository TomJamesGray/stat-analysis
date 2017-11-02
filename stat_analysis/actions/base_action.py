import logging
from kivy.uix.label import Label
from kivy.app import App
from stat_analysis.form_inputs import combo_box,check_box,numeric_bounded

logger = logging.getLogger(__name__)

form_input_maps = {
    "combo_box":combo_box.FormDropDown,
    "check_box":check_box.FormCheckBox,
    "numeric_bounded":numeric_bounded.FormNumericBounded
}


class BaseAction(object):
    def render(self):
        logger.info("Rendering action {}".format(self.type))
        for group in self.form:

            group_lbl = Label(text=group["group_name"],size_hint=(1,None),
                                                height=30,font_size="22",color=App.get_running_app().accent_col)
            group_lbl.bind(size=group_lbl.setter("text_size"))
            self.output_widget.add_widget(group_lbl)

            for item in group["inputs"]:
                try:
                    cls = form_input_maps[item["input_type"]]
                except KeyError:
                    logger.error("Form input {} not found in form_input_maps".format(item["input_type"]))
                    # Go to next form input
                    continue
                # Give the form widget the whole dict so it can parse the data there
                self.output_widget.add_widget(cls(item))