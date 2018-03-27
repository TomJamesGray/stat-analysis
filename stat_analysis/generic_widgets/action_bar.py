from kivy.uix.actionbar import ActionItem,ActionButton,ActionGroup
from kivy.properties import BooleanProperty,ListProperty
from kivy.core.window import Window


class GenericActionBtn(ActionItem):
    """
    Generic widget that the buttons and drop downs (groups) for the top bar extends.
    Provides the hovering functionality of changing the bg colors on exit/enter
    """
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
            self.on_enter()
        elif self.hovering and not collision:
            # Mouse exit button
            self.on_exit()

        self.hovering = collision

    def on_exit(self):
        self.background_color = self.background_normal_color

    def on_enter(self):
        self.background_color = self.background_hover_color


class CustomActionBtn(GenericActionBtn,ActionButton):
    def __init__(self,**kwargs):
        self.background_normal = ""
        self.background_down = ""
        super().__init__(**kwargs)
        self.height = 30
        self.size_hint_y = None

    def on_press(self,**kwargs):
        self.on_exit()
        # Run the super classes on press methods to run bound functions
        super().on_press(**kwargs)


class CustomActionGroup(GenericActionBtn,ActionGroup):
    def _toggle_dropdown(self, *largs):
        super()._toggle_dropdown(*largs)

        for child in self._dropdown.container.children:
            # Manually set the height of the children of the dropdown, otherwise heights
            # are inconsistent
            child.height = 28
            child.background_normal = ""

    def on_is_open(self, instance, opened):
        super().on_is_open(instance,opened)

        # Keep button highlighted when drop down is open
        if opened:
            self.background_color = self.background_hover_color
            Window.unbind(mouse_pos=self.mouse_pos)
        elif not opened:
            self.background_color = self.background_normal_color
            Window.bind(mouse_pos=self.mouse_pos)
