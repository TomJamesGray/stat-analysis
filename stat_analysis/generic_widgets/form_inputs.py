from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.properties import StringProperty,BooleanProperty
from kivy.app import App
from kivy.core.window import Window

class FormInputLabel(GridLayout):
    """
    Container class for form labels, handles the creation of tool tips and the actual text for the label
    """
    def __init__(self,text=None,tip=None,**kwargs):
        self.height = 20
        super().__init__(**kwargs)
        self.rows = 1
        self.size_hint_x = 1
        self.size_hint_y = None

        if tip == None:
            main_lbl = FormInputLabelText(text=text)
            self.add_widget(main_lbl)
        else:
            main_lbl = FormInputLabelText(text=text,size_hint=(1,None))
            self.add_widget(main_lbl)
            # Create tool tip
            tooltip = ToolTip(source="res/tooltip.png",width=15,height=15,size_hint=(None,1),tip_text=tip)
            Window.bind(mouse_pos=tooltip.mouse_pos)
            self.add_widget(tooltip)


class FormInputLabelText(Label):
    """
    Widget that displays the text for form input labels
    """
    pass


class ToolTip(Image):
    tip_text = StringProperty("")
    hovering = BooleanProperty(False)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))

        root_widget = App.get_running_app().root_widget
        if self.hovering and collision:
            # Mouse moved within the button
            return
        elif collision and not self.hovering:
            # Mouse enter button
            org_pos = self.to_window(*self.pos)
            text_pos = (org_pos[0]+self.width, org_pos[1]+self.height)
            self.tip_text_widget = ToolTipText(pos=text_pos,text=self.tip_text)
            root_widget.add_widget(self.tip_text_widget)

        elif self.hovering and not collision:
            # Mouse exit button
            root_widget.remove_widget(self.tip_text_widget)

        self.hovering = collision

class ToolTipText(Label):
    """
    Widget that displays the text when a user hovers over a tool tip
    """
    pass