

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton
from kivymd.toast import toast
from kivymd.uix.card import MDCard


from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock

# importando firebase
import requests
import json

from functools import partial
from datetime import datetime

# print(datetime.today().isoweekday())

class Manager(ScreenManager):
    pass


class LoginManager(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'

    def load_refresh(self, *args):

        try:
            # pegando o locaoid
            LINK_GET_ID = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'


            with open('refreshtoken.json', 'r') as arquivo:
                refresh = json.load(arquivo)

            info = {"grant_type": "refresh_token",
                    "refresh_token": refresh}

            requisicao = requests.post(LINK_GET_ID, data=info)
            requisicao_dic = requisicao.json()

            # email = requisicao_dic["email"]
            user_id = requisicao_dic["user_id"]
            print(user_id)

            if requisicao.ok:
                LINK_DATA_MANAGER = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{user_id}.json'

                requisicao_data_manager = requests.get(LINK_DATA_MANAGER)
                requisicao_data_manager_dic = requisicao_data_manager.json()

                Clock.schedule_once(self.load_screen, 2)

                # print('teste ',requisicao_data_manager_dic)
            else:
                print('usuario não encontrado')
        except:
            pass

        # print(requisicao_dic)

    def load_screen(self, *args):
        MDApp.get_running_app().root.current = 'homepage'

    def on_pre_enter(self, *args):
        self.load_refresh()


class CreatProfile(Screen):

    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'

    def valid_field(self):
        if self.ids.nome.text == '':
            self.ids.warning.text = 'Sem informação de [color=#D40A00][b]nome[/b][/color]'
            return False
        elif self.ids.senha.text != self.ids.rep_senha.text:
            self.ids.warning.text = 'Senha [color=#D40A00][b]incorreta[/b][/color]'
            return False
        else:
            return True

    def creat_profile(self,localid, *args):
        LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{localid}.json'

        nome = self.ids.nome.text

        info = f'{{"nome":"{nome}"}}'

        requisicao = requests.patch(LINK_SALAO, data=info)
        self.ids.warning.text = 'Perfil creado com sucesso!'


    def creat_bill(self, *args):
        if self.valid_field():
            try:
                nome = self.ids.nome.text
                email = self.ids.email.text
                senha = self.ids.senha.text

                LINK = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'

                info_bill = {"email":email,
                             "password":senha,
                             "returnSecureToken":True}

            # creat account of manager of app
                requisicao = requests.post(LINK, data=info_bill)
                requisicao_dic = requisicao.json()

            # geting information of account of manager
                id_token = requisicao_dic["idToken"]
                local_id = requisicao_dic["localId"]
                refreshe_token = requisicao_dic["refreshToken"]

            # if the requisition this right
                if requisicao.ok:
                    with open('refreshtoken.json', 'w') as arquivo:
                        json.dump(refreshe_token, arquivo)

                 # creat profile
                    self.creat_profile(local_id)
                    self.ids.warning.text = 'Perfil creado com sucesso!'
                else:
                    pass

                print(requisicao.json())
            except:
                self.ids.warning.text = requisicao_dic["error"]["message"]
        else:
            pass

class HomePage(Screen):
    pass

class ManagerProfile(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'

    def __init__(self,*args,**kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.creat_profile()
        self.insert_hours()
        Clock.schedule_once(self.infill,2)

    # Here only return the id of user
    def get_id_whith_refreshtoken(self, *args):
        with open('refreshtoken.json', 'r') as arquivo:
            refresh_token = json.load(arquivo)

        LINK_CHANGE_REFRESH = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'

        info = {"grant_type": "refresh_token",
                "refresh_token": refresh_token}

        requisicao_rest = requests.post(LINK_CHANGE_REFRESH, data=info)
        requisicao_dic = requisicao_rest.json()

        user_id = requisicao_dic['user_id']

        return user_id

    def creat_profile(self, *args):
        self.user_id = self.get_id_whith_refreshtoken()

        LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'

        requisicao_base_salao = requests.get(LINK_BASE_SALAO)
        requisicao_salao_dic = requisicao_base_salao.json()

        name = requisicao_salao_dic['nome']
        self.ids.text_name.text = str(name)

        try:
            self.ids.entry.text = requisicao_salao_dic['entrada']
            self.ids.exit.text = requisicao_salao_dic['saida']
        except:
            pass


    def insert_hours(self, *args, **kwargs):
        for hours, min in enumerate(range(24)):
            h = f'{str(hours).zfill(2)}:00'
            bt = MDTextButton(text=str(h), md_bg_color=(0.13, 0.53, 0.95,.1))
            self.ids.hours.add_widget(bt)
            bt.bind(on_release=self.insert)

            h2 = f'{str(hours).zfill(2)}:30'
            bt = MDTextButton(text=str(h2),md_bg_color=(0.13, 0.53, 0.95,.3))
            self.ids.hours.add_widget(bt)

            bt.bind(on_release=self.insert)

    # Here get the TextField selectioning for be insert of hours
    def validate(self,msg,**kwargs):
        self.msg = msg

    # Receiv the hours and insert in field
    def insert(self,texto,**kwargs):
        """
        Here choice the field for will be insert hours
        :param texto: receiv the hours
        :param kwargs:
        :return:
        """

        try:
            msg = self.msg

            if msg == 'entry' :
                self.ids.entry.text = str(texto.text)
            elif msg == 'exit':
                self.ids.exit.text = str(texto.text)
        except AttributeError:
            toast('escolha o campo a ser preenchido! Entrada ou Saida', duration=5)

    def save_data(self,*args):
        try:
            LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'

            entrada = self.ids.entry.text
            saida = self.ids.exit.text

            info = f'{{"entrada":"{entrada}",\
                     "saida": "{saida}"}}'
            requisica = requests.patch(LINK_BASE_SALAO, info)
            toast('Tabela de horas salva com sucesso!', duration=4)
        except:
            print('erro no save data')

    def save_servicos(self,*args):
        LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos.json'

        nome_servico = self.ids.nome_servico.text
        tempo = self.ids.tempo.text
        valor = self.ids.valor.text

        info = f'{{"nome_servico":"{nome_servico}",' \
               f'"tempo":"{tempo}",' \
               f'"valor":"{valor}"}}'

        requisicao = requests.post(LINK_BASE_SALAO, info)
        toast('Categoria criada', duration=4)

        self.infill()

    def infill(self, *args):
        LINK_CATEGORIA = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao/3pYGyBmzqoZN548BO7hDrtgoToz2/servicos.json'

        requisicao_get = requests.get(LINK_CATEGORIA)
        requisicao_get_dic = requisicao_get.json()

        self.ids.categorie.clear_widgets()

        for id in requisicao_get_dic:
            LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/3pYGyBmzqoZN548BO7hDrtgoToz2/servicos/{id}.json'

            requisicao_get_categoria = requests.get(LINK_ID)
            requisicao_get_categoria_dic = requisicao_get_categoria.json()

            nome_servico = requisicao_get_categoria_dic['nome_servico']
            tempo = requisicao_get_categoria_dic['tempo']
            valor = requisicao_get_categoria_dic['valor']

            self.ids.categorie.add_widget(MyBoxCategorie(nome_servico,tempo,valor))

            # print(requisicao_get_categoria_div['nome_servico'])

    def save_socio(self,*args):
        LINK_SOCIO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/socios.json'

        nome_socio = self.ids.text_socio.text

        info = f'{{"nome":"{nome_socio}",' \
               f'"id":1}}'

        requisicao = requests.post(LINK_SOCIO, data=info)

        toast('Socio criado com sucesso!')


class MyButtonCard(MDCard):
    pass

class MyBoxCategorie(MDCard):

    def __init__(self, servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)
        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class Table_shedule(MDBoxLayout):

    def __init__(self,entrada='',tempo='',client='',**kwargs):
        super().__init__(**kwargs)
        self.entrada = str(entrada)
        self.client = str(client)
        self.tempo = tempo


class ViewSchedule(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.entrada = 7
        self.saida = 20
        self.tempo = 30


        # link = requests.get(f'https://shedule-vitor-default-rtdb.firebaseio.com/.json')
        link = requests.get(f'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json')
        self.dados = link.json()

    def actualizar(self, *args):
        self.ids.grid_shedule.clear_widgets()

        # for informacao in self.dados[1:]:
        for enum,informacao in enumerate(range(self.entrada,self.saida + self.entrada + 1)):
            # self.ids.grid_shedule.add_widget(Table_shedule(informacao['proficional'], informacao['agendados'][1]['cliente']))

            if enum >= self.entrada:
                self.ids.grid_shedule.add_widget(Table_shedule(f'{str(enum).zfill(2)}:00', f'{enum}:{self.tempo}' ))
            else:
                pass

    def on_pre_enter(self, *args):
        self.actualizar()

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'



class AgendamentoApp(MDApp):

    Builder.load_string(open('agendamento_vitor.kv', encoding='utf-8').read())

    def build(self):

        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()