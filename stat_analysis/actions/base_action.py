import logging
from kivy.uix.button import Button
from stat_analysis.form_inputs import combo_box

logger = logging.getLogger(__name__)

class BaseAction(object):
    def render(self):
        logger.info("Rendering action {}".format(self.type))
        for item in self.form:
            # self.output_widget.add_widget(Button())
            self.output_widget.add_widget(combo_box.FormDropDown(label=item["visible_name"],
                inputs=[{"u_name":"ONE"},{"u_name":"TWO"}]))