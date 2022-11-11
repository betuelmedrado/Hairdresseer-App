
#requere python 3.8

# kivymd ###
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDTextButton, MDFlatButton, MDRaisedButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivymd.uix.taptargetview import MDTapTargetView

# kivy ###
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import NumericProperty

# importando firebase
import requests
import os
import certifi
import json

from functools import partial
from datetime import datetime, timedelta

from random import randint
import webbrowser

# from datetime import datetime

Window.size = 400,820

os.environ["SSL_CERT_FILE"] = certifi.where()

class Manager(ScreenManager):
    pass


class HomePage(Screen):
    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com'
    lista_id_user = []

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.day_semana = datetime.today().isoweekday()

        # Creating the files go then open app
        Clock.schedule_once(self.creat_files, 1)

        self.id_manager = self.get_id_manager()
        self.id_socios = self.get_id_socios()
        # Clock.schedule_once(self.get_client_data, 2)
        Clock.schedule_once(self.get_info, 1)
        Clock.schedule_once(self.get_local, 1)

    def call_back(self,windown, key, *args):

        if key == 27:
            try:
                MDApp().stop()
            except:
                raise

        else:
            pass



    def help(self):

        help_text = '"Atenção!" antes de fazer seu agendamento certifique-se que ira comparecer ao estábelecimento. ' \
                    'O não comparecimento no horárion pode ser cobrado uma taxa pelo salão!' \
                    ' Você tem a opção de cancelar o agendamento dentro do tempo estabecido pelo salão!'

        infohelp = ''
        try:
            with open('infohelp.txt', 'r', encoding='utf-8') as help:
                infohelp = help.read()
        except:
            with open('infohelp.txt', 'w', encoding='utf-8') as help:
                infohelp = help.write(help_text)

            with open('infohelp.txt', 'r', encoding='utf-8') as help:
                infohelp = help.read()

        button_ok = MDFlatButton(text='OK')

        dialog = MDDialog(title='Menssagen importante!',text=str(infohelp), buttons=[button_ok])

        button_ok.bind(on_release=dialog.dismiss)

        dialog.open()

    def load_widget(self, *args, **kwargs):

        # The "md_label" not show!
        md_label = MDLabel(text='Carregando...', color=(1,1,1,1))
        spiner = MDSpinner(active=True, size_hint=(None,None), size=('56dp','56dp'), pos_hint=({'center_x':.5,'center_y':.5}))
        self.box_dialog = MDDialog(buttons=[md_label])


        self.box_dialog.add_widget(spiner)
        # self.parent.parent.add_widget(self.boxlayout)
        self.box_dialog.open()

    def on_pre_enter(self, *args):

        Window.bind(on_keyboard=self.call_back)

        # Here to when entry or exit of Viwshcedule exclud content of file
        with open('select_works.json','w') as exclud_content:
            json.dump([],exclud_content)


        with open('load_home.json','r') as load_h:
            load_home = json.load(load_h)

        # Permition to load scree home ###################################
        if load_home['load_home']:
            # toast('Aguarde carregando as informações!...')
            self.load_widget()
            Clock.schedule_once(self.get_info, 1)

            load = {}
            load['load_home'] = False
            with open('load_home.json', 'w') as load_home:
                json.dump(load, load_home, indent=2)
        else:
            pass
        return True


    # def get_client_data(self, *args):
    #     try:
    #         with open('info_user.json','r') as file:
    #             info = json.load(file)
    #
    #         link = f'{self.LINK_SALAO}/client/{info["id_user"]}.json'
    #
    #         requisicao = requests.get(link)
    #         requisicao_dic = requisicao.json()
    #
    #         data_dic = {}
    #
    #         data_dic["nome"] = requisicao_dic["nome"]
    #
    #         # Here is to insert a cpf valid! ##################################
    #         try:
    #             data_dic["cpf"] = requisicao_dic["cpf"]
    #         except:
    #             data_dic["cpf"] = str("00000000000")
    #
    #         #  Here insert the e-mail if it is not e-mail ######################
    #         try:
    #             data_dic["email"] = requisicao_dic["email"]
    #         except:
    #             data_dic["email"] = ''
    #
    #         data_dic["bloqueado"] = requisicao_dic["bloqueado"]
    #         data_dic["quant_cancelado"] = requisicao_dic["quant_cancelado"]
    #
    #         with open('get_client_data.json','w', encoding='utf-8') as file_data:
    #             json.dump(data_dic, file_data, indent=2)
    #     except:
    #         pass

    def get_inf_schedule(self, *args):
        pass

    def get_local(self, *args):
        try:
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_id_manager(self, *args):
        try:
            link = f'{self.LINK_SALAO}/salao.json'
            id = ''
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
            for ids in requisicao_dic:
                id = ids
            return id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_info(self,*args, **kwargs):

        self.ids.my_card_button.clear_widgets()
        try:
            # with open('info_user.json', 'r') as file:
            #     id_user = json.load(file)

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
                    self.my_card_button = MyCardButton(requisicao_id_dic['manager'], self.id_manager, requisicao_id_dic['nome'])
                    self.my_card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                    self.ids.my_card_button.add_widget(self.my_card_button)
                else:
                    self.ids.my_card_button.add_widget(MyCardButton(requisicao_id_dic['manager'], self.id_manager, requisicao_id_dic['nome']))

                # for id_socios in requisicao_id_dic['socios']:
                #     lista.append(id_socios)
            except:
                pass

            # getting ids of user which is schedule ############################################################################
            # for enum, id in enumerate(lista):

            for enum, id in enumerate(self.id_socios[0]):
                try:
                    # Here getting socio to read of data ##############################################################################
                    # LINK_ID = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios/{id}.json'
                    # requisicao_to_socio = requests.get(LINK_ID)
                    # requisicao_to_socio_dic = requisicao_to_socio.json()
                    requisicao_to_socio_dic = self.get_id_socios()

                    try:
                        if check_socio[enum]:
                            card_button = MyCardButton(requisicao_to_socio_dic[1][id]['manager'], id, requisicao_to_socio_dic[1][id]['nome'])
                            card_button.ids.image_check.add_widget(Image(source='images/check.png'))
                            self.ids.my_card_button.add_widget(card_button)
                        else:
                            self.ids.my_card_button.add_widget(MyCardButton(requisicao_to_socio_dic[1][id]['manager'], id, requisicao_to_socio_dic[1][id]['nome']))
                    except:
                        self.ids.my_card_button.add_widget(
                            MyCardButton(requisicao_to_socio_dic[1][id]['manager'], id, requisicao_to_socio_dic[1][id]['nome']))
                except:
                    pass
            try:
                Clock.schedule_once(self.box_dialog.dismiss,2)
            except:
                pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_id_socios(self, *args):

        lista_id_socio = []
        try:
            LINK_SOCIOS = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}/socios.json'
            requisicao = requests.get(LINK_SOCIOS)
            requisicao_dic = requisicao.json()

            data_dic = requisicao_dic

            for id in requisicao_dic:
                lista_id_socio.append(id)

            # passing a lista of ids and a list of data ####
            return lista_id_socio, data_dic

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def creat_files(self, *args):
        try:
            with open('select_works.json','r') as select:
                json.load(select)
        except FileNotFoundError:
            with open('select_works.json','w') as select:
                json.dump([],select)

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

        try:
            with open('infoscheduleclient.json', 'r') as file_info:
                json.load(file_info)
        except:
            with open('infoscheduleclient.json', 'w') as file_info:
                json.dump('', file_info)

        try:
            with open('inf_to_infoschedule_drawer.json', 'r') as file_info:
                json.load(file_info)
        except:
            with open('inf_to_infoschedule_drawer.json', 'w') as file_info:
                json.dump('', file_info)

        try:
            with open('get_client_data.json', 'r') as file_data:
                json.load(file_data)
        except:
            with open('get_client_data.json', 'w') as file_data:
                json.dump('', file_data)

        try:
            with open('load_home.json', 'r') as load_home:
                json.load(load_home)
        except:
            load = {}
            load['load_home'] = False
            with open('load_home.json', 'w') as load_home:
                json.dump(load, load_home, indent=2)

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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
            return False
        except:
            return False

    def check_socio_scheduling(self, *args):
        """
        function to insert image ok in button of barber
        :param args:
        :return: list_of_id whith true or false
        """
        list_of_id = []

        with open('info_user.json', 'r') as file:
            id_user = json.load(file)

        try:
            for enum, idsocio in enumerate(self.id_socios[0]):
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
                            pass
                            # list_of_id.append(False)
                except:
                    list_of_id.append(False)

            return list_of_id
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
            list_of_id.append(False)
            return list_of_id
        except:
            list_of_id.append(False)
            return list_of_id


