
from kivymd.app import MDApp


from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

Window.size = 400,820

class ManagerScreen(ScreenManager):
    pass

class MsgToApp(Screen):
    pass



class ScreenTest(MDApp):

    def build(self):
        Builder.load_string(open('testscreen.kv', encoding='utf-8').read())

        return MsgToApp()

ScreenTest().run()