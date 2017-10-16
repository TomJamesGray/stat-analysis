from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.button import Button
from kivy.core.window import Window

class StatAnalysis(Widget):
    pass

class ActionsScroller(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1,None)
        self.bar_width = 5
        tv = TreeView(size_hint=(1,None),hide_root=True)
        tv.bind(minimum_height=tv.setter("height"))
        n1 = tv.add_node(TreeViewLabel(color=(0,0,0,1),text="Item 1"))
        for i in range(100):
            tv.add_node(TreeViewLabel(color=(0,0,0,1),text="Sub-item {}".format(i)),n1)

        self.add_widget(tv)

class StatApp(App):
    def build(self):
        self.title = "Stat Analysis"
        Window.clearcolor = (1,1,1,1)
        Window.size = (1336,768)
        a = StatAnalysis()
        return a

def main():
    StatApp().run()