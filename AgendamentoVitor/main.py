
# requeriment python 3.8

# Imports kivymd
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton, MDFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.navigationdrawer import  MDNavigationDrawer
from kivymd.uix.dialog import  MDDialog
from kivymd.uix.floatlayout import MDFloatLayout

# from kivymd_extension.akivymd.uix.loader import AKLabelLoader, AKImageLoader

#imports kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import NumericProperty


# importando firebase
import requests
import os
import certifi
import json

# Transition of screen
from kivy.uix.screenmanager import RiseInTransition, FadeTransition

from functools import partial
from datetime import datetime, timedelta

# print(datetime.today().isoweekday())

# Window.size = 400,820
Window.size = 800,800
Window.minimum_width = 800
Window.minimum_height = 800


# print(help(Window))


# Window.pos =

os.environ["SSL_CERT_FILE"] = certifi.where()


class Manager(ScreenManager):
    pass


class LoginManager(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    LINK_ID_MANAGER = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def on_pre_enter(self, *args):
        # Clock.schedule_once(self.spiner,1)
        self.creat_files()
        self.load_refresh()

    def get_id_manager(self, *args):
        try:
            id_manager = ''
            link = f'{self.LINK_ID_MANAGER}.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def not_can_client(self):
        lista_info_ids = []
        ID_MANAGER = ''
        link = f'{self.LINK_ID_MANAGER}.json'

        try:
            # Geting id of manager #########################################################################################
            requisicao_manager = requests.get(link)
            requisicao_manager_dic = requisicao_manager.json()

            for id in requisicao_manager_dic:
                ID_MANAGER = id
                lista_info_ids.append(id)

            # Geting ids of socios #########################################################################################

            LINK_SOCIOS = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{ID_MANAGER}/socios.json'
            requisicao_socio = requests.get(LINK_SOCIOS)
            requisicao_socio_dic = requisicao_socio.json()

            for id_socio in requisicao_socio_dic:
                lista_info_ids.append(id_socio)

            return lista_info_ids
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def login(self, *args):

        try:
            lista_info_ids =  self.not_can_client()

            id_manager = self.get_id_manager()

            dic_login = {}

            LINK_API = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'

            email = self.ids.email.text
            senha = self.ids.senha.text

            info={"email":email,
                  "password":senha,
                  "returnSecureToken":True}

            requisicao = requests.post(LINK_API, data=info)
            requisicao_dic = requisicao.json()

            if requisicao.ok:
                if requisicao_dic['localId'] in lista_info_ids:
                    with open('refreshtoken.json','w') as file:
                        json.dump(requisicao_dic['refreshToken'], file)

                    # dic_login['nome'] = requisicao_dic['']
                    dic_login['email'] = requisicao_dic['email']
                    dic_login['id_login'] = requisicao_dic['localId']

                    with open('info_login.json','w') as file_login:
                        json.dump(dic_login, file_login, indent=2)

                    self.info_login(requisicao_dic['localId'])

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

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def info_login(self, localo_id):

        try:
            link = f'{self.LINK_ID_MANAGER}/{localo_id}.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
            info = requisicao_dic['manager']

            with open('is_manager_or_socio.json','w') as file:
                json.dump('manager', file)

            MDApp.get_running_app().root.current = 'homepage'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:

            with open('is_manager_or_socio.json','w') as file:
                json.dump('socio', file)

            MDApp.get_running_app().root.current = 'homepage'


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

                Clock.schedule_once(self.load_screen, 1)
            else:
                toast('usuario não encontrado!')
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass


    def load_screen(self, *args):
        MDApp.get_running_app().root.transition = FadeTransition()
        MDApp.get_running_app().root.current = 'homepage'

    def creat_files(self):

        try:
            with open('write_id_manager.json', 'r') as arquivo:
                json.load(arquivo)
        except FileNotFoundError:
            with open('write_id_manager.json', 'w') as arquivo:
                json.dump('',arquivo)

        try:
            with open('infoscheduleclient.json', 'r') as file:
                json.load(file)
        except:
            with open('infoscheduleclient.json', 'w') as file:
                json.dump('', file)

        try:
            with open('select_works.json', 'r') as file_work:
                json.load(file_work)
        except:
            with open('select_works.json', 'w') as file_work:
                json.dump([],file_work)

        try:
            with open('is_manager_or_socio.json', 'r') as file_is_manager:
                json.load(file_is_manager)
        except:
            with open('is_manager_or_socio.json', 'w') as file_is_manager:
                json.dump('', file_is_manager)

        try:
            with open('info_login.json', 'r') as file_login:
                json.load(file_login)
        except:
            with open('info_login.json', 'w') as file_login:
                json.dump('', file_login) 

    # def spiner(self, *args):
    #     self.ids.float_home.add_widget(
    #         MDSpinner(size_hint=(None, None,), size=('46dp', '46dp'), pos_hint={'center_x': .5, 'center_y': .5}))


    def password_view(self, msg):
        if msg.password == False:
            self.ids.senha.password = True
            self.ids.eye.icon = 'eye-off'
        elif msg.password == True:
            self.ids.senha.password = False
            self.ids.eye.icon = 'eye'


class CreatProfile(Screen):

    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.LINK_DATABASE_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

        Clock.schedule_once(self.call_init,1)

    def call_init(self, *args):
        self.id_manager = self.get_manager()

    def get_manager(self):
        try:
            requisicao = requests.get(self.LINK_DATABASE_SALAO + '.json')
            requisicao_dic = requisicao.json()
            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Sem concção a internet!')

    def call_login(self, window, key, *args, **kwargs):

        if key == 27:
            MDApp.get_running_app().root.current = 'loginmanager'
        else:
            pass
        return True

    def on_pre_enter(self, *args):

        Window.bind(on_keyboard=self.call_login)

        try:
            verification = self.verification_if_manger()

            if verification:
                pass
            else:
                self.ids.enter_as_socio.text = 'Cadastro de Sócio'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def valid_field(self):
        if self.ids.nome.text == '':
            self.ids.warning.text = 'Sem informação de [color=#D40A00][b]nome[/b][/color]'
            return False
        elif self.ids.senha.text != self.ids.rep_senha.text:
            self.ids.warning.text = 'Senha [color=#D40A00][b]incorreta[/b][/color]'
            return False
        else:
            return True

    # creat one file to get if is manager or socio ################################
    def verification_if_manger(self, *args):
        try:
            requisicao = requests.get(self.LINK_DATABASE_SALAO + '.json')
            requisicao_dic = requisicao.json()

            if requisicao.ok :
                if requisicao_dic == '':
                    with open('is_manager_or_socio.json','w') as file:
                        json.dump('manager', file)
                    return True
                else:
                    with open('is_manager_or_socio.json', 'w') as file:
                        json.dump('socio', file)
                    return False
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    #  Here I will change to change the id
    def creat_profile(self,id_token, localid, refreshtoken, *args):
        try:
            LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{localid}.json'

            nome = self.ids.nome.text

            info = f'{{"nome":"{nome}",' \
                   f'"manager":True}}'

            requisicao = requests.patch(LINK_SALAO, data=info)
            self.ids.warning.text = 'Perfil creado com sucesso!'

            with open('refreshtoken.json','w') as file:
                json.dump(refreshtoken, file)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')


    def creat_socio(self, id_token, localid, refreshtoken, *args):
        try:
            LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{localid}.json'

            nome = self.ids.nome.text

            info = f'{{"nome":"{nome}",' \
                   f'"manager":"False",'\
                   f'"agenda":"",' \
                   f'"entrada":"",' \
                   f'"saida":"",' \
                   f'"servicos":""}}'


            requisicao = requests.patch(LINK_SALAO, data=info)
            self.ids.warning.text = 'Perfil creado com sucesso!'

            with open('refreshtoken.json', 'w') as file:
                json.dump(refreshtoken, file)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def creat_bill(self, *args):
        try:
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
                        manager_socio = self.verification_if_manger()

                        if manager_socio == False:
                            self.creat_socio(idtoken, localid, refreshtoken)

                        else:
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
            else:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def password_view(self, msg):
        if msg.password == False:
            self.ids.senha.password = True
            self.ids.eye.icon = 'eye-off'
        elif msg.password == True:
            self.ids.senha.password = False
            self.ids.eye.icon = 'eye'

    def rep_password_view(self, msg):
        if msg.password == False:
            self.ids.rep_senha.password = True
            self.ids.eye_repeat.icon = 'eye-off'
        elif msg.password == True:
            self.ids.rep_senha.password = False
            self.ids.eye_repeat.icon = 'eye'


class RedefinitionSenha(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'

    def send_email(self, *args):
        """
        Function for redefinited the password
        :param args:
        :return:
        """
        try:
            LINK_FOR_API = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.API_KEY}'

            email = self.ids.email.text

            info = {"requestType":"PASSWORD_RESET",
                   "email": email}

            requisicao = requests.post(LINK_FOR_API, data=info)
            requisicao_dic = requisicao.json()

            error = requisicao_dic['error']['message']

            if requisicao.ok:
                toast('Foi enviado uma mensagem no email informado para redefinir a senha!', length_long=False)
            elif error == 'MISSING_EMAIL':
                toast('Insira um e-mail valido!')
            elif error == 'INVALID_EMAIL':
                toast('Email invalido!')
            elif error  == 'EMAIL_NOT_FOUND':
                toast('Email não encontrado!')
            else:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def return_login(self):
        MDApp.get_running_app().root.current = 'loginmanager'


class HomePage(Screen):
    LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.day_semana = datetime.today().isoweekday()

        Clock.schedule_once(self.call_init,1)

    def call_init(self, *args):
        self.id_manager = self.get_id_manager()

        Clock.schedule_once(self.delet_day,1)

    def return_login(self):
        with open('refreshtoken.json','w') as file:
            json.dump('',file)

        MDApp.get_running_app().root.current = 'loginmanager'

    def on_pre_enter(self):
        Clock.schedule_once(self.get_local, 1)

    def get_id_manager(self, *args):
        try:
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Sem conecção a internet!')

    def get_local(self, *args):
        try:
            id_manager = self.get_id_manager()

            link = f'{self.LINK_SALAO}/{id_manager}.json'

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            local = requisicao_dic['local']
            number = requisicao_dic['numero']

            try:
                self.ids.rua.text = str(local.title())
                self.ids.num.text = str(number)
            except KeyError:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_ids_socios(self):
        # usad in fuction :
            # delet_day,
        try:
            lista_id = []

            link = f'{self.LINK_SALAO}/{self.id_manager}/socios.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                lista_id.append(id)
            return lista_id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def delet_day(self, *args):

    # Clean all schedule #############################################################
        try:
            with open('info_login.json', 'r') as file_login:
                id_login = json.load(file_login)

            day = int(self.day_semana) + 1

            if day > 7:
                day = 1

            lista_id = self.get_ids_socios()

            # Manager Here to delet three day before #################################################
            for dia in range(5):
                # link = f'{self.LINK_SALAO}/{id_login["id_login"]}/agenda/{day}.json'
                link = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{day}.json'
                requisicao_manager = requests.delete(link)
                day += 1

                if day > 7:
                    day = 1

            #Here to delet three day of schedule socion  #################################################

            day = int(self.day_semana) + 1

            for id_socio in lista_id:
                for dia in range(2):
                    link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{id_socio}/agenda/{day}.json'
                    requisicao = requests.delete(link)
                    day += 1

                    if day > 7:
                        day = 1

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')


class ClientBlocked(Screen):

    LINK_DATA = 'https://shedule-vitor-default-rtdb.firebaseio.com'

    # In use in function "search_client_blocked" first
     # List to geting the clients e filter the blockeds
    LIST_DATA_CLIENT = []

    # In use in function "insert_box" first
     # Here geting all clients
    LIST_ID_CLIENT = []

    def on_pre_enter(self):
        self.insert_box()

    def return_home(self):
        MDApp.get_running_app().root.current = 'homepage'

    def insert_box(self,*args):
        self.ids.scrool_blocked.clear_widgets()
        self.LIST_DATA_CLIENT.clear()

        try:
            LINK = f'{self.LINK_DATA}/client.json'

            list_id = []

            # Geting id of client ##########################################################################
            requisicao = requests.get(LINK)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                list_id.append(id)
            # ##############################################################################################

            for data_id in list_id:
                try:
                    if requisicao_dic[data_id]["bloqueado"] == "True":

                        self.LIST_DATA_CLIENT.append({"nome":requisicao_dic[data_id]["nome"],"quant_cancelado":requisicao_dic[data_id]["quant_cancelado"],"cpf":str(requisicao_dic[data_id]["cpf"]),"email":requisicao_dic[data_id]["email"], "id_client":data_id})

                        if int(requisicao_dic[data_id]["quant_cancelado"]) <= 1:
                            # self.ids.color_card.md_bg_color = (0.75, 0.86, 0.44, .4)
                            self.ids.scrool_blocked.add_widget(BoxBlocked(requisicao_dic[data_id]["nome"],requisicao_dic[data_id]["quant_cancelado"],str(requisicao_dic[data_id]["cpf"]),requisicao_dic[data_id]["email"], data_id))
                        elif int(requisicao_dic[data_id]["quant_cancelado"]) == 2:
                            # self.ids.color_card.md_bg_color = (1.00, 0.61, 0.44, .4)
                            self.ids.scrool_blocked.add_widget(BoxBlocked(requisicao_dic[data_id]["nome"],requisicao_dic[data_id]["quant_cancelado"],str(requisicao_dic[data_id]["cpf"]),requisicao_dic[data_id]["email"], data_id))
                        elif int(requisicao_dic[data_id]["quant_cancelado"]) >= 3:
                            # self.ids.color_card.md_bg_color = (0.48, 0.04, 0.00, .4)
                            self.ids.scrool_blocked.add_widget(BoxBlocked(requisicao_dic[data_id]["nome"],requisicao_dic[data_id]["quant_cancelado"],str(requisicao_dic[data_id]["cpf"]),requisicao_dic[data_id]["email"], data_id))
                    else:
                        pass
                except:
                    pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def search_client_blocked(self):
        self.ids.scrool_blocked.clear_widgets()

        search_text = self.ids.text_search.text

        for index, data in enumerate(self.LIST_DATA_CLIENT):
            # print(data)
            # try:
            if search_text in data["nome"]:
                if int(data["quant_cancelado"]) <= 1:
                    # self.ids.color_card.md_bg_color = (0.75, 0.86, 0.44, .4)
                    self.ids.scrool_blocked.add_widget(
                        BoxBlocked(data["nome"],data["quant_cancelado"],
                                   data["cpf"], data["email"], data["id_client"]))

                elif int(data["quant_cancelado"]) == 2:
                    # self.ids.color_card.md_bg_color = (1.00, 0.61, 0.44, .4)
                    self.ids.scrool_blocked.add_widget(
                        BoxBlocked(data["nome"], data["quant_cancelado"],
                                   data["cpf"], data["email"], data["id_client"]))

                elif int(data["quant_cancelado"]) >= 3:
                    # self.ids.color_card.md_bg_color = (0.48, 0.04, 0.00, .4)
                    self.ids.scrool_blocked.add_widget(
                        BoxBlocked(data["nome"], data["quant_cancelado"],
                                   data["cpf"], data["email"], data["id_client"]))

                elif search_text == ' ':
                    pass
            # except:
            #     pass


class ManagerProfile(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'
    list_day = []

    def __init__(self,*args,**kwargs):
        super().__init__(**kwargs)

        self.dia_atual = datetime.today().isoweekday()

        # print('dia ',self.dia_atual)
        Clock.schedule_once(self.call_init,1)

    # function that init with 'init'
    def call_init(self, *args):
        self.id_manager = self.get_id_manager()
        self.state_focus = None


    def insert_day(self, state, dia):
        """
        function whit receive the state e the day to be inserting in database
        :param state: the state of the button
        :param dia: day of the week
        :return:
        """
        if state == 'down':
            self.list_day.append(dia)
        elif state == 'normal':
            self.list_day.remove(dia)

    def on_valor(self):
        try:
            valor = float(self.ids.valor.text)

            self.ids.valor.text = str(valor)
        except ValueError:
            self.ids.valor.text = ''

        # if self.ids.valor.text >= 'a':
        #     pass
        # else:
        #     self.ids.valor.text = str(valor[0:len(self.ids.valor.text)-1])

    def un_focus(self):
        first = self.ids.tempo.text[:2]
        last = self.ids.tempo.text[2:]

        self.ids.tempo.text.split(':')

        if self.ids.tempo.text == '':
            self.state_focus = False
        elif len(self.ids.tempo.text) < 5:
            if int(first) > 23:
                self.ids.tempo.text = f'00:{str(first).zfill(2)}'
                self.state_focus = False
            else:
                self.state_focus = True
                self.ids.tempo.text = f'{str(first).zfill(2)}:{str(last).zfill(2)}'

    def on_text_temp(self,*args):
        text_temp = ''
        tamanho = self.ids.tempo.text

        if self.ids.tempo.text.isnumeric() or self.state_focus == True:
            if len(self.ids.tempo.text) >= 5:
                if self.state_focus == True:
                    self.ids.tempo.text = str(tamanho[0:len(tamanho)])
                else:
                    self.ids.tempo.text = str(tamanho[0:len(tamanho) - 1])
            else:
                pass
        else:
            self.ids.tempo.text = str(tamanho[0:len(tamanho)-1])

    def show_focus(self, stado, day, *args, **kwargs):

        entrada = ''
        saida = ''
        space_temp = ''
        dia = day
        semana = ''

        with open('is_manager_or_socio.json', 'r') as file:
            is_manager = json.load(file)

        if int(dia) == 1:
            semana = 'Segunda'
        elif int(dia) == 2:
            semana = 'Terça'
        elif int(dia) == 3:
            semana = 'Quarta'
        elif int(dia) == 4:
            semana = 'Quinta'
        elif int(dia) == 5:
            semana = 'Sexta'
        elif int(dia) == 6:
            semana = 'Sabado'
        elif int(dia) == 7:
            semana = 'Domingo'

        try:
            if stado == 'down':
                if is_manager == 'manager':
                    link = f'{self.LINK_SALAO}/{self.id_manager}/{dia}.json'
                    requisicao = requests.get(link)
                    requisicao_dic = requisicao.json()

                    entrada = requisicao_dic['entrada']
                    saida = requisicao_dic['saida']
                    space_temp = requisicao_dic['space_temp']


                elif is_manager == 'socio':

                    with open('info_login.json', 'r') as file_login:
                        id = json.load(file_login)

                    link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{id["id_login"]}/{dia}.json'
                    requisicao = requests.get(link)
                    requisicao_dic = requisicao.json()

                    entrada = requisicao_dic['entrada']
                    saida = requisicao_dic['saida']
                    space_temp = requisicao_dic['space_temp']

                toast(f'       {semana}\nEntrada - {entrada}\nSaida   -   {saida}\ntempo  -  {space_temp}')
            else:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            toast(f'"{semana}"\nNem uma agenda criada nesse dia!')

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.preview)
        try:
            self.creat_profile()
            self.insert_hours()
            self.only_manager_local()
            Clock.schedule_once(self.get_socios,2)
            Clock.schedule_once(self.infill,3)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.preview)

    def preview(self, windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'homepage'
        return True

    def get_id_manager(self, *args):
        try:
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Sem conecção a internet!')

    # Here only return the id of user
    def get_id_whith_refreshtoken(self, *args):
        with open('refreshtoken.json', 'r') as arquivo:
            refresh_token = json.load(arquivo)

        try:
            LINK_CHANGE_REFRESH = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'

            info = {"grant_type": "refresh_token",
                    "refresh_token": refresh_token}

            requisicao_rest = requests.post(LINK_CHANGE_REFRESH, data=info)
            requisicao_dic = requisicao_rest.json()


            user_id = requisicao_dic['user_id']

            return user_id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def creat_profile(self, *args):
        try:
            self.user_id = self.get_id_whith_refreshtoken()
            try:
                LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'

                requisicao_base_salao = requests.get(LINK_BASE_SALAO)
                requisicao_salao_dic = requisicao_base_salao.json()

                name = requisicao_salao_dic['nome']
                self.ids.text_name.text = str(name).title()

                # saving infomation if is manager or socio #################################################################
                with open('is_manager_or_socio.json','w', encoding='utf-8') as file:
                    json.dump('manager', file)

            except TypeError:

                LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}.json'

                requisicao_base_salao = requests.get(LINK_BASE_SALAO)
                requisicao_salao_dic = requisicao_base_salao.json()

                name = requisicao_salao_dic['nome']
                self.ids.text_name.text = str(name).title()

                # saving infomation is manager or socio
                with open('is_manager_or_socio.json','w', encoding='utf-8') as file:
                    json.dump('socio', file)

            try:
                self.ids.entry.text = requisicao_salao_dic[f'{self.dia_atual}']['entrada']
                self.ids.exit.text = requisicao_salao_dic[f'{self.dia_atual}']['saida']
                self.ids.space_temp.text = requisicao_salao_dic[f'{self.dia_atual}']['space_temp']
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def insert_hours(self, *args, **kwargs):
        """
        function that receiv the hours
        :param args:
        :param kwargs:
        :return:
        """
        self.ids.hours.clear_widgets()
        for hours, min in enumerate(range(24)):
            h = f'{str(hours).zfill(2)}:00'
            bt = MDTextButton(text=str(h),font_style='Body2',bold=True ,pos_hint=({'center_x':.5}))
            bt.md_bg_color=(0.13, 0.53, 0.95,.1)
            bt.font_size='25sp'
            self.ids.hours.add_widget(bt)
            bt.bind(on_release=self.insert)

            h2 = f'{str(hours).zfill(2)}:30'
            bt = MDTextButton(text=str(h2),font_style='Body2', bold=True ,pos_hint=({'center_x':.5})) # ,md_bg_color=(0.13, 0.53, 0.95,.3)
            bt.md_bg_color=(0.13, 0.53, 0.95,.3)
            bt.font_size='20sp'
            self.ids.hours.add_widget(bt)

            bt.bind(on_release=self.insert)

    # Here get the TextField selectioning for be insert of hours
    def validate(self,msg,**kwargs):
        self.msg = msg

    # Receiv the hours and insert in field
    def insert(self,texto,**kwargs):
        """
        Here choice the field of entry or exit for will be insert hours
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
            elif msg == 'time_cancel':
                self.ids.time_cancel.text = str(texto.text)
        except AttributeError:


            self.focus_entry_press()
            Clock.schedule_once(self.focus_exit_press,2)
            Clock.schedule_once(self.focus_time_cancel_press,3)



            toast('Escolha o campo a ser preenchido! Entrada ou Saida')
            # Clock.schedule_once(self.focus_time_cancel, 3)

    # Functions to gyve  'Focus' in TextField ###############################
    def focus_entry_press(self, *args):
        self.ids.entry.focus = True
        Clock.schedule_once(self.focus_entry_leave,2)

    def focus_entry_leave(self, *args):
        self.ids.entry.focus = False

    def focus_exit_press(self, *args):
        self.ids.exit.focus = True
        Clock.schedule_once(self.focus_exit_leave,2)

    def focus_exit_leave(self, *args):
        self.ids.exit.focus = False

    def focus_time_cancel_press(self, *args):
        self.ids.time_cancel.focus = True
        Clock.schedule_once(self.focus_time_cancel_leave,2)

    def focus_time_cancel_leave(self, *args):
        self.ids.time_cancel.focus = False
    #/########################################################################

    def save_data(self,*args):

        with open('is_manager_or_socio.json','r') as file:
            if_manager = json.load(file)
        try:

            if if_manager == 'socio':

                for day in self.list_day:
                    LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/{day}.json'

                    self.entrada = self.ids.entry.text
                    self.saida = self.ids.exit.text
                    self.space_tempo = self.ids.space_temp.text

                    info = f'{{"entrada":"{self.entrada}",\
                             "saida": "{self.saida}",\
                             "space_temp":"{self.space_tempo}",\
                             "agenda":"" }}'

                    requisica = requests.patch(LINK_BASE_SALAO, info)

                self.ids.sunday.state = 'normal'
                self.ids.monday.state = 'normal'
                self.ids.tuesday.state = 'normal'
                self.ids.wednesday.state = 'normal'
                self.ids.thursday.state = 'normal'
                self.ids.friday.state = 'normal'
                self.ids.saturday.state = 'normal'

                self.ids.carosel.load_next()

                toast('Tabela de horas salva com sucesso!')
    # "For in end Point" ??????????????????????????????????????????????????????????????????????????????
            elif if_manager == 'manager':

                for day in self.list_day:
                    LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/{day}.json'


                    self.entrada = self.ids.entry.text
                    self.saida = self.ids.exit.text
                    self.space_tempo = self.ids.space_temp.text

                    info = f'{{"entrada":"{self.entrada}",\
                               "saida": "{self.saida}",\
                               "space_temp":"{self.space_tempo}"}}'

                    requisicao = requests.patch(LINK_BASE_SALAO, info)


                time_cancel = self.ids.time_cancel.text
                LINK_BASE_TIME_CANCEL = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'
                info_cancel = f'{{"time_cancel":"{time_cancel}"}}'
                requisica = requests.patch(LINK_BASE_TIME_CANCEL, info_cancel)

                self.ids.sunday.state = 'normal'
                self.ids.monday.state = 'normal'
                self.ids.tuesday.state = 'normal'
                self.ids.wednesday.state = 'normal'
                self.ids.thursday.state = 'normal'
                self.ids.friday.state = 'normal'
                self.ids.saturday.state = 'normal'

                self.ids.carosel.load_next()

                toast('Tabela de horas salva com sucesso!')
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def save_servicos(self,*args):

        nome_servico = self.ids.nome_servico.text.upper()
        tempo = self.ids.tempo.text
        valor = self.ids.valor.text

        with open('is_manager_or_socio.json', 'r') as file:
            is_manager = json.load(file)
        try:
            if nome_servico != '' and tempo != '' and valor != '':

                if is_manager == 'socio':
                    LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos.json'

                    info = f'{{"nome_servico":"{nome_servico}",' \
                           f'"tempo":"{tempo}",' \
                           f'"valor":"{valor}",' \
                           f'"servicos":"",' \
                           f'"agenda":""}}'

                    requisicao = requests.post(LINK_BASE_SALAO, info)
                    toast('Categoria criada')

                    self.infill()
                    self.ids.carosel.load_next()

                    self.ids.nome_servico.text = ''
                    self.ids.tempo.text = ''
                    self.ids.valor.text = ''

                elif is_manager == 'manager':
                    LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos.json'

                    info = f'{{"nome_servico":"{nome_servico}",' \
                           f'"tempo":"{tempo}",' \
                           f'"valor":"{valor}",' \
                           f'"servicos":""}}'

                    requisicao = requests.post(LINK_BASE_SALAO, info)
                    toast('Categoria criada')

                    self.infill()

                    self.ids.carosel.load_next()

                    self.ids.nome_servico.text = ''
                    self.ids.tempo.text = ''
                    self.ids.valor.text = ''
            else:
                toast('Precisa de todas as informções de serviços!')
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def infill(self, *args):
        socio_ou_gerente = False
        requisicao_get = ''

        with open('is_manager_or_socio.json','r') as file:
            is_manager = json.load(file)
        try:
            # Para saber si quem esta acessando é o socio ou o gerente #####################################################
            if is_manager == 'socio':
                LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos.json'
                requisicao_get = requests.get(LINK_CATEGORIA)
                socio_ou_gerente = True
            elif is_manager == 'manager':
                LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos.json'
                requisicao_get = requests.get(LINK_CATEGORIA)
                socio_ou_gerente = False

            requisicao_get_dic = requisicao_get.json()

            self.ids.categorie.clear_widgets()

            try:
                # Here I am also getting the work id ####################################################################
                # Aqui eu também estou recebendo o id de trabalho
                for id in requisicao_get_dic:
                    if socio_ou_gerente:
                        LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos/{id}.json'
                    else:
                        LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos/{id}.json'

                    requisicao_get_categoria = requests.get(LINK_ID)
                    requisicao_get_categoria_dic = requisicao_get_categoria.json()

                    nome_servico = requisicao_get_categoria_dic['nome_servico']
                    tempo = requisicao_get_categoria_dic['tempo']
                    valor = str(float(requisicao_get_categoria_dic['valor']))

                    mybox_categorie = MyBoxCategorie(id, nome_servico,tempo,valor)
                    mybox_categorie.bind(on_release=partial(self.pop_alteration, id, nome_servico,tempo,valor))
                    self.ids.categorie.add_widget(mybox_categorie)
            except TypeError:
                pass

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def save_socio(self,*args):
        try:
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_socios(self,*args):

        self.ids.box_socio.clear_widgets()

        # geting the id of manager to send in class MyBoxSocio
        id_manager = self.get_id_manager()

        print('id__', id_manager)

        lista = []

        try:
            LINK_SOCIO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/socios.json'
            socio = requests.get(LINK_SOCIO)
            socio_dic = socio.json()

            try:
                for id_socio in socio_dic:
                    nome = socio_dic[id_socio]
                    nome_dic = nome
                    self.ids.box_socio.add_widget(MyBoxSocio(str(nome_dic['nome']), id_socio, id_manager))
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def only_manager_local(self, *args):
        try:
            with open('is_manager_or_socio.json','r') as file:
                manager_or_socio = json.load(file)

            if manager_or_socio == 'manager':
                bt = self.ids.button_local
                bt.bind(on_release=self.insert_local)
                bt.md_bg_color = (0.13, 0.53, 0.95,1)
            elif manager_or_socio == 'socio':
                bt = self.ids.button_local
                bt.unbind(on_release=self.insert_local)
                bt.md_bg_color = (1,0,0,1)
        except:
            pass

    def insert_local(self, *args):

        try:
            link = f'{self.LINK_SALAO}/{self.id_manager}.json'

            local = self.ids.rua.text
            number = self.ids.number.text

            if local != '' and number != '':

                info = f'{{"local":"{local}",' \
                       f'"numero":{number} }}'

                requisicao = requests.patch(link, data=info)

                toast('Local inserido com exito!')
                self.ids.carosel.load_next()
            else:
                toast('Local não foi inserido folta de informação!')
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def pop_alteration(self,id_work, servico, tempo, valor, *args, **kwargs):
        box_main = MDBoxLayout(orientation='vertical',md_bg_color=([1,1,1,1]),radius=(5,5,5,5))

        box_widgets = MDBoxLayout()
        box_buttons = MDBoxLayout(size_hint_y=None,height=('30dp'),spacing=8, padding=8)

        self.popup = Popup(title_color=(1, 1, 1, .0), separator_color=([0,1,1,1]), background_color=([1, 1, 1, 0]),
                           size_hint=(None, None), size=('240dp', '400dp'),
                           content=box_main)

        box_widgets.add_widget(Popup_widgets(self.id_manager, self.user_id, id_work, servico, tempo, valor))

        box_main.add_widget(box_widgets)
        # box_main.add_widget(box_buttons)

        self.popup.open()

    def dismiss_popup(self, *args):
        self.popup.dismiss()


# Essa class é a propria conteudo do popup da class ManagerProfile()
class Popup_widgets(MDBoxLayout):
    list_tempo = []
    def __init__(self,id_manager='', user_id='', id_work='', servico='',tempo='', valor='', **kwargs):
        super().__init__(**kwargs)

        self.id_manager = id_manager
        self.user_id = user_id

        self.id_work = id_work
        self.servico = servico
        self.tempo = tempo
        self.valor = valor

    def pop_edit(self, id_work, *args, **kwargs):

        try:
            tempo = self.ids.id_tempo.text
            valor = self.ids.id_valor.text

            with open('is_manager_or_socio.json', 'r') as file:
                is_manager = json.load(file)

            info = f'{{"tempo":"{tempo}",' \
                   f'"valor":"{valor}"}}'

            try:
                # Para saber si quem esta acessando é o socio ou o gerente #####################################################
                if is_manager == 'socio':
                    LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos{id_work}.json'
                    requisicao_get = requests.patch(LINK_CATEGORIA, data=info)

                elif is_manager == 'manager':
                    LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos/{id_work}.json'
                    requisicao_get = requests.patch(LINK_CATEGORIA, data=info)

                toast('Alterações feita com sucesso!')

                self.parent.parent.parent.parent.parent.dismiss()

                MDApp.get_running_app().root.current = 'managerprofile'

                # ManagerProfile().test()
            except:
                toast('Deu Algum erro! não foi alterado ')
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def pop_delet_work(self, id_work):

        with open('is_manager_or_socio.json', 'r') as file:
            is_manager = json.load(file)

        try:
            # Para saber si quem esta acessando é o socio ou o gerente #####################################################
            if is_manager == 'socio':
                LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos{id_work}.json'
                requisicao_get = requests.delete(LINK_CATEGORIA)

            elif is_manager == 'manager':
                LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos/{id_work}.json'
                requisicao_get = requests.delete(LINK_CATEGORIA)

            toast('Serviço excluido!')

            self.parent.parent.parent.parent.parent.dismiss()

            MDApp.get_running_app().root.current = 'managerprofile'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            toast('Deu Algum erro! não foi excluido ')


class BoxBlocked(MDCard):

    LINK_DATA = 'https://shedule-vitor-default-rtdb.firebaseio.com'

    def __init__(self,nome, quant_cancel, cpf, tel='', id_client='', *args, **kwargs):
        super().__init__(**kwargs)

        self.nome = nome
        self.quant_cancel = quant_cancel
        self.cpf = cpf
        self.tel = tel
        self.id_client = id_client

        if int(quant_cancel) <= 1:
            self.ids.color_card.md_bg_color = (0.75, 0.86, 0.44, .4)
            self.ids.text_quant.color = (0.75, 0.86, 0.44, 1)
        elif int(quant_cancel) == 2:
            self.ids.color_card.md_bg_color = (1.00, 0.61, 0.44, .4)
            self.ids.text_quant.color = (1.00, 0.61, 0.44, 1)

        elif int(quant_cancel) >= 3:
            self.ids.color_card.md_bg_color = (0.83, 0.04, 0.00, .4)
            self.ids.text_quant.color = (0.83, 0.04, 0.00, 1)

    def pop_dis_block(self,eu, nome, id_client, *args, **kwargs):
        # box = MDBoxLayout(orientation='vertical')
        # box_button = MDBoxLayout(padding=15, spacing='70dp')

        img = Label(text=f'"{nome}"?',bold=True)

        bt_sim = MDFlatButton(text='Sim', theme_text_color="Custom",text_color=(1, 0, 0, .8))
        bt_nao = MDFlatButton(text='Não')

        self.popup = MDDialog(title=f'Desbloquear cliente? ', buttons=[bt_sim, bt_nao])

        bt_sim.bind(on_release=partial(self.dis_blocked,eu, id_client))
        bt_nao.bind(on_release=self.popup.dismiss)

        self.popup.open()

    def dis_blocked(self, eu, id_client, *args):
        try:
            link_client = f'{self.LINK_DATA}/client/{id_client}.json'

            info = f'{{"bloqueado":"False",' \
                   f'"quant_cancelado":"0"}}'

            requisicao = requests.patch(link_client, data=info)

            self.popup.dismiss()
            toast('Cliente Desbloqueado!')
            eu.parent.remove_widget(eu)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')


class MyButtonCard(MDCard):
    pass


class MyButtonCard_2(MDCard):
    pass


class MyBoxCategorie(MDCard):

    def __init__(self,id_work='', servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)
        self.id_work = id_work
        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class CategoriesWork(MDCard):

    def __init__(self, servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)

        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class MyBoxCategorieLabel(MDCard):
    def __init__(self, servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)

        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class MyBoxSocio(MDCard):

    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self,name, id_socio, id_manager, **kwargs):
        super().__init__(**kwargs)
        self.nome = name
        self.id_socio = id_socio
        self.id_manager = id_manager

    def dialog_delet(self, id_socio, id_manager, *args, **kwargs):

        bt_sim = MDFlatButton(text='Sim')
        bt_sim.color = (1,0,0,1)

        bt_nao = MDFlatButton(text='Não')

        self.dialog = MDDialog(title='Deseja delêtar este sócio?', buttons=[bt_sim, bt_nao])

        bt_sim.bind(on_release=partial(self.delet_socio, id_socio, id_manager))
        bt_nao.bind(on_release=self.dialog.dismiss)

        self.dialog.open()

    def delet_socio(self, id_socio, id_manager, *args, **kwargs):

        link_to_delet = f'{self.LINK_SALAO}/{id_manager}/socios/{id_socio}.json'

        requisicao = requests.delete(link_to_delet)

        managerprofile = ManagerProfile()
        managerprofile.__init__()

        self.dialog.dismiss()
        toast('Sócio Deletado com sucesso!')


class Table_shedule(MDBoxLayout):

    def __init__(self,id_button='', id_schedule='',hours='', hours_second='', time='',time_cancel='', client='', email='',cpf='', **kwargs):
        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.hours_second = hours_second
        self.time = time
        self.time_cancel = time_cancel
        self.client = str(client)
        self.email = str(email)
        self.cpf = str(cpf)


class TableEnpty(MDBoxLayout):

    def __init__(self,id_button='', id_schedule='',hours='', hours_second='', time='', client='',**kwargs):
        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.hours_second = hours_second
        self.time = time
        self.client = str(client)


class TableInfo(MDBoxLayout):
    # def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='',**kwargs):
    def __init__(self,id_button='', id_schedule='',hours='', hours_second='', time='', client='', email='', cpf='', *args, **kwargs):
        super().__init__(**kwargs)

        #         # self.id_button = id_button
        #         # self.id_schedule = id_schedule
        #         # self.hours = str(hours)
        #         # self.client = str(client)
        #         # self.hours_2 = hours2

        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.hours_2 = hours_second
        self.time = time
        self.client = str(client)
        self.email = str(email)
        self.cpf = str(cpf)


class CardButtonProficional(MDCard):

    def __init__(self, socio_or_manager='', id_user='', nome='', **kwargs):
        super().__init__(**kwargs)

        self.socio_or_manager = socio_or_manager
        self.id_user = id_user
        self.nome = nome

    def send_info(self, socio_or_manager, id_user):
        dictionary = {}

        dictionary['manager'] = socio_or_manager
        dictionary['id_user'] = id_user

        with open('write_id_manager.json', 'w') as arquivo:
            json.dump(dictionary, arquivo, indent=2)

        MDApp.get_running_app().root.current = 'viewshedule'


class ScreenChoiceSchedule(Screen):
    LINK_DATABASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.call_init,1)

    def call_init(self, *args):
        try:
            self.id_manager =  self.get_id_manager()
            Clock.schedule_once(self.get_info, 1)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def on_pre_enter(self):
        Window.bind(on_keyboard=self.previews)

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.previews)

    def previews(self,windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'homepage'
        else:
            pass
        return True

    # Geting id of manager ########################################################
    def get_id_manager(self):
        try:
            requisicao = requests.get(self.LINK_DATABASE_SALAO + '.json')
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_info(self, *args):

        self.ids.choice_schedule.clear_widgets()
        try:
            link_salao = self.LINK_DATABASE_SALAO + '/' + self.id_manager + '.json'

            requisicao = requests.get(link_salao)
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']
            socio_or_manager = requisicao_dic['manager']
            self.ids.choice_schedule.add_widget(CardButtonProficional(socio_or_manager, self.id_manager, nome))

            for id_socio in requisicao_dic['socios']:
                link_socio = self.LINK_DATABASE_SALAO + '/' + self.id_manager + '/socios/' + f'/{id_socio}.json'
                requiscao_socio = requests.get(link_socio)
                requiscao_socio_dic = requiscao_socio.json()
                self.ids.choice_schedule.add_widget(CardButtonProficional(requiscao_socio_dic['manager'], id_socio ,requiscao_socio_dic['nome'] ))
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
    # def on_pre_enter(self, *args):
    #     self.get_info()

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'


class ViewSchedule(Screen):
    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"
    x = NumericProperty(0)
    y = NumericProperty(0)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.dia_atual = datetime.today().isoweekday()

        # self.LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'

        self.LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

        try:
            # Getting the id of manager ####################################################################################
            self.id_manager = self.get_manager()
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_data_hall(self):

        requisicao = requests.get(self.LINK_SALAO + '.json')
        requisicao_dic = requisicao.json()
        return requisicao_dic

    def on_pre_enter(self, *args):
        try:
            Clock.schedule_once(self.actualizar, 1)
            Window.bind(on_keyboard=self.previews)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def previews(self,windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'screenchoiceschedule'
        else:
            pass
        return True

    def time_now(self):
        h = datetime.today().hour
        mim = datetime.today().minute
        horas = f'{str(h).zfill(2)}:{str(mim).zfill(2)}'

        return horas

    def get_manager(self, *args):
        try:
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()
            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_id_proficional(self, *args):
        dic_information = {}

        with open('write_id_manager.json', 'r') as arquivo:
            dic_informing = json.load(arquivo)
        return dic_informing

    def info_login_file(self, *args):
        with open('info_login.json','r') as file:
            info_login = json.load(file)
        return info_login

    def log_aut(self,*args):
        try:
            LINK = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
            try:
                with open('refreshtoken.json', 'r') as arquivo:
                    refresh = json.load(arquivo)
                info = {"grant_type":"refresh_token",
                        "refresh_token":refresh}

                requisicao = requests.post(LINK, data=info)
                requisicao_dic = requisicao.json()

                idtoken = requisicao_dic["id_token"]
                user_id = requisicao_dic["user_id"]

                if requisicao.ok:
                    return user_id
                else:
                    pass
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def info_entrace_salao(self, *args):
        try:
            id_manager = self.get_id_proficional()
            lista_info = []

            try:
                # information socio ############################################################################################
                if id_manager["manager"] == 'False':
                    # Here if not manager then get the socio #########################################################################
                    LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager["id_user"]}.json'
                    requisicao = requests.get(LINK_SALAO)
                    requisicao_dic_socio = requisicao.json()

                    nome = requisicao_dic_socio['nome']
                    self.ids.title_toobar.title = f'Agenda {str(nome)}'

                    self.entrada = requisicao_dic_socio[f'{self.dia_atual}']['entrada']

                    self.saida = requisicao_dic_socio[f'{self.dia_atual}']['saida']

                    self.space_temp = requisicao_dic_socio[f'{self.dia_atual}']['space_temp']

                    try:
                        # Estes "FOR" é porque esta dando erro as vêzes quer "self.dia_atual" STR ou INT #######################
                        try:
                            for id_agenda in requisicao_dic_socio['agenda'][int(self.dia_atual)]:
                                lista_info.append(requisicao_dic_socio['agenda'][int(self.dia_atual)][id_agenda])
                        except:
                            for id_agenda in requisicao_dic_socio['agenda'][str(self.dia_atual)]:
                                lista_info.append(requisicao_dic_socio['agenda'][str(self.dia_atual)][id_agenda])
                        return lista_info
                    except:
                        return lista_info

                elif id_manager["manager"] == 'True':

                    # Here to geting the id of manager to get schedule #######################################
                    requisicao = requests.get(f'{self.LINK_SALAO}/{self.id_manager}.json')
                    requisicao_dic = requisicao.json()

                    nome = requisicao_dic['nome']
                    self.ids.title_toobar.title = f'Agenda {str(nome)}'


                    self.entrada = requisicao_dic[f'{self.dia_atual}']['entrada']

                    self.saida = requisicao_dic[f'{self.dia_atual}']['saida']

                    self.space_temp = requisicao_dic[f'{self.dia_atual}']['space_temp']

                    # Here get the ids of schedule client ######################################################################
                    try:
                        # Estes "FOR" é porque esta dando erro as vêzes quer "self.dia_atual" STR ou INT #######################
                        try:
                            for id_agenda in requisicao_dic['agenda'][int(self.dia_atual)]:
                                lista_info.append(requisicao_dic['agenda'][int(self.dia_atual)][id_agenda])
                        except:
                            for id_agenda in requisicao_dic['agenda'][str(self.dia_atual)]:
                                lista_info.append(requisicao_dic['agenda'][str(self.dia_atual)][id_agenda])
                        return lista_info

                    except:
                        return lista_info
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def loop_actualizar(self, *args):
        # Clock.schedule_once(self.actualizar,30)
        pass

    def actualizar(self, *args):

        try:
            # get user id ##################################################################################################
            user_id = self.log_aut()
            lista_info = self.info_entrace_salao()

            list_content = []

            entrada = self.entrada
            saida = self.saida
            tempo = self.space_temp

            data_hall = self.get_data_hall()
            id_manager = self.get_manager()
            print(data_hall[id_manager]['time_cancel'])


            time_c = data_hall[id_manager]['time_cancel']
            # Time Mensage of cancel ot schedule #############################
            time_cancel = f'[color=#6B0A00][b]"Atenção":[/b][/color][b]{time_c}[/b] [size=18]H/M[/size] para desmarcar apos agendamento!'

            # variable to show the first schedule if it is scheduled, is implemented in "for range", I do this to display the correct schedule table
            # variável para mostrar o primeiro agendamento se for agendado, está implementado no "for range", Eu faço isso para exibir a tabela de agendamento correta
            ranger_init = 0
            ranger_last = 61

            # lista = ['']
            block = False
            permition_to_sum = True

            # To conting the position of schedule to verification of next schedule
            cont = 00

            self.ids.grid_shedule.clear_widgets()

            # Here i am sorting the list "lista_info" in key "['id_horas']" #########################################################
            ordem = sorted(lista_info, key=lambda valor: valor['id_horas'])
            lista_info = ordem

            # try:
            while entrada[:2] < saida[:2]:
                for num, agenda in enumerate(lista_info):
                    ranger_init = 0

                    # In field email and cpf if not go manager then givin an error of keyError:
                    # In the e-mail and cpf field if it is not a manager then it gives a keyError error: ## traduzido
                    # No campo e-mail e cpf se não for gerenciador então dá erro de keyError:
                    try:
                        email = lista_info[num]['email']
                    except:
                        email = ''

                    try:
                        cpf = lista_info[num]['cpf']
                    except:
                        cpf = ''

                    try:
                        if entrada[:2] == lista_info[num]['id_horas'][:2]:
                            for mim in range(ranger_init, ranger_last):

                                entry_future = datetime.strptime(entrada, '%H:%M')
                                fmim = str(f'00:{mim}').zfill(2)
                                ft_hours, ft_min = map(int, fmim.split(':'))
                                delta_minutes = timedelta(hours=ft_hours, minutes=ft_min)
                                soma_future = entry_future + delta_minutes

                                try:
                                    if soma_future.strftime("%H:%M") > lista_info[1]['id_horas']:
                                        entrada = lista_info[num]['id_horas']
                                        mim = lista_info[num]['id_horas'][3:]
                                    else:
                                        pass
                                except:
                                    if soma_future.strftime("%H:%M") > lista_info[0]['id_horas']:
                                        entrada = lista_info[num]['id_horas']
                                        mim = lista_info[num]['id_horas'][3:]
                                    else:
                                        pass

                                # conparing the minutes ###################################################################################
                                if str(mim).zfill(2) == lista_info[0]['id_horas'][3:]:
                                    ent = int(str(entrada[:2]).zfill(2))
                                    entrada = f'{str(ent).zfill(2)}:{str(mim).zfill(2)}'

                                    entry = datetime.strptime(entrada, '%H:%M')
                                    temp = lista_info[0]['tempo']
                                    hours, minute = map(int, temp.split(':'))
                                    delta_temp = timedelta(hours=hours, minutes=minute)
                                    soma_horas = entry + delta_temp

                                    # Here comparat the ids to know  if is of manager I take of  the number inserting on last
                                    # Aqui comparo os ids  para saber se é do manager tiro os numeros adicionados no final
                                    id_primay = len(user_id)
                                    id_secont = lista_info[0]['id_user'][0:id_primay]

                                    if user_id == lista_info[0]['id_user'] or user_id == id_secont:
                                        # Insert table #####################################################################################
                                        table = TableInfo(str(cont), lista_info[0]['id_user'], entrada,
                                                              f'{soma_horas.strftime("%H:%M")}', lista_info[num]['tempo'], lista_info[num]['nome'], str(email), str(cpf))
                                        table.msg = f'[color=#6B0A00][b]"Atenção":[/b][/color] Você tem {data_hall[id_manager]["time_cancel"]} minutos para desmarcar apos agendamento!'
                                        # print(table)
                                        self.ids.grid_shedule.add_widget(table)
                                        entrada = soma_horas.strftime('%H:%M')
                                        block = True
                                        permition_to_sum = False
                                        ranger_init = entrada[3:]
                                        del(lista_info[0])

                                        # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                        cont += 1
                                        break
                                    else:
                                        table = Table_shedule(str(cont), lista_info[num]['id_user'], entrada,
                                                              f'{soma_horas.strftime("%H:%M")}', lista_info[num]['tempo'], str(time_cancel), lista_info[num]['nome'], str(email), str(cpf))
                                        table.msg = f'[color=#6B0A00][b]"Atenção":[/b][/color] Você tem {data_hall[id_manager]["time_cancel"]} minutos para desmarcar apos agendamento!'
                                        self.ids.grid_shedule.add_widget(table)
                                        list_content.append(entrada)
                                        entrada = soma_horas.strftime('%H:%M')
                                        block = True
                                        permition_to_sum = False
                                        ranger_init = entrada[3:]
                                        del (lista_info[0])
                                        cont += 1
                                        break

                                # To not give error, of disappear the scheduling previous
                                # para não dá erro, de sumir o agendamento anterior
                                elif str(int(mim) + 1).zfill(2) == tempo[3:] and soma_future.strftime('%H:%M') <= lista_info[0]['id_horas'] :
                                    table = TableEnpty(str(cont), '', entrada, f'', '')
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append('')
                                    block = True
                                    permition_to_sum = True
                                    ranger_init = entrada[3:]
                                    cont += 1
                    except:
                        print('Deu algum erro na função actualizar da class "ViewSchedule"')

                # except:
                #     print('Deu algum erro na função actualizar da class "ViewSchedule"')

                # Here block to not have repetition ########################################################################
                # Aqui bloqueia para não ter repetições

                if block == False:

                    soma_entrada = datetime.strptime(entrada, '%H:%M')
                    h_tempo, m_tempo = map(int, tempo.split(':'))
                    delta_soma = timedelta(hours=h_tempo, minutes=m_tempo)

                    soma_tempo = soma_entrada + delta_soma

                    try:
                        if soma_tempo.strftime('%H:%M') <= lista_info[0]['id_horas']:
                            table = TableEnpty(str(cont), '', entrada, f'', '')
                            self.ids.grid_shedule.add_widget(table)
                            list_content.append('')
                            permition_to_sum = True
                            anger_init = entrada[3:]
                            cont += 1
                        else:
                            permition_to_sum = True
                    except IndexError:
                        table = TableEnpty(str(cont), '', entrada, f'', '')
                        self.ids.grid_shedule.add_widget(table)
                        list_content.append('')
                        permition_to_sum = True
                        anger_init = entrada[3:]
                        cont += 1

                block = False

                if permition_to_sum == True:

                    # adding up the hours ####################################
                    # somando as horas ##
                    inicio = datetime.strptime(entrada, '%H:%M')
                    horas, minutos = map(int, tempo.split(':'))
                    delta_tempo = timedelta(hours=horas, minutes=minutos)
                    final = inicio + delta_tempo
                    entrada = final.strftime('%H:%M')


            # using in class "HoursSchedule" function "hours_limit" ###########
            with open('list_content.json', 'w') as file:
                json.dump(list_content, file)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            toast('Nenhuma Horário para hoje!')


        # Clock.schedule_once(self.loop_actualizar, 3)

    def refresh_callback(self, *args):
        '''A method that updates the state of your application
        while the spinner remains on the screen.'''

        def refresh_callback(interval):
            self.ids.grid_shedule.clear_widgets()
            self.x = 0
            self.y = 0

            self.actualizar()
            self.ids.refresh_id.refresh_done()


        Clock.schedule_once(refresh_callback, 1)

    def popup_mark_off(self, id_button, id_schedule, hours, hours_second, time, client, email, cpf, *args, **kwargs):

        try:
            id_user = ''
            with open('write_id_manager.json', 'r') as file:
                id_user = json.load(file)

            box = MDBoxLayout(orientation='vertical')
            box_button = MDBoxLayout(padding=5,spacing=5)

            img = Image(source='images/atencao.png')

            bt_sim = Button(text='Sim',background_color=(0,1,1,1),color=(1,0,0,.8), size_hint=(1,None),height='40dp')
            bt_nao = Button(text='Não',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')
            bt_view = Button(text='View',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')

            box_button.add_widget((bt_sim))
            box_button.add_widget((bt_nao))
            box_button.add_widget((bt_view))

            box.add_widget((img))
            box.add_widget((box_button))

            self.popup  = Popup(title='Deseja cancelar o agendamento?',
                           size_hint=(.8,None), height='200dp',content=box)

            bt_sim.bind(on_release = partial(self.cancel_schedule, id_schedule))
            bt_sim.bind(on_press = partial(self.load_widget))
            bt_nao.bind(on_release = self.popup.dismiss)
            bt_view.bind(on_release = partial(self.wait_inf_schedule_client, id_button, id_schedule, hours, hours_second, time, client, email, cpf))
            self.popup.open()
        except:
            pass

    def load_widget(self, *args, **kwargs):

        # The "md_label" not show!
        try:
            md_label = MDLabel(text='Carregando...', color=(1, 1, 1, 1))
            spiner = MDSpinner(active=True, size_hint=(None, None), size=('56dp', '56dp'),
                               pos_hint=({'center_x': .5, 'center_y': .5}))
            self.box_dialog = MDDialog(buttons=[md_label])

            self.box_dialog.add_widget(spiner)
            # self.parent.parent.add_widget(self.boxlayout)
            self.box_dialog.open()
        except:
            pass

    def cancel_schedule(self, id_user, *args, **kwargs):

        data_hall = self.get_data_hall()

        # eval_data_hall = eval(data_hall)
        # print(data_hall[id_user]['agenda_do_salao'])

        try:
            id_proficional = self.get_id_proficional()
            id_manager = self.id_manager
            # info_login = self.info_login_file()

            link = ''
            link_agenda_salao = ''

            if id_proficional['manager'] == "False":
                # link = self.LINK_SALAO + f'/{id_manager}/socios/{id_user}/agenda/{self.dia_atual}/{info_login["id_login"]}.json'
                link = self.LINK_SALAO + f'/{id_manager}/socios/{id_user}/agenda/{self.dia_atual}/{id_user}.json'
                link_agenda_salao = self.LINK_SALAO + f'/{id_manager}/socios/{id_user}/agenda_do_salao/{self.dia_atual}/{id_user}.json'
            elif id_proficional['manager'] == "True":
                # link = self.LINK_SALAO + f'/{id_manager}/agenda/{self.dia_atual}/{info_login["id_login"]}.json'
                link = self.LINK_SALAO + f'/{id_manager}/agenda/{self.dia_atual}/{id_user}.json'
                link_agenda_salao = self.LINK_SALAO + f'/{id_manager}/agenda_do_salao/{self.dia_atual}/{id_user}.json'


            requisicao = requests.delete(link)
            requisicao2 = requests.delete(link_agenda_salao)

            self.actualizar()
            self.popup.dismiss()
            Clock.schedule_once(self.box_dialog.dismiss, 5)

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def sum_hours_end_time(self,hours, time, *args):

        id_hours = datetime.strptime(hours,'%H:%M')

        horas , min = map(int, time.split(':'))
        delta = timedelta(hours=horas, minutes=min)

        soma = delta + id_hours

        return soma.strftime('%H:%M')

    def wait_blocked_schedule(self,id_button, id_schedule, hours, hours_second, client, *args):
        """
        Função para chamar a função "blocked_schedule" depois de um  tempo, só para mostrar que a tela esta sendo
        carregada
        :param id_button:
        :param id_schedule:
        :param hours:
        :param hours_second:
        :param client:
        :param args:
        :return:
        """
        Clock.schedule_once(partial(self.blocked_schedule,id_button, id_schedule, hours, hours_second, client, *args),2)

    def blocked_schedule(self,id_button, id_schedule, hours, hours_second, client, *args):
        """
        Sendo chamada pela função "wait_blocked_schedule"
        being called by function "wait_blocked_schedule"
        :param id_button:
        :param id_schedule:
        :param hours:
        :param hours_second:
        :param client:
        :param args:
        :return:
        """
        try:
            # id_manager_id_button = self.id_manager + f'{id_button}'
            horas_hoje = self.time_now()
            list_works = []
            list_ids_schedule = []
            link = ''

            # variable to infomation of schedule ######################
            list_id_marked = []
            link_info = ''
            free = ''
            second_free = ''
            list_comparate_hours = []
            list_second_hours = []

            # geting the id of Manager ##############################
            # name_id = self.get_id_diverse()
            if_manager = self.get_id_proficional()


            with open('info_login.json','r') as arquivo:
                info_user = json.load(arquivo)

            id_user = info_user['id_login']
            # id_log_id_button = id_user + f'{id_button}'
            id_log_id_button = id_user

            horas = hours
            valor = 0

            # Here is to know is have schedule marked ##############################################
            if if_manager['manager'] == "False":
                link_info = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.dia_atual}.json'
            elif if_manager['manager'] == "True":
                link_info = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.dia_atual}.json'

            try:
                requisicao_if_scheduled = requests.get(link_info)
                if_scheduled = requisicao_if_scheduled.json()

                # Geting the id marked on schedule ###
                for pos, info in enumerate(if_scheduled):
                    list_id_marked.append(info)

                    # The id of user recive more an number of position
                    id_log_id_button = id_user + f'{pos}'


                # Here getting the hours of marked ###
                for id_marked in list_id_marked:
                    list_comparate_hours.append(if_scheduled[id_marked]['id_horas'])

                    time_marked = self.sum_hours_end_time(if_scheduled[id_marked]['id_horas'],
                                                          if_scheduled[id_marked]['tempo'])
                    list_second_hours.append(time_marked)

                    if if_scheduled[id_marked]['id_horas'] < horas and time_marked > horas:
                        second_free = True
                        break
                free = horas in list_comparate_hours
            except TypeError:
                pass
            except requests.exceptions.ConnectionError:
                toast('Você não esta conectado a internet!')
            except:
                pass
            # ######################################################################################

            if if_manager['manager'] == "False":
                link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.dia_atual}/{id_log_id_button}.json'
            elif if_manager['manager'] == "True":
                link = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.dia_atual}/{id_log_id_button}.json'

            # Creating the schedule Here ##########################################################################
            info = f'{{"id_posicao":"{id_button}",' \
                   f'"id_horas":"{horas}",' \
                   f'"id_user":"{id_log_id_button}",' \
                   f'"tempo":"{self.space_temp}",' \
                   f'"valor":"{valor}",' \
                   f'"nome":"Reservado!",' \
                   f'"horas_agendamento": "{horas_hoje}",' \
                   f'"servicos":"{[]}"}}'

            if free or second_free:
                # toast('Desculpe mais alguem acabou de agendar esse horário!')
                bt = MDFlatButton(text='OK')
                dialog = MDDialog(title='"Aviso!"',
                                  text=f'Desculpe mais outra pessoa acabou de agendar esse horário! das {horas} até as {time_marked}',
                                  radius=[20, 7, 20, 7], buttons=[bt])

                bt.bind(on_release=dialog.dismiss)
                dialog.open()
            else:
                # Saved the schedule
                requisicao = requests.patch(link, data=info)


                # Here geting the schedule of Hall ########
                if if_manager['manager'] == "False":
                    link2 = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda_do_sala/{self.dia_atual}/{id_log_id_button}.json'
                elif if_manager['manager'] == "True":
                    link2 = f'{self.LINK_SALAO}/{self.id_manager}/agenda_do_salao/{self.dia_atual}/{id_log_id_button}.json'

                info2 = f'{{"agenda":"{id_log_id_button}"}}'

                requisicao2 = requests.patch(link2, data=info2)

                toast(f'Hora reservada!')

            if if_manager['manager'] == "False":
                # getting ids that are already scheduled ###########################################################################
                link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'
                requisicao_client_get = requests.get(link_cliente)
                requisicao_client_get_dic = requisicao_client_get.json()

                # list_ids_schedule receiver the ids what is in cloud ##############################################################
                if requisicao_client_get_dic != '':
                    list_ids_schedule.append(requisicao_client_get_dic)

                # list_ids_schedule receiver the id what go be schedule ############################################################
                list_ids_schedule.append(if_manager['id_user'])

                # Insert ids of schedule in user ###################################################################################
                link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'

                info = f'{{"ids_agendado":"{list_ids_schedule}" }}'

                requisicao_client = requests.patch(link_cliente, data=info)
            else:
                pass

            self.actualizar()
            try:
                Clock.schedule_once(self.box_dialog.dismiss, 2)
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_hours(self,id_button, id_schedule, hours, hours_second, time, client, *args):
        hours_dic = {}

        hours_dic['proficional'] = 'True'
        hours_dic['id_button'] = id_button
        hours_dic['id_schedule'] = id_schedule
        hours_dic['hours'] = hours
        hours_dic['hours_second'] = hours_second
        hours_dic['time'] = time
        hours_dic['client'] = client

        with open('infoscheduleclient.json','w') as arquivo:
            json.dump(hours_dic, arquivo, indent=2)
        MDApp.get_running_app().root.current = 'hoursschedule'

    def wait_inf_schedule_client(self, id_button, id_schedule, hours, hours_second, time, client, email, cpf, *args):
        self.load_widget()
        Clock.schedule_once(partial(self.inf_schedule_client, id_button, id_schedule, hours, hours_second, time, client, email, cpf, *args))

    def inf_schedule_client(self,id_button, id_schedule, hours, hours_second, time, client, email, cpf, *args, **kwargs):
        dic_info = {}

        dic_info['id_button'] = id_button
        dic_info['id_schedule'] = id_schedule
        dic_info['hours'] = hours
        dic_info['hours_second'] = hours_second
        dic_info['time'] = time
        dic_info['client'] = client
        dic_info['email'] = email
        dic_info['cpf'] = str(cpf)

        print(email)
        print(cpf)

        print(dic_info)

        with open('infoscheduleclient.json', 'w') as file:
            json.dump(dic_info, file, indent=2)

        MDApp.get_running_app().root.current = 'infoscheduleclient'

        try:
            self.popup.dismiss()
        except:
            pass

        try:
            Clock.schedule_once(self.box_dialog.dismiss, 3)
        except:
            pass

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard = self.previews)
        self.ids.grid_shedule.clear_widgets()
        self.ids.title_toobar.title = ''

    def return_schoice_schedule(self):
        MDApp.get_running_app().root.current = 'screenchoiceschedule'


class HoursSchedule(Screen):

    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'
    def __init__(self,hours='', **kwargs):
        super().__init__(**kwargs)
        # Clock.schedule_once(self.get_works, 2)
        self.semana = datetime.today().isoweekday()
        self.hours = hours
        self.id_manager = self.get_manager()

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.previews)

        try:
            with open('infoscheduleclient.json', 'r') as arquivo:
                horas = json.load(arquivo)
            self.ids.hours.text = horas['hours']
        except FileNotFoundError:
            pass
        try:
            self.ids.categorie.add_widget(MDSpinner(size_hint=(None,None,), size=('46dp','46dp'),pos_hint={'center_x':.5,'center_y':.1}))
            Clock.schedule_once(self.get_works, 3)
            self.includ_color_select()
            self.soma_hours_values()

            self.valid_button_save()
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def previews(self, windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'viewshedule'
        else:
            pass
        return True


    def valid_button_save(self):
        with open('select_works.json', 'r') as arquivo:
            my_select = json.load(arquivo)

        if my_select == []:
            self.ids.card_save.md_bg_color = 1, 0, 0, .1
            self.ids.card_save.unbind(on_release=self.save_scheduleing)
            self.ids.card_save.bind(on_release=self.nada)
        else:
            pass
        self.ids.card_save.unbind(on_release=self.nada)

    def time_now(self):
        h = datetime.today().hour
        mim = datetime.today().minute
        horas = f'{str(h).zfill(2)}:{str(mim).zfill(2)}'

        return horas

    def on_leave(self, *args):
        Window.unbind(on_keyboard = self.previews)
        self.ids.categorie.clear_widgets()

    def get_manager(self, *args):
        try:
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()
            for id in requisicao_dic:
                return id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_id_diverse(self):
        if_manager = {}

        with open('write_id_manager.json','r') as arquivo:
            if_manager = json.load(arquivo)
        return if_manager

# Consert the endpoint this function ?????????????????????????????
    def get_works(self,*args):
        self.ids.categorie.clear_widgets()
        try:
            lista = []
            lista_name = []
            lista_color = []
            socio_or_manager = False
            self.id_diverse = self.get_id_diverse()
            link = ''

            # LINK DATA BASE
            if self.id_diverse['manager'] == "False":
                link = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + self.id_diverse["id_user"] + '.json'
                socio_or_manager = True
            elif self.id_diverse['manager'] == "True":
                link = self.LINK_SALAO + '/' + self.id_manager + '.json'
                socio_or_manager = False

            requisicao = requests.get(link)

            try:
                requisicao_dic = requisicao.json()

                for get_id_work in requisicao_dic['servicos']:
                    lista.append(get_id_work)

                try:
                    with open('select_works.json','r') as arquivo_color:
                        lista_color = json.load(arquivo_color)
                except:
                    pass

            # LINK DATA BASE
                for num, id_work in enumerate(lista):

                    if socio_or_manager:
                        link_id = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + self.id_diverse["id_user"] + '/servicos/' + id_work + '.json'
                    else:
                        link_id = self.LINK_SALAO + '/' + self.id_manager + '/' + 'servicos' + '/' + id_work + '.json'

                    works = requests.get(link_id)
                    works_dic = works.json()

                    servico = works_dic['nome_servico']
                    tempo = works_dic['tempo']
                    valor = works_dic['valor']


                    for iten in lista_color:
                        lista_name.append(iten['servico'])

                    if servico in lista_name:
                        self.ids.categorie.add_widget(CategoriesWork(str(servico), str(tempo), str(float(valor)).replace('.',','), md_bg_color=[0.13, 0.53, 0.95,.2]))
                    else:
                        self.ids.categorie.add_widget(CategoriesWork(str(servico), str(tempo), str(float(valor)).replace('.',',')))
            except:
                try:
                    if socio_or_manager:
                        work_socio = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + self.id_diverse["id_user"] + '/' + id_work + '.json'
                    else:
                        work_socio = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + id_work + '.json'
                except:
                    pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def changer_color(self,eu,servico,*args):
        color = eu.md_bg_color
        dic = {}
        lista = []

        dic['servico'] = eu.servico
        dic['tempo'] = eu.tempo
        dic['valor'] = eu.valor

        if color == [0.61, 0.60, 0.58,.7]:
            eu.md_bg_color = 0.13, 0.53, 0.95,.5

            try:
                with open('select_works.json', 'r') as arquivo:
                    my_select = json.load(arquivo)
                    lista = (my_select)
            except:
               pass

            lista.append(dic)

            with open('select_works.json','w') as arquivo:
                my_select = json.dump(lista, arquivo, indent=2)

            self.ids.work_select.clear_widgets()
            for work in lista:
                self.ids.work_select.add_widget(MyBoxCategorieLabel(work['servico'].title(), work['tempo'].title(), work['valor'].title()))
            self.soma_hours_values(eu)

        else:
            to_delet = []
            eu.md_bg_color = 0.61, 0.60, 0.58,.7

            # Geting the info in file ###################
            with open('select_works.json','r') as arquivo:
                to_delet = json.load(arquivo)

            for num, item in enumerate(to_delet):
                if servico == item['servico']:
                    del(to_delet[num])

            # save info in file ##########################
            with open('select_works.json', 'w') as arquivo:
                json.dump(to_delet, arquivo, indent=2)

            # includ the color in button #################
            self.includ_color_select()

            # do the sum of hours and values #############
            self.soma_hours_values(eu)

        if self.ids.work_select.children == []:
            self.ids.card_save.md_bg_color = 1, 0, 0, .1
            self.ids.card_save.unbind(on_release=self.save_scheduleing)
            self.ids.card_save.bind(on_release=self.nada)

    def includ_color_select(self,*args):

        # mdcard = MDCard(size_hint_y=(None), height=('20dp'))

        lista = []
        self.ids.work_select.clear_widgets()

        try:
            with open('select_works.json','r') as arquivo:
                lista = json.load(arquivo)
        except:
            pass
        for work in lista:
            self.ids.categorie.children.md_bg_color = 0.13, 0.53, 0.95,1
            self.ids.work_select.add_widget(MyBoxCategorieLabel(work['servico'].title(), work['tempo'].title(), work['valor'].title()))

    def soma_hours_values(self, eu=''):
        list_info = []
        # try:
        with open('select_works.json','r') as arquivo:
            list_info = json.load(arquivo)

        tempo = 0
        hours = 0
        minute = 0
        valor = 0

        # Formating and sum the hours #####################
        for h in list_info:
            h, m = map(int,h['tempo'].split(':'))
            hours += h
            minute += m

        # here is for the minutes not to exceed 59 ########
            if minute >= 60:
                minute = minute % 60
                hours += 1

        # Sum the values ##################################
        for v in list_info:
            valor += float(str(v['valor']).replace(',','.'))


        # Geting the hours
        tempo = f'{str(hours).zfill(2)}:{str(minute).zfill(2)}'

        self.ids.time.text = str(tempo)
        self.ids.valor.text = str(valor).replace('.',',')

        self.hours_limit(tempo)

    def hours_limit(self, tempo, *args):

        lista_pos = ''

        with open('infoscheduleclient.json','r') as file_info:
            info = json.load(file_info)

        with open('list_content.json','r') as lista:
            lista_content = json.load(lista)

        # hours of schedule
        h = datetime.strptime(info['hours'],'%H:%M')

        hora_tempo, minuto_tempo = map(int,tempo.split(':'))
        delta_time = timedelta(hours=hora_tempo, minutes=minuto_tempo)
        soma_horas = h + delta_time

        posicao = info['id_button']
        hora = info['hours']
        try:
            lista_pos = lista_content[int(posicao)]
        except:
            pass

        #Here return one boolian ##############################
        boolian = bool(soma_horas.strftime('%H:%M') > lista_pos)

        #if lista_pos is empty  then boolian receive False ####
        if lista_pos == '':

            for field in lista_content[int(posicao):]:
                boolian = bool(soma_horas.strftime('%H:%M') > str(field))
                if field == '':
                    boolian = False
                else:
                    boolian = bool(soma_horas.strftime('%H:%M') > str(field))
                    # if the schedule is bigger than the next schedule then stop of througn list
                    if boolian:
                        break

        if boolian:
            self.ids.card_save.md_bg_color = 1,0,0,.1
            self.ids.card_save.unbind(on_release = self.save_scheduleing)
            self.ids.card_save.bind(on_release = self.disable_release)
            toast('Excedeu o horário do proximo agendamento escolha outro horário ou outro Proficional!')
        elif boolian == False:
            self.ids.card_save.unbind(on_release = self.disable_release)
            self.ids.card_save.md_bg_color = 0.13, 0.53, 0.95,1
            self.ids.card_save.bind(on_release = self.save_scheduleing)

    def check_time(self, *args):
        pass

    def get_name_user(self, info_user, *args):
        # LINK_DATA_NAME = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}.json'
        # name = requests.get(LINK_DATA_NAME)
        # name_dic = name.json()

        info_dic = {}

        try:
            # if info_user['manager'] == 'True':
            try:
                link = f'{self.LINK_SALAO}/{info_user["id_login"]}.json'

                requisicao = requests.get(link)
                info_dic = requisicao.json()

            # elif info_user['manager'] == 'False':
            except:
                id_manager = self.get_manager()
                link = f'{self.LINK_SALAO}/{id_manager}/socios/{info_user["id_login"]}.json'

                requisicao = requests.get(link)
                info_dic = requisicao.json()

            return info_dic['nome']
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def nada(self,*args):
        toast('Selecione o tipo de serviço!')

    def disable_release(self,*args):
        toast('Excedeu o horário do proximo agendamento escolha outro horário ou outro Proficional!', length_long=False)

    def sum_hours_end_time(self,hours, time, *args):

        id_hours = datetime.strptime(hours,'%H:%M')

        horas , min = map(int, time.split(':'))
        delta = timedelta(hours=horas, minutes=min)

        soma = delta + id_hours

        print(soma.strftime('%H:%M'))
        return soma.strftime('%H:%M')

    def save_scheduleing(self, *args):
        try:
            horas_hoje = self.time_now()
            list_works = []
            list_ids_schedule = []
            link = ''

            # variable to infomation of schedule ######################
            list_id_marked = []
            link_info = ''
            second_free = ''
            free = ''
            list_comparate_hours = []
            list_second_hours = []

            # geting the id of Manager ##############################
            # name_id = self.get_id_diverse()
            if_manager = self.get_id_diverse()

            # geting the info of work ###############################
            with open('select_works.json','r') as select_work:
                list_works = json.load(select_work)

            with open('info_login.json','r') as arquivo:
                info_user = json.load(arquivo)

            with open('infoscheduleclient.json', 'r') as file_info:
                id_pos = json.load(file_info)


            id_user = info_user['id_login']
            nome = self.get_name_user(info_user)
            horas = self.ids.hours.text
            tempo = self.ids.time.text
            valor = self.ids.valor.text

            # Here is to know is have schedule marked ##############################################
            if if_manager['manager'] == "False":
                link_info = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.semana}.json'
            elif if_manager['manager'] == "True":
                link_info = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.semana}.json'

            try:
                requisicao_if_scheduled = requests.get(link_info)
                if_scheduled = requisicao_if_scheduled.json()

                # Geting the id marked on schedule ###
                for info in if_scheduled:
                    list_id_marked.append(info)

                # Here getting the hours of marked ###
                for id_marked in list_id_marked:
                    list_comparate_hours.append(if_scheduled[id_marked]['id_horas'])

                    time_marked = self.sum_hours_end_time(if_scheduled[id_marked]['id_horas'],
                                                          if_scheduled[id_marked]['tempo'])
                    list_second_hours.append(time_marked)

                    if if_scheduled[id_marked]['id_horas'] < horas and time_marked > horas:
                        second_free = True
                        break
                free = horas in list_comparate_hours
            except requests.exceptions.ConnectionError:
                toast('Você não esta conectado a internet!')
            except TypeError:
                pass
            # ######################################################################################


            if if_manager['manager'] == "False":
                link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.semana}/{id_user}.json'
            elif if_manager['manager'] == "True":
                link = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.semana}/{id_user}.json'

            # Creating the schedule Here ##########################################################################
            info = f'{{"id_posicao":"{id_pos["id_button"]}",' \
                   f'"id_horas":"{horas}",' \
                   f'"id_user":"{id_user}",' \
                   f'"tempo":"{tempo}",' \
                   f'"valor":"{valor}",' \
                   f'"nome":"{nome}",'\
                   f'"horas_agendamento": "{horas_hoje}",'\
                   f'"servicos":"{list_works}"}}'

            if free or second_free:
                # toast('Desculpe mais alguem acabou de agendar esse horário!')
                bt = MDFlatButton(text='OK')
                dialog = MDDialog(title='"Aviso!"',
                                  text=f'Desculpe mais outra pessoa acabou de agendar esse horário! das {horas} até as {time_marked}',
                                  radius=[20, 7, 20, 7], buttons=[bt])

                bt.bind(on_release=dialog.dismiss)
                dialog.open()
            else:
                requisicao = requests.patch(link, data=info)
                toast(f'Agendamento Marcado!')

            if if_manager['manager'] == "False":
                # getting ids that are already scheduled ###########################################################################
                    link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'
                    requisicao_client_get = requests.get(link_cliente)
                    requisicao_client_get_dic = requisicao_client_get.json()

                # list_ids_schedule receiver the ids what is in cloud ##############################################################
                    if requisicao_client_get_dic != '':
                        list_ids_schedule.append(requisicao_client_get_dic)

                # list_ids_schedule receiver the id what go be schedule ############################################################
                    list_ids_schedule.append(if_manager['id_user'])

                # Insert ids of schedule in user ###################################################################################
                    link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'

                    info = f'{{"ids_agendado":"{list_ids_schedule}" }}'

                    requisicao_client = requests.patch(link_cliente, data=info)
            else:
                pass

        # Clearing file "select_work" after of save ########################################################################
            with open('select_works.json','w') as file:
                json.dump([], file)
            MDApp.get_running_app().root.current = 'viewshedule'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')


class InfoScheduleClient(Screen):

    LINK_DATA_BASE = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.manager_main = self.id_manager()

        self.day_actual = datetime.today().isoweekday()

    def on_pre_enter(self):
        Window.bind(on_keyboard=self.preview)
        self.inf_schedule_client()

    def preview(self,windows,key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'viewshedule'
        return True

    def on_leave(self):
        Window.unbind(on_keyboard=self.preview)
        self.ids.img_block.source = ''
        self.ids.label_block.text = ''

    def id_manager(self):

        manager = ''

        link_work = self.LINK_DATA_BASE + '.json'
        requisicao = requests.get(link_work)
        requisicao_dic = requisicao.json()

        for id in requisicao_dic:
            manager = id
        return manager

    def inf_schedule_client(self):
        dic_inf = {}
        with open('infoscheduleclient.json', 'r') as file:
            info_schedule = json.load(file)

        id_client = info_schedule['id_schedule']
        cpf = info_schedule['cpf']

        self.ids.nome.text = f'[size=20][color=#9B9894]Nome[/color][/size]\n[color=#6B0A00]{info_schedule["client"]}[/color]'
        self.ids.hours.text = f'[b]Agendado as[/b] [color=#6B0A00]{info_schedule["hours"]}[/color] hs'
        self.ids.hours_second.text = f'[b]Termino do serviço[/b] [color=#6B0A00]{info_schedule["hours_second"]}[/color] hs'
        self.ids.time.text = f'[b]Tempo de serviço[/b] [color=#6B0A00]{info_schedule["time"]}[/color] hs'
        self.ids.email.text = str(info_schedule['email'])
        self.ids.cpf.text = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

        self.work(id_client)
        self.info_cliente_and_cancel(id_client)

    def info_cliente_and_cancel(self,id_client,*args):

        link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        try:
            self.ids.quant_cancelada.text = str(requisicao_dic['quant_cancelado'])

            # Here change the color and the number of quant cancel #########################################################
            if int(requisicao_dic['quant_cancelado']) == 0:
                self.ids.color_quant.md_bg_color = [0,1,0,1]
                self.ids.quant_cancelada.color = [0,1,0,1]
            elif int(requisicao_dic['quant_cancelado']) == 1:
                self.ids.color_quant.md_bg_color = 1.00, 0.65, 0.16,1
                self.ids.quant_cancelada.color = 1.00, 0.65, 0.16,1
            elif int(requisicao_dic['quant_cancelado']) == 2:
                self.ids.color_quant.md_bg_color = 1.00, 0.33, 0.03,1
                self.ids.quant_cancelada.color = 1.00, 0.33, 0.03,1
            elif int(requisicao_dic['quant_cancelado']) >= 3:
                self.ids.color_quant.md_bg_color = 1,0,0,1
                self.ids.quant_cancelada.color = 1,0,0,1

            # Get if go cancel or not ######################################################################################
            if requisicao_dic['bloqueado'] == 'True':
                self.ids.img_block.source = 'images/bloqueado.png'
                self.ids.label_block.text = 'Cliente bloqueado!'
            else:
                self.ids.img_block.source = ''
                self.ids.label_block.text = ''
        except:
            pass

    def done(self):
        try:
            cancelada = int(self.ids.quant_cancelada.text)
            cancelada  = 0

            with open('infoscheduleclient.json', 'r') as file:
                info_schedule = json.load(file)
            id_client = info_schedule['id_schedule']


            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

            info = f'{{"quant_cancelado":"{cancelada}"}}'
            requisicao = requests.patch(link, data=info)

            self.ids.quant_cancelada.text = str(cancelada)

            self.ids.color_quant.md_bg_color = [0, 1, 0, 1]
            self.ids.quant_cancelada.color = [0, 1, 0, 1]

        except:
            pass

    def client_missed(self):

        try:
            cancelada = int(self.ids.quant_cancelada.text)
            cancelada += 1

            with open('infoscheduleclient.json', 'r') as file:
                info_schedule = json.load(file)
            id_client = info_schedule['id_schedule']


            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

            info = f'{{"quant_cancelado":"{cancelada}"}}'
            requisicao = requests.patch(link, data=info)

            self.ids.quant_cancelada.text = str(cancelada)

            if cancelada == 1:
                self.ids.color_quant.md_bg_color = 1.00, 0.65, 0.16,1
                self.ids.quant_cancelada.color = 1.00, 0.65, 0.16,1
            elif cancelada == 2:
                self.ids.color_quant.md_bg_color = 1.00, 0.33, 0.03,1
                self.ids.quant_cancelada.color = 1.00, 0.33, 0.03,1
            elif cancelada >= 3:
                self.ids.color_quant.md_bg_color = 1,0,0,1
                self.ids.quant_cancelada.color = 1,0,0,1
        except:
            pass

    def block_client(self):
        with open('infoscheduleclient.json', 'r') as file:
            info_schedule = json.load(file)
        id_client = info_schedule['id_schedule']


        link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

        info = f'{{"bloqueado":"True"}}'
        requisicao = requests.patch(link, data=info)

        self.ids.img_block.source = 'images/bloqueado.png'
        self.ids.label_block.text = 'Cliente bloqueado!'

    def popup_leave(self, *args, **kwargs):

        if self.ids.img_block.source != '':
            box_content = MDBoxLayout(orientation='vertical',spacing='5')
            box_bt = MDBoxLayout(spacing='10dp', padding='5dp')

            pop = Popup(title='Liberar cliente?', size_hint=(None, None),
                        size=('240dp', '200dp'), content=box_content)

            bt_sim = Button(text='Sim!', background_color=(0.13, 0.53, 0.95,1),on_release=pop.dismiss)
            bt_nao = Button(text='Não!',color=(0,0,0,1),background_color=(0.13, 0.53, 0.95,1), on_release=pop.dismiss)

            box_bt.add_widget(bt_sim)
            box_bt.add_widget(bt_nao)

            image = Image(source='images/atencao.png')

            box_content.add_widget(image)
            box_content.add_widget(box_bt)

            bt_sim.bind(on_press=self.leave_client)

            pop.open()
        else:
            pass

    def leave_client(self, *args):

        with open('infoscheduleclient.json', 'r') as file:
            info_schedule = json.load(file)
        id_client = info_schedule['id_schedule']

        link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

        info = f'{{"bloqueado":"False"}}'
        requisicao = requests.patch(link, data=info)

        self.ids.img_block.source = ''
        self.ids.label_block.text = ''

    def work(self, id_client):
        self.ids.box_work.clear_widgets()

        list_string = ''
        list_work = []
        valor = 0

        with open('write_id_manager.json','r') as file:
            id_worker = json.load(file)

        if id_worker['manager'] == 'True':
            link_work = self.LINK_DATA_BASE + f'/{id_worker["id_user"]}/agenda/{self.day_actual}/{id_client}/servicos.json'
            requisicao = requests.get(link_work)
            requisicao_dic = requisicao.json()

            list_string = requisicao_dic

        elif id_worker['manager'] == 'False':

            manager_main = self.manager_main

            link_work = self.LINK_DATA_BASE + f'/{manager_main}/socios/{id_worker["id_user"]}/agenda/{self.day_actual}/{id_client}/servicos.json'
            requisicao = requests.get(link_work)
            requisicao_dic = requisicao.json()

            list_string = requisicao_dic
        try:
            # "eval" To transform str in dictionary ##################################################################
            list_work = eval(list_string)

            for enum, work in enumerate(list_work):
                valor += float(work['valor'].replace(',','.'))
                myboxcategorie = MyBoxCategorie('',work['servico'], work['tempo'], str(float(str(work['valor']).replace(',','.'))).replace('.',','))

                myboxcategorie.bind(on_release=self.nada_pass)
                self.ids.box_work.add_widget(myboxcategorie)
        except TypeError:
            pass

        self.ids.id_valor.text = str(valor).replace('.',',') + ' [size=15][b]R$[/b][/size]'

    def nada_pass(selfm, *args):
        """
        Function with not return none
        :return:
        """
        pass

    def return_schedule(self):
        MDApp.get_running_app().root.current = 'viewshedule'


class RegisterOfBox(Screen):

    def return_home(self):
        MDApp.get_running_app().root.current = 'homepage'


class AgendamentoApp(MDApp):

    Builder.load_string(open('agendamento_vitor.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/my_box_socio.kv', encoding='utf-8').read())
    Builder.load_string(open('file_kv/choice_schedule.kv', encoding='utf-8').read())


    def build(self):

        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()