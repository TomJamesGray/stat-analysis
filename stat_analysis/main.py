import logging
import logging.handlers
import subprocess
import os
import logging.config
import pickle
from kivy.factory import Factory
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView,TreeViewLabel
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

try:
    # Try and import pygame stuff
    import pygame.cursors
    import pygame.mouse
    from kivy.core.window.window_pygame import WindowPygame
except ModuleNotFoundError:
    pass

try:
    # Try and import sdl stuff
    from kivy.core.window.window_sdl2 import WindowSDL
except ModuleNotFoundError:
    pass

from kivy.properties import StringProperty,ObjectProperty,BooleanProperty,NumericProperty,ListProperty
from kivy.modules import inspector
from kivy.resources import resource_find
from stat_analysis.actions import stats,data,graph
from stat_analysis.generic_widgets.action_bar import CustomActionBtn
from stat_analysis.generic_widgets.bordered import BorderedButton
from stat_analysis.generic_widgets.files import FileChooserSaveDialog,FileChooserLoadDialog
from stat_analysis.generic_widgets.right_click_menu import RightClickMenu
from stat_analysis.generic_widgets.popup_inputs import PopupStringInput
from kivy.app import App

# Register the CustomActionBtn class with kivy, otherwise it wouldn't be detected
Factory.register("CustomActionBtn",cls=CustomActionBtn)


class LogViewOutputHandler(logging.StreamHandler):
    """
    Customer logging class that will output to the logging box in the program
    """
    def emit(self,record):
        try:
            App.get_running_app().log_this(record.msg)
        except:
            pass


# Make the logging module aware of the custom log handler
logging.handlers.log_view_output_handler = LogViewOutputHandler
# Configure logging
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
            "level":"INFO"
        },
        "stat_analysis.form_inputs":{
            "handlers":["gui"],
            "level":"INFO"
        },
        "stat_analysis.generic_widgets":{
            "handlers":["gui"],
            "level":"INFO"
        }
    }
}
# Setup logging
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
        self.bar_width = 5
        tv = TreeView(size_hint=(1,None),hide_root=True)
        # Use all available height
        tv.bind(minimum_height=tv.setter("height"))
        for group in App.get_running_app().actions:
            # Create parent group labels based off the actions property of the app
            parent_node = TreeViewLabel(text=group["group_name"],color=(0,0,0,1))
            tv.add_node(parent_node)
            for action in group["actions"]:
                # Create the labels that display the individual actions
                x = ActionTreeViewLabel(color=(0,0,0,1),text=action.view_name,stored_action=action)
                # When the button is pressed, load the action by using the refresh method of the primary pane
                x.bind(on_touch_down=lambda *args:self.primary_pane_edit.refresh(args[0].stored_action))
                tv.add_node(x,parent_node)

        self.add_widget(tv)

    def toggle_view(self):
        if self.scroller_visible:
            # Minimise the actions scroller
            self.prev_width = self.width
            self.parent.strip_size = 0
            self.parent.width = 0
            self.background_normal = ""
            self.width = 0

            self.scroller_visible = False
        else:
            self.width = self.prev_width
            self.parent.width = self.prev_width
            self.parent.strip_size = "10pt"

            self.scroller_visible = True


class HomeView(ScrollView):
    """
    Widget for the main home screen
    """
    datasets_grid = ObjectProperty(None)
    actions_grid = ObjectProperty(None)


