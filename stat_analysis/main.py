import logging
import logging.config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty,NumericProperty,ObjectProperty
from kivy.modules import inspector
from stat_analysis.actions import stats
from kivy.app import App


logging_config = {
    "version":1,
    "disable_existing_loggers":False,
    "formatters":{
        "main":{"format":"%(name)s-%(lineno)d: %(message)s"},
    },
    "handlers":{
        "gui":{
            "class":"logging.StreamHandler",
            "formatter":"main",
            "level":"INFO"},
        "actions":{
            "class":"logging.StreamHandler",
            "formatter":"main",
            "level":"INFO"},
    },
    "loggers":{
        "stat_analysis.main":{
            "handlers":["gui"],
            "level":"INFO"
        },
        "stat_analysis.actions":{
            "handlers":["actions"],
            "level":"INFO"
        }
    }
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

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
        logger.info("Changing the active pane to: {}".format(action.type))
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1,1),cols=1,padding=(5,5),spacing=(10,10))
        self.add_widget(output_widget)
        self.active_action = action(output_widget)
        self.active_action.render()


class BorderedLabel(Label):
    b_width = NumericProperty(1)


class BorderedSpinner(Spinner):
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
        logger.info("Initialising application")
        self.actions = [stats.regression.Regression]
        self.title = "Stat Analysis"
        Window.clearcolor = (.85,.85,.85,1)
        Window.size = (1336,768)
        a = StatAnalysis()
        inspector.create_inspector(Window,a)
        return a


def main():
    StatApp().run()