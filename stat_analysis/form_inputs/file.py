import os
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty


class FormFile(GridLayout):
    def __init__(self,input_dict,*args):
        super().__init__(*args)
        self.cols = 1
        self.size_hint_y = None
        self.size_hint_x = None
        self.height = 55
        self.width = 200
        self.file_location = None
        input_label = Label(text=input_dict["visible_name"],halign="left",size_hint=(1,None),height=25,color=(0,0,0,1),
                            valign="middle",font_size="14")
        input_label.bind(size=input_label.setter("text_size"))
        self.file_chooser_btn = Button(text="Select File")
        self.file_chooser_btn.bind(on_press=self.open_f_selector)

        self.add_widget(input_label)
        self.add_widget(self.file_chooser_btn)

    def open_f_selector(self,*args):
        self.popup = Popup(title="Select file",size_hint=(None,None),size=(400,400))
        f_chooser = FileChooserListViewCustom(popup=self.popup,file_chooser_btn=self.file_chooser_btn,
                                              filters=[lambda _,filename: filename.endswith(".csv")],
                                              path=os.path.expanduser("~"),form_parent=self)
        self.popup.content = f_chooser
        self.popup.open()


class FileChooserListViewCustom(FileChooserListView):
    popup = ObjectProperty(None)
    file_chooser_btn = ObjectProperty(None)
    form_parent = ObjectProperty(None)

    def on_submit(self, selected, touch=None):
        self.popup.dismiss()
        self.form_parent.file_location = selected[0]
        self.file_chooser_btn.text = os.path.basename(selected[0])