class Register(Screen):

    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"
    link = f'https://shedule-vitor-default-rtdb.firebaseio.com'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Verify if have msg to the app ####


    def on_pre_enter(self, *args):
        Clock.schedule_once( self.get_msg_to_app, 1)
#     Clock.schedule_once(self.log_aut,1)

    def info_msg_user(self, *args):
        # with open('info_user.json', 'r') as file:
        #     id_user = json.load(file)
        #
        # link = f'{self.link}/client/{id_user["id_user"]}.json'
        #
        # requisicao = requests.get(link)
        # requisicao_dic = requisicao.json()

        try:
            with open('msg_to_app.json', 'r') as file_msg:
                msg = json.load(file_msg)
        except FileNotFoundError:
            link = f'{self.link}/msg_to_app.json'

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
            msg = requisicao_dic['msg_client']

            with open('msg_to_app.json', 'w') as file_msg:
                json.dump(msg, file_msg, indent=2)

            with open('msg_to_app.json', 'r') as file_msg:
                msg = json.load(file_msg)

        return msg

    def get_msg_to_app(self, *args):

        # Geting the info of user app msg ######
        info_msg_user = self.info_msg_user()

        # Link to see if have msg #############
        link = f'{self.link}/msg_to_app.json'

        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        try:
            msg = requisicao_dic['msg_client']

            if int(info_msg_user['valid']) < int(msg['valid']):
                # with open('msg_to_app.json','w',encoding='utf-8') as file:
                #     json.dump(msg, file, indent=2)

                self.show_msg_to_app()
            else:
                self.log_aut()
        except:
            pass

    def show_msg_to_app(self,*args):
        MDApp.get_running_app().root.current = 'msgtoapp'

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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
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
        try:
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
            return lista_info_ids

    def get_client_data(self, *args):
        try:
            with open('info_user.json','r') as file:
                info = json.load(file)

            link = f'{self.link}/client/{info["id_user"]}.json'

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            data_dic = {}

            data_dic["nome"] = requisicao_dic["nome"]

            # Here is to insert a cpf valid! ##################################
            try:
                data_dic["cpf"] = requisicao_dic["cpf"]
            except:
                data_dic["cpf"] = str("00000000000")


            #  Here insert the e-mail if it is not e-mail ######################
            try:
                data_dic["email"] = requisicao_dic["email"]
            except:
                data_dic["email"] = ''

            data_dic["bloqueado"] = requisicao_dic["bloqueado"]
            data_dic["quant_cancelado"] = requisicao_dic["quant_cancelado"]

            with open('get_client_data.json','w', encoding='utf-8') as file_data:
                json.dump(data_dic, file_data, indent=2)
        except:
            pass

    def logar(self,*args):

        try:
            lista_info_ids = self.not_can_client()

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

                    # Call the function that read the costomer data ######################
                    # função de chamada que lê os dados do cliente
                    self.get_client_data()

                    MDApp.get_running_app().root.current = 'homepage'
                else:
                    self.ids.warning.text = 'Email ou senha [color=D40A00]Invalida[/color]\n[size=15]Faça o seu cadastro logo abaixo![/size]'
            else:
                erro = str(requisicao_dic['error']['message'])

                if erro == 'INVALID_EMAIL':
                    self.ids.warning.text = 'Email [color=D40A00]Invalido[/color]\n[size=15]Faça o seu cadastro logo abaixo![/size]'
                elif erro == 'MISSING_PASSWORD':
                    self.ids.warning.text = 'Sem informação de [color=D40A00]Senha[/color]'
                elif erro == 'INVALID_PASSWORD':
                    self.ids.warning.text = 'Senha [color=D40A00]Invalido[/color]'
                elif erro == 'EMAIL_NOT_FOUND':
                    self.ids.warning.text = 'Email não [color=D40A00]Encontrado[/color]\n[size=15]Faça o seu cadastro logo abaixo![/size]'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def password_view(self, msg):
        if msg.password == False:
            self.ids.senha.password = True
            self.ids.eye.icon = 'eye-off'
        elif msg.password == True:
            self.ids.senha.password = False
            self.ids.eye.icon = 'eye'


