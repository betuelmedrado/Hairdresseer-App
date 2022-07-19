
#requere python 3.8

# kivymd ###
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDTextButton, MDFlatButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.label import MDLabel


# kivy ###
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button

# importando firebase
import requests
import os
import certifi
import json
from kivymd.toast import toast

from functools import partial
from datetime import datetime, timedelta

# from datetime import datetime

Window.size = 400,820

os.environ["SSL_CERT_FILE"] = certifi.where()

class Manager(ScreenManager):
    pass

class HomePage(Screen):
    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'
    lista_id_user = []

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.day_semana = datetime.today().isoweekday()

        self.id_manager = self.get_id_manager()
        self.id_socios = self.get_id_socios()
        # Clock.schedule_once(self.get_info, 1)
        Clock.schedule_once(self.get_local, 2)

    def on_pre_enter(self, *args):
        self.creat_files()
        toast('Aguarde estamos carregando as informações!...')

        Clock.schedule_once(self.get_info, 1)

    def get_local(self, *args):

        link = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}.json'

        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        local = requisicao_dic['local']
        number = requisicao_dic['numero']

        try:
            self.ids.rua.text = str(local.title())
            self.ids.num.text = str(number)
        except KeyError:
            pass

    def get_id_manager(self, *args):
        id = ''
        requisicao = requests.get(self.LINK_SALAO)
        requisicao_dic = requisicao.json()
        for ids in requisicao_dic:
            id = ids
        return id

    def get_info(self,*args):

        self.ids.my_card_button.clear_widgets()

        with open('info_user.json', 'r') as file:
            id_user = json.load(file)

        # lista = []

        # verification if have schedule in manager ########################################################################
        check_image_manager = self.check_manager_scheduling()

        # verification if have schedule in socio ##########################################################################
        check_socio = self.check_socio_scheduling()

        # geting the id of manager
        try:
            LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}.json'
            requisicao_id = requests.get(LINK_ID)
            requisicao_id_dic = requisicao_id.json()

            if check_image_manager:
                my_card_button = MyCardButton(requisicao_id_dic['manager'], self.id_manager, requisicao_id_dic['nome'])
                my_card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                self.ids.my_card_button.add_widget(my_card_button)
            else:
                self.ids.my_card_button.add_widget(MyCardButton(requisicao_id_dic['manager'], self.id_manager, requisicao_id_dic['nome']))

            # for id_socios in requisicao_id_dic['socios']:
            #     lista.append(id_socios)
        except:
            pass

        # getting ids of user which is schedule ############################################################################
        # for enum, id in enumerate(lista):
        for enum, id in enumerate(self.id_socios):
            try:
                # Here getting socio to read of data ##############################################################################
                LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id}.json'
                requisicao_to_socio = requests.get(LINK_ID)
                requisicao_to_socio_dic = requisicao_to_socio.json()

                try:
                    if check_socio[enum]:
                        card_button = MyCardButton(requisicao_to_socio_dic['manager'], id, requisicao_to_socio_dic['nome'])
                        card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                        self.ids.my_card_button.add_widget(card_button)
                    else:
                        self.ids.my_card_button.add_widget(MyCardButton(requisicao_to_socio_dic['manager'], id, requisicao_to_socio_dic['nome']))
                except:
                    self.ids.my_card_button.add_widget(
                        MyCardButton(requisicao_to_socio_dic['manager'], id, requisicao_to_socio_dic['nome']))
            except:
                pass

    def get_id_socios(self, *args):

        lista_id_socio = []
        try:
            LINK_SOCIOS = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios.json'
            requisicao = requests.get(LINK_SOCIOS)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                lista_id_socio.append(id)
            return lista_id_socio
        except:
            pass

    def creat_files(self):
        try:
            open('select_works.json','r')
        except FileNotFoundError:
            open('select_works.json','w')

        try:
            with open('info_schedule.json','r') as arquivo:
                json.load(arquivo)
        except FileNotFoundError:
            with open('info_schedule.json','w') as arquivo:
                json.dump('', arquivo)

        try:
            with open('list_content.json','r') as lista:
                json.load(lista)
        except:
            with open('list_content.json', 'w') as lista:
                json.dump([],lista)

        try:
            with open('info_user.json','r') as file:
                json.load(file)
        except:
            with open('info_user.json', 'w') as file:
                json.dump([], file)

    def return_login(self):

        # excluding refreshToken to not entry automatic in home page
        with open('refreshtoken.json','w') as arquivo:
            json.dump('',arquivo)
        MDApp.get_running_app().root.current = 'register'

    def check_manager_scheduling(self, *args):
        list_of_id = []

        with open('info_user.json','r') as file:
            id_user = json.load(file)

        # id_manager = self.id_manager()

        try:
            LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/agenda/{self.day_semana}.json'
            requisicao = requests.get(LINK)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                list_of_id.append(id)

            if id_user['id_user'] in list_of_id:
                return True
            else:
                return False
        except:
            return False

    def check_socio_scheduling(self, *args):
        list_of_id = []

        with open('info_user.json', 'r') as file:
            id_user = json.load(file)

        # try:
        for idsocio in self.id_socios:
            LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{idsocio}/agenda/{self.day_semana}.json'
            requisicao = requests.get(LINK)
            requisicao_dic = requisicao.json()

            try:
                for id in requisicao_dic:
                    # list_of_id.append(id)
                    if id_user['id_user'] == id:
                        list_of_id.append(True)
                        break
                    else:
                        list_of_id.append(False)
            except:
                list_of_id.append(False)

        return list_of_id
        # except:
        #     list_of_id.append(False)
        #     return list_of_id

