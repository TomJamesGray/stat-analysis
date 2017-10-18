from kivy.uix.button import Button


class BaseAction(object):
    def render(self):
        for item in self.form:
            self.output_widget.add(Button())