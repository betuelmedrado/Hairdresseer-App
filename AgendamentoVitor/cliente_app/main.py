
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
import json
from kivymd.toast import toast

from functools import partial
from datetime import datetime, timedelta

# from datetime import datetime

Window.size = 590,800

class Manager(ScreenManager):
    pass

class HomePage(Screen):
    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao.json'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.id_manager = self.id_manager()

    def on_pre_enter(self, *args):
        self.get_info()
        self.creat_files()

    def id_manager(self, *args):
        id = ''
        requisicao = requests.get(self.LINK_SALAO)
        requisicao_dic = requisicao.json()
        for ids in requisicao_dic:
            id = ids
        return id

    def get_info(self,*args):

        self.ids.my_card_button.clear_widgets()

        lista = []

        check_image_manager = self.check_manager_scheduling()
        check_socio = self.check_socio_scheduling()

        print(self.id_manager)
    # geting the id of manager
        try:
            LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}.json'
            requisicao_id = requests.get(LINK_ID)
            requisicao_id_dic = requisicao_id.json()

            if check_image_manager:
                my_card_button = MyCardButton(self.id_manager, requisicao_id_dic['nome'])
                my_card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                self.ids.my_card_button.add_widget(my_card_button)
            else:
                self.ids.my_card_button.add_widget(MyCardButton(self.id_manager, requisicao_id_dic['nome']))

            for id_socio in requisicao_id_dic['socios']:
                lista.append(id_socio)
        except:
            pass

        # geting the id of client
        for id_socio in lista:
            LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_socio}.json'
            requisicao_to_socio = requests.get(LINK_ID)
            requisicao_to_socio_dic = requisicao_to_socio.json()

            if check_socio:
                my_card_button = MyCardButton(id_socio, requisicao_to_socio_dic['nome'])
                my_card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                self.ids.my_card_button.add_widget(my_card_button)
            else:
                self.ids.my_card_button.add_widget(MyCardButton(id_socio, requisicao_to_socio_dic['nome']))

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
            LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/agenda.json'
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

        try:
            LINK = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios.json'
            requisicao = requests.get(LINK)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic.values():
                list_of_id.append(id['agenda'])

            if id_user['id_user'] in list_of_id:
                return True
            else:
                return False
        except:
            return False

class Register(Screen):

    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

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
                MDApp.get_running_app().root.current = 'homepage'
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

    def logar(self,*args):
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
            self.save_refreshtoken(refresh_token)
            MDApp.get_running_app().root.current = 'homepage'
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

                idtoken = requisicao_dic['idToken']
                localid = requisicao_dic['localId']
                refreshtoken = requisicao_dic['refreshToken']

                print(requisicao_dic)

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

class Table_shedule(MDBoxLayout):
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='',**kwargs):

        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2

