

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout



from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window

# importando firebase
import requests
import json

Window.size = 590,960

class Manager(ScreenManager):
    pass

class HomePage(Screen):
    pass

class Register(Screen):

    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

    def log_aut(self,*args):
        LINK = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'

        with open('refreshtoken.json', 'r') as arquivo:
            refresh = json.load(arquivo)
        info = {"grant_type":"refresh_token",
                "refresh_token":refresh}

        requisicao = requests.post(LINK, data=info)
        requisicao_dic = requisicao.json()

        idtoken = requisicao_dic["id_token"]
        user_id = requisicao_dic["user_id"]

        if requisicao.ok:
            MDApp.get_running_app().root.current = 'viewshedule'
        else:
            pass
        # print(requisicao_dic)

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.log_aut,2)



class CreatBill(Screen):
    #idToken
    #refreshToken
    #localId
    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

    def valid_field(self):
        if self.ids.nome.text == '':
            self.ids.warning.text = 'Sem informação de [color=#D40A00][b]nome[/b][/color]'
            return False
        elif self.ids.senha.text != self.ids.rep_senha.text:
            self.ids.warning.text = 'Senha [color=#D40A00][b]incorreta[/b][/color]'
            return False
        else:
            return True

    def fire_base_creat(self,idtoken,localid,refreshtoken):
        """
        Here creat the account of user
        :param idtoken:
        :param localid: the id of user
        :param refreshtoken: for permanent login
        :return:
        """
        LINK_FIREBASE = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{localid}.json'

        with open('refreshtoken.json','w') as arquivo:
            json.dump(refreshtoken, arquivo)

        nome = self.ids.nome.text

        # info_user = '{"avatar":"photos2.png", "equipe":"", "total_vendas":"0","vendas":""}'
        info_user = f'{{"nome":"{nome}",' \
                    f' "quant_cancelado":"0",' \
                    f' "bloqueado":"False"}}'

        print(nome)
        creat_user = requests.patch(LINK_FIREBASE, data=info_user)

    def creat_bill(self, *args, **kwargs):

        if self.valid_field():
            try:
                LINK = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"

                email = self.ids.email.text
                senha = self.ids.senha.text

                info = {"email": email,
                        "password": senha,
                        "returnSecureToken": True}

                requisicao = requests.post(LINK, data=info)
                requisicao_dic = requisicao.json()

                print(requisicao_dic)

                idtoken = requisicao_dic['idToken']
                localid = requisicao_dic['localId']
                refreshtoken = requisicao_dic['refreshToken']


                if requisicao.ok:
                    self.fire_base_creat(idtoken,localid,refreshtoken)
                    self.ids.warning.text = '[b]Conta criada com sucesso![/b]'
                    # MDApp.get_running_app().root.current = 'viewshedule'
                else:
                    self.ids.warning.text = requisicao_dic["error"]["message"]
            except KeyError:
                self.ids.warning.text = requisicao_dic["error"]["message"]
        else:
            pass

class Table_shedule(MDBoxLayout):

    def __init__(self,hours='',client='',**kwargs):
        super().__init__(**kwargs)
        self.hours = str(hours)
        self.client = str(client)


class ViewSchedule(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)



        # agendados = self.dados[1]
        # print(agendados)

    def actualizar(self, *args):
        self.ids.grid_shedule.clear_widgets()

        # for informacao in self.dados[1:]:
        for enum,informacao in enumerate(range(self.entrada,self.saida + self.entrada + 1)):
            # hours_entry = int(informacao['hours_entry'])
            # print(informacao['proficional'])
            # self.ids.grid_shedule.add_widget(Table_shedule(informacao['proficional'], informacao['agendados'][1]['cliente']))

            if enum >= self.entrada:
                self.ids.grid_shedule.add_widget(Table_shedule(f'{enum}  proficional','agendados'))
            else:
                pass

    def on_pre_enter(self, *args):
        # Clock.schedule_once(self.actualizar, 2)
        pass




class AgendamentoApp(MDApp):

    Builder.load_string(open('cliente.kv', encoding='utf-8').read())
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()