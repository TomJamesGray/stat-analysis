from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty,NumericProperty
from kivy.modules import inspector


class StatAnalysis(Widget):
    """
    Root widget for the app
    """
    pass


class ActionsScroller(ScrollView):
    """
    Widget that displays the available actions in a tree format
    """
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


class HomeView(GridLayout):
    """
    Widget for the main home screen
    """
    pass


class BorderedLabel(Label):
    b_width = NumericProperty(1)


class TitlePane(Label):
    """
    Generic Label for use in the titles of the sections
    """
    title = StringProperty("")


class LogView(GridLayout):
    """
    Widget displays the log output
    """
    pass


class ScrollableLabel(ScrollView):
    """
    Generic widget that displays text in a scrolling box
    """
    text = StringProperty("")


class StatApp(App):
    accent_col = (243/255,119/255,66/255,1)

    def build(self):
        self.title = "Stat Analysis"
        Window.clearcolor = (.85,.85,.85,1)
        Window.size = (1336,768)
        a = StatAnalysis()
        inspector.create_inspector(Window,a)
        return a


def main():
    StatApp().run()