class TableInfo(MDBoxLayout):
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='',**kwargs):

        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2

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

        # agendados = self.dados[1]
        # print(agendados)

        LINK_ID_MANAGER = requests.get('https://shedule-vitor-default-rtdb.firebaseio.com/salao.json')
        for id in LINK_ID_MANAGER.json():
            self.id_manager = id

        # Link of SALÃO ##############################################################################
        self.LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}'

        self.user_id = self.log_aut()


    def get_id_proficional(self, *args):
        with open('write_id_manager.json', 'r') as arquivo:
            id_informing = json.load(arquivo)
        return id_informing

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

        try:
            # Here to geting the id of manager to get schedule #######################################
            requisicao = requests.get(self.LINK_SALAO + '.json')
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']

            self.entrada = requisicao_dic['entrada']
            self.minuto_entrada = int(requisicao_dic['entrada'][3:])

            self.saida = requisicao_dic['saida']
            self.minuto_saida = int(requisicao_dic['saida'][3:])

            self.space_temp = requisicao_dic['space_temp']

            self.ids.title_toobar.title = f'Agenda {str(nome)}'

            try:
                for id_agenda in requisicao_dic['agenda']:
                    LINK_SCHEDULE = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{id_manager}/agenda/{id_agenda}.json'
                    requisicao_schedule = requests.get(LINK_SCHEDULE)
                    requisicao_schedule_dic = requisicao_schedule.json()
                    lista_info.append(requisicao_schedule_dic)
                return lista_info
            except:
                return lista_info

        #information socio ############################################################################################
        except TypeError:

                # Here if not manager then get the socio #########################################################################
            LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager}.json'
            requisicao = requests.get(LINK_SALAO)
            requisicao_dic = requisicao.json()

            nome = requisicao_dic['nome']

            self.entrada = requisicao_dic['entrada']
            self.minuto_entrada = int(requisicao_dic['entrada'][3:])

            self.saida = requisicao_dic['saida']
            self.minuto_saida = int(requisicao_dic['saida'][3:])

            self.space_temp = requisicao_dic['space_temp']

            self.ids.title_toobar.title = f'Agenda {str(nome)}'

            for id_agenda in requisicao_dic['agenda']:
                LINK_SCHEDULE = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager}/nome.json'
                requisicao_schedule = requests.get(LINK_SCHEDULE)
                requisicao_schedule_dic = requisicao_schedule.json()
                lista_info.append(requisicao_schedule_dic)
                print(requisicao_schedule_dic)
            return lista_info

    def actualizar(self, *args):

        # get user id ##################################################################################################
        user_id = self.log_aut()
        lista_info = self.info_entrace_salao()
        list_content = []

        entrada = self.entrada
        saida = self.saida
        tempo = self.space_temp
        # lista = ['']
        block = False
        permition_to_sum = True

        # To conting the position of schedule to verification of next schedule
        cont = 0

        self.ids.grid_shedule.clear_widgets()

        # self.ids.grid_shedule.add_widget(Table_shedule('', '', entrada, '', ''))

        # try:
        while entrada[:2] < saida[:2]:

            for num, agenda in enumerate(lista_info):
                try:
                    if entrada[:2] == lista_info[num]['id_horas'][:2]:
                        for mim in range(0,60):
                            if str(mim).zfill(2) == lista_info[num]['id_horas'][3:]:
                                entry = datetime.strptime(entrada,'%H:%M')

                                temp = lista_info[num]['tempo']
                                hours, minute = map(int,temp.split(':'))
                                delta_temp = timedelta(hours=hours, minutes=minute)
                                soma_horas = entry + delta_temp

                                if user_id == lista_info[num]['id_user']:
                                    # Insert table #####################################################################################
                                    table = TableInfo(str(cont), '', entrada, 'Você agendou esse horarion', f'{soma_horas.strftime("%H:%M")}')
                                    self.ids.grid_shedule.add_widget(table)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    break
                                else:
                                    table = Table_block(str(cont), '', entrada, 'Agendado!', f'{soma_horas.strftime("%H:%M")}')
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append(entrada)
                                    entrada = soma_horas.strftime('%H:%M')
                                    block = True
                                    permition_to_sum = False
                                    break
                except:
                    print('Deu algum erro na função actualizar da class "ViewSchedule"')
        # except:
        #     print('Deu algum erro na função actualizar da class "ViewSchedule"')

            # Here block to not have repetition ########################################################################
            # Aqui bloqueia para não ter repetições
            if block == False:
                table = Table_shedule(str(cont), '', entrada, f'', '')
                self.ids.grid_shedule.add_widget(table)
                list_content.append('')
                permition_to_sum = True
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
        with open('list_content.json','w') as file:
            json.dump(list_content, file)

    def _actualizar(self, *args):
        pass
    #     """
    #     funciont what receiv the actualization of screen
    #     :param args:
    #     :return:
    #     """
    #     info = None
    #     lista_info = ''
    #     lista_content = []
    #     soma_horas = ''
    #
    #     # this variable is to see which field I will insert
    #     # esta variavel  é para ver qual campo e vou inserir
    #     if_insert_fild_empyt = False
    #
    #     self.ids.grid_shedule.clear_widgets()
    #
    #     id_manager = self.get_id_proficional()
    #
    #     try:
    #         # Here to geting the id of manager to get schedule #######################################
    #         LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{id_manager}.json'
    #         requisicao = requests.get(LINK_SALAO)
    #         requisicao_dic = requisicao.json()
    #
    #         nome = requisicao_dic['nome']
    #
    #         self.entrada = int(requisicao_dic['entrada'][:2])
    #         self.minuto_entrada = int(requisicao_dic['entrada'][3:])
    #
    #         self.saida = int(requisicao_dic['saida'][:2])
    #         self.minuto_saida = int(requisicao_dic['saida'][3:])
    #
    #         self.ids.title_toobar.title = f'Agenda {str(nome)}'
    #
    #     except TypeError:
    #
    #         # Here if not manager then get the socio #########################################################################
    #         LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id_manager}.json'
    #         requisicao = requests.get(LINK_SALAO)
    #         requisicao_dic = requisicao.json()
    #
    #         nome = requisicao_dic['nome']
    #
    #         self.entrada = int(requisicao_dic['entrada'][:2])
    #         self.minuto_entrada = int(requisicao_dic['entrada'][3:])
    #
    #         self.saida = int(requisicao_dic['saida'][:2])
    #         self.minuto_saida = int(requisicao_dic['saida'][3:])
    #
    #         self.ids.title_toobar.title = f'Agenda {str(nome)}'
    #
    #     # ID to know the profissional in the area ###############################################
    #     id_informing = self.get_id_proficional()
    #
    #     LINK_DATA = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{id_informing}/agenda.json'
    #     requisicao = requests.get(LINK_DATA)
    #     requisicao_dic = requisicao.json()
    #
    #     # formating the table of hours ##########################################################
    #     # for enum,informacao in enumerate(range(self.entrada,self.saida + self.entrada + 1)):
    #     print('entrada', self.entrada)
    #     print('saida', self.saida)
    #
    #     enum = 0
    #     while enum <= self.saida :
    #         if_insert_fild_empyt = False
    #
    #         # hours formated ###################################################################
    #         horas = f'{str(enum).zfill(2)}:{str(self.minuto_entrada).zfill(2)}'
    #         # horas = f'{self.entrada}'
    #
    #         # entrada = datetime.strptime(horas, '%H:%M')
    #
    #
    #         if enum < self.entrada:
    #
    #         # just to get list position  inside of schedule position###############################
    #         # apenas para obter a posição da lista dentro da posição da agenda ####################
    #             lista_content.append('')
    #
    #         # here only go intry if the hours go bigger or equal
    #         # aqui só entra se o horário for maior ou igual
    #         if enum >= self.entrada:
    #
    #             try:
    #         # percorrendo alista para saber a posicao que o agendamento vai entrar ################
    #                 for agenda in requisicao_dic.values():
    #                     lista_info = (agenda)
    #
    #                     if enum == int(lista_info['id_posicao']):
    #
    #                         hour_table = horas # geting the hours
    #                         inicio = datetime.strptime(hour_table,'%H:%M') # formating the hours ############
    #                         tempo = lista_info['tempo'] # get work time #####################################
    #                         hours, minutos = map(int,tempo.split(':')) # formating hours
    #
    #                         termino = timedelta(hours=hours, minutes=minutos)
    #
    #                         soma = inicio + termino
    #                         soma_horas = soma.strftime('%H:%M')
    #
    #                         # print(soma_horas[:2])
    #                         # print(soma_horas[3:])
    #
    #                         self.minuto_entrada = int(soma_horas[3:])
    #
    #                         # comparing the id of user ######################################################
    #                         block = self.log_aut()
    #
    #                         print('soma horas ',soma_horas)
    #                         if block == lista_info['id_user']:
    #                             table = Table_shedule(str(enum), str(enum), horas,'Você agendou esse horário',str(soma_horas))
    #                             lista_content.append(lista_info['id_horas'])
    #                             self.ids.grid_shedule.add_widget(table)
    #                             horas = soma_horas
    #                             enum = int(soma_horas[:2])
    #                         else:
    #                             libera = Table_block(str(enum), str(enum), lista_info['id_horas'], 'Agendado!',str(soma_horas))
    #                             self.ids.grid_shedule.add_widget(libera)
    #                             lista_content.append(lista_info['id_horas'])
    #                             horas = soma_horas
    #                             enum = int(soma_horas[:2])
    #
    #                         # To insert empty field ##########################################################
    #                         if_insert_fild_empyt = True
    #             except AttributeError:
    #                 pass
    #
    #         if enum >= self.entrada and if_insert_fild_empyt == False:
    #             print('last soma ', soma_horas)
    #             horas = f'{str(enum-1).zfill(2)}:{str(soma_horas[3:]).zfill(2)}'
    #             if soma_horas[3:] != '00':
    #                 self.ids.grid_shedule.add_widget(Table_shedule(str(enum), str(enum), horas,'',f'{str(enum).zfill(2)}:00'))
    #             else:
    #                 self.ids.grid_shedule.add_widget(Table_shedule(str(enum), str(enum), horas,'',str()))
    #             lista_content.append('')
    #         horas = soma_horas
    #
    #         with open('list_content.json','w') as lista:
    #             json.dump(lista_content, lista)
    #         enum += 1
    #     print(lista_content)

    # Open and inserting the hours in class HoursSchedule #######################################

    def spiner(self,id_button, hours, *args, **kwargs):
        self.spiner = MDSpinner(size_hint=(None, None,), size=('46dp', '46dp'), pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.spiner)
        Clock.schedule_once(partial(self.popup_mark_off, id_button, hours),2)

    def popup_mark_off(self,id_button,hours, *args, **kwargs):
        id_user = ''
        info_schedule = self.info_entrace_salao()
        for id in info_schedule:
            if id['id_user'] == self.user_id:
                id_user = id['id_user']


        box = MDBoxLayout(orientation='vertical')
        box_button = MDBoxLayout(padding=15,spacing=15)



        img = Image(source='images/atencao.png')

        bt_sim = Button(text='Sim',background_color=(0,1,1,1),color=(1,0,0,.8), size_hint=(1,None),width='23dp')
        bt_nao = Button(text='Não',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),width='23dp')
        bt_view = Button(text='View',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),width='23dp')

        box_button.add_widget((bt_sim))
        box_button.add_widget((bt_nao))
        box_button.add_widget((bt_view))

        box.add_widget((img))
        box.add_widget((box_button))

        popup  = Popup(title='Deseja cancelar o agendamento?',
                       size_hint=(.8,.5),content=box)

        bt_sim.bind(on_release = partial(self.cancel_schedule, id_user))
        bt_nao.bind(on_release = popup.dismiss)

        popup.open()

    def cancel_schedule(self, id_user, *args, **kwargs):
        link = self.LINK_SALAO +'/'+'agenda/'+f'{id_user}.json'
        requisicao = requests.delete(link)
        self.actualizar()

    def get_hours(self,id_button, hours):
        hours_dic = {}

        hours_dic['id_posicao'] = id_button
        hours_dic['horas'] = hours

        with open('info_schedule.json','w') as arquivo:
            json.dump(hours_dic, arquivo, indent=2)

        MDApp.get_running_app().root.current = 'hoursschedule'

    def on_pre_enter(self, *args):
        self.actualizar()

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'


