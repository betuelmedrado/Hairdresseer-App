

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton, MDFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

# importando firebase
import requests
import json

from functools import partial
from datetime import datetime, timedelta

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
            return id

    def not_can_client(self):
        lista_info_ids = []
        ID_MANAGER = ''

        # Geting id of manager #########################################################################################
        LINK_MANAGER = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'
        requisicao_manager = requests.get(LINK_MANAGER)
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

    def login(self, *args):

        lista_info_ids =  self.not_can_client()

        print(lista_info_ids)

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
            if requisicao_dic['localId'] in lista_info_ids:
                with open('refreshtoken.json','w') as file:
                    json.dump(requisicao_dic['refreshToken'], file)
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

                Clock.schedule_once(self.load_screen, 1)
            else:
                print('usuario não encontrado')
        except:
            pass

        # print(requisicao_dic)

    def load_screen(self, *args):
        MDApp.get_running_app().root.current = 'homepage'

    def creat_files(self):

        try:
            with open('write_id_manager.json', 'r') as arquivo:
                json.load(arquivo)
        except FileNotFoundError:
            with open('write_id_manager.json', 'w') as arquivo:
                json.dump('',arquivo)

    def on_pre_enter(self, *args):
        self.load_refresh()
        self.creat_files()


class CreatProfile(Screen):

    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.LINK_DATABASE_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

        self.id_manager = self.get_manager()

    def get_manager(self):
        requisicao = requests.get(self.LINK_DATABASE_SALAO + '.json')
        requisicao_dic = requisicao.json()
        for id in requisicao_dic:
            return id

    def on_pre_enter(self, *args):

        verification = self.verification_if_manger()

        if verification:
            pass
        else:
            self.ids.enter_as_socio.text = 'Cadastro de Sócio'

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

    #  Here I will change to change the id
    def creat_profile(self,id_token, localid, refreshtoken, *args):
        LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{localid}.json'

        nome = self.ids.nome.text

        info = f'{{"nome":"{nome}",' \
               f'"manager":True}}'

        requisicao = requests.patch(LINK_SALAO, data=info)
        self.ids.warning.text = 'Perfil creado com sucesso!'

        with open('refreshtoken.json','w') as file:
            json.dump(refreshtoken, file)

    def creat_socio(self, id_token, localid, refreshtoken, *args):
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
                    if self.verification_if_manger():
                        self.creat_socio(idtoken, localid, refreshtoken)
                        print('socio')
                    else:
                        self.creat_profile(idtoken, localid, refreshtoken)
                        print('managerr')

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


class HomePage(Screen):

    def return_login(self):
        with open('refreshtoken.json','w') as file:
            json.dump('',file)

        MDApp.get_running_app().root.current = 'loginmanager'


