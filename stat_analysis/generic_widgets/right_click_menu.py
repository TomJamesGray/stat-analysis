from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import Property

class RightClickMenu(GridLayout):
    def __init__(self,**kwargs):
        self.cols = 1
        self.size_hint = (None,None)
        self.width = 100
        self.row_default_height = 30
        self.row_force_default = True
        self.bind(minimum_height=self.setter("height"))
        self.options = []
        super().__init__(**kwargs)

    def add_opt(self,text,fn):
        self.options.append(MenuBtn(text=text,func=fn,on_press=self.do_option))

    def open(self):
        for opt in self.options:
            self.add_widget(opt)
        # Window.bind(on_touch_down=self.clear_menu)

    def do_option(self,instance):
        instance.func()
        self.clear_menu()

    def clear_menu(self,*args):
        print("Clearing menu")
        Window.unbind(on_touch_down=self.clear_menu)
        self.clear_widgets()
        self.remove_widget(self)
        del self

class MenuBtn(Button):
    func = Property(None)