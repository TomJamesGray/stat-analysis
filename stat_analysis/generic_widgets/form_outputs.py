from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import StringProperty,BooleanProperty


class ExportableImage(GridLayout):
    source = StringProperty("")
    nocache = BooleanProperty(False)

    def __init__(self,**kwargs):
        self.cols = 1
        super().__init__(**kwargs)
        self.image = Image(source=self.source,nocache=self.nocache,size_hint_y=1)
        self.image.bind(size=self.update_toolbar)
        self.add_widget(self.image)

        self.toolbar = GridLayout(rows=1,size_hint_x=1,size_hint=(None,None),width=self.image.texture_size[0],
                                  height=30)
        self.spacer = Widget(height=30,width=(self.width-self.image.texture_size[0])/2,size_hint=(None,None))
        self.toolbar.add_widget(self.spacer)
        self.toolbar.add_widget(Button(text="Export Image",height=30,size_hint=(None,None)))

        self.add_widget(self.toolbar)

    def update_toolbar(self,*args):
        self.toolbar.width = self.image.texture_size[0]
        self.spacer.width = (self.width-self.image.texture_size[0])/2