class ManagerProfile(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'
    LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self,*args,**kwargs):
        super().__init__(**kwargs)

        self.id_manager = self.get_id_manager()

    def on_pre_enter(self, *args):
        self.creat_profile()
        self.insert_hours()
        Clock.schedule_once(self.get_socios,2)
        Clock.schedule_once(self.infill,3)

    def get_id_manager(self, *args):
        requisicao = requests.get(self.LINK_SALAO + '.json')
        requisicao_dic = requisicao.json()

        for id in requisicao_dic:
            return id

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
        self.ids.hours.clear_widgets()
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
        except AttributeError:
            toast('escolha o campo a ser preenchido! Entrada ou Saida', duration=5)

    def save_data(self,*args):

        with open('is_manager_or_socio.json','r') as file:
            if_manager = json.load(file)

        if if_manager == 'socio':
            LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}.json'

            self.entrada = self.ids.entry.text
            self.saida = self.ids.exit.text
            self.space_tempo = self.ids.space_temp.text

            get_requisicao = requests.get(LINK_BASE_SALAO)


            info = f'{{"entrada":"{self.entrada}",\
                     "saida": "{self.saida}",\
                     "space_temp":"{self.space_tempo}",\
                     "agenda":"" }}'

            requisica = requests.patch(LINK_BASE_SALAO, info)
            toast('Tabela de horas salva com sucesso!', duration=4)

        elif if_manager == 'manager':

            LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}.json'

            self.entrada = self.ids.entry.text
            self.saida = self.ids.exit.text
            self.space_tempo = self.ids.space_temp.text

            info = f'{{"entrada":"{self.entrada}",\
                                 "saida": "{self.saida}",\
                                 "space_temp":"{self.space_tempo}"}}'

            requisica = requests.patch(LINK_BASE_SALAO, info)
            toast('Tabela de horas salva com sucesso!', duration=4)

    def save_servicos(self,*args):

        nome_servico = self.ids.nome_servico.text.upper()
        tempo = self.ids.tempo.text
        valor = self.ids.valor.text

        with open('is_manager_or_socio.json', 'r') as file:
            is_manager = json.load(file)

        if nome_servico != '' and tempo != '' and valor != '':

            if is_manager == 'socio':
                LINK_BASE_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos.json'

                info = f'{{"nome_servico":"{nome_servico}",' \
                       f'"tempo":"{tempo}",' \
                       f'"valor":"{valor}",' \
                       f'"servicos":"",' \
                       f'"agenda":""}}'

                requisicao = requests.post(LINK_BASE_SALAO, info)
                toast('Categoria criada', duration=4)

                self.infill()

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
                toast('Categoria criada', duration=4)

                self.infill()

                self.ids.nome_servico.text = ''
                self.ids.tempo.text = ''
                self.ids.valor.text = ''
        else:
            toast('Precisa de todas as informções de serviços!', duration=4)

    def infill(self, *args):
        socio_ou_gerente = False
        requisicao_get = ''

        with open('is_manager_or_socio.json','r') as file:
            is_manager = json.load(file)

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

                self.ids.categorie.add_widget(MyBoxCategorie(id, nome_servico,tempo,valor))
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

    # def edit(self, id_work='', tempo='', valor='', *args, **kwargs):
    #
    #     print(tempo)
    #     print(valor)
    #
    #     requisicao_get = ''
    #
    #     with open('is_manager_or_socio.json', 'r') as file:
    #         is_manager = json.load(file)
    #
    #     info = f'{{"tempo":"{tempo}",' \
    #            f'" valor":"{valor}"}}'
    #
    #     # Para saber si quem esta acessando é o socio ou o gerente #####################################################
    #     # if is_manager == 'socio':
    #     #     LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{self.user_id}/servicos{id_work}.json'
    #     #     requisicao_get = requests.patch(LINK_CATEGORIA, data=info)
    #     #
    #     # elif is_manager == 'manager':
    #     #     LINK_CATEGORIA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.user_id}/servicos/{id_work}.json'
    #     #     requisicao_get = requests.patch(LINK_CATEGORIA, data=info)
    #     #
    #     # self.infill()

    # def pop_alteration(self,id_work, servico, tempo, valor, *args, **kwargs):
    #     box_main = MDBoxLayout(orientation='vertical',md_bg_color=([1,1,1,1]),radius=(5,5,5,5))
    #     box_widgets = MDBoxLayout(orientation='vertical', padding='15dp',spacing='10')
    #
    #     box_work = MDBoxLayout(orientation='vertical')
    #     box_time = MDBoxLayout(orientation='vertical')
    #     box_values = MDBoxLayout(orientation='vertical')
    #     box_buttons = MDBoxLayout(size_hint_y=None,height=('30dp'),spacing=8, padding=8)
    #
    #     # Inserting the widget in box of work #########################################################################
    #     label_work = MDLabel(text='Servico', size_hint_y=None,height='15dp')
    #     text_work = TextInput(text=servico,size_hint_y=None,height='30dp')
    #     box_work.add_widget(label_work)
    #     box_work.add_widget(text_work)
    #
    #     # Inserting the widget in box of time #########################################################################
    #     label_time = MDLabel(text='Tempo',size_hint_y=None,height='15dp')
    #     text_time = TextInput(text=tempo,size_hint_y=None,height='30dp')
    #     box_time.add_widget(label_time)
    #     box_time.add_widget(text_time)
    #
    #     # Inserting the widget in box of values #########################################################################
    #     label_values = MDLabel(text='Valor: R$',size_hint_y=None,height='15dp')
    #     text_values = TextInput(text=valor,size_hint_y=None,height='30dp')
    #     box_values.add_widget(label_values)
    #     box_values.add_widget(text_values)
    #
    #
    #     popup = Popup(title_color=(1, 1, 1, .0), separator_color=([0,1,1,1]), background_color=([1, 1, 1, 0]),
    #                   size_hint=(None, None), size=('240dp', '400dp'),
    #                   content=box_main)
    #
    #     box_widgets.add_widget(box_work)
    #     box_widgets.add_widget(box_time)
    #     box_widgets.add_widget(box_values)
    #     box_widgets.add_widget(Widget(size_hint_y=None, height='30dp'))
    #
    #     tempos = text_time.text
    #     valors = text_values.text
    #
    #     bt_edit = MDRaisedButton(text='Editar', text_color=(0,0,0,1) ,md_bg_color=(0,1,1,1), on_release=partial(self.edit, id_work, tempos, valors))
    #     bt_exclud = MDRaisedButton(text='Excluir', md_bg_color=(0,1,1,1))
    #     bt_exit = MDFlatButton(text='sair', on_release=popup.dismiss)
    #
    #     box_buttons.add_widget(bt_edit)
    #     box_buttons.add_widget(bt_exclud)
    #     box_buttons.add_widget(bt_exit)
    #
    #     box_main.add_widget(box_widgets)
    #     box_main.add_widget(box_buttons)
    #
    #     popup.open()

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

        except:
            toast('Deu Algum erro! não foi excluido ')