class Register(Screen):

    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.log_aut,1)

    def entry_home(self, *args):
        MDApp.get_running_app().root.current = 'homepage'

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
                Clock.schedule_once(self.entry_home, 1)
            else:
                pass
            return user_id
        except:
            pass

    def save_refreshtoken(self,msg, *args):
        with open('refreshtoken.json', 'w') as arquivo:
            json.dump(msg, arquivo)

    def save_info_user(self, id_user, id_token):
        info = {"id_user":id_user,
                "id_token":id_token}

        with open('info_user.json','w') as arquivo:
            json.dump(info, arquivo, indent=2)

    def not_can_client(self):
        lista_info_ids = []
        ID_MANAGER = ''

        # Geting id of manager #########################################################################################
        LINK_MANAGER = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'
        requisicao_manager = requests.get(LINK_MANAGER)
        requisicao_manager_dic = requisicao_manager.json()

        for id in requisicao_manager_dic:
            ID_MANAGER = id

        # Geting ids of socios #########################################################################################

        LINK_SOCIOS = f'https://shedule-vitor-default-rtdb.firebaseio.com/client.json'
        requisicao_socio = requests.get(LINK_SOCIOS)
        requisicao_socio_dic = requisicao_socio.json()

        for id_socio in requisicao_socio_dic:
            lista_info_ids.append(id_socio)

        return lista_info_ids

    def logar(self,*args):

        lista_info_ids = self.not_can_client()
        print('listaaa ',lista_info_ids)

        LINK = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'

        email = self.ids.email.text
        senha = self.ids.senha.text
        id_user = ''
        id_token = ''
        refresh_token = ''

        info = {"email":email,
                "password":senha,
                "returnSecureToken":True}
        requisicao = requests.post(LINK, data=info)
        requisicao_dic = requisicao.json()

        try:
            # ID of user #################################
            id_user = requisicao_dic['localId']

            # ID of authentication of user ###############
            id_token = requisicao_dic['idToken']

            # RefreshToken of user
            refresh_token = requisicao_dic['refreshToken']

            # Saving info of user ########################
            self.save_info_user(id_user, id_token)
        except:
            pass

        if requisicao.ok:
            if requisicao_dic['localId'] in lista_info_ids:
                self.save_refreshtoken(refresh_token)
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
            self.ids.warning.text = 'Confirmação de [color=#D40A00][b]Senha[/b][/color] Invalid'
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
                    f' "bloqueado":"False",' \
                    f'"ids_agendado":""}}'
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

                idtoken = requisicao_dic['idToken']
                localid = requisicao_dic['localId']
                refreshtoken = requisicao_dic['refreshToken']

                if requisicao.ok:
                    self.fire_base_creat(idtoken,localid,refreshtoken)
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

class RedefinitionSenha(Screen):
    API_KEY = 'AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk'


    def send_email(self, *args):
        """
        Function for redefinited the password
        :param args:
        :return:
        """
        LINK_FOR_API = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.API_KEY}'

        email = self.ids.email.text

        info = {"requestType":"PASSWORD_RESET",
               "email": email}

        requisicao = requests.post(LINK_FOR_API, data=info)
        requisicao_dic = requisicao.json()

        error = requisicao_dic['error']['message']

        if requisicao.ok:
            toast('Foi enviado uma mensagem no email informado para redefinir a senha!')
        elif error == 'MISSING_EMAIL':
            toast('Insira um e-mail valido!')
        elif error == 'INVALID_EMAIL':
            toast('Email invalido!')
        elif error  == 'EMAIL_NOT_FOUND':
            toast('Email não encontrado!')
        else:
            pass

    def return_login(self):
        MDApp.get_running_app().root.current = 'register'

class Table_shedule(MDBoxLayout):
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='', time_cancel='',**kwargs):

        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2
        self.time_cancel = str(time_cancel)

class TableInfo(MDBoxLayout):
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='', time_cancel='',**kwargs):

        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2
        self.time_cancel = str(time_cancel)

class Table_block(MDBoxLayout):
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='',**kwargs):
        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2

