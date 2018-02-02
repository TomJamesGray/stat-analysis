import logging
import logging.handlers
import subprocess
import os
import logging.config
import pickle
import argparse
from kivy.config import Config
from kivy.resources import resource_find
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty,ObjectProperty,BooleanProperty,NumericProperty,ListProperty,Property
from kivy.modules import inspector
from kivy.resources import resource_find
from stat_analysis.actions import stats,data,graph
# # Import CustomActionBtn so kivy is made aware of it for the kv file
from stat_analysis.generic_widgets.action_bar import CustomActionBtn
from stat_analysis.generic_widgets.bordered import BorderedButton
from stat_analysis.generic_widgets.files import FileChooserSaveDialog,FileChooserLoadDialog
from stat_analysis.generic_widgets.right_click_menu import RightClickMenu
from stat_analysis.generic_widgets.popup_inputs import PopupStringInput
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
    prev_width = NumericProperty()
    scroller_visible = BooleanProperty(True)

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

    def toggle_view(self):
        if self.scroller_visible:
            # Minimise the actions scroller
            self.prev_width = self.width
            self.parent.size_hint_x = None
            self.parent.strip_size = 0
            self.parent.width = 0
            self.background_normal = ""
            self.width = 0
            self.size_hint_x = None

            self.scroller_visible = False
        else:
            self.width = self.prev_width
            self.parent.width = self.prev_width

            self.parent.strip_size = "10pt"
            self.parent.size_hint_x = 0.2
            self.size_hint_x = 0.2

            self.scroller_visible = True


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
            self.add_btn(header,header=True)

    def add_btn(self,text,header=False):
        x = BorderedButton(b_width=1, padding=(5, 5), size_hint_x=0.4, color=(0, 0, 0, 1), text=str(text),
                          valign="middle", halign="left",background_color=(1,1,1,1),background_normal="")
        if header:
            x.color = App.get_running_app().accent_col
        x.bind(size=x.setter("text_size"))
        self.add_widget(x)
        return x

    def render(self,re_render=False):
        if re_render:
            self.clear_widgets()
            for header in self.headers:
                self.add_btn(header,header=True)

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
            if self.click_menu_active != False:
                if self.click_menu_active.collide_point(touch.x,touch.y):
                    return False

            if touch.button == "left":
                App.get_running_app().root_widget.primary_pane.refresh(data.view_data.ViewData,dataset=instance.text)

            elif touch.button == "right":
                new_pos = self.to_window(touch.x,touch.y)
                menu = RightClickMenu(x=new_pos[0],y=new_pos[1])
                menu.add_opt("Delete",lambda *args: App.get_running_app().get_dataset_by_name(instance.text).delete_dataset(
                    callback=self.delete_dataset_callback
                ))
                menu.open()
                self.click_menu_active = menu
                App.get_running_app().root_widget.add_widget(menu)


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
                menu.add_opt("Delete",lambda *args: App.get_running_app().get_action_by_name(instance.text).delete_action(
                    callback=self.delete_action_callback
                ))
                menu.open()
                self.click_menu_active = menu
                App.get_running_app().root_widget.add_widget(menu)

    def delete_action_callback(self,*args):
        self.data_tbl = App.get_running_app().saved_actions
        self.render(re_render=True)

    def delete_dataset_callback(self,*args):
        self.data_tbl = App.get_running_app().datasets
        self.render(re_render=True)

class ActionTreeViewLabel(TreeViewLabel):
    stored_action = ObjectProperty(None)


