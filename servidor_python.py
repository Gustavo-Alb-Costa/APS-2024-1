from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import analise

app = Flask(__name__)
socketio = SocketIO(app)

devices = set()
# print(type(devices))

UPLOAD_FOLDER = 'uploads' # a pasta vai ficar no mesmo lugar que o script
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#if not os.path.exists(UPLOAD_FOLDER):
#    os.makedirs(UPLOAD_FOLDER)

def atualiza_tabela():
    print("Atualizando tabela...")
    # Gera a tabela HTML com os dados processados
    tabela_html = analise.generate_predictions()
    # Emite um evento para atualizar a tabela nos clientes conectados
    socketio.emit('atualiza_tabela', {'tabela': tabela_html}, broadcast=True)
    print("Tabela atualizada!")

@app.route('/')
# html do host alimentada com a qtd. de aparelhos
def index():
    print("Acessando página index...")
    # Gera a tabela HTML com os dados processados
    tabela_html = analise.generate_predictions()
    return render_template('index.html', num_devices=len(devices), tabela=tabela_html)

@app.route('/celular')
# página do dispositivo / celular
def device():
    print("Acessando página do dispositivo / celular...")
    # Gera a tabela HTML com os dados processados
    tabela_html = analise.generate_predictions()
    return render_template('celular.html', tabela=tabela_html)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Recebendo arquivo...")
    if 'file' not in request.files:
        print("Nenhum arquivo encontrado no formulário!")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        print("Nenhum arquivo selecionado!")
        return redirect(request.url)
    if file:
        filename = file.filename
        print("Salvando arquivo: ", filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        atualiza_tabela()
        return redirect(url_for('index'))

#_______________________________________________
# PARTE QUE ATUALIZA INFORMAÇÕES
#_______________________________________
@socketio.on('connect')
def handle_connect():
    devices.add(request.sid)
    emit('update_devices', {'num_devices': len(devices)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    devices.remove(request.sid)
    emit('update_devices', {'num_devices': len(devices)}, broadcast=True)
#________________________________________________________

# AQUI A GENTE PODE COLOCAR EVENTOS E ENVIOS DE DADOS ENTRE DISPOSITIVOS
@socketio.on('host_teste')
def teste_host_celular():
    emit('show_popup', {'message': 'Um dispositivo testou a comunicação'}, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    emit('display_message', {'message': data['message']}, broadcast=True)

#______________________________________________________________

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