class ViewSchedule(Screen):
    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        # Geting day actual ##########################################################################
        self.dia_atual = datetime.today().isoweekday()

        LINK_ID_MANAGER = requests.get('https://shedule-vitor-default-rtdb.firebaseio.com/salao.json')
        for id in LINK_ID_MANAGER.json():
            self.id_manager = id

        # Link of SALÃO ##############################################################################
        self.LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}'

        # Geting information of manager ##############################################################
        self.info_manager = self._info_manager()

    def _info_manager(self, *args):
        link = f'{self.LINK_SALAO}.json'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        return requisicao_dic

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.actualizar, 1)
        self.user_id = self.log_aut()

    def time_now(self):
        h = datetime.today().hour
        mim = datetime.today().minute
        horas = f'{str(h).zfill(2)}:{str(mim).zfill(2)}'

        return horas

    def get_id_proficional(self, *args):
        dic_information = {}

        with open('write_id_manager.json', 'r') as arquivo:
            dic_informing = json.load(arquivo)
        return dic_informing

    # Get id user ####################################################################################
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
        lista_requisicao = []

        # try:
        # information socio ############################################################################################
        if id_manager["manager"] == 'False':
            # Here if not manager then get the socio #########################################################################
            LINK_SALAO = f'{self.LINK_SALAO}/socios/{id_manager["id_user"]}.json'
            requisicao = requests.get(LINK_SALAO)
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']
            self.ids.title_toobar.title = f'Agenda {str(nome)}'

            self.entrada = requisicao_dic[f'{self.dia_atual}']['entrada']

            self.saida = requisicao_dic[f'{self.dia_atual}']['saida']

            self.space_temp = requisicao_dic[f'{self.dia_atual}']['space_temp']

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

        elif id_manager["manager"] == 'True':
            # Here to geting the id of manager to get schedule #######################################
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']
            self.ids.title_toobar.title = f'Agenda {str(nome)}'

            self.entrada = requisicao_dic[f'{self.dia_atual}']['entrada']

            self.saida = requisicao_dic[f'{self.dia_atual}']['saida']

            self.space_temp = requisicao_dic[f'{self.dia_atual}']['space_temp']

            # print(requisicao_dic['agenda'][self.dia_atual])

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
        # else:
        #     self.entrada = '00:00'
        #     self.saida = '00:00'
        #     self.space_temp = '00:00'
        #     self.ids.title_toobar.title = f' Agenda {str(nome)}'
        #     return lista_info
        # except:
        #     pass

    def actualizar(self, *args):
        try:
            # get user id ##################################################################################################
            # Variaveis #############################
            user_id = self.log_aut()
            lista_info = self.info_entrace_salao()

            self.agenda_marcada = False
            list_content = []
            entrada = self.entrada
            saida = self.saida
            tempo = self.space_temp


            time_c = self.info_manager['time_cancel']
            time_cancel = f'[color=#6B0A00][b]"Atenção":[/b][/color] Você tem {time_c} /H para desmarcar apos agendamento!'

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
                # Aqui é para saber a quantidade de agenda marcadas ############################################################
                for num, agenda in enumerate(lista_info):
                    # try:

                    ranger_init = 0

                    # ---------------------------------------------------------------------CHANGE
                    # entry_temp = datetime.strptime(entrada, '%H:%M')
                    #
                    # # ftemp = str(f'00:{tempo}').zfill(2)
                    # fhours, fmin = map(int, tempo.split(':'))
                    # delta = timedelta(hours=fhours, minutes=fmin)
                    # soma = entry_temp + delta
                    # format_soma = soma.strftime('%H:%M')
                    #
                    # if format_soma > lista_info[num]['id_horas']:
                    #     block = True
                    #     permition_to_sum = True
                    # --------------------------------------------------------------------------/CHANGE

                    # Aqui compara o horario na posição horas e compara com o orario marcado na lista
                    if entrada[:2] == lista_info[0]['id_horas'][:2] :#or entrada[:2] == lista_info[0]['id_horas'][:2]: # --------------------------------------------- [0] [num]
                        for mim in range(ranger_init, ranger_last): # -----------------------------------------------Change +1

                            # ---------------------------------------------------------------------CHANGE

                            entry_future = datetime.strptime(entrada,'%H:%M')
                            fmim = str(f'00:{mim}').zfill(2)
                            ft_hours, ft_min = map(int,fmim.split(':'))
                            delta_minutes = timedelta(hours=ft_hours ,minutes=ft_min)
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

                            # --------------------------------------------------------------------------/CHANGE

                            # conparing the minutes ###################################################################################
                            if str(mim).zfill(2) == lista_info[0]['id_horas'][3:]: # ------------------ [0] [num]
                                ent = int(str(entrada[:2]).zfill(2))
                                entrada = f'{str(ent).zfill(2)}:{str(mim).zfill(2)}'

                                entry = datetime.strptime(entrada,'%H:%M')
                                # temp = lista_info[num]['tempo']
                                temp = lista_info[0]['tempo'] # ----------------------------------------[0][num]
                                hours, minute = map(int,temp.split(':'))
                                delta_temp = timedelta(hours=hours, minutes=minute)
                                soma_horas = entry + delta_temp

                                if user_id == lista_info[0]['id_user']: # -----------------------------[0]
                                    # Insert table #####################################################################################
                                    table = TableInfo(str(cont), '', entrada, 'Você agendou esse horarion', f'{soma_horas.strftime("%H:%M")}', time_cancel)
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append(entrada)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    seletor_schedule = True
                                    # Variable to not permiting the cliet make other schedule ###########################################
                                    self.agenda_marcada = True
                                    ranger_init = entrada[3:]
                                    # del(lista_info[num])
                                    del(lista_info[0]) # ------------------------------------------

                                    # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                    # if ranger_init == 0:
                                    #     # ranger_init = int(tempo[3:])
                                    #     ranger_init = int(entrada[3:]) # -------------------------------Change
                                    #     ranger_last = 60 # ------------------------------------------------Change 60
                                    # elif ranger_init == int(tempo[3:]):
                                    #     ranger_init = 0
                                    #     ranger_last = int(tempo[3:]) + 1
                                    cont += 1
                                    break
                                else:
                                    table = Table_block(str(cont), '', entrada, 'Agendado!', f'{soma_horas.strftime("%H:%M")}')
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append(entrada)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    seletor_schedule = True
                                    ranger_init = entrada[3:]
                                    # del(lista_info[num])
                                    del(lista_info[0]) # ----------------------------------------------------

                                    # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                    # if ranger_init == 0:
                                    #     # ranger_init = int(tempo[3:])
                                    #     ranger_init = int(entrada[3:]) #-------------------------------------Change
                                    #     ranger_last = 60 # --------------------------------------------------Change 60
                                    # elif ranger_init == int(tempo[3:]):
                                    #     ranger_init = 0
                                    #     ranger_last = int(tempo[3:]) + 1
                                    cont += 1
                                    break

                            # para não dá erro, de sumir o agendamento anterior
                            elif str(int(mim) + 1).zfill(2) == tempo[3:] and soma_future.strftime('%H:%M') <= lista_info[0]['id_horas'] :

                                # elif str(mim).zfill(2) == tempo[3:] and seletor_schedule == True :
                                table = Table_shedule(str(cont), '', entrada, f'first', '', time_cancel)
                                self.ids.grid_shedule.add_widget(table)
                                list_content.append('')
                                block = True
                                permition_to_sum = True
                                ranger_init = entrada[3:]
                                cont += 1
                                # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                                # if ranger_init == 0:
                                #     ranger_init = int(tempo[3:])
                                #     ranger_last = 60
                                # elif ranger_init == int(tempo[3:]):
                                #     ranger_init = 0
                                #     ranger_last = int(tempo[3:]) + 1

                            # elif int(mim) + 1 == int(tempo[3:] ):
                            #
                            #     # try:
                            #     #     if soma_future.strftime("%H:%M") > lista_info[num + 1]['id_horas']:
                            #     #         entrada = lista_info[num]['id_horas']
                            #     #         mim = lista_info[num]['id_horas'][3:]
                            #     #     else:
                            #     #         table = Table_shedule(str(cont), '', entrada, f'second', '', time_cancel)
                            #     #         self.ids.grid_shedule.add_widget(table)
                            #     #         list_content.append('')
                            #     #         block = True
                            #     #         permition_to_sum = True
                            #     #         seletor_schedule = False
                            #     #         ranger_init = entrada[3:]
                            #     #         cont += 1
                            #     # except:
                            #     #     if soma_future.strftime("%H:%M") > lista_info[num]['id_horas']:
                            #     #         entrada = lista_info[num]['id_horas']
                            #     #         mim = lista_info[num]['id_horas'][3:]
                            #     #     else:
                            #     #         table = Table_shedule(str(cont), '', entrada, f'second', '', time_cancel)
                            #     #         self.ids.grid_shedule.add_widget(table)
                            #     #         list_content.append('')
                            #     #         block = True
                            #     #         permition_to_sum = True
                            #     #         seletor_schedule = False
                            #     #         ranger_init = entrada[3:]
                            #     #         cont += 1
                            #
                            #     table = Table_shedule(str(cont), '', entrada, f'second', '', time_cancel)
                            #     self.ids.grid_shedule.add_widget(table)
                            #     list_content.append('')
                            #     block = True
                            #     permition_to_sum = True
                            #     seletor_schedule = False
                            #     cont += 1
                            # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                            # if ranger_init == 0:
                            #     ranger_init = int(tempo[3:])
                            #     ranger_last = 60
                            # elif ranger_init == int(tempo[3:]):
                            #     ranger_init = 0
                            #     ranger_last = int(tempo[3:]) + 1

                    # except:
                    #     print('Deu algum erro na função actualizar da class "ViewSchedule"')

                # except:
                #     print('Deu algum erro na função actualizar da class "ViewSchedule"')

                # Here block to not have repetition ########################################################################
                # Aqui bloqueia para não ter repetições

                # ranger_init = 30
                # ranger_last = 60

                if block == False:

                    soma_entrada = datetime.strptime(entrada,'%H:%M')
                    h_tempo, m_tempo = map(int,tempo.split(':'))
                    delta_soma = timedelta(hours=h_tempo, minutes=m_tempo)

                    soma_tempo = soma_entrada + delta_soma

                    try:
                        if soma_tempo.strftime('%H:%M') <= lista_info[0]['id_horas']:
                            table = Table_shedule(str(cont), '', entrada, f'last', '', time_cancel)
                            self.ids.grid_shedule.add_widget(table)
                            list_content.append('')
                            permition_to_sum = True
                            ranger_init = entrada[3:]
                            cont += 1
                        else:
                            permition_to_sum = True
                    except IndexError:
                        table = Table_shedule(str(cont), '', entrada, f'last 2', '', time_cancel)
                        self.ids.grid_shedule.add_widget(table)
                        list_content.append('')
                        permition_to_sum = True
                        ranger_init = entrada[3:]
                        cont += 1

                    # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
                    # if ranger_init == 0:
                    #     ranger_init = int(tempo[3:])
                    #     ranger_last = 60
                    # elif ranger_init == int(tempo[3:]):
                    #     ranger_init = 0
                    #     ranger_last = int(tempo[3:]) + 1
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
            with open('list_content.json','w') as file_list:
                json.dump(list_content, file_list)
        except:
            toast('Nenhuma agenda para hoje!')
            # raise

    # def actualizar(self, *args):
    #     try:
    #         # get user id ##################################################################################################
    #         # Variaveis #############################
    #         user_id = self.log_aut()
    #         lista_info = self.info_entrace_salao()
    #
    #         self.agenda_marcada = False
    #         list_content = []
    #         entrada = self.entrada
    #         saida = self.saida
    #         tempo = self.space_temp
    #         time_c = self.info_manager['time_cancel']
    #         time_cancel = f'[color=#6B0A00][b]"Atenção":[/b][/color] Você tem {time_c} /H para desmarcar apos agendamento!'
    #         pos_lista = 0
    #
    #         # variable to show the first schedule if it is scheduled, is implemented in "for range", I do this to display the correct schedule table
    #         # variável para mostrar o primeiro agendamento se for agendado, está implementado no "for range", Eu faço isso para exibir a tabela de agendamento correta
    #         ranger_init = 0
    #         ranger_last = int(tempo[3:])
    #
    #         # lista = ['']
    #         block = False
    #         permition_to_sum = True
    #
    #         # To conting the position of schedule to verification of next schedule
    #         cont = 00
    #
    #         self.ids.grid_shedule.clear_widgets()
    #
    #         # Here i am sorting the list "lista_info" in key "['id_horas']" #########################################################
    #         ordem = sorted(lista_info, key=lambda valor: valor['id_horas'])
    #         lista_info = ordem
    #
    #         # try:
    #         while entrada[:2] < saida[:2]:
    #             # Aqui é para saber a quantidade de agenda marcadas ############################################################
    #             for num, agenda in enumerate(lista_info):
    #                 pos_lista = num
    #
    #                 # try:
    #                 # Aqui compara o horario na posição horas e compara com o orario marcado na lista
    #                 if entrada[:2] == lista_info[num]['id_horas'][:2]:
    #                     for mim in range(ranger_init,
    #                                      ranger_last):  # -----------------------------------------------Change +1
    #                         # ---------------------------------------------------------------------CHANGE
    #                         entry_future = datetime.strptime(entrada, '%H:%M')
    #
    #                         fmim = str(f'00:{mim}').zfill(2)
    #                         ft_hours, ft_min = map(int, fmim.split(':'))
    #                         delta_minutes = timedelta(hours=ft_hours, minutes=ft_min)
    #                         soma_future = entry_future + delta_minutes
    #
    #                         try:
    #                             if soma_future.strftime("%H:%M") > lista_info[num + 1]['id_horas']:
    #                                 entrada = lista_info[num]['id_horas']
    #                                 mim = lista_info[num]['id_horas'][3:]
    #                             else:
    #                                 pass
    #                         except:
    #                             if soma_future.strftime("%H:%M") > lista_info[num]['id_horas']:
    #                                 entrada = lista_info[num]['id_horas']
    #                                 mim = lista_info[num]['id_horas'][3:]
    #                             else:
    #                                 pass
    #
    #                         # --------------------------------------------------------------------------/CHANGE
    #
    #                         # conparing the minutes ###################################################################################
    #                         if str(mim).zfill(2) == lista_info[num]['id_horas'][3:]:
    #                             ent = int(str(entrada[:2]).zfill(2))
    #                             entrada = f'{str(ent).zfill(2)}:{str(mim).zfill(2)}'
    #
    #                             entry = datetime.strptime(entrada, '%H:%M')
    #                             temp = lista_info[num]['tempo']
    #                             hours, minute = map(int, temp.split(':'))
    #                             delta_temp = timedelta(hours=hours, minutes=minute)
    #                             soma_horas = entry + delta_temp
    #
    #                             if user_id == lista_info[num]['id_user']:
    #                                 # Insert table #####################################################################################
    #                                 table = TableInfo(str(cont), '', entrada, 'Você agendou esse horarion',
    #                                                   f'{soma_horas.strftime("%H:%M")}', time_cancel)
    #                                 self.ids.grid_shedule.add_widget(table)
    #                                 entrada = soma_horas.strftime('%H:%M')
    #                                 block = True
    #                                 permition_to_sum = False
    #                                 # Variable to not permiting the cliet make other schedule ###########################################
    #                                 self.agenda_marcada = True
    #                                 del (lista_info[num])
    #
    #                                 # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
    #                                 if ranger_init == 0:
    #                                     # ranger_init = int(tempo[3:])
    #                                     ranger_init = int(entrada[3:])  # -------------------------------Change
    #                                     ranger_last = 60  # ------------------------------------------------Change 60
    #                                 elif ranger_init == int(tempo[3:]):
    #                                     ranger_init = 0
    #                                     ranger_last = int(tempo[3:]) + 1
    #
    #                                 break
    #                             else:
    #                                 table = Table_block(str(cont), '', entrada, 'Agendado!',
    #                                                     f'{soma_horas.strftime("%H:%M")}')
    #                                 self.ids.grid_shedule.add_widget(table)
    #                                 list_content.append(entrada)
    #                                 entrada = soma_horas.strftime('%H:%M')
    #                                 block = True
    #                                 permition_to_sum = False
    #                                 del (lista_info[num])
    #
    #                                 # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
    #                                 if ranger_init == 0:
    #                                     # ranger_init = int(tempo[3:])
    #                                     ranger_init = int(entrada[3:])  # -------------------------------------Change
    #                                     ranger_last = 60  # --------------------------------------------------Change 60
    #                                 elif ranger_init == int(tempo[3:]):
    #                                     ranger_init = 0
    #                                     ranger_last = int(tempo[3:]) + 1
    #                                 break
    #
    #                         # para não dá erro, de sumir o agendamento anterior
    #                         elif str(mim).zfill(2) == tempo[3:]:
    #                             table = Table_shedule(str(cont), '', entrada, f'', '', time_cancel)
    #                             self.ids.grid_shedule.add_widget(table)
    #                             list_content.append('')
    #                             block = True
    #                             permition_to_sum = True
    #
    #                             # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
    #                             if ranger_init == 0:
    #                                 ranger_init = int(tempo[3:])
    #                                 ranger_last = 60
    #                             elif ranger_init == int(tempo[3:]):
    #                                 ranger_init = 0
    #                                 ranger_last = int(tempo[3:]) + 1
    #
    #                 # except:
    #                 #     print('Deu algum erro na função actualizar da class "ViewSchedule"')
    #
    #             # except:
    #             #     print('Deu algum erro na função actualizar da class "ViewSchedule"')
    #
    #             # Here block to not have repetition ########################################################################
    #             # Aqui bloqueia para não ter repetições
    #
    #             # ranger_init = 30
    #             # ranger_last = 60
    #
    #             if block == False:
    #                 table = Table_shedule(str(cont), '', entrada, f'', '', time_cancel)
    #                 self.ids.grid_shedule.add_widget(table)
    #                 list_content.append('')
    #                 permition_to_sum = True
    #
    #                 # Exemplo: conta por exemplo 07:30  e depois 08:00  para saber si já tem agenda marcada nesse horário para não ocultar agenda ############
    #                 if ranger_init == 0:
    #                     ranger_init = int(tempo[3:])
    #                     ranger_last = 60
    #                 elif ranger_init == int(tempo[3:]):
    #                     ranger_init = 0
    #                     ranger_last = int(tempo[3:]) + 1
    #             block = False
    #
    #             if permition_to_sum == True:
    #
    #                 # adding up the hours ####################################
    #                 # somando as horas ##
    #                 inicio = datetime.strptime(entrada, '%H:%M')
    #                 horas, minutos = map(int, tempo.split(':'))
    #                 delta_tempo = timedelta(hours=horas, minutes=minutos)
    #                 final = inicio + delta_tempo
    #                 entrada = final.strftime('%H:%M')
    #
    #             cont += 1
    #
    #         # using in class "HoursSchedule" function "hours_limit" ###########
    #         with open('list_content.json', 'w') as file:
    #             json.dump(list_content, file)
    #     except:
    #         toast('Nenhuma agenda para hoje!')

    # Open and inserting the hours in class HoursSchedule #######################################

    def spiner(self,id_button, hours, *args, **kwargs):
        self.spiner = MDSpinner(size_hint=(None, None,), size=('46dp', '46dp'), pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.spiner)
        Clock.schedule_once(partial(self.popup_mark_off, id_button, hours),2)

    def popup_mark_off(self,id_button,hours, *args, **kwargs):
        id_user = ''
        # info_schedule = self.info_entrace_salao()
        # for id in info_schedule:
        #     if id['id_user'] == self.user_id:
        #         id_user = id['id_user']

        with open('info_user.json', 'r') as file:
            id_user = json.load(file)


        box = MDBoxLayout(orientation='vertical')
        box_button = MDBoxLayout(padding=5,spacing=5)

        img = Image(source='images/atencao.png')

        bt_sim = Button(text='Sim',background_color=(0,1,1,1),color=(1,0,0,.8), size_hint=(1,None),height='40dp')
        bt_nao = Button(text='Sair',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')
        bt_view = Button(text='View',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')

        box_button.add_widget((bt_sim))
        box_button.add_widget((bt_nao))
        box_button.add_widget((bt_view))

        box.add_widget((img))
        box.add_widget((box_button))

        self.popup  = Popup(title='Deseja cancelar o agendamento?',
                            size_hint=(.8,None), height='200dp',content=box)

        bt_sim.bind(on_release = partial(self.cancel_schedule, id_user["id_user"]))
        bt_nao.bind(on_release = self.popup.dismiss)

        self.popup.open()

    def check_time_cancel(self,cancel, time):

        permitido = cancel

        time_schedule = time
        time_s = datetime.strptime(time_schedule, '%H:%M')

        hour_now = self.time_now()
        hours, minute = map(int, permitido.split(':'))
        delta_temp = timedelta(hours=hours, minutes=minute)

        soma_horas = delta_temp + time_s

        info = hour_now > soma_horas.strftime('%H:%M')

        return info

    def cancel_schedule(self, id_user, *args, **kwargs):
        id_proficional = self.get_id_proficional()
        time_cancel = self.info_manager['time_cancel']

        link = ''

        if id_proficional['manager'] == "False":
            link = self.LINK_SALAO + f'/socios/{id_proficional["id_user"]}/agenda/{self.dia_atual}/{id_user}.json'

        elif id_proficional['manager'] == "True":
            link = self.LINK_SALAO + f'/agenda/{self.dia_atual}/{id_user}.json'

        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        cancelar = self.check_time_cancel(str(time_cancel),requisicao_dic['horas_agendamento'])

        if cancelar:
            toast(f'O agendamento não pode ser cancelado\nPassou do tempo de {time_cancel} h/m!')
        else:
            requisicao = requests.delete(link)
            self.actualizar()

        self.popup.dismiss()

    def if_blocked(self,id_button, hours):

        if self.agenda_marcada:
            toast('Você já tem um agendamento marcado aqui para fazer outro agendamento\nCancele o seu agendamento!')
        else:
            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{self.user_id}.json'

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            try:
                if requisicao_dic['bloqueado'] == 'True':
                    toast('Você foi bloqueado! Entre em contato com um proficional ')
                elif requisicao_dic['bloqueado'] == 'False':
                    self.get_hours(id_button, hours)
            except:
                pass

    def get_hours(self,id_button, hours):
        hours_dic = {}

        hours_dic['id_posicao'] = id_button
        hours_dic['horas'] = hours

        with open('info_schedule.json','w') as arquivo:
            json.dump(hours_dic, arquivo, indent=2)

        MDApp.get_running_app().root.current = 'hoursschedule'

    def on_leave(self, *args):
        self.ids.grid_shedule.clear_widgets()

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'


class HoursSchedule(Screen):

    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'
    def __init__(self,hours='', **kwargs):
        super().__init__(**kwargs)
        # Clock.schedule_once(self.get_works, 2)
        self.semana = datetime.today().isoweekday()
        self.hours = hours
        self.id_manager = self.get_manager()

        self.LINK_SALAO_ID_MANAGER = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}'
        self.info_manager = self._info_manager()

    def on_pre_enter(self, *args):
        try:
            with open('info_schedule.json', 'r') as arquivo:
                horas = json.load(arquivo)
            self.ids.hours.text = horas['horas']
        except FileNotFoundError:
            pass

        self.ids.categorie.add_widget(MDSpinner(size_hint=(None,None,), size=('46dp','46dp'),pos_hint={'center_x':.5}))
        Clock.schedule_once(self.get_works, 2)
        self.includ_color_select()
        self.soma_hours_values()

        self.valid_button_save()

    def _info_manager(self, *args):
        link = f'{self.LINK_SALAO_ID_MANAGER}.json'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        return requisicao_dic

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
        self.ids.categorie.clear_widgets()

    def get_manager(self, *args):
        requisicao = requests.get(self.LINK_SALAO + '.json')
        requisicao_dic = requisicao.json()
        for id in requisicao_dic:
            return id

    def get_id_diverse(self):
        if_manager = {}

        with open('write_id_manager.json','r') as arquivo:
            if_manager = json.load(arquivo)
        return if_manager

    def get_works(self,*args):
        self.ids.categorie.clear_widgets()

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
                    self.ids.categorie.add_widget(MyBoxCategorie(str(servico), str(tempo), str(valor), md_bg_color=[0.13, 0.53, 0.95,.2]))
                else:
                    self.ids.categorie.add_widget(MyBoxCategorie(str(servico), str(tempo), str(valor)))
        except:
            try:
                if socio_or_manager:
                    work_socio = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + self.id_diverse["id_user"] + '/' + id_work + '.json'
                else:
                    work_socio = self.LINK_SALAO + '/' + self.id_manager + '/socios/' + id_work + '.json'
            except:
                pass

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
            valor += float(v['valor'])


        # Geting the hours
        tempo = f'{str(hours).zfill(2)}:{str(minute).zfill(2)}'

        self.ids.time.text = str(tempo)
        self.ids.valor.text = str(valor)

        self.hours_limit(tempo)

    def hours_limit(self, tempo, *args):

        lista_pos = ''

        with open('info_schedule.json','r') as file_info:
            info = json.load(file_info)

        with open('list_content.json','r') as lista:
            lista_content = json.load(lista)

        # hours of schedule
        h = datetime.strptime(info['horas'],'%H:%M')

        hora_tempo, minuto_tempo = map(int,tempo.split(':'))
        delta_time = timedelta(hours=hora_tempo, minutes=minuto_tempo)
        soma_horas = h + delta_time

        posicao = info['id_posicao']
        hora = info['horas']
        try:
            lista_pos =lista_content[int(posicao)]
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
            toast('O gendamento excede o horario do proximo agendamento escolha outro horario ou outro cabeleleiro!')
        elif boolian == False:
            self.ids.card_save.unbind(on_release = self.disable_release)
            self.ids.card_save.md_bg_color = 0.13, 0.53, 0.95,1
            self.ids.card_save.bind(on_release = self.save_scheduleing)

    def check_time(self, *args):
        pass

    def get_name_user(self, id_user, *args):
        LINK_DATA_NAME = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}.json'
        name = requests.get(LINK_DATA_NAME)
        name_dic = name.json()

        return name_dic['nome']

    def nada(self,*args):
        toast('Selecione o tipo de serviço!')

    def disable_release(self,*args):
        toast('O gendamento excede o horario do proximo agendamento escolha outro horario ou outro cabeleleiro!')

    def verification_if_schedule(self, *args):
        link = f'{self.LINK_SALAO}/'



    def save_scheduleing(self, *args):
        time_cancel = self.info_manager['time_cancel']
        horas_hoje = self.time_now()
        # list_works = []
        # list_ids_schedule = []

        # variable to infomation of schedule ######################
        list_id_marked = []
        link = ''
        free = ''
        list_comparate_hours = []

        # geting the id of Manager ##############################
        # name_id = self.get_id_diverse()
        if_manager = self.get_id_diverse()

        # geting the info of work ###############################
        with open('select_works.json','r') as select_work:
            list_works = json.load(select_work)

        with open('info_user.json','r') as arquivo:
            info_user = json.load(arquivo)

        with open('info_schedule.json', 'r') as file_info:
            id_pos = json.load(file_info)


        id_user = info_user['id_user']
        nome = self.get_name_user(id_user)
        horas = self.ids.hours.text
        tempo = self.ids.time.text
        valor = self.ids.valor.text
        link_info = ''

        # Here is to know is have schedule marked ##############################################
        if if_manager['manager'] == "False":
            link_info = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.semana}.json'
        elif if_manager['manager'] == "True":
            link_info = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.semana}.json'
        # ######################################################################################

        try:
            requisicao_if_scheduled = requests.get(link_info)
            if_scheduled = requisicao_if_scheduled.json()

            # Geting the id marked on schedule ###
            for info in if_scheduled:
                list_id_marked.append(info)

            # Here getting the hours of marked ###
            for id_marked in list_id_marked:
                list_comparate_hours.append(if_scheduled[id_marked]['id_horas'])
                print(list_comparate_hours)

            free = horas in list_comparate_hours
        except TypeError:
            pass


        if if_manager['manager'] == "False":
            link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.semana}/{id_user}.json'
        elif if_manager['manager'] == "True":
            link = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.semana}/{id_user}.json'

        info = f'{{"id_posicao":"{id_pos["id_posicao"]}",' \
               f'"id_horas":"{horas}",' \
               f'"id_user":"{id_user}",' \
               f'"tempo":"{tempo}",' \
               f'"valor":"{valor}",' \
               f'"nome":"{nome}",'\
               f'"horas_agendamento": "{horas_hoje}",'\
               f'"servicos":"{list_works}"}}'

        if free:
            toast('Desculpe mais alguem acabou de agendar esse horário!')
        else:
            requisicao = requests.patch(link, data=info)
            toast(f'Agendamento Marcado! Você tem {time_cancel} H/m para cancelar!')


        # if if_manager['manager'] == "False":
        #     # getting ids that are already scheduled ###########################################################################
        #         link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'
        #         requisicao_client_get = requests.get(link_cliente)
        #         requisicao_client_get_dic = requisicao_client_get.json()
        #
        #     # list_ids_schedule receiver the ids what is in cloud ##############################################################
        #         if requisicao_client_get_dic != '':
        #             list_ids_schedule.append(requisicao_client_get_dic)
        #
        #     # list_ids_schedule receiver the id what go be schedule ############################################################
        #         list_ids_schedule.append(if_manager['id_user'])
        #
        #     # Insert ids of schedule in user ###################################################################################
        #         link_cliente = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}/ids_agendado.json'
        #
        #         info = f'{{"ids_agendado":"{list_ids_schedule}" }}'
        #
        #         requisicao_client = requests.patch(link_cliente, data=info)
        # else:
        #     pass

    # Clearing file "select_work" after of save ########################################################################
        with open('select_works.json','w') as file:
            json.dump([], file)
        MDApp.get_running_app().root.current = 'viewshedule'

class MyCardButton(MDCard):

    def __init__(self, socio_or_manager='', id_user='', nome='', **kwargs):
        super().__init__(**kwargs)
        self.socio_or_manager = socio_or_manager
        self.id_user = id_user
        self.nome = nome

    def send_info(self,socio_or_manager, id_user):
        dictionary = {}

        dictionary['manager'] = socio_or_manager
        dictionary['id_user'] = id_user

        with open('write_id_manager.json', 'w') as arquivo:
            json.dump(dictionary, arquivo, indent=2)

        MDApp.get_running_app().root.current = 'viewshedule'

class MyBoxCategorie(MDCard):

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


class AgendamentoApp(MDApp):

    Builder.load_string(open('cliente.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/card_button.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/table_schedule.kv', encoding='utf-8').read())
    Builder.load_string(open('module_screen/my_box_categorie.kv', encoding='utf-8').read())
    def build(self):
        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()