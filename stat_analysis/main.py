import logging
import logging.handlers
import os
import logging.config
import pickle
import argparse
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty,ObjectProperty,BooleanProperty,NumericProperty,ListProperty
from kivy.modules import inspector
from stat_analysis.actions import stats,data,graph
from stat_analysis.generic_widgets.bordered import BorderedButton
from stat_analysis.generic_widgets.files import FileChooserSaveDialog,FileChooserLoadDialog
from stat_analysis.generic_widgets.right_click_menu import RightClickMenu
from kivy.app import App

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class LogViewOutputHandler(logging.StreamHandler):
    def emit(self,record):
        try:
            App.get_running_app().log_this(record.msg)
        except:
            pass


logging.handlers.log_view_output_handler = LogViewOutputHandler

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
            "level":"DEBUG"},
        "actions":{
            "class":"logging.StreamHandler",
            "formatter":"main",
            "level":"DEBUG"},
        "log_view":{
            "class":"logging.handlers.log_view_output_handler",
            "formatter":"main",
            "level":"INFO"}
    },
    "loggers":{
        "stat_analysis.main":{
            "handlers":["gui","log_view"],
            "level":"INFO"
        },
        "stat_analysis.actions":{
            "handlers":["actions","log_view"],
            "level":"DEBUG"
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


class MainSplitterStrip(Button):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.text = "HI"


class StatAnalysis(Widget):
    """
    Root widget for the app
    """
    primary_pane = ObjectProperty(None)
    log_view = ObjectProperty(None)


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
                x.bind(on_touch_down=lambda *args:self.primary_pane_edit.refresh(args[0].stored_action))
                tv.add_node(x,parent_node)

        self.add_widget(tv)


class HomeView(ScrollView):
    """
    Widget for the main home screen
    """
    datasets_grid = ObjectProperty(None)
    actions_grid = ObjectProperty(None)


class ActionsGrid(GridLayout):
    data_tbl = ListProperty([])

    def __init__(self,btn_fn={},**kwargs):
        self.btn_fn = btn_fn
        super().__init__(**kwargs)
        self.headers = ["Name","Type"]
        self.cols = len(self.headers)
        self.click_menu_active = False
        for header in self.headers:
            self.add_btn(header)

    def add_btn(self,text):
        x = BorderedButton(b_width=1, padding=(2, 2), size_hint_x=0.4, color=(0, 0, 0, 1), text=str(text),
                          valign="middle", halign="left",background_color=(1,1,1,1),background_normal="")
        x.bind(size=x.setter("text_size"))
        self.add_widget(x)
        return x

    def render(self,re_render=False):
        if re_render:
            self.clear_widgets()
            for header in self.headers:
                self.add_btn(header)

        for action in self.data_tbl:
            if action.save_name == None:
                # Don't display this action as it can't be viewed, eg
                # transform data
                continue

            col1 = self.add_btn(action.save_name)
            if 0 in self.btn_fn.keys():
                col1.bind(on_touch_down=self.btn_fn[0])

            col2 = self.add_btn(action.type)
            if 1 in self.btn_fn.keys():
                col1.bind(on_touch_down=self.btn_fn[1])

    def view_dataset(self,instance,touch):
        if instance.collide_point(touch.x, touch.y):
            if touch.button == "left":
                App.get_running_app().root_widget.primary_pane.refresh(data.view_data.ViewData,dataset=instance.text)

    def load_action(self,instance,touch):
        if instance.collide_point(touch.x,touch.y):
            if self.click_menu_active != False:
                if self.click_menu_active.collide_point(touch.x,touch.y):
                    return False

            if touch.button == "left":
                action = App.get_running_app().get_action_by_name(instance.text)
                if action == False:
                    # Action not found
                    return False
                App.get_running_app().root_widget.primary_pane.reload_action(action)
            elif touch.button == "right":
                new_pos = self.to_window(touch.x,touch.y)
                menu = RightClickMenu(x=new_pos[0],y=new_pos[1])
                menu.add_opt("Delete",lambda *args: App.get_running_app().get_action_by_name(instance.text).delete(
                    callback=self.delete_callback
                ))
                menu.open()
                self.click_menu_active = menu
                App.get_running_app().root_widget.add_widget(menu)

    def delete_callback(self,*args):
        self.data_tbl = App.get_running_app().saved_actions
        self.render(re_render=True)


class ActionTreeViewLabel(TreeViewLabel):
    stored_action = ObjectProperty(None)


class PrimaryPane(GridLayout):
    title = StringProperty("")

    def refresh(self,action,**kwargs):
        logger.info("Changing the active pane to: {}".format(action.type))
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1,1),cols=2)
        self.add_widget(output_widget)
        active_action = action(output_widget,**kwargs)
        active_action.render()

    def reload_action(self,action,**kwargs):
        logger.info("Loading pre-loaded action")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1, 1), cols=2)
        self.add_widget(output_widget)
        active_action = action
        action.output_widget = output_widget

        active_action.set_default_form_vals()
        active_action.render()
        active_action.run(quiet=False,validate=False,preloaded=True,use_cached=True)

    def go_home(self,*args):
        logger.info("Changing active pane to home screen")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                # item.clear_widgets()
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
    output = ObjectProperty(None)
    close_btn = ObjectProperty(None)
    scroll_view = ObjectProperty(None)
    log_visible = BooleanProperty(True)
    prev_height = NumericProperty(20)

    def log_msg(self,msg):
        if self.output.text != "":
            self.output.text += "\n" + msg
        else:
            self.output.text  += msg

    def toggle_log_view(self):
        if self.log_visible:
            print("Hiding log view")
            # Minimise the scroll view
            self.prev_height = self.scroll_view.height
            self.parent.size_hint_y = 0
            self.parent.strip_size = 0
            self.scroll_view.height = 0
            self.height = self.close_btn.height
            self.size_hint_y = None

            self.close_btn.background_normal = "res/un_minimise.png"
            self.log_visible = False
        else:
            self.scroll_view.height = self.prev_height
            self.height = 100
            self.parent.strip_size = "10pt"
            self.parent.size_hint_y = 0.2
            self.scroll_view.height = self.prev_height
            self.size_hint_y = 0.2

            self.close_btn.background_normal = "res/minimise.png"
            self.log_visible = True

