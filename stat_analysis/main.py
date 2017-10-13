from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

class StatAnalysis(Widget):
    pass

class StatApp(App):
    def build(self):
        self.title = "Stat Analysis"
        Window.clearcolor = (1,1,1,1)
        a = StatAnalysis()
        return a

def main():
    StatApp().run()