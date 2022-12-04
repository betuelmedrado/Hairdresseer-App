

import requests


APP_MANAGER = 'https://shedule-vitor-default-rtdb.firebaseio.com/msg_to_app/msg_manager.json'
APP_CLIENT = 'https://shedule-vitor-default-rtdb.firebaseio.com/msg_to_app/msg_client.json'

msg_client = ('Por favor faça a atualização do App!')
link_app = 'https://play.google.com/store/apps/details?id=org.barbershopcliente.barbershopcliente&pli=1'

info = f'{{"msg_actualiza":"{msg_client}", ' \
       f'"link":"{link_app}",' \
       f'"valid":{3} }}'   # l have what change this option in app


info_cidificado = info.encode('utf-8')

requisicao_manager = requests.patch(APP_CLIENT, data=info_cidificado)

# delrequisica = requests.delete(APP_CLIENT)

print('rodou')