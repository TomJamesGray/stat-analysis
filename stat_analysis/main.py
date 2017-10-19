from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty,NumericProperty,ObjectProperty
from kivy.modules import inspector
from stat_analysis.actions import stats
from kivy.app import App


class StatAnalysis(Widget):
    """
    Root widget for the app
    """
    pass


class ActionsScroller(ScrollView):
    """
    Widget that displays the available actions in a tree format
    """
    primary_pane_edit = ObjectProperty(None)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1,None)
        self.bar_width = 5
        tv = TreeView(size_hint=(1,None),hide_root=True)
        tv.bind(minimum_height=tv.setter("height"))
        # n1 = tv.add_node(TreeViewLabel(color=(0,0,0,1),text="Item 1"))
        # for i in range(100):
        #     tv.add_node(TreeViewLabel(color=(0,0,0,1),text="Sub-item {}".format(i)),n1)
        for action in App.get_running_app().actions:
            x = ActionTreeViewLabel(color=(0,0,0,1),text=action.type,stored_action=action)
            x.bind(on_touch_down=lambda *args:self.primary_pane_edit.refresh(x.stored_action))
            tv.add_node(x)

        self.add_widget(tv)


class HomeView(GridLayout):
    """
    Widget for the main home screen
    """
    pass

class ActionTreeViewLabel(TreeViewLabel):
    stored_action = ObjectProperty(None)


class PrimaryPane(GridLayout):
    title = StringProperty("")

    def refresh(self,action,*args):
        print(action.type)
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        output_widget = Widget()
        self.add_widget(output_widget)
        self.active_action = action(output_widget)
        self.active_action.render()


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
    primary_pane = ObjectProperty(None)

    def build(self):
        # print(stats.regression)
        self.actions = [stats.regression.Regression]
        self.title = "Stat Analysis"
        Window.clearcolor = (.85,.85,.85,1)
        Window.size = (1336,768)
        a = StatAnalysis()
        inspector.create_inspector(Window,a)
        return a


def main():
    StatApp().run()