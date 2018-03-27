import argparse
from kivy.app import App
from kivy.modules import inspector
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
# Import CustomActionBtn so it can be used in the KV file
from stat_analysis.generic_widgets.action_bar import CustomActionBtn

class HelpView(Widget):
    help_text = StringProperty("")


class HelpViewApp(App):
    help_text = StringProperty("")

    def build(self):
        Window.clearcolor = (.9,.9,.9,1)
        Window.size = (400,500)
        Window.title = "Stat Analysis Help"
        x = HelpView(help_text=self.help_text,size_hint=(1,1))
        inspector.create_inspector(Window,x)
        return x


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("help_text",type=str)
    results = parser.parse_args()

    app = HelpViewApp(help_text=results.help_text)
    app.run()