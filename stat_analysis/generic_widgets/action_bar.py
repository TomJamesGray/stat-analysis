from kivy.uix.actionbar import ActionItem,ActionButton,ActionGroup,ActionDropDown
from kivy.properties import BooleanProperty,ListProperty
from kivy.core.window import Window

class GenericActionBtn(ActionItem):
    hovering = BooleanProperty(False)
    background_normal_color = ListProperty([34/255,34/255,34/255,1])
    background_hover_color = ListProperty([70/255,70/255,70/255,1])

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.background_color = self.background_normal_color
        Window.bind(mouse_pos=self.mouse_pos)

    def mouse_pos(self,*args):
        if not self.get_root_window():
            # Widget isn't displayed so exit
            return
        # Determine whether mouse is over the button
        collision = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering and collision:
            # Mouse moved within the button
            return
        elif collision and not self.hovering:
            # Mouse enter button
            self.background_color = self.background_hover_color
        elif self.hovering and not collision:
            # Mouse exit button
            self.background_color = self.background_normal_color

        self.hovering = collision

class CustomActionBtn(GenericActionBtn,ActionButton):
    pass

class CustomActionGroup(GenericActionBtn,ActionGroup):
    pass