class LogText(TextInput):
    """
    Generic widget that displays text in a scrolling box
    """
    def insert_text(self, substring, from_undo=False):
        # This disables user input of text but still allows for internally adding
        # to the text property
        return


class StatApp(App):
    accent_col = (219/255,46/255,52/255,1)
    title_pane_col = (34/255,34/255,34/255,1)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.load_popup,self.save_popup = None, None
        self.actions = [
            {
                "group_name": "Stats",
                "actions": [stats.regression.Regression, stats.summary.Summary,
                            stats.logistic_regression.LogisticRegression,stats.k_means_clustering.KMeansClustering,
                            stats.normal_distribution.NormalDistribution,stats.poisson_distribution.PoissonDistribution]
            },
            {
                "group_name": "Data",
                "actions": [data.csv.ImportCSV, data.view_data.ViewData, data.set_col_types.SetColTypes,
                            data.get_random_sample.DataSample,data.transform_data.TransformData]
            },
            {
                "group_name": "Graph",
                "actions": [graph.bar_chart.BarChart,graph.scatter.ScatterPlot]
            }
        ]
        self.startup_messages = ""
        self.started_up = False
        self.saved_actions = []
        self.datasets = []

    def build(self):
        self.title = "Stat Analysis"
        Window.clearcolor = (.85,.85,.85,1)
        Window.size = (1336,768)
        self.root_widget = StatAnalysis()
        inspector.create_inspector(Window,self.root_widget)
        self.started_up = True
        self.log_this(self.startup_messages)
        return self.root_widget

    def get_dataset_by_name(self,name):
        # Find the data set
        dataset = None
        for d in self.datasets:
            if d.save_name == name:
                dataset = d
                break
        if dataset == None:
            logger.error("Dataset name {} from get_cols_from not found".format(name))
            return False

        return dataset

    def get_action_by_name(self,name):
        # Find the data set
        action = None
        for a in self.saved_actions:
            if a.save_name == name:
                action = a
                break
        if action == None:
            logger.error("Action {} couldn't be found".format(name))
            return False

        return action


    def load_btn(self,*args):
        self.load_popup = Popup(size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserLoadDialog()
        f_chooser.on_load = self.do_load
        f_chooser.on_cancel = lambda :self.load_popup.dismiss()
        self.load_popup.content = f_chooser
        self.load_popup.open()

    def do_load(self,path,filename):
        self.load_file(os.path.join(path,filename[0]))

    def load_file(self,fpath):
        if self.load_popup != None:
            self.load_popup.dismiss()
        actions = []
        for group in self.actions:
            for action in group["actions"]:
                actions.append(action)
        with open(fpath, "rb") as f:
            dump = pickle.load(f)

        actions_loaded = 0
        for item in dump:
            # Find the correct action specified by "type"
            type_action = None
            for action in actions:
                if action.type == item[1]["type"]:
                    type_action = action(None)
                    break
            if type_action == None:
                logger.error("In loading save file action type {} not found, stopping load".format(item[1]["type"]))
                continue
            success = type_action.load(item[1])
            if success == True:
                actions_loaded += 1
            else:
                # Error occured when loading the save file via a command line argument
                # add the error to the startup messages so user will be informed in the log view
                self.startup_messages += "Error in loading saved action. Error:\n{}\n" \
                                         "View log file for more info\n\n".format(success,item[1]["type"])

        logger.info("Loading completed, {} actions/datasets loaded".format(actions_loaded))

    def save_btn(self,*args):
        self.save_popup = Popup(size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserSaveDialog(default_file_name="Project.stat")
        f_chooser.on_save = self.do_save
        f_chooser.on_cancel = lambda: self.save_popup.dismiss()
        self.save_popup.content = f_chooser
        self.save_popup.open()

    def do_save(self,path,filename):
        self.save_popup.dismiss()
        to_save = []
        for dataset in self.datasets:
            to_save.append(("dataset",dataset.serialize()))

        for action in self.saved_actions:
            to_save.append(("action",action.serialize()))

        with open(os.path.join(path,filename),"wb") as f:
            pickle.dump(to_save,f)

    def log_this(self,msg):
        self.root_widget.log_view.log_msg(msg)

    def add_dataset(self,dataset):
        for set in self.datasets:
            if dataset.save_name == set.save_name:
                raise ValueError("A dataset with that name already exists")

        self.datasets.append(dataset)

    def add_action(self,action):
        for set in self.saved_actions:
            if action.save_name == set.save_name and action.save_name != None:
                raise ValueError("A dataset with that name already exists")

        self.saved_actions.append(action)

def main():
    parser = argparse.ArgumentParser(description="Stat Analysis")
    parser.add_argument("save_file",nargs="?",default=None,type=str)
    results = parser.parse_args()

    app = StatApp()
    if results.save_file != None:
        app.load_file(results.save_file)
    app.run()