class ActionsGrid(GridLayout):
    data_tbl = ListProperty([])
    empty_msg = StringProperty("")

    def __init__(self,btn_fn={},**kwargs):
        self.btn_fn = btn_fn
        super().__init__(**kwargs)
        # Set headers
        self.headers = ["Name","Type"]
        self.cols = len(self.headers)
        self.click_menu_active = False

    def add_btn(self,text,header=False):
        # Create button that changes the cursor to the "click" cursor on hover
        x = BorderedHoverButton(b_width=1, padding=(5, 5), size_hint_x=0.4, color=(0, 0, 0, 1), text=str(text),
                                valign="middle", halign="left",background_color=(1,1,1,1),background_normal="",
                                markup=True)
        if header:
            # Set the color to red if this is a header
            x.color = App.get_running_app().accent_col
        # Make the text use all available space so aligning works
        x.bind(size=x.setter("text_size"))
        self.add_widget(x)
        return x

    def render(self,re_render=False):
        self.clear_widgets()

        # Make sure there are saved actions with saved names that aren't None
        empty = True
        for x in self.data_tbl:
            if x.save_name != None:
                empty = False
                # A saved action that can be displayed has been found so exit the loop
                break

        if empty:
            # Display the empty message
            x = Label(text=self.empty_msg,color=(0,0,0,1))
            # Make the text use all available space so aligning works
            x.bind(size=x.setter("text_size"))
            self.add_widget(x)

            return

        for header in self.headers:
            # Add the headers
            self.add_btn(header,header=True)

        for action in self.data_tbl:
            if action.save_name == None:
                # Don't display this action as it can't be viewed, eg
                # transform data
                continue

            col1 = self.add_btn(action.save_name)
            if 0 in self.btn_fn.keys():
                # Add the function that is called when the button in the 1st column is pressed
                col1.bind(on_touch_down=self.btn_fn[0])
                # When the mouse moves run the mouse_pos method so the cursor can change
                Window.bind(mouse_pos=col1.mouse_pos)

            col2 = self.add_btn(action.type)
            if 1 in self.btn_fn.keys():
                # Add the function that is called when the button in the 2nd column is pressed
                col2.bind(on_touch_down=self.btn_fn[1])
                # When the mouse moves run the mouse_pos method so the cursor can change
                Window.bind(mouse_pos=col2.mouse_pos)

    def view_dataset(self,instance,touch):
        # Reset the cursor to the normal arrow cursor
        App.get_running_app().set_cursor("arrow")
        # Check if the touch collides with the button
        if instance.collide_point(touch.x, touch.y):
            if self.click_menu_active != False:
                # Check if user is instead just pressing a right click menu that just happens to be over this widget
                if self.click_menu_active.collide_point(touch.x,touch.y):
                    return False

            if touch.button == "left":
                # View the data set
                App.get_running_app().root_widget.primary_pane.refresh(data.view_data.ViewData,dataset=instance.text)

            elif touch.button == "right":
                # Get the position of the press
                new_pos = self.to_window(touch.x,touch.y)
                # Create the right click menu
                menu = RightClickMenu(x=new_pos[0],y=new_pos[1])
                # Add the option to delete the data set
                menu.add_opt("Delete",lambda *args: App.get_running_app().get_dataset_by_name(instance.text).
                             delete_dataset(callback=self.delete_dataset_callback
                ))
                # Open the right click menu
                menu.open()
                self.click_menu_active = menu
                # Display the right click menu
                App.get_running_app().root_widget.add_widget(menu)

    def load_action(self,instance,touch):
        # Reset the cursor to the normal arrow cursor
        App.get_running_app().set_cursor("arrow")
        # Check if the touch collides with the button
        if instance.collide_point(touch.x,touch.y):
            # Check if user is instead just pressing a right click menu that just happens to be over this widget
            if self.click_menu_active != False:
                if self.click_menu_active.collide_point(touch.x,touch.y):
                    return False

            if touch.button == "left":
                # Get the action that has been selected
                action = App.get_running_app().get_action_by_name(instance.text)
                if action == False:
                    # Action not found
                    return False

                try:
                    # Try and run the action
                    App.get_running_app().root_widget.primary_pane.reload_action(action)
                except Exception as e:
                    # The action hasn't run as expected
                    if not App.get_running_app().devel_mode:
                        # Not in development mode so don't crash
                        logger.error("Error in running action {}\nGoing back to home".format(repr(e)))
                        # Go back home
                        App.get_running_app().root_widget.primary_pane.go_home()
                    else:
                        # Raise the error since we're in development mode so the traceback would display useful info
                        raise e

            elif touch.button == "right":
                # Get the position of the press
                new_pos = self.to_window(touch.x, touch.y)
                # Create the right click menu
                menu = RightClickMenu(x=new_pos[0], y=new_pos[1])
                # Add the option to delete the action set
                menu.add_opt("Delete",lambda *args: App.get_running_app().get_action_by_name(instance.text).delete_action(
                    callback=self.delete_action_callback
                ))
                # Open the right click menu
                menu.open()
                self.click_menu_active = menu
                # Display the right click menu
                App.get_running_app().root_widget.add_widget(menu)

    def delete_action_callback(self,*args):
        # Refresh the table after a action has been deleted
        self.data_tbl = App.get_running_app().saved_actions
        self.render()

    def delete_dataset_callback(self,*args):
        # Refresh the table after a data set has been deleted
        self.data_tbl = App.get_running_app().datasets
        self.render()