class PrimaryPane(GridLayout):
    title = StringProperty("")
    home_view_active = BooleanProperty(True)
    home_view = ObjectProperty(None)
    active_action = None

    def refresh(self,action,**kwargs):
        logger.info("Changing the active pane to: {}".format(action.type))
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1,1),cols=2)
        self.add_widget(output_widget)
        self.active_action = action(output_widget,**kwargs)
        self.active_action.render()
        self.home_view_active = False

    def reload_action(self,action,**kwargs):
        logger.info("Loading pre-loaded action")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        self.title = action.type
        output_widget = GridLayout(size_hint=(1, 1), cols=2)
        self.add_widget(output_widget)
        self.active_action = action
        self.active_action.output_widget = output_widget

        self.active_action.set_default_form_vals()
        self.active_action.render()
        self.active_action.run(quiet=False,validate=False,preloaded=True,use_cached=True)
        self.home_view_active = False

    def go_home(self,*args):
        logger.info("Changing active pane to home screen")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                # item.clear_widgets()
                self.remove_widget(item)
        self.title = "Home"
        self.home_view_active = True
        self.home_view = HomeView()
        self.add_widget(self.home_view)
        self.active_action = None

    def try_refresh_home_view(self):
        if self.home_view_active:
            self.home_view.datasets_grid.data_tbl = App.get_running_app().datasets
            self.home_view.datasets_grid.render(re_render=True)
            self.home_view.actions_grid.data_tbl = App.get_running_app().saved_actions
            self.home_view.actions_grid.render(re_render=True)

    # def show_help(self):


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

        self.scroll_view.scroll_y = 0

    def toggle_log_view(self):
        if self.log_visible:
            # Minimise the scroll view
            self.prev_height = self.scroll_view.height
            self.parent.size_hint_y = 0
            self.parent.strip_size = 0
            self.scroll_view.height = 0
            self.height = 0
            self.size_hint_y = None

            self.log_visible = False
        else:
            self.scroll_view.height = self.prev_height
            self.height = 100
            self.parent.strip_size = "10pt"
            self.parent.size_hint_y = 0.2
            self.scroll_view.height = self.prev_height
            self.size_hint_y = 0.2

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
        # Get the absolute path of the "temporary" file directory
        self.tmp_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"tmp")
        self.help_text =\
        """[size=16][b]Stat Analysis Help[/b][/size]

Stat Analysis is a statistical analysis program that implements features such as K Means clustering, logisitc regression and more as well as more traditional features such as mean and standard deviation.

[b]Get started[/b]

If you don't have any datasets of your own to use, you can use some of the pre-loaded datasets, such as heights and exam passes. If you already have a CSV dataset to use then you can go to Data > CSV Import and follow the instructions from there.

Some actions also have additional help available via Help > 'Help for this action'.
        """
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

    def load_example_dataset(self,name):
        datasets = {
            "heights":("heights",resource_find("res/example_datasets/heights/heights_example_dataset.stat")),
            "exam_scores": ("exam_scores",
                            resource_find("res/example_datasets/exam_results/exam_results_example_dataset.stat"))
        }
        str_input = PopupStringInput(label="Dataset name")
        str_input.text_input.text = datasets[name][0]
        popup = Popup(size_hint=(None,None),size=(400,150))

        str_input.submit_btn.bind(on_press=lambda *args:self.submit_load_example(
            str_input,popup,datasets[name][1]))

        popup.content = str_input
        popup.open()

    def submit_load_example(self,str_input,popup,dataset_location):
        """
        Handles the submit button for the "PopupStringInput" displayed when a example dataset is loaded.
        It loads the save file for the dataset, dismisses the popup and refreshes the home view, so the
        Actions grid show the new datasets
        :param str_input: Instance of the PopupStringInput
        :param popup: The Popup widget that the str_input is within
        :param dataset_location: The location of the save file for the example dataset
        :return:
        """
        self.load_file(dataset_location,override_dataset_name=str_input.text_input.text)
        popup.dismiss()
        self.root_widget.primary_pane.try_refresh_home_view()

    def load_btn(self):
        self.load_popup = Popup(size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserLoadDialog()
        f_chooser.on_load = self.do_load
        f_chooser.on_cancel = lambda :self.load_popup.dismiss()
        self.load_popup.content = f_chooser
        self.load_popup.open()

    def do_load(self,path,filename):
        self.load_file(os.path.join(path,filename[0]))

    def load_file(self,fpath,**kwargs):
        """
        Loads all the saved actions from a given file
        :param fpath: The absolute path of the file to load from
        :return: The amount of actions successful loaded
        """
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
            success = type_action.load(item[1],**kwargs)
            if success == True:
                actions_loaded += 1
            else:
                # Error occured when loading the save file via a command line argument
                # add the error to the startup messages so user will be informed in the log view
                self.startup_messages += "Error in loading saved action. Error:\n{}\n" \
                                         "View log file for more info\n\n".format(success,item[1]["type"])

        logger.info("Loading completed, {} actions/datasets loaded".format(actions_loaded))
        return actions_loaded

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
        try:
            self.root_widget.log_view.log_msg(msg)
        except:
            pass

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

    def show_app_help(self):
        """
        Shows the help window for the app
        """
        subprocess.Popen(["python", resource_find("help_view.py"), self.help_text])

def main():
    parser = argparse.ArgumentParser(description="Stat Analysis")
    parser.add_argument("save_file",nargs="?",default=None,type=str)
    results = parser.parse_args()

    app = StatApp()
    if results.save_file != None:
        app.load_file(results.save_file)
    app.run()
