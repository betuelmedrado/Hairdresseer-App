

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

    def get_id_manager(self, *args):
        LINK_ID_MANAGER = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'

        id_manager = ''

        requisicao = requests.get(LINK_ID_MANAGER)
        requisicao_dic = requisicao.json()

        for id in requisicao_dic:
            print(id)
            return id

    def login(self, *args):

        id_manager = self.get_id_manager()

        LINK_API = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'

        email = self.ids.email.text
        senha = self.ids.senha.text

        info={"email":email,
              "password":senha,
              "returnSecureToken":True}

        requisicao = requests.post(LINK_API, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            if requisicao_dic['localId'] == id_manager:
                MDApp.get_running_app().root.current = 'homepage'
            else:
                self.ids.warning.text = 'Email ou senha [color=D40A00]Invalida[/color]'
        else:
            erro = str(requisicao_dic['error']['message'])

            if erro == 'INVALID_EMAIL':
                self.ids.warning.text = 'Email [color=D40A00]Invalido[/color]'
            elif erro == 'MISSING_PASSWORD':
                self.ids.warning.text = 'Sem informação de [color=D40A00]Senha[/color]'
            elif erro == 'INVALID_PASSWORD':
                self.ids.warning.text = 'Senha [color=D40A00]Invalido[/color]'
            elif erro == 'EMAIL_NOT_FOUND':
                self.ids.warning.text = 'Email não [color=D40A00]Encontrado[/color]'

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

            if requisicao.ok:
                # LINK_DATA_MANAGER = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{user_id}.json'
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

#  Here I will change to change the id
    def creat_profile(self,id_token, localid, refreshtoken, *args):
        LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{localid}.json'

        nome = self.ids.nome.text

        info = f'{{"nome":"{nome}"}}'

        requisicao = requests.patch(LINK_SALAO, data=info)
        self.ids.warning.text = 'Perfil creado com sucesso!'

        with open('refreshtoken.json','w') as file:
            json.dump(refreshtoken, file)

    def creat_bill(self, *args):
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

                idtoken = requisicao_dic['idToken']
                localid = requisicao_dic['localId']
                refreshtoken = requisicao_dic['refreshToken']

                if requisicao.ok:
                    self.creat_profile(idtoken, localid, refreshtoken)
                    self.ids.warning.text = '[b][color=D40A00]Conta criada[/color] com sucesso![/b]'
                    MDApp.get_running_app().root.current = 'homepage'
                else:
                    erro = str(requisicao_dic['error']['message'])

                    if erro == 'INVALID_EMAIL':
                        self.ids.warning.text = 'Email [color=D40A00]Invalido[/color]'
                    elif erro == 'MISSING_PASSWORD':
                        self.ids.warning.text = 'Sem informação de [color=D40A00]Senha[/color]'
                    elif erro == 'INVALID_PASSWORD':
                        self.ids.warning.text = 'Senha [color=D40A00]Invalido[/color] digite pelominos 6 digitos'
                    elif erro == 'EMAIL_NOT_FOUND':
                        self.ids.warning.text = 'Email não [color=D40A00]Encontrado[/color]'
            except KeyError:
                erro = str(requisicao_dic['error']['message'])

                if erro == 'INVALID_EMAIL':
                    self.ids.warning.text = 'Email [color=D40A00]Invalido[/color]'
                elif erro == 'MISSING_PASSWORD':
                    self.ids.warning.text = 'Sem informação de [color=D40A00]Senha[/color]'
                elif erro == 'INVALID_PASSWORD':
                    self.ids.warning.text = 'Senha [color=D40A00]Invalido[/color] digite pelominos 6 digitos'
                elif erro == 'EMAIL_NOT_FOUND':
                    self.ids.warning.text = 'Email não [color=D40A00]Encontrado[/color]'
                elif erro == 'EMAIL_EXISTS':
                    self.ids.warning.text = 'Esse [color=D40A00]Email[/color] já possue uma conta'
                elif erro == 'WEAK_PASSWORD : Password should be at least 6 characters':
                    self.ids.warning.text = 'A [color=D40A00]senha[/color] deve ter pelo menos\n6 caracteres'
                print(erro)
        else:
            print('last')

class HomePage(Screen):

    def return_login(self):
        with open('refreshtoken.json','w') as file:
            json.dump('',file)

        MDApp.get_running_app().root.current = 'loginmanager'

class ManagerProfile(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'

    def __init__(self,*args,**kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.creat_profile()
        self.insert_hours()
        Clock.schedule_once(self.get_socios,2)
        Clock.schedule_once(self.infill,3)

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
            self.ids.space_temp.text = requisicao_salao_dic['space_temp']
        except:
            pass


    def insert_hours(self, *args, **kwargs):
        """
        function that receiv the hours
        :param args:
        :param kwargs:
        :return:
        """
        for hours, min in enumerate(range(24)):
            h = f'{str(hours).zfill(2)}:00'
            bt = MDTextButton(text=str(h),pos_hint=({'center_x':.5}), md_bg_color=(0.13, 0.53, 0.95,.1))
            self.ids.hours.add_widget(bt)
            bt.bind(on_release=self.insert)

            h2 = f'{str(hours).zfill(2)}:30'
            bt = MDTextButton(text=str(h2),pos_hint=({'center_x':.5}),md_bg_color=(0.13, 0.53, 0.95,.3))
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

            self.entrada = self.ids.entry.text
            self.saida = self.ids.exit.text
            self.space_tempo = self.ids.space_temp.text

            info = f'{{"entrada":"{self.entrada}",\
                     "saida": "{self.saida}",\
                     "space_temp":"{self.space_tempo}"}}'

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
               f'"valor":"{valor}",' \
               f'"servicos":""}}'

        requisicao = requests.post(LINK_BASE_SALAO, info)
        toast('Categoria criada', duration=4)

        self.infill()

        self.ids.nome_servico.text = ''
        self.ids.tempo.text = ''
        self.ids.valor.text = ''

    def infill(self, *args):
        LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos.json'

        requisicao_get = requests.get(LINK_CATEGORIA)
        requisicao_get_dic = requisicao_get.json()

        self.ids.categorie.clear_widgets()

        try:
            for id in requisicao_get_dic:
                LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos/{id}.json'

                requisicao_get_categoria = requests.get(LINK_ID)
                requisicao_get_categoria_dic = requisicao_get_categoria.json()

                nome_servico = requisicao_get_categoria_dic['nome_servico']
                tempo = requisicao_get_categoria_dic['tempo']
                valor = requisicao_get_categoria_dic['valor']

                self.ids.categorie.add_widget(MyBoxCategorie(nome_servico,tempo,valor))
        except TypeError:
            pass

            # print(requisicao_get_categoria_div['nome_servico'])

    def save_socio(self,*args):
        LINK_ETRADA_SAIDA =f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'
        requisicao_entrada_saida = requests.get(LINK_ETRADA_SAIDA)
        entrada_saida = requisicao_entrada_saida.json()

        entrada = entrada_saida['entrada']
        saida = entrada_saida['saida']

        LINK_SOCIO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/socios.json'


        nome_socio = self.ids.text_socio.text

        if nome_socio == '':
            toast('Nenhum nome informado!')
        else:
            info = f'{{"nome":"{nome_socio}",' \
                   f'"id":1,' \
                   f'"agenda":"",' \
                   f'"entrada":"{entrada}",' \
                   f'"saida":"{saida}",' \
                   f'"servicos":""}}'

            requisicao = requests.post(LINK_SOCIO, data=info)
            toast('Socio criado com sucesso!')
            self.ids.box_socio.add_widget(MyBoxSocio(nome_socio))

    def get_socios(self,*args):

        self.ids.box_socio.clear_widgets()

        lista = []

        LINK_SOCIO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/socios.json'
        socio = requests.get(LINK_SOCIO)
        socio_dic = socio.json()

        try:
            for id_socio in socio_dic:
                LINK_ID_SOCIO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/socios/{id_socio}.json'
                nome = requests.get(LINK_ID_SOCIO)
                nome_dic = nome.json()
                self.ids.box_socio.add_widget(MyBoxSocio(str(nome_dic['nome'])))
        except:
            pass

class MyButtonCard(MDCard):
    pass

class MyBoxCategorie(MDCard):

    def __init__(self, servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)
        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)

class MyBoxSocio(MDCard):
    def __init__(self,name, **kwargs):
        super().__init__(**kwargs)
        self.nome = name


class Table_shedule(MDBoxLayout):

    def __init__(self,id_schedulr='',hours='',client='',**kwargs):
        super().__init__(**kwargs)
        self.id_schedule = id_schedulr
        self.hours = str(hours)
        self.client = str(client)


class ViewSchedule(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        LINK = requests.get(f'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json')
        self.dados = LINK.json()

    def actualizar(self, *args):

        for id in self.dados:
            self.id_dados = id

        self.ids.grid_shedule.clear_widgets()
        LINK_AGENDA = requests.get(f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_dados}.json')
        link_agenda = LINK_AGENDA.json()

        self.entrada = int(link_agenda['entrada'][:2])
        self.minuto_entrada = int(link_agenda['entrada'][3:])
        self.saida = int(link_agenda['saida'][:2])
        self.minuto_saida = int(link_agenda['saida'][3:])


        for enum,informacao in enumerate(range(self.entrada,self.saida + self.entrada + 1)):
            # self.ids.grid_shedule.add_widget(Table_shedule(informacao['proficional'], informacao['agendados'][1]['cliente']))

            if enum >= self.entrada:
                self.ids.grid_shedule.add_widget(
                    Table_shedule(str(enum), f'{str(enum).zfill(2)}:{str(self.minuto_entrada).zfill(2)}'))
            else:
                pass

    def on_pre_enter(self, *args):
        self.actualizar()


    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'



class AgendamentoApp(MDApp):

    Builder.load_string(open('agendamento_vitor.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/my_box_socio.kv', encoding='utf-8').read())

    def build(self):

        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()