import logging
import logging.config
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty,ObjectProperty
from kivy.modules import inspector
from stat_analysis.actions import stats,data
from stat_analysis.generic_widgets.bordered import BorderedButton
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
        },
        "stat_analysis.form_inputs":{
            "handlers":["gui"],
            "level":"DEBUG"
        },
        "stat_analysis.generic_widgets":{
            "handlers":["gui"],
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
    primary_pane = ObjectProperty(None)


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
        for group in App.get_running_app().actions:
            parent_node = TreeViewLabel(text=group["group_name"],color=(0,0,0,1))
            tv.add_node(parent_node)
            for action in group["actions"]:
                x = ActionTreeViewLabel(color=(0,0,0,1),text=action.view_name,stored_action=action)
                x.bind(on_touch_down=lambda *args:self.primary_pane_edit.refresh(args))
                tv.add_node(x,parent_node)

        self.add_widget(tv)


class HomeView(GridLayout):
    """
    Widget for the main home screen
    """
    pass


class ActionsGrid(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        headers = ["Name","Type","Status"]
        for header in headers:
            self.add_btn(header)
        for action in App.get_running_app().saved_actions:
            name_btn = self.add_btn(action.save_name)
            name_btn.saved_action = action
            name_btn.bind(on_press=lambda x:App.get_running_app().root_widget.primary_pane.load_action(x))

            self.add_btn(action.type)
            self.add_btn(action.status)

    def add_btn(self,text):
        x = BorderedButton(b_width=1, padding=(2, 2), size_hint_x=0.4, color=(0, 0, 0, 1), text=str(text),
                          valign="middle", halign="left",background_color=(1,1,1,1),background_normal="")
        x.bind(size=x.setter("text_size"))
        self.add_widget(x)
        return x


class ActionTreeViewLabel(TreeViewLabel):
    stored_action = ObjectProperty(None)


class PrimaryPane(GridLayout):
    title = StringProperty("")

    def refresh(self,args):
        action = args[0].stored_action
        logger.info("Changing the active pane to: {}".format(action.type))
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1,1),cols=2)
        self.add_widget(output_widget)
        self.active_action = action(output_widget)
        self.active_action.render()

    def load_action(self,lbl):
        logger.info("Loading action {}".format(lbl.saved_action))

    def go_home(self,*args):
        logger.info("Changing active pane to home screen")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = "Home"
        self.add_widget(HomeView())


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
    accent_col = (219/255,46/255,52/255,1)
    title_pane_col = (34/255,34/255,34/255,1)

    def build(self):
        logger.info("Initialising application")
        # self.actions = [stats.regression.Regression]
        self.actions = [
            {
                "group_name":"Stats",
                "actions":[stats.regression.Regression]
            },
            {
                "group_name":"Data",
                "actions":[data.csv.ImportCSV,data.view_data.ViewData]
            }
        ]
        self.saved_actions = []
        self.datasets = []
        self.title = "Stat Analysis"
        Window.clearcolor = (.85,.85,.85,1)
        Window.size = (1336,768)
        self.root_widget = StatAnalysis()
        inspector.create_inspector(Window,self.root_widget)
        return self.root_widget


def main():
    StatApp().run()