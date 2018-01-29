
import argparse
from kivy.app import App
from kivy.uix.label import Label
from kivy.properties import StringProperty

class HelpViewApp(App):
    help_text = StringProperty("")

    def build(self):
        return Label(text=self.help_text,markup=True)


if __name__ == "__main__":
    # print(sys.argv[1:])
    parser = argparse.ArgumentParser()
    parser.add_argument("help_text",type=str)
    results = parser.parse_args()

    app = HelpViewApp(help_text=results.help_text)
    app.run()