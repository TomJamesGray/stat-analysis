from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window

class StatAnalysis(Widget):
    pass

class ActionsScroller(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1,None)
        self.bar_width = 5
        layout = GridLayout(cols=1,spacing=10,size_hint_x = 1,size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))
        layout.bind(width=lambda *args: self.width)
        for i in range(100):
            btn = Button(text=str(i),size_hint_y=None,height=40)
            layout.add_widget(btn)
            btn.bind(width=lambda *args: self.width)
        self.add_widget(layout)

class StatApp(App):
    def build(self):
        self.title = "Stat Analysis"
        Window.clearcolor = (1,1,1,1)
        Window.size = (1336,768)
        a = StatAnalysis()
        return a

def main():
    StatApp().run()