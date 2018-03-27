from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.properties import Property
from stat_analysis.generic_widgets.bordered import BorderedHoverButton

class RightClickMenu(GridLayout):
    def __init__(self,**kwargs):
        self.cols = 1
        self.size_hint = (None,None)
        self.width = 150
        self.row_default_height = 30
        self.row_force_default = True
        self.bind(minimum_height=self.setter("height"))
        self.options = []
        super().__init__(**kwargs)

    def add_opt(self,text,fn):
        """
        Add an option to the list of options
        :param text: Text to be displayed on the button
        :param fn: Function to be called when the user presses the button
        """
        self.options.append(MenuBtn(text=text,func=fn,on_press=self.do_option,color=(1,1,1,1),height=30))

    def open(self):
        """
        Open the menu
        """
        for opt in self.options:
            Window.bind(mouse_pos=opt.mouse_pos)
            self.add_widget(opt)
        Window.bind(on_touch_down=self.decide_clear_menu)

    def do_option(self,instance):
        instance.func()
        self.clear_menu()

    def decide_clear_menu(self,instance,touch):
        if not self.collide_point(touch.x,touch.y):
            if touch.button == "left":
                self.clear_menu()

    def clear_menu(self):
        """
        Clear the RightClickMenu so nothing is displayed, done when user clicks out of the menu
        :return:
        """
        Window.unbind(on_touch_down=self.decide_clear_menu)
        self.clear_widgets()
        self.remove_widget(self)
        del self

class MenuBtn(BorderedHoverButton):
    func = Property(None)