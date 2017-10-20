import logging
from kivy.uix.button import Button
from stat_analysis.form_inputs import combo_box

logger = logging.getLogger(__name__)

form_input_maps = {
    "combo_box":combo_box.FormDropDown
}


class BaseAction(object):
    def render(self):
        logger.info("Rendering action {}".format(self.type))
        for item in self.form:
            try:
                cls = form_input_maps[item["input_type"]]
            except KeyError:
                logger.error("Form input {} not found in form_input_maps".format(item["input_type"]))
                pass
            finally:
                # Give the form widget the whole dict so it can parse the data there
                self.output_widget.add_widget(cls(item))