class MyButtonCard(MDCard):
    pass

class MyBoxCategorie(MDCard):

    def __init__(self,id_work='', servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)
        self.id_work = id_work
        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class MyBoxSocio(MDCard):
    def __init__(self,name, **kwargs):
        super().__init__(**kwargs)
        self.nome = name


class Table_shedule(MDBoxLayout):

    def __init__(self,id_button='', id_schedule='',hours='', hours_second='', time='', client='',**kwargs):
        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.hours_second = hours_second
        self.time = time
        self.client = str(client)

class TableEnpty(MDBoxLayout):

    def __init__(self,id_button='', id_schedule='',hours='', hours_second='', time='', client='',**kwargs):
        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.hours_second = hours_second
        self.time = time
        self.client = str(client)

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

        self.id_manager =  self.get_id_manager()
        Clock.schedule_once(self.get_info, 1)

    # Geting id of manager ########################################################
    def get_id_manager(self):
        requisicao = requests.get(self.LINK_DATABASE_SALAO + '.json')
        requisicao_dic = requisicao.json()

        for id in requisicao_dic:
            return id

    def get_info(self, *args):

        self.ids.choice_schedule.clear_widgets()

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

    # def on_pre_enter(self, *args):
    #     self.get_info()

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'


class ViewSchedule(Screen):
    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        # self.LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'

        self.LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao'
        requisicao = requests.get(self.LINK_SALAO + '.json')
        requisicao_dic = requisicao.json()

        # Getting the id of manager ####################################################################################
        for id in requisicao_dic:
            self.id_manager = id

    def get_id_proficional(self, *args):
        dic_information = {}

        with open('write_id_manager.json', 'r') as arquivo:
            dic_informing = json.load(arquivo)
        return dic_informing

    def log_aut(self,*args):
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

    def info_entrace_salao(self, *args):

        id_manager = self.get_id_proficional()
        lista_info = []

        # try:
            # information socio ############################################################################################
        if id_manager["manager"] == 'False':
            # Here if not manager then get the socio #########################################################################
            LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager["id_user"]}.json'
            requisicao = requests.get(LINK_SALAO)
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']

            self.entrada = requisicao_dic['entrada']

            self.saida = requisicao_dic['saida']

            self.space_temp = requisicao_dic['space_temp']

            self.ids.title_toobar.title = f'Agenda {str(nome)}'
            try:
                for id_agenda in requisicao_dic['agenda']:
                    LINK_SCHEDULE = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager["id_user"]}/agenda/{id_agenda}.json'
                    requisicao_schedule = requests.get(LINK_SCHEDULE)
                    requisicao_schedule_dic = requisicao_schedule.json()
                    lista_info.append(requisicao_schedule_dic)
                return lista_info
            except:
                return lista_info

        elif id_manager["manager"] == 'True':

            # Here to geting the id of manager to get schedule #######################################
            requisicao = requests.get(self.LINK_SALAO + f'/{self.id_manager}.json')
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']

            self.entrada = requisicao_dic['entrada']

            self.saida = requisicao_dic['saida']

            self.space_temp = requisicao_dic['space_temp']

            self.ids.title_toobar.title = f'Agenda {str(nome)}'

            try:
                for id_agenda in requisicao_dic['agenda']:
                    LINK_SCHEDULE = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/agenda/{id_agenda}.json'
                    requisicao_schedule = requests.get(LINK_SCHEDULE)
                    requisicao_schedule_dic = requisicao_schedule.json()

                    lista_info.append(requisicao_schedule_dic)
                return lista_info
            except:
                return lista_info
        # except:
        #     pass

        #information socio ############################################################################################
        # except TypeError:
        #
        #         # Here if not manager then get the socio #########################################################################
        #     LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager}.json'
        #     requisicao = requests.get(LINK_SALAO)
        #     requisicao_dic = requisicao.json()
        #     nome = requisicao_dic['nome']
        #
        #     self.entrada = requisicao_dic['entrada']
        #
        #     self.saida = requisicao_dic['saida']
        #
        #     self.space_temp = requisicao_dic['space_temp']
        #
        #     self.ids.title_toobar.title = f'Agenda {str(nome)}'
        #
        #     for id_agenda in requisicao_dic['agenda']:
        #         LINK_SCHEDULE = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager}/nome.json'
        #         requisicao_schedule = requests.get(LINK_SCHEDULE)
        #         requisicao_schedule_dic = requisicao_schedule.json()
        #         lista_info.append(requisicao_schedule_dic)
        #         print(requisicao_schedule_dic)
        #     return lista_info

    def actualizar(self, *args):

        # try:
        # get user id ##################################################################################################
        user_id = self.log_aut()
        lista_info = self.info_entrace_salao()

        print('actualizar ',lista_info)

        list_content = []
        entrada = self.entrada
        saida = self.saida
        tempo = self.space_temp

        # variable to show the first schedule if it is scheduled, is implemented in "for range", I do this to display the correct schedule table
        # variável para mostrar o primeiro agendamento se for agendado, está implementado no "for range", Eu faço isso para exibir a tabela de agendamento correta
        ranger_init = 0
        ranger_last = int(tempo[3:])

        # lista = ['']
        block = False
        permition_to_sum = True

        # To conting the position of schedule to verification of next schedule
        cont = 00

        self.ids.grid_shedule.clear_widgets()

        # try:
        while entrada[:2] < saida[:2]:
            for num, agenda in enumerate(lista_info):
                try:
                    if entrada[:2] == lista_info[num]['id_horas'][:2]:
                        for mim in range(ranger_init, ranger_last):
                            # conparing the minutes ###################################################################################
                            if str(mim).zfill(2) == lista_info[num]['id_horas'][3:]:
                                # id_hours = lista_info[num]['id_horas']
                                # entry = datetime.strptime(entrada,'%H:%M')
                                ent = int(str(entrada[:2]).zfill(2))
                                entrada = f'{str(ent).zfill(2)}:{str(mim).zfill(2)}'

                                entry = datetime.strptime(entrada, '%H:%M')
                                temp = lista_info[num]['tempo']
                                hours, minute = map(int, temp.split(':'))
                                delta_temp = timedelta(hours=hours, minutes=minute)
                                soma_horas = entry + delta_temp

                                if user_id == lista_info[num]['id_user']:
                                    # Insert table #####################################################################################
                                    table = TableInfo(str(cont), '', entrada, 'Você agendou esse horarion',
                                                      f'{soma_horas.strftime("%H:%M")}')
                                    self.ids.grid_shedule.add_widget(table)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    del (lista_info[num])

                                    # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                    if ranger_init == 0:
                                        ranger_init = int(tempo[3:])
                                        ranger_last = 60
                                    elif ranger_init == int(tempo[3:]):
                                        ranger_init = 0
                                        ranger_last = int(tempo[3:])

                                    break
                                else:
                                    table = Table_shedule(str(cont), '', entrada,
                                                          f'{soma_horas.strftime("%H:%M")}', lista_info[num]['tempo'], lista_info[num]['nome'])
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append(entrada)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    del (lista_info[num])

                                    # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                    if ranger_init == 0:
                                        ranger_init = int(tempo[3:])
                                        ranger_last = 60
                                    elif ranger_init == int(tempo[3:]):
                                        ranger_init = 0
                                        ranger_last = int(tempo[3:])
                                    break

                            # para não dá erro, de sumir o agendamento anterior
                            elif str(mim).zfill(2) == tempo[3:]:
                                table = TableEnpty(str(cont), '', entrada, f'', '')
                                self.ids.grid_shedule.add_widget(table)
                                list_content.append('')
                                block = True
                                permition_to_sum = True

                                # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                if ranger_init == 0:
                                    ranger_init = int(tempo[3:])
                                    ranger_last = 60
                                elif ranger_init == int(tempo[3:]):
                                    ranger_init = 0
                                    ranger_last = int(tempo[3:])

                except:
                    print('Deu algum erro na função actualizar da class "ViewSchedule"')
            # except:
            #     print('Deu algum erro na função actualizar da class "ViewSchedule"')

            # Here block to not have repetition ########################################################################
            # Aqui bloqueia para não ter repetições

            if block == False:
                table = TableEnpty(str(cont), '', entrada, f'', '')
                self.ids.grid_shedule.add_widget(table)
                list_content.append('')
                permition_to_sum = True

                # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                if ranger_init == 0:
                    ranger_init = int(tempo[3:])
                    ranger_last = 60
                elif ranger_init == int(tempo[3:]):
                    ranger_init = 0
                    ranger_last = int(tempo[3:])
            block = False

            if permition_to_sum == True:

                # adding up the hours ####################################
                # somando as horas ##
                inicio = datetime.strptime(entrada, '%H:%M')
                horas, minutos = map(int, tempo.split(':'))
                delta_tempo = timedelta(hours=horas, minutes=minutos)
                final = inicio + delta_tempo
                entrada = final.strftime('%H:%M')

            cont += 1

        # using in class "HoursSchedule" function "hours_limit" ###########
        with open('list_content.json', 'w') as file:
            json.dump(list_content, file)
        # except:
        #     pass

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.actualizar, 1)

    def on_pre_leave(self, *args):
        self.ids.grid_shedule.clear_widgets()

    def return_schoice_schedule(self):
        MDApp.get_running_app().root.current = 'screenchoiceschedule'


class AgendamentoApp(MDApp):

    Builder.load_string(open('agendamento_vitor.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/my_box_socio.kv', encoding='utf-8').read())
    Builder.load_string(open('file_kv/choice_schedule.kv', encoding='utf-8').read())


    def build(self):

        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()