class CreatBill(Screen):
    #idToken
    #refreshToken
    #localId
    API_KEY = "AIzaSyAue2_eYU5S5TsUc692vHNlyxIHrlBVZjk"

    def cpf_validate(self,numbers):
        try:
            #  Obtém os números do CPF e ignora outros caracteres
            # cpf = [int(char) for char in numbers if char.isdigit()]
            cpf = []

            for char in numbers:
                if char.isdigit():
                    cpf.append(int(char))

            #  Verifica se o CPF tem 11 dígitos
            if len(cpf) != 11:
                return False

            #  Verifica se o CPF tem todos os números iguais, ex: 111.111.111-11
            #  Esses CPFs são considerados inválidos mas passam na validação dos dígitos
            #  Antigo código para referência: if all(cpf[i] == cpf[i+1] for i in range (0, len(cpf)-1))
            if cpf == cpf[::-1]:
                return False

            #  Valida os dois dígitos verificadores
            for i in range(9, 11):
                value = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
                digit = ((value * 10) % 11) % 10
                if digit != cpf[i]:
                    return False
            return True
        except:
            return False

    def valid_field(self):

        cpf = self.ids.cpf.text

        if self.cpf_validate(cpf):
            if self.ids.nome.text == '':
                self.ids.warning.text = 'Sem informação de [color=#D40A00][b]nome[/b][/color]'
                return False
            elif self.ids.senha.text != self.ids.rep_senha.text:
                self.ids.warning.text = 'Confirmação de [color=#D40A00][b]Senha[/b][/color] Invalid'
                return False
            elif self.ids.senha.text == '' or self.ids.rep_senha.text == '':
                self.ids.warning.text = 'Campo de [color=#D40A00][b]Senha[/b][/color] vazio!'
                return False
            else:
                return True

        elif self.ids.cpf.text == '':
            self.ids.warning.text = 'Campo de [color=#D40A00][b]cpf[/b][/color] vazio!'
            return False
        else:
            self.ids.warning.text = '[color=#D40A00][b]CPF invalido![/b][/color]'
            return False

    def fire_base_creat(self,idtoken,localid,refreshtoken):
        """
        Here creat the account of user
        :param idtoken:
        :param localid: the id of user
        :param refreshtoken: for permanent login
        :return:
        """

        try:
            LINK_FIREBASE = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{localid}.json'

            with open('refreshtoken.json','w') as arquivo:
                json.dump(refreshtoken, arquivo)

            nome = self.ids.nome.text
            email = self.ids.email.text
            cpf = self.ids.cpf.text

            # info_user = '{"avatar":"photos2.png", "equipe":"", "total_vendas":"0","vendas":""}'
            info_user = f'{{"nome":"{nome}",' \
                        f'"cpf":"{cpf}",' \
                        f'"email":"{email}",' \
                        f'"quant_cancelado":"0",' \
                        f'"bloqueado":"False",' \
                        f'"ids_agendado":"",' \
                        f'"msg":{0},' \
                        f'"id":"{localid}" }}'

            creat_user = requests.patch(LINK_FIREBASE, data=info_user)

            # dictionary to save the data of client
            info_data_client = {}
            info_data_client["nome"] = nome
            info_data_client["cpf"] = cpf
            info_data_client["email"] = email
            info_data_client["bloqueado"] = "False"
            info_data_client["quant_cancelado"] = "0"

            # savaing the data of cliente creat
            with open('get_client_data.json', 'w') as save_info:
                json.dump(info_data_client, save_info, indent=2)


            info_user_dic = {}

            info_user_dic['id_user'] = localid
            info_user_dic['id_token'] = idtoken

            with open('info_user.json', 'w') as file:
                json.dump(info_user_dic, file, indent=2)

        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def creat_bill(self, *args, **kwargs):

        if self.valid_field() :
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
            except requests.exceptions.ConnectionError:
                toast('Você não esta conectado a internet!')
        else:
            pass

    def password_view(self, msg):
        if msg.password == False:
            self.ids.senha.password = True
            self.ids.eye.icon = 'eye-off'
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
                toast('Foi enviado uma mensagem no email informado para redefinir a senha!')
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
    def __init__(self,id_button='',id_schedule='',hours='',client='',hours2='', time='', time_cancel='',**kwargs):

        super().__init__(**kwargs)
        self.id_button = id_button
        self.id_schedule = id_schedule
        self.hours = str(hours)
        self.client = str(client)
        self.hours_2 = hours2
        self.time = time
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

    # Variable to loading the screen again "X" e "Y"
    x = NumericProperty(0)
    y = NumericProperty(0)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        # Geting day actual ##########################################################################
        self.dia_atual = datetime.today().isoweekday()

        Clock.schedule_once(self.call_init,2)

    def load_widget(self, *args, **kwargs):

        # The "md_label" not show!
        md_label = MDLabel(text='Carregando...', color=(1, 1, 1, 1))
        spiner = MDSpinner(active=True, size_hint=(None, None), size=('56dp', '56dp'),
                           pos_hint=({'center_x': .5, 'center_y': .5}))
        self.box_dialog = MDDialog(buttons=[md_label])

        self.box_dialog.add_widget(spiner)
        # self.parent.parent.add_widget(self.boxlayout)
        self.box_dialog.open()

    def call_init(self, *args):
        try:
            LINK_ID_MANAGER = requests.get('https://shedule-vitor-default-rtdb.firebaseio.com/salao.json')
            for id in LINK_ID_MANAGER.json():
                self.id_manager = id

            # Link of SALÃO ##############################################################################
            self.LINK_SALAO = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}'

            # Geting information of manager ##############################################################
            self.info_manager = self._info_manager()
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def _info_manager(self, *args):
        try:
            link = f'{self.LINK_SALAO}.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            return requisicao_dic
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.actualizar, 1)
        self.user_id = self.log_aut()
        Window.unbind(on_keyboard=self.call_back)
        Window.bind(on_keyboard=self.call_back)

    def call_back(self,windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'homepage'
            return True
        else:
            pass

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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def info_entrace_salao(self, *args):
        id_manager = self.get_id_proficional()
        lista_info = []
        lista_requisicao = []

        try:
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

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

            # Time Mensage of cancel ot schedule #############################
            time_cancel = f'[color=#6B0A00][b]"Atenção":[/b][/color] Você tem [b]{time_c}[/b] [size=13]H/M[/size] para desmarcar apos agendamento!'

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
                    ranger_init = 0
                    try:

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
                                        table = TableInfo(str(cont), lista_info[num]['id_user'], entrada, 'Você agendou esse horarion', f'{soma_horas.strftime("%H:%M")}', lista_info[num]['tempo'], time_cancel)
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
                                        cont += 1
                                        break

                                # para não dá erro, de sumir o agendamento anterior
                                elif str(int(mim) + 1).zfill(2) == tempo[3:] and soma_future.strftime('%H:%M') <= lista_info[0]['id_horas'] :

                                    # elif str(mim).zfill(2) == tempo[3:] and seletor_schedule == True :
                                    table = Table_shedule(str(cont), '', entrada, f'', '', time_cancel)
                                    self.ids.grid_shedule.add_widget(table)
                                    list_content.append('')
                                    block = True
                                    permition_to_sum = True
                                    ranger_init = entrada[3:]
                                    cont += 1

                    except:
                        raise

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
                            table = Table_shedule(str(cont), '', entrada, f'', '', time_cancel)
                            self.ids.grid_shedule.add_widget(table)
                            list_content.append('')
                            permition_to_sum = True
                            ranger_init = entrada[3:]
                            cont += 1
                        else:
                            permition_to_sum = True
                    except IndexError:
                        table = Table_shedule(str(cont), '', entrada, f'', '', time_cancel)
                        self.ids.grid_shedule.add_widget(table)
                        list_content.append('')
                        permition_to_sum = True
                        ranger_init = entrada[3:]
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
            with open('list_content.json','w') as file_list:
                json.dump(list_content, file_list)
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            toast('Nenhuma agenda para hoje!')

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

    def spiner(self,id_button, hours, *args, **kwargs):
        self.spiner = MDSpinner(size_hint=(None, None,), size=('46dp', '46dp'), pos_hint={'center_x': .5, 'center_y': .1})
        self.add_widget(self.spiner)
        Clock.schedule_once(partial(self.popup_mark_off, id_button, hours),2)

    def popup_mark_off(self,id_button='', id_schedule='', hours='', client='', hours_second='', time='', time_cancel='', *args, **kwargs):
        id_user = ''
        with open('info_user.json', 'r') as file:
            id_user = json.load(file)

        with open('infoscheduleclient.json','r') as info:
            info_schedule = json.load(info)
        try:
            hours_of_schedule = info_schedule['hours_of_schedule']
        except:
            hours_of_schedule = ''

        box = MDBoxLayout(orientation='vertical')
        box_button = MDBoxLayout(padding=5,spacing=5)

        img = Image(source='images/atencao.png')

        bt_sim = Button(text='Sim',background_color=(0,1,1,1),color=(1,0,0,.8), size_hint=(1,None),height='40dp')
        bt_view = Button(text='View',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')
        bt_nao = Button(text='Sair',background_color=(0,1,1,1),color=(0,0,0,1),size_hint=(1,None),height='40dp')

        box_button.add_widget((bt_sim))
        box_button.add_widget((bt_view))
        box_button.add_widget((bt_nao))

        box.add_widget((img))
        box.add_widget((box_button))

        self.popup  = Popup(title='Deseja cancelar o agendamento?',
                            size_hint=(.8,None), height='200dp',content=box)

        # bt_sim.bind(on_release = partial(self.cancel_schedule, id_user["id_user"]))
        bt_sim.bind(on_release = partial(self.wait_cancel_schedule, id_user["id_user"]))
        bt_view.bind(on_release=partial(self.wait_call_info_schedule, id_button, id_schedule, hours, client, hours_second, time, hours_of_schedule,time_cancel))
        bt_nao.bind(on_release = self.popup.dismiss)

        self.popup.open()

    def wait_call_info_schedule(self,id_button='',id_schedule='',hours='', client='', hours_second='', time='', hours_of_schedule='', time_cancel='', *args):
        self.load_widget()
        Clock.schedule_once(partial(self.call_info_schedule, id_button,id_schedule,hours, client, hours_second, time, hours_of_schedule, time_cancel, *args),2)


    def call_info_schedule(self,id_button='',id_schedule='',hours='', client='', hours_second='', time='', hours_of_schedule='', time_cancel='', *args):
        dic_info = {}
        horas_agendamento = hours_of_schedule

        dic_info['id_button'] = id_button
        dic_info['id_schedule'] = id_schedule
        dic_info['hours'] = hours
        dic_info['client'] = client
        dic_info['hours_second'] = hours_second
        dic_info['time'] = time
        dic_info["hours_of_schedule"] = str(horas_agendamento)
        dic_info['time_cancel'] = time_cancel

        with open('infoscheduleclient.json', 'w') as file:
            json.dump(dic_info, file, indent=2)

        MDApp.get_running_app().root.current = 'infoscheduleclient'

        Clock.schedule_once(self.box_dialog.dismiss, 3)

        try:
            self.popup.dismiss()
        except:
            pass

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

    def wait_cancel_schedule(self ,id_user, *args, **kwargs):
        self.load_widget()

        Clock.schedule_once(partial(self.cancel_schedule, id_user), 1)


    def cancel_schedule(self, id_user, *args, **kwargs):

        try:
            id_proficional = self.get_id_proficional()
            time_cancel = self.info_manager['time_cancel']

            link = ''

            time = self.format_hours(time_cancel)


            if id_proficional['manager'] == "False":
                link = self.LINK_SALAO + f'/socios/{id_proficional["id_user"]}/agenda/{self.dia_atual}/{id_user}.json'

            elif id_proficional['manager'] == "True":
                link = self.LINK_SALAO + f'/agenda/{self.dia_atual}/{id_user}.json'

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            cancelar = self.check_time_cancel(str(time_cancel),requisicao_dic['horas_agendamento'])

            if cancelar:
                try:
                    self.box_dialog.dismiss()
                except:
                    pass

                bt = MDFlatButton(text='OK')
                dialog = MDDialog(title='"Aviso!"',
                                  text=f'O agendamento não pode ser cancelado Passou do tempo de  "{time[0]}{time[1]}"!',
                                  radius=[40, 7, 40, 7], buttons=[bt])

                bt.bind(on_release=dialog.dismiss)
                dialog.open()

            else:
                requisicao = requests.delete(link)

                with open('inf_to_infoschedule_drawer.json','r') as read_file:
                    read = json.load(read_file)

                for pos, items in enumerate(read):
                    id = eval(items['id_proficional'])

                    if id['id_user'] == id_proficional['id_user']:
                        del(read[pos])

                with open('inf_to_infoschedule_drawer.json', 'w') as file:
                    json.dump(read, file, indent=2)
                self.actualizar()

                # Allow loading ##########################################
                load = {}
                load['load_home'] = True
                with open('load_home.json', 'w') as load_home:
                    json.dump(load, load_home, indent=2)

            self.popup.dismiss()
            self.box_dialog.dismiss()
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def dialog_of_mensagen(self,msg, *args):
        bt = MDFlatButton(text='OK!')
        dialog = MDDialog(title='"Aviso!"',
                          text=msg,
                           buttons=[bt])
        bt.bind(on_release=dialog.dismiss)
        dialog.open()

    def if_blocked(self,id_button, hours):
        self.load_widget()
        try:
            if self.agenda_marcada:
                Clock.schedule_once(self.dismiss_dialog, 1)
                self.dialog_of_mensagen('Você já tem um agendamento marcado aqui para fazer outro agendamento\nCancele o seu agendamento!')
            else:
                link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{self.user_id}.json'

                requisicao = requests.get(link)
                requisicao_dic = requisicao.json()

                try:
                    if requisicao_dic['bloqueado'] == 'True':
                        toast('Você foi bloqueado! Entre em contato com um proficional do salão! ')
                    elif requisicao_dic['bloqueado'] == 'False':
                        self.get_hours(id_button, hours)
                except:
                    pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_hours(self,id_button, hours):
        hours_dic = {}

        hours_dic['id_posicao'] = id_button
        hours_dic['horas'] = hours

        with open('info_schedule.json','w') as arquivo:
            json.dump(hours_dic, arquivo, indent=2)

        Clock.schedule_once(self.dismiss_dialog, 5)
        MDApp.get_running_app().root.current = 'hoursschedule'

    def dismiss_dialog(self, *args):
        self.box_dialog.dismiss()

    def on_leave(self, *args):
        self.ids.grid_shedule.clear_widgets()
        Window.unbind(on_keyboard=self.call_back)

    def format_hours(self, msg):

        time = ''

        horas = msg[0:2]
        minutos = msg[3:]


        if horas == '00' and minutos < '60':
            time = msg
            return msg, 'm'
        elif horas == '00' and minutos >= '60':
            time = '01:00'
            return time, 'h'
        elif horas != '00':
            time = msg
            return time, 'h'

    def return_homepage(self):
        MDApp.get_running_app().root.current = 'homepage'


class HoursSchedule(Screen):

    LINK_SALAO = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'
    def __init__(self,hours='', **kwargs):
        super().__init__(**kwargs)
        # Clock.schedule_once(self.get_works, 2)
        self.semana = datetime.today().isoweekday()

        self.day = datetime.today().day
        self.month = datetime.today().month
        self.year = datetime.today().year

        self.hours = hours
        self.id_manager = self.get_manager()

        self.LINK_SALAO_ID_MANAGER = f'https://shedule-vitor-default-rtdb.firebaseio.com/salao/{self.id_manager}'
        self.info_manager = self._info_manager()


    def on_pre_enter(self, *args):

        Window.bind(on_keyboard=self.call_back)

        try:
            with open('info_schedule.json', 'r') as arquivo:
                horas = json.load(arquivo)
            self.ids.hours.text = horas['horas']
        except FileNotFoundError:
            pass

        # self.ids.categorie.add_widget(MDSpinner(size_hint=(None,None,), size=('46dp','46dp'),color=(0,0,0,1),pos_hint={'center_x':.5,'center_y':.1}))
        Clock.schedule_once(self.get_works, 2)
        self.includ_color_select()
        self.soma_hours_values()

        self.valid_button_save()

    def call_back(self, windown, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'viewshedule'
        else:
            pass
        return True

    def _info_manager(self, *args):
        try:
            link = f'{self.LINK_SALAO_ID_MANAGER}.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            return requisicao_dic
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def valid_button_save(self):
        with open('select_works.json', 'r') as arquivo:
            my_select = json.load(arquivo)

        if my_select == []:
            self.ids.card_save.md_bg_color = 1, 0, 0, .1
            self.ids.color_card_fundo.md_bg_color = 0.55, 0.57, 0.63, 1
            self.ids.card_save.unbind(on_release=self.wait_save_scheduleing)
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
        Window.unbind(on_keyboard=self.call_back)
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
                    valor = (works_dic['valor'])


                    for iten in lista_color:
                        lista_name.append(iten['servico'])

                    if servico in lista_name:
                        self.ids.categorie.add_widget(MyBoxCategorie('',str(servico), str(tempo), str(float(valor)).replace('.',','), md_bg_color=[0.13, 0.53, 0.95,.2]))
                    else:
                        self.ids.categorie.add_widget(MyBoxCategorie('', str(servico), str(tempo), str(float(valor)).replace('.',',')))
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
            self.ids.color_card_fundo.md_bg_color = 0.55, 0.57, 0.63,1
            self.ids.card_save.unbind(on_release=self.wait_save_scheduleing)
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
            self.ids.color_card_fundo.md_bg_color = 0.55, 0.57, 0.63,1
            self.ids.card_save.unbind(on_release = self.wait_save_scheduleing)
            self.ids.card_save.bind(on_release = self.disable_release)

            self.disable_release()

        elif boolian == False:
            self.ids.card_save.unbind(on_release = self.disable_release)
            self.ids.card_save.md_bg_color = 0.13, 0.53, 0.95,1
            self.ids.color_card_fundo.md_bg_color = 0.13, 0.53, 0.95,1
            self.ids.card_save.bind(on_release = self.wait_save_scheduleing)

    def check_time(self, *args):
        pass

    def get_name_user(self, id_user, *args):
        try:
            LINK_DATA_NAME = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_user}.json'
            name = requests.get(LINK_DATA_NAME)
            name_dic = name.json()

            return name_dic
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def nada(self,*args):
        toast('Selecione o tipo de serviço!')

    def disable_release(self,*args):
        bt = MDFlatButton(text='OK!')
        dialog = MDDialog(title='"Aviso!"',
                          text='O gendamento excede o horario do proximo agendamento escolha outro horário ou outro barbeiro!',
                           buttons=[bt])
        bt.bind(on_release=dialog.dismiss)
        dialog.open()

    def sum_hours_end_time(self,hours, time, *args):

        id_hours = datetime.strptime(hours,'%H:%M')

        horas , min = map(int, time.split(':'))
        delta = timedelta(hours=horas, minutes=min)

        soma = delta + id_hours

        return soma.strftime('%H:%M')

    def load_widget(self, *args, **kwargs):

        # The "md_label" not show!
        md_label = MDLabel(text='Carregando...', color=(1, 1, 1, 1))
        spiner = MDSpinner(active=True, size_hint=(None, None), size=('56dp', '56dp'),
                           pos_hint=({'center_x': .5, 'center_y': .5}))
        self.box_dialog = MDDialog(buttons=[md_label])

        self.box_dialog.add_widget(spiner)
        # self.parent.parent.add_widget(self.boxlayout)
        self.box_dialog.open()

    def wait_save_scheduleing(self, *args):
        self.load_widget()
        Clock.schedule_once(self.save_scheduleing, 2)

    def save_scheduleing(self, *args):

        date = f'{self.day}/{self.month}/{self.year}'

        time_cancel = self.info_manager['time_cancel']
        horas_hoje = self.time_now()
        # list_works = []
        # list_ids_schedule = []

        # variable to infomation of schedule ######################
        list_id_marked = []
        link = ''
        free = ''
        second_free = ''
        list_comparate_hours = []
        list_second_hours = []
        information_of_file = {}
        list_of_schedule = []

        # geting the id of Manager ##############################
        # name_id = self.get_id_diverse()
        if_manager = self.get_id_diverse()

        try:
            # geting the info of work ###############################
            with open('select_works.json','r') as select_work:
                list_works = json.load(select_work)

            with open('info_user.json','r') as arquivo:
                info_user = json.load(arquivo)

            with open('info_schedule.json', 'r') as file_info:
                id_pos = json.load(file_info)

            with open('inf_to_infoschedule_drawer.json','r') as get_to_save:
                file_save = json.load(get_to_save)
        except:
            pass

        for iten in file_save:
            list_of_schedule.append(iten)


        get_data = self.get_name_user(info_user['id_user'])


        id_user = info_user['id_user']
        nome = self.get_name_user(id_user)
        horas = self.ids.hours.text
        tempo = self.ids.time.text
        valor = self.ids.valor.text
        link_info = ''
        try:
            email = get_data['email']
            cpf = get_data['cpf']
        except:
            email = ''
            cpf = ''

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

                time_marked = self.sum_hours_end_time(if_scheduled[id_marked]['id_horas'],if_scheduled[id_marked]['tempo'])
                list_second_hours.append(time_marked)

                if if_scheduled[id_marked]['id_horas'] < horas and time_marked > horas:
                    second_free = True
                    break
            free = horas in list_comparate_hours
        except TypeError:
            pass
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')


        if if_manager['manager'] == "False":
            link = f'{self.LINK_SALAO}/{self.id_manager}/socios/{if_manager["id_user"]}/agenda/{self.semana}/{id_user}.json'
        elif if_manager['manager'] == "True":
            link = f'{self.LINK_SALAO}/{self.id_manager}/agenda/{self.semana}/{id_user}.json'

        # information of date base #########################
        info = f'{{"id_posicao":"{id_pos["id_posicao"]}",' \
               f'"id_horas":"{horas}",' \
               f'"id_user":"{id_user}",' \
               f'"tempo":"{tempo}",' \
               f'"valor":"{valor}",' \
               f'"nome":"{nome["nome"]}",'\
               f'"horas_agendamento": "{horas_hoje}",'\
               f'"servicos":"{list_works}",' \
               f'"cpf":"{cpf}",' \
               f'"email":"{email}"}}'

        # information of file "infoscheduleclient" ##########
        second_hours =self.sum_hours_end_time(horas,tempo)

        information_of_file["date"] = date
        information_of_file["id_button"] = id_pos["id_posicao"]
        information_of_file["id_schedule"] = id_user
        information_of_file["hours"] = horas
        information_of_file["client"] = 'Você agendou esse horarion!'
        information_of_file["hours_second"] = str(second_hours)
        information_of_file["hours_of_schedule"] = str(horas_hoje)
        information_of_file["time"] = str(tempo)
        information_of_file["id_proficional"] = str(if_manager)
        information_of_file["cpf"] = str(cpf)
        information_of_file["email"] = str(email)

        list_of_schedule.append(information_of_file)


        if free or second_free:
            bt = MDFlatButton(text='OK')
            dialog = MDDialog(title='"Aviso!"',text=f'Desculpe mais outra pessoa acabou de agendar esse horário! das {horas} até as {time_marked}',radius=[40, 7, 40, 7],buttons=[bt])

            bt.bind(on_release=dialog.dismiss)
            dialog.open()
        else:
            try:
                requisicao = requests.patch(link, data=info)

                with open('inf_to_infoschedule_drawer.json', 'w', encoding='utf-8') as file:
                    json.dump(list_of_schedule, file, indent=2)

                with open('infoscheduleclient.json', 'w', encoding='utf-8') as file:
                    json.dump(information_of_file, file, indent=2)


                time = self.format_hours(time_cancel)

                print(time)

                bt = MDFlatButton(text='OK')
                dialog2 = MDDialog(title='"Aviso!"',
                                  text=f'Agendamento Marcado! Você tem {time[0]}{time[1]} para cancelar!',
                                  radius=[20, 7, 20, 7], buttons=[bt])

                bt.bind(on_release=dialog2.dismiss)
                dialog2.open()

                load = {}
                load['load_home'] = True
                with open('load_home.json', 'w') as load_home:
                    json.dump(load, load_home, indent=2)

            except requests.exceptions.ConnectionError:
                toast('Você não esta conectado a internet!')

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

        try:
            Clock.schedule_once(self.box_dialog.dismiss, 2)
        except:
            pass

    def format_hours(self, msg):

        time = ''

        horas = msg[0:2]
        minutos = msg[3:]


        if horas == '00' and minutos < '60':
            time = msg
            return msg, 'm'
        elif horas == '00' and minutos >= '60':
            time = '01:00'
            return time, 'h'
        elif horas != '00':
            time = msg
            return time, 'h'



class InfoScheduleClient(Screen):

    LINK_DATA_BASE = 'https://shedule-vitor-default-rtdb.firebaseio.com/salao'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.manager_main = self.id_manager()

        self.day_actual = datetime.today().isoweekday()

    def on_pre_enter(self):
        self.inf_schedule_client()
        Window.bind(on_keyboard=self.call_back)

    def call_back(self, windown, key, *args):

        if key == 27:
            MDApp.get_running_app().root.current = 'viewshedule'
            return True
        else:
            pass

    def on_leave(self):
        self.ids.img_block.source = ''
        self.ids.label_block.text = ''

    def id_manager(self):
        try:
            manager = ''

            link_work = self.LINK_DATA_BASE + '.json'
            requisicao = requests.get(link_work)
            requisicao_dic = requisicao.json()

            for id in requisicao_dic:
                manager = id
            return manager
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

    def get_id_diverse(self):
        if_manager = {}

        with open('write_id_manager.json','r') as arquivo:
            if_manager = json.load(arquivo)
        return if_manager

    def inf_schedule_client(self):
        dic_inf = {}
        cpf = ''
        e_mail = ''

        id_diverse = self.get_id_diverse()

        with open('infoscheduleclient.json', 'r') as file:
            info_schedule = json.load(file)

        # Here is only for geting the cpf and email ###################
        with open('inf_to_infoschedule_drawer.json','r') as file_cpf_email:
            cpf_email = json.load(file_cpf_email)

        id_proficional = self.get_id_diverse()

        try:
            cpf = str(cpf_email[0]["cpf"])
            e_meil = str(cpf_email[0]["email"])
        except:
            with open('get_client_data.json', 'r') as date:
                date_client = json.load(date)
                cpf  = date_client['cpf']
                e_mail = date_client['email']

        # for info_schedule in info_schedules:

            # Transformation the str in dictionary ##################
            # id_proficional = eval(info_schedule['id_proficional'])

        try:
            # if id_proficional['id_user'] == str(id_diverse['id_user']):

            id_client = info_schedule['id_schedule']
            self.ids.scheduling.text = info_schedule['hours_of_schedule']

            self.ids.nome.text = f'[color=#6B0A00]{info_schedule["client"]}[/color]'
            self.ids.hours.text = f'[b]Agendado as[/b] [color=#6B0A00]{info_schedule["hours"]}[/color] [size=20]hs[/size]'
            self.ids.hours_second.text = f'[b]Termino do serviço[/b] [color=#6B0A00]{info_schedule["hours_second"]}[/color] [size=20]hs[/size]'
            self.ids.time.text = f'[b]Tempo de serviço[/b] [color=#6B0A00]{info_schedule["time"]}[/color] [size=20]hs[/size]'
            self.ids.cpf.text = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
            self.ids.email.text = str(e_mail)

            self.work(id_client, id_proficional)
            self.info_cliente_and_cancel(id_client)
        except:
            self.ids.nome.text = '"Nem uma hora marcada!"'
            raise

    def info_cliente_and_cancel(self,id_client,*args):
        try:
            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
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
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def block_client(self):
        with open('infoscheduleclient.json', 'r') as file:
            info_schedule = json.load(file)
        id_client = info_schedule['id_schedule']

        try:
            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

            info = f'{{"bloqueado":"True"}}'
            requisicao = requests.patch(link, data=info)

            self.ids.img_block.source = 'images/bloqueado.png'
            self.ids.label_block.text = 'Cliente bloqueado!'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')

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
        try:
            link = f'https://shedule-vitor-default-rtdb.firebaseio.com/client/{id_client}.json'

            info = f'{{"bloqueado":"False"}}'
            requisicao = requests.patch(link, data=info)

            self.ids.img_block.source = ''
            self.ids.label_block.text = ''
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            pass

    def work(self, id_client, t_f):
        self.ids.box_work.clear_widgets()

        list_string = ''
        list_work = []
        valor = 0

        # with open('write_id_manager.json','r') as file:
        #     id_worker = json.load(file)
        id_worker = t_f

        try:
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
                    myboxcategorie = MyBoxCategorieLabel(work['servico'], work['tempo'], str(float(str(work['valor']).replace(',','.'))).replace('.',','))

                    myboxcategorie.bind(on_release=self.nada_pass)
                    self.ids.box_work.add_widget(myboxcategorie)
            except TypeError:
                pass

            self.ids.id_valor.text = str(valor).replace('.',',') + ' [size=15][b]R$[/b][/size]'
        except requests.exceptions.ConnectionError:
            toast('Você não esta conectado a internet!')
        except:
            raise

    def nada_pass(selfm, *args):
        """
        Function with not return none
        :return:
        """
        pass

    def return_schedule(self):
        MDApp.get_running_app().root.current = 'homepage'


class DrawerInfoSchedule(InfoScheduleClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.day = datetime.today().day
        self.month = datetime.today().month
        self.year = datetime.today().year


    def on_pre_enter(self):
        self.set_info_day()
        self.inf_schedule_client()
        Window.bind(on_keyboard=self.call_back)

    def call_back(self, windown, key, *args):

        if key == 27:
            MDApp.get_running_app().root.current = 'homepage'
            return True
        else:
            pass

    def set_info_day(self):

        # current days for day comparison from inf_to_infoschedule_drawer file ###
        set_day = f'{self.day}/{self.month}/{self.year}'

        lista = []

        try:
            with open('inf_to_infoschedule_drawer.json','r') as file_day:
                day_file = json.load(file_day)

            for day in day_file:

                if day['date'] == set_day:
                    lista.append(day)
                else:
                    pass

            with open('inf_to_infoschedule_drawer.json', 'w') as set:
                json.dump(lista, set, indent=2)

        except:
            pass

    def choose_pos(self,texto_pos,*args):
        number_pos = texto_pos
        dic_inf = {}
        with open('inf_to_infoschedule_drawer.json', 'r') as file:
            info_schedule = json.load(file)

        cpf =  str(info_schedule[number_pos]["cpf"])

        try:
            self.ids.inf_agenda.text = f'{texto_pos + 1}º'
            id_client = info_schedule[number_pos]['id_schedule']
            self.ids.scheduling.text = info_schedule[number_pos]['hours_of_schedule']
            tru_fal = eval(info_schedule[number_pos]['id_proficional'])

            self.ids.nome.text = f'[size=20][color=#9B9894]Nome[/color][/size]\n[color=#6B0A00]{info_schedule[number_pos]["client"]}[/color]'
            self.ids.hours.text = f'[b]Agendado as[/b] [color=#6B0A00]{info_schedule[number_pos]["hours"]}[/color] [size=20]hs[/size]'
            self.ids.hours_second.text = f'[b]Termino do serviço[/b] [color=#6B0A00]{info_schedule[number_pos]["hours_second"]}[/color] [size=20]hs[/size]'
            self.ids.time.text = f'[b]Tempo de serviço[/b] [color=#6B0A00]{info_schedule[number_pos]["time"]}[/color] [size=20]hs[/size]'
            self.ids.cpf.text = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
            self.ids.email.text = str(info_schedule[number_pos]["email"])

            self.work(id_client, tru_fal)
            self.info_cliente_and_cancel(id_client)
        except:
            self.ids.nome.text = '"Nem uma hora marcada! chose"'
            raise

    def inf_schedule_client(self):
        dic_inf = {}
        with open('inf_to_infoschedule_drawer.json', 'r') as file:
            info_schedule = json.load(file)

        number_pos = 0
        self.ids.scroll_bt.clear_widgets()

        try:
            cpf = str(info_schedule[number_pos]["cpf"])
        except:
            pass

        for number_pos, items in enumerate(info_schedule):
            bt_pos = MDRaisedButton(text=f'{number_pos + 1}º',font_size=('15sp'), md_bg_color=(0.25, 0.53, 0.67,1))
            self.ids.scroll_bt.add_widget(bt_pos)
            bt_pos.bind(on_release=partial(self.choose_pos, number_pos))

        try:
            self.ids.inf_agenda.text = f'1º'
            id_client = info_schedule[0]['id_schedule']
            self.ids.scheduling.text = info_schedule[0]['hours_of_schedule']

            tru_fal = eval(info_schedule[0]['id_proficional'])

            self.ids.nome.text = f'[size=20][color=#9B9894]Nome[/color][/size]\n[color=#6B0A00]{info_schedule[0]["client"]}[/color]'
            self.ids.hours.text = f'[b]Agendado as[/b] [color=#6B0A00]{info_schedule[0]["hours"]}[/color] [size=20]hs[/size]'
            self.ids.hours_second.text = f'[b]Termino do serviço[/b] [color=#6B0A00]{info_schedule[0]["hours_second"]}[/color] [size=20]hs[/size]'
            self.ids.time.text = f'[b]Tempo de serviço[/b] [color=#6B0A00]{info_schedule[0]["time"]}[/color] [size=20]hs[/size]'
            self.ids.cpf.text = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
            self.ids.email.text = str(info_schedule[0]["email"])

            self.work(id_client, tru_fal)
            self.info_cliente_and_cancel(id_client)
        except:
            self.ids.nome.text = '"Nem uma hora marcada!"'

class Perfil(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.get_client_data()

    def return_home(self):
        MDApp.get_running_app().root.current = 'homepage'

    def get_client_data(self):
        is_bloqued = ''

        # try:
        with open('get_client_data.json','r') as data:
            data_client = json.load(data)

        if data_client["bloqueado"] == "False":
            is_bloqued = 'Não'
        elif data_client["bloqueado"] == 'True':
            is_bloqued = 'Bloqueado!'

        set_cpf = f'{data_client["cpf"][:3]}.{data_client["cpf"][3:6]}.{data_client["cpf"][6:9]}-{data_client["cpf"][9:]}'

        self.ids.nome.text = str(data_client["nome"])
        self.ids.cpf.text = str(set_cpf)
        self.ids.email.text = str(data_client["email"])
        self.ids.bloqueio.text = str(is_bloqued)
        self.ids.quant_cancel.text = str(data_client["quant_cancelado"])
        # except:
        #     pass


class MyCardButton(MDCard):

    def __init__(self, socio_or_manager='', id_user='', nome='', **kwargs):
        super().__init__(**kwargs)
        self.socio_or_manager = socio_or_manager
        self.id_user = id_user
        self.nome = nome

        # self.tap_target = MDTapTargetView(
        #     widget=self,
        #     title_text="This is an add button",
        #     description_text="This is a description of the button",
        #     widget_position="left_bottom",
        # )
        #
        # self.tap_target.start()

    def send_info(self,socio_or_manager, id_user):
        dictionary = {}

        dictionary['manager'] = socio_or_manager
        dictionary['id_user'] = id_user

        with open('write_id_manager.json', 'w') as arquivo:
            json.dump(dictionary, arquivo, indent=2)

        MDApp.get_running_app().root.current = 'viewshedule'


class MyBoxCategorie(MDCard):

    def __init__(self,id_work='', servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)
        self.id_work = id_work
        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)


class MyBoxCategorieLabel(MDCard):
    def __init__(self, servico='', tempo='', valor='', **kwargs):
        super().__init__(**kwargs)

        self.servico = str(servico)
        self.tempo = str(tempo)
        self.valor = str(valor)

class MsgToApp(Screen):
    link = f'https://shedule-vitor-default-rtdb.firebaseio.com'


    def set_msg(self, *args):
        # webbrowser.open("https://play.google.com/store/apps/details?id=com.dominio.app")

        # Geting the number of valid to sum ######
        with open('msg_to_app.json','r') as file:
            msg = json.load(file)

        link = msg['link']

        soma_msg = msg['valid']
        soma_msg += 1

        with open('info_user.json', 'r') as file:
            id_user = json.load(file)

        link_client = f'{self.link}/client/{id_user["id_user"]}.json'

        info = f'{{"msg":{soma_msg} }}'

        requisicao = requests.patch(link_client, data=info)

        webbrowser.open(link)


    def on_pre_enter(self, *args):
        # with open('msg_to_app.json','r') as file:
        #     msg = json.load(file)
        #
        # self.ids.msg.text = msg['msg_actualiza']
        # self.ids.link.text = msg['link']
        self.dialog_msg()


    def dialog_msg(self,*args, **kwargs):
        with open('msg_to_app.json', 'r') as file:
            msg_file = json.load(file)

        msg = msg_file['msg_actualiza']
        # msg = msg_file['link']

        button_ok = MDFlatButton(text='OK')

        dialog = MDDialog(title='Atualização necessária', text=str(msg), buttons=[button_ok])

        button_ok.bind(on_release=self.set_msg)
        dialog.open()


class AgendamentoApp(MDApp):

    Builder.load_string(open('cliente.kv', encoding='utf-8').read())
    Builder.load_string(open('module/card_button.kv', encoding='utf-8').read())
    Builder.load_string(open('file_kv/table_schedule.kv', encoding='utf-8').read())
    Builder.load_string(open('module/my_box_categorie.kv', encoding='utf-8').read())
    def build(self):
        # self.theme_cls.theme_style = 'Dark'
        return Manager()

AgendamentoApp().run()