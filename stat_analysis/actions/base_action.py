import logging
from kivy.uix.button import Button

logger = logging.getLogger(__name__)

class BaseAction(object):
    def render(self):
        logger.info("Rendering action {}".format(self.type))
        for item in self.form:
            self.output_widget.add_widget(Button())