class HoursSchedule(Screen):

    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao/'
    def __init__(self,hours='', **kwargs):
        super().__init__(**kwargs)
        # Clock.schedule_once(self.get_works, 2)
        self.hours = hours

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

    def on_leave(self, *args):
        self.ids.categorie.clear_widgets()

    def get_id_manager(self):
        with open('write_id_manager.json','r') as arquivo:
            id_manager = json.load(arquivo)
        return id_manager

    def get_works(self,*args):
        self.ids.categorie.clear_widgets()

        lista = []
        lista_name = []
        lista_color = []
        self.id_manager = self.get_id_manager()

# LINK DATA BASE
        link = self.LINK_SALAO + self.id_manager + '.json'

        try:
            requisicao = requests.get(link)
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
                link_id = self.LINK_SALAO + self.id_manager + '/' + 'servicos' + '/' + id_work + '.json'
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
                work_socio = self.LINK_SALAO + self.id_manager + '/' + 'socios' + '/' + id_work + '.json'
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

            # print(servico)

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
            toast('O gendamento excede o horario do proximo agendamento escolha outro horario ou outro cabeleleiro!', duration=6)
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
        print('nadaa')

    def disable_release(self,*args):
        print('disablad')

    def save_scheduleing(self, *args):

        list_work = []

        # geting the id of Manager ##############################
        name_id = self.get_id_manager()

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

        link = self.LINK_SALAO + name_id +'/'+'agenda'+'/'+ id_user + '.json'

        info = f'{{"id_posicao":"{id_pos["id_posicao"]}",' \
               f'"id_horas":"{horas}",' \
               f'"id_user":"{id_user}",' \
               f'"tempo":"{tempo}",' \
               f'"valor":"{valor}",' \
               f'"nome":"{nome}",'\
               f'"servicos":"{list_works}"}}'

        requisicao = requests.patch(link, data=info)

        toast('Agendamento criado! Você tem Uma(1) Hora para cancelar\n "3" cancelamento abaixo disso você tera que pagar uma taxa', duration=10)

        # Clearing file "select_work" after of save #################
        with open('select_works.json','w') as file:
            json.dump([], file)


class MyCardButton(MDCard):

    def __init__(self,id_user='',nome='', **kwargs):
        super().__init__(**kwargs)

        self.id_user = id_user
        self.nome = nome

    def send_info(self,id_user):
        print(id_user)

        with open('write_id_manager.json', 'w') as arquivo:
            json.dump(id_user, arquivo)

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
        self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()