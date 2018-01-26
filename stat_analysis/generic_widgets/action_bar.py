from kivy.uix.actionbar import ActionItem,ActionButton,ActionGroup
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
    def __init__(self,**kwargs):
        self.background_normal = ""
        self.background_down = ""
        super().__init__(**kwargs)
        self.height = 30
        self.size_hint_y = None

    def mouse_pos(self,*args):
        super().mouse_pos(*args)
        # self.height = 30
        # self.background_normal = ""


class CustomActionGroup(GenericActionBtn,ActionGroup):
    def _toggle_dropdown(self, *largs):
        super()._toggle_dropdown(*largs)

        for child in self._dropdown.container.children:
            child.height = 28
            child.background_normal = ""

    def on_is_open(self, instance, value):
        super().on_is_open(instance,value)

        if value:
            self.background_color = self.background_hover_color
            Window.unbind(mouse_pos=self.mouse_pos)
        elif not value:
            self.background_color = self.background_normal_color
            Window.bind(mouse_pos=self.mouse_pos)