class BorderedHoverButton(BorderedButton):
    hovering = BooleanProperty(False)
    bottom = BooleanProperty(False)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering and collision:
            # Mouse moved within the button
            # Ensure the curreent cursor is the "hand" cursor
            if App.get_running_app().current_cursor != "hand":
                App.get_running_app().set_cursor("hand")
            return
        elif collision and not self.hovering:
            # Mouse enter button
            App.get_running_app().set_cursor("hand")
        elif self.hovering and not collision:
            # Mouse exit button
            App.get_running_app().set_cursor("arrow")

        self.hovering = collision

    def on_touch_down(self, touch):
        # Reset hover state of button
        self.hovering = False
        super().on_touch_down(touch)


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
        # Set the title to the name of the action that is being loaded
        self.title = action.view_name
        # Create the output widget
        output_widget = GridLayout(size_hint=(1,1),cols=2,spacing=(5,5))
        self.add_widget(output_widget)
        # Initialise the action
        self.active_action = action(output_widget,**kwargs)
        # Render the action
        self.active_action.render()
        self.home_view_active = False

    def reload_action(self,action,**kwargs):
        logger.info("Loading pre-loaded action")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        # Display the type of action and name of saved action in the title bar
        self.title = "{} - {}".format(action.view_name,action.save_name)
        # Create the output widget
        output_widget = GridLayout(size_hint=(1, 1), cols=2,spacing=(5,5))
        self.add_widget(output_widget)
        self.active_action = action
        self.active_action.output_widget = output_widget
        # Set the default form values in the form property based off the saved form outputs
        self.active_action.set_default_form_vals()
        # Render the action
        self.active_action.render()
        # Run the action without validating and use cached data
        self.active_action.run(quiet=False,validate=False,use_cached=True)
        self.home_view_active = False

    def go_home(self,*args):
        logger.info("Changing active pane to home screen")
        for item in self.children:
            # Remove all widgets that aren't the title pane
            if type(item) != TitlePane:
                self.remove_widget(item)
        # Set the title to "Home"
        self.title = "Home"
        self.home_view_active = True
        # Initialise the home view widget
        self.home_view = HomeView()
        self.add_widget(self.home_view)
        self.active_action = None

    def try_refresh_home_view(self):
        if self.home_view_active:
            # Update the data used by the data sets grid
            self.home_view.datasets_grid.data_tbl = App.get_running_app().datasets
            # Re-render it
            self.home_view.datasets_grid.render()
            # Update the data used by the actions sets grid
            self.home_view.actions_grid.data_tbl = App.get_running_app().saved_actions
            # Re-render it
            self.home_view.actions_grid.render()


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

    def log_msg(self,msg):
        if self.output.text != "":
            # Separate messages by a new line
            self.output.text += "\n" + msg
        else:
            self.output.text += msg
        # Scroll to the bottom of the log view when a message is logged
        self.scroll_view.scroll_y = 0

    def toggle_log_view(self):
        if self.log_visible:
            # Minimise the scroll view
            self.parent.size_hint_y = 0
            self.parent.strip_size = 0
            self.scroll_view.height = 0
            self.height = 0
            self.size_hint_y = None

            self.log_visible = False
        else:
            # Show the log view
            self.height = 100
            self.parent.strip_size = "10pt"
            self.parent.size_hint_y = 0.2
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
    # These are the colors that should be used for graphs, order: Green, sky blue, red, purple, blue
    graph_colors = [(80/255,167/255,31/255),(64/255,175/255,194/255),(223/255,46/255,29/255),(156/255,68/255,181/255),
                    (52/255,99/255,233/255)]

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.devel_mode = False
        self.load_popup,self.save_popup = None, None
        # Set the actions that are available to users
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
                            data.transform_data.TransformData]
            },
            {
                "group_name": "Graph",
                "actions": [graph.bar_chart.BarChart,graph.scatter.ScatterPlot]
            }
        ]
        self.example_datasets = {
            "heights": ("heights", resource_find("res/example_datasets/heights/heights_example_dataset.stat")),
            "exam_scores": ("exam_scores",
                            resource_find("res/example_datasets/exam_results/exam_results_example_dataset.stat"))
        }
        # Get the absolute path of the "temporary" file directory
        self.tmp_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"tmp")
        # Set the help text for the "general help"
        self.help_text =\
        """[size=16][b]Stat Analysis Help[/b][/size]

Stat Analysis is a statistical analysis program that implements features such as K Means clustering, logisitc regression and more as well as more traditional features such as mean and standard deviation.

[b]Get started[/b]

If you don't have any datasets of your own to use, you can use some of the pre-loaded datasets, such as heights and exam passes. If you already have a CSV dataset to use then you can go to Data > CSV Import and follow the instructions from there.

Some actions also have additional help available via Help > 'Help for this action'.
        """
        # Initialise properties
        self.startup_messages = ""
        self.started_up = False
        self.saved_actions = []
        self.datasets = []
        self.current_cursor = "arrow"
        self.pygame_cursors = {}
        # Get cursor info setup, ie for pygame import the modules and any xbms
        if self.get_window_provider() == "pygame":
            # Compile the resize cursor
            cursor, mask = pygame.cursors.compile(pygame.cursors.sizer_x_strings, "X", ".")
            self.pygame_cursors["size_we"] = ((24, 16), (7, 11), cursor, mask)
            # Load the custom hand arrow cursor and compile it
            cursor = pygame.cursors.load_xbm(resource_find("res/handarrow.xbm"),resource_find("res/handarrow-mask.xbm"))
            self.pygame_cursors["hand"] = cursor
            self.pygame_cursors["arrow"] = pygame.cursors.arrow

    def build(self):
        # Set the window title
        self.title = "Stat Analysis"
        # Set the background color of the window
        Window.clearcolor = (.85,.85,.85,1)
        # Set the size of the window
        Window.size = (1336,768)
        # Create the root widget
        self.root_widget = StatAnalysis()

        if self.devel_mode:
            # Enable any development options
            inspector.create_inspector(Window,self.root_widget)
            self.startup_messages += "Enabling development mode\n"
        else:
            # Disable the dots that show on left click
            Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
            # Disable exiting on escape
            Config.set('kivy', 'exit_on_escape', '0')
            # Disable the default kivy settings window
            self.open_settings = lambda *args:None

        self.started_up = True
        # Log any important messages that occurred before the logging widget was initialised
        self.log_this(self.startup_messages)
        return self.root_widget

    def get_dataset_by_name(self,name):
        dataset = None
        for d in self.datasets:
            # Find the data set
            if d.save_name == name:
                # Data set has been found so exit the loop
                dataset = d
                break
        if dataset == None:
            logger.error("Dataset name {} not found".format(name))
            return False

        return dataset

    def get_action_by_name(self,name):
        action = None
        for a in self.saved_actions:
            # Find the data set
            if a.save_name == name:
                action = a
                # Action has been found so exit the loop
                break
        if action == None:
            logger.error("Action {} couldn't be found".format(name))
            return False

        return action

    def load_example_dataset(self,name):
        # Create input for the data set name
        str_input = PopupStringInput(label="Dataset name")
        # Set the default name for the example data set
        str_input.text_input.text = self.example_datasets[name][0]
        # Create the popup
        popup = Popup(size_hint=(None,None),size=(400,150),title="Example Dataset Save Name")
        # When the submit button is pressed on the input run the submit_load_example method
        str_input.submit_btn.bind(on_press=lambda *args:self.submit_load_example(
            str_input,popup,self.example_datasets[name][1]))
        str_input.dismiss_btn.bind(on_press=lambda *args:popup.dismiss())
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
        # Load the save file that contains the instructions for the example data set
        self.load_file(dataset_location,override_dataset_name=str_input.text_input.text)
        # Close the popup
        popup.dismiss()
        # Refresh the widgets on the home view to show the new data sets
        self.root_widget.primary_pane.try_refresh_home_view()

    def load_btn(self):
        self.load_popup = Popup(size_hint=(None,None),size=(400,400),title="Load Save File")
        # Create the file dialog, filter the files show it only shows .stat files
        f_chooser = FileChooserLoadDialog(filters=[lambda _,filename: filename.endswith(".stat")])
        # When the load file button is pressed in the file chooser run the do_load method
        f_chooser.on_load = self.do_load
        f_chooser.on_cancel = lambda :self.load_popup.dismiss()
        self.load_popup.content = f_chooser
        self.load_popup.open()

    def do_load(self,path,filename):
        # Load the file
        self.load_file(os.path.join(path,filename[0]))
        # Refresh the widgets on the home view to show the new data sets
        self.root_widget.primary_pane.try_refresh_home_view()

    def load_file(self,fpath,**kwargs):
        """
        Loads all the saved actions from a given file
        :param fpath: The absolute path of the file to load from
        :return: The amount of actions successful loaded
        """
        if self.load_popup != None:
            # Dismiss any popups
            self.load_popup.dismiss()
        actions = []
        for group in self.actions:
            for action in group["actions"]:
                # Create a list of the actions
                actions.append(action)
        # Open the save file
        with open(fpath, "rb") as f:
            try:
                # Load the data in with pickle
                dump = pickle.load(f)
            except pickle.UnpicklingError:
                logger.error("Error in loading save file {}, possibly corrupted".format(fpath))
                return

        actions_loaded = 0
        for item in dump:
            # Find the correct action specified by "type" from the list of the actions
            type_action = None
            for action in actions:
                if action.type == item[1]["type"]:
                    # Initialise the action
                    type_action = action(None)
                    # Action has been found so exit the loop
                    break
            if type_action == None:
                logger.error("In loading save file action type {} not found, stopping load".format(item[1]["type"]))
                continue
            # Run the load method of the action
            success = type_action.load(item[1],**kwargs)

            if success == True:
                # Action has been successfully loaded
                actions_loaded += 1
            else:
                # Error occured when loading the save file via a command line argument
                # add the error to the startup messages so user will be informed in the log view
                self.startup_messages += "Error in loading saved action. Error:\n{}\n" \
                                         "View log file for more info\n\n".format(success,item[1]["type"])

        logger.info("Loading completed, {} actions/datasets loaded".format(actions_loaded))
        return actions_loaded

    def save_btn(self,*args):
        self.save_popup = Popup(size_hint=(None,None),size=(400,400),title="Save Project")
        # Create the file chooser dialog
        f_chooser = FileChooserSaveDialog(default_file_name="Project.stat")
        # When the save button in the file dialog is pressed run the do_save method
        f_chooser.on_save = self.do_save
        f_chooser.on_cancel = lambda: self.save_popup.dismiss()
        self.save_popup.content = f_chooser
        self.save_popup.open()

    def do_save(self,path,filename):
        # Close the popup
        self.save_popup.dismiss()
        # List to hold the data that is to be saved
        to_save = []
        for dataset in self.datasets:
            # Serialize the data sets
            to_save.append(("dataset",dataset.serialize()))

        for action in self.saved_actions:
            # Serialize the actions
            to_save.append(("action",action.serialize()))

        with open(os.path.join(path,filename),"wb") as f:
            # Write the data to the save file
            pickle.dump(to_save,f)

    def log_this(self,msg):
        try:
            # Add text to the log view
            self.root_widget.log_view.log_msg(msg)
        except:
            # Catch any exceptions caused by logging before the log_view widget is initialised
            pass

    def add_dataset(self,dataset):
        for set in self.datasets:
            if dataset.save_name == set.save_name:
                # Dataset with the same name exists so exit
                raise ValueError("A dataset with that name already exists")
        # Add the data set to the list of saved data sets
        self.datasets.append(dataset)

    def add_action(self,save_action):
        # If save name is None, then allow duplicates
        if save_action.save_name != None:
            for set in self.saved_actions:
                if save_action.save_name == set.save_name:
                    # Action with the same name exists so exit
                    raise ValueError("An action with that name already exists")
        # Add the action to the list of saved actions
        self.saved_actions.append(save_action)

    def show_app_help(self):
        """
        Shows the help window for the app
        """
        subprocess.Popen(["python", resource_find("help_view.py"), self.help_text])

    def set_cursor(self,cursor_name):
        """
        Sets the cursor for the window, this is different to the kivy window `set_system_cursor` as it has
        support for pygame and sdl2 windows. Currently on size_we,hand and arrow are implemented for pygame, however
        it is easy to add support for more.
        :param cursor_name: Cursor name recognized by sdl window provider
        https://kivy.org/docs/api-kivy.core.window.html#kivy.core.window.WindowBase.set_system_cursor
        """
        provider = self.get_window_provider()
        if provider == "pygame":
            # Set the mouse cursor with pygame
            pygame.mouse.set_cursor(*self.pygame_cursors[cursor_name])
        elif provider == "sdl2":
            # Set the mouse cursor with sdl2
            Window.set_system_cursor(cursor_name)
        else:
            logger.warning("Window provider {} currently has no support to set cursor".format(provider))
            return
        self.current_cursor = cursor_name

    def get_window_provider(self):
        """
        Determines the window provider being used
        :return: "pygame", "sdl2" or "other
        """
        if isinstance(Window,WindowPygame):
            return "pygame"
        elif isinstance(Window,WindowSDL):
            return "sdl2"
        else:
            return "other"


def main(results):
    app = StatApp()
    # Set the development mode property
    app.devel_mode = results.devel

    if results.save_file != None:
        if os.path.isfile(results.save_file):
            # If the save file exists run the load_file method
            app.load_file(results.save_file)
        else:
            app.startup_messages += "Save file {} doesn't exist\n".format(results.save_file)
    # Run the app
    app.run()
