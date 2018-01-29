import logging
import subprocess
import time

from kivy.app import App
from kivy.graphics import Color,Rectangle
from kivy.properties import ObjectProperty,BooleanProperty
from kivy.resources import resource_find
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from stat_analysis.form_inputs import combo_box,check_box,numeric_bounded,numeric,file,string,action_columns

logger = logging.getLogger(__name__)

form_input_maps = {
    "combo_box":combo_box.FormDropDown,
    "check_box":check_box.FormCheckBox,
    "numeric_bounded":numeric_bounded.FormNumericBounded,
    "numeric":numeric.FormNumeric,
    "file":file.FormFile,
    "string":string.FormString,
    "action_columns":action_columns.ActionColumns
}


class BaseAction(object):
    form_width = 220
    help_text = """
    No help is available for this action
    """

    def render(self):
        """
        This is the basic method that renders an action by going through the form property.
        The form property should be structured as a list of form groups. The form group is purely
        for aesthetic reasons currently. The following is an example of a form group:
         {
            "group_name":"Regression",
            "inputs":[
                {
                    "input_type": "check_box",
                    "form_name": "regression",
                    "visible_name": "Regression"
                }
            ]
        }
        The inputs property is a list of dictionaries defining each individual input. Input_type is
        the type of input to be used and will be looked up in form_input_maps. Form name is the
        key for the value in the form_outputs that will be set by the validate method. Visible name
        is the label that will be shown to the user
        :return:
        """
        logger.debug("Rendering action {}".format(self.type))
        form_layout = GridLayout(cols=1,padding=(5,5),spacing=(10,10),width=self.form_width,size_hint=(None,None))
        form_layout.bind(minimum_height=form_layout.setter("height"))
        self.form_items = []
        for group in self.form:
            group_lbl = Label(text=group["group_name"],size_hint=(1,None),
                              height=30,font_size="22",color=App.get_running_app().accent_col)
            group_lbl.bind(size=group_lbl.setter("text_size"))
            form_layout.add_widget(group_lbl)

            for item in group["inputs"]:
                try:
                    cls = form_input_maps[item["input_type"]]
                except KeyError:
                    logger.error("Form input {} not found in form_input_maps".format(item["input_type"]))
                    # Go to next form input
                    continue
                # Give the form widget the whole dict so it can parse the data there
                logger.debug("Adding form item {} for {}".format(cls,item["form_name"]))
                form_cls = cls(item,parent_action=self)
                form_layout.add_widget(form_cls)
                self.form_items.append(form_cls)

        # Add the run action button to end of form
        form_layout.add_widget(Button(text="Run action",on_press=lambda *_:self.timed_run(),size_hint=(1,None),
                                      height=30))

        scroller = ScrollView(size_hint=(None,1),width=self.form_width)
        scroller.add_widget(form_layout)
        self.output_widget.add_widget(scroller)

        # Create the border between the form area and the result area
        self.output_widget.bind(size=self._draw_border)

        # Create the generic output area
        result_output_scroller = ScrollView(size_hint=(1,1))

        result_output = ResultOutputWidget(cols=1,size_hint=(1,None))
        result_output.bind(minimum_height=result_output.setter('height'))

        result_output_scroller.add_widget(result_output)
        self.output_widget.add_widget(result_output_scroller)
        # Add property so that the result output can be added to when the action is run
        self.result_output = result_output

    def timed_run(self,**kwargs):
        start_time = time.time()
        self.run(**kwargs)
        logger.info("Action {} finished in {} seconds".format(self.type,time.time()-start_time))

    def _draw_border(self,*args):
        try:
            self.output_widget.canvas.before.remove(self._rect)
        except Exception:
            pass

        with self.output_widget.canvas.before:
            Color(.6,.6,.6,1)
            self._rect = Rectangle(pos=(self.output_widget.x+self.form_width,self.output_widget.y+10),
                      size=(1,self.output_widget.height-20))

    def validate_form(self):
        """
        Validates the form based on the input dictionaries for each form input,
        handles exceptions thrown by the individual form items on get_val method
        and validation based on input dict criterion.
        If the form is valid the values and form_name's of each input is stored in
        a dict in form_inputs, if the form is invalid the errors are stored in
        form_errors
        :return: Boolean depending on whether form was filled out properly or not
        """
        output = {}
        errors = []
        for item in self.form_items:
            logger.debug("Validating {}".format(item))
            try:
                # Handle errors that may be found in get_val method, ie can't cast to float
                # in numeric input
                val = item.get_val()
            except Exception as e:
                errors.append(repr(e))
                logger.warning(errors[-1])
                continue

            if item.input_dict["required"] and val == None:
                errors.append("Field '{}' is required".format(item.input_dict["visible_name"]))
                logger.warning(errors[-1])

            # Add the input value to the output dictionary
            output[item.input_dict["form_name"]] = val

        if errors == []:
            self.form_outputs = output
            return True
        else:
            self.form_errors = errors
            return False

    def set_default_form_vals(self):
        for group in self.form:
            for  _input in group["inputs"]:
                if self.form_outputs[_input["form_name"]] != None:
                    _input["default"] = self.form_outputs[_input["form_name"]]

    def serialize(self):
        return {"type":self.type,"form_outputs":self.form_outputs}

    def load(self,state):
        self.form_outputs = state["form_outputs"]
        try:
            success = self.run(validate=False,quiet=True)
        except Exception as e:
            err = "Error in loading {}\n{}".format(self.type,repr(e))
            logger.error(err)
            return err

        return True

    def make_err_message(self,msg):
        """
        Makes a simple error message with a popup
        :param msg: Single string or list of strings to be displayed
        :return:
        """
        bullet = "•"

        popup = Popup(size_hint=(None,None),title="Error",width=300)
        cont = GridLayout(cols=1)
        cont.bind(minimum_height=lambda _,height:popup.__setattr__("height",height+150))
        if isinstance(msg,str):
            disp_msg = "{} {}".format(bullet,msg)
        else:
            disp_msg = ""
            for line in msg:
                disp_msg += "{} {}\n".format(bullet,line)

        error_label = Label(text=disp_msg,halign="left",valign="middle")
        error_label.bind(size=error_label.setter("text_size"))
        cont.add_widget(error_label)

        dismiss_btn = Button(text="Dismiss",size_hint=(1,None),padding=(0,10))
        dismiss_btn.bind(on_press=lambda *args:popup.dismiss())
        dismiss_btn.bind(texture_size=dismiss_btn.setter("size"))
        cont.add_widget(dismiss_btn)

        popup.content = cont
        popup.open()

    def delete_action(self,callback=None):
        """
        Removes this action from saved_actions
        """
        App.get_running_app().saved_actions.remove(self)
        print("Removed: {}".format(App.get_running_app().saved_actions))
        if callback != None:
            callback()

    def delete_dataset(self,callback=None):
        """
        Removes this action from saved_actions
        """
        App.get_running_app().datasets.remove(self)
        print("Removed: {}".format(App.get_running_app().datasets))
        if callback != None:
            callback()

    def display_help(self):
        subprocess.Popen(["python",resource_find("help_view.py"),self.help_text])



class ResultOutputWidgetLabelHeader(Label):
    pass


class ResultOutputWidget(GridLayout):
    label_header = ObjectProperty(None)
    # This property is needed to prevent kivy from throwing errors about label header not
    # existing if it's been removed, even if you're only testing whether it exists
    label_header_removed = BooleanProperty(False)

    def clear_outputs(self,all=False):
        if self.label_header_removed:
            # Label header has been removed so clear all outputs and add the result label back
            self.clear_widgets()
            self.label_header = ResultOutputWidgetLabelHeader()
            self.add_widget(self.label_header)
            self.label_header_removed = False
            return

        if not all:
            children = self.children[:]
            for item in children:
                if item != self.label_header:
                    self.remove_widget(item)
        else:
            self.clear_widgets()
            self.label_header_removed = True