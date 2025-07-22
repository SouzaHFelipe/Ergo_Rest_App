import sys
import os
import logging
import re
import json
from PySide6.QtCore import QTimer, QEvent, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox)

# Obtém o diretório onde está o script principal
root_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho do log
log_path = os.path.join(root_dir, 'Rest_App.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rest App')
        self.resize(300, 100)
        self.lyt = QVBoxLayout()
        self.setLayout(self.lyt)

        # Timers
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.contar_tempo)

        self.timer_alert = QTimer(self)
        self.timer_alert.setInterval(1000)
        self.timer_alert.timeout.connect(self.contar_alert)

        self.timer_minimizar = QTimer(self)
        self.timer_minimizar.setSingleShot(True)
        self.timer_minimizar.timeout.connect(self.showMinimized)

        # Contadores
        self.contador = 0
        self.contador_alert = 0
        self.tempo = 0

        # Interface
        self.txt_tempo = QLineEdit()
        self.txt_tempo.setPlaceholderText('Digite o tempo para descanso (em segundos)')
        self.lyt.addWidget(self.txt_tempo)

        self.lbl = QLabel("Time  :  00:00")
        self.lyt.addWidget(self.lbl)


        self.btn = QPushButton('Clique para iniciar')
        self.lyt.addWidget(self.btn)
        self.btn.clicked.connect(self.iniciador_tempo)

        self.btn_parar = QPushButton('Clique para parar')
        self.btn_parar.hide()
        self.lyt.addWidget(self.btn_parar)
        self.btn_parar.clicked.connect(self.para_tempo)

        self.btn_continuar_tempo = QPushButton('Continuar Tempo')
        self.btn_continuar_tempo.hide()
        self.lyt.addWidget(self.btn_continuar_tempo)
        self.btn_continuar_tempo.clicked.connect(self.continuar_tempo)

        self.reiniciar_tempo = QPushButton('Reiniciar Tempo')
        self.reiniciar_tempo.hide()
        self.lyt.addWidget(self.reiniciar_tempo)
        self.reiniciar_tempo.clicked.connect(self.reiniciar_timer)

        # Login
        self.login_app()
        self.validar_user_criado()

    def login_app(self):
        self.login = QWidget()
        self.login.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.login.setWindowTitle('Login')
        self.login.resize(300, 100)

        self.login_name = QLineEdit()
        self.login_name.setPlaceholderText('Coloque seu nome de usuário')

        self.login_btn = QPushButton('Entrar')
        self.login_lyt = QVBoxLayout()
        self.login_lyt.addWidget(self.login_name)
        self.login_lyt.addWidget(self.login_btn)
        self.login.setLayout(self.login_lyt)
        self.login_btn.clicked.connect(self.validar_login)

    def salvar_usuario(self, nome):
        self.dados = {"usuario": nome}
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4)

    def carregar_usuario(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.dados = json.load(f)
                return self.dados.get("usuario", "")
        except FileNotFoundError:
            return ""

    def validar_user_criado(self):
        usuario_salvo = self.carregar_usuario()
        if usuario_salvo:
            logging.info(f'Login automático para: {usuario_salvo}')
            self.criar_botao_excluir()
            self.show()
        else:
            self.login.show()

    def criar_botao_excluir(self):
        if not hasattr(self, 'btn_excluir_user'):
            self.btn_excluir_user = QPushButton('Excluir usuário')
            self.lyt.addWidget(self.btn_excluir_user)
            self.btn_excluir_user.clicked.connect(self.delete_user)

    def delete_user(self):
        self.hide()
        self.login.show()
        self.timer.stop()
        self.timer_minimizar.stop()
        self.contador = 0
        self.lbl.setText("Time  :  00:00")
        self.btn.show()
        self.btn_parar.hide()
        self.btn_continuar_tempo.hide()
        self.reiniciar_tempo.hide()
        self.dados = {}
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4)
        logging.info("User Deletado")

    def validar_login(self):
        texto_usuario = self.login_name.text().strip()
        if not re.fullmatch(r'[A-Za-z]+', texto_usuario):
            logging.info('Erro no login: nome inválido')
            QMessageBox.warning(self.login, "Aviso", "Digite apenas letras, sem espaços ou números.")
        else:
            nome_existente = self.carregar_usuario()
            if texto_usuario != nome_existente:
                logging.info('Usuário criado')
                self.salvar_usuario(texto_usuario)
                QMessageBox.information(self.login, "Aviso", "Usuário registrado!")
                self.login.close()
                self.show()
            else:
                logging.info(f'Login Realizado: {texto_usuario}')
                QMessageBox.information(self.login, "Aviso", "Login realizado com sucesso!")
                self.login.close()
                self.show()

    def iniciador_tempo(self):
        logging.info("Começou o tempo.")
        tempo_valido = self.adicionar_tempo()
        if tempo_valido > 0:
            self.contador = 0
            self.timer.start()
            self.btn.hide()
            self.btn_parar.show()
            self.reiniciar_tempo.hide()
            self.btn_continuar_tempo.hide()
            self.minimizar_depois()

    def para_tempo(self):
        self.timer.stop()
        self.timer_minimizar.stop()
        logging.info("Timer pausado.")
        self.btn_parar.hide()
        self.btn_continuar_tempo.show()
        self.reiniciar_tempo.show()

    def continuar_tempo(self):
        self.timer.start()
        logging.info("Timer continuado.")
        self.btn_continuar_tempo.hide()
        self.reiniciar_tempo.hide()
        self.btn_parar.show()
        self.minimizar_depois()

    def reiniciar_timer(self):
        self.timer.stop()
        self.contador = 0
        self.lbl.setText("Time  :  00:00")
        logging.info("Timer reiniciado!")
        self.btn_continuar_tempo.hide()
        self.reiniciar_tempo.hide()
        self.btn_parar.show()
        self.timer.start()
        self.minimizar_depois()

    def adicionar_tempo(self):
        texto = self.txt_tempo.text()
        try:
            if re.fullmatch(r'\s*', texto):
                raise ValueError("Campo vazio ou apenas espaços")
            self.tempo = int(texto)
            if self.tempo <= 0:
                raise ValueError("Tempo deve ser maior que zero")
            logging.info(f"Tempo definido: {self.tempo} segundos.")
            return self.tempo
        except ValueError as e:
            self.timer.stop()
            logging.warning(f"Valor inválido digitado: {e}")
            QMessageBox.warning(self, "Aviso", str(e))
            self.tempo = 0
            return self.tempo

    def alert_pop(self):
        self.contador_alert = 0
        self.pop_up = QWidget()
        self.pop_up.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.pop_up.setStyleSheet("border-radius: 12px;")
        self.lbl_pop = QLabel('Tempo de descanso iniciado!\n Time: 00:00')
        self.lbl_pop.setAlignment(Qt.AlignCenter)
        self.lbl_pop.setStyleSheet("color: black; font-size: 16px; padding: 10px;")
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_pop)

        self.btn_alert = QPushButton('Pular Descanso')
        self.btn_alert.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #2E7D32; }
        """)
        self.btn_alert.clicked.connect(self.fechar_pop)
        layout.addWidget(self.btn_alert)

        self.pop_up.setLayout(layout)
        self.pop_up.resize(300, 100)
        self.timer_alert.start()
        self.pop_up.show()
        self.hide()

        QTimer.singleShot(1000 * 60, self.fechar_pop)

    def fechar_pop(self):
        self.timer_alert.stop()
        self.pop_up.close()
        self.show()

    def contar_alert(self):
        self.contador_alert += 1
        minutos = self.contador_alert // 60
        segundos = self.contador_alert % 60
        self.lbl_pop.setText(f'Tempo de descanso iniciado!\n Time: {minutos:02d}:{segundos:02d}')

    def contar_tempo(self):
        self.contador += 1
        minutos = self.contador // 60
        segundos = self.contador % 60
        self.lbl.setText(f'Time  :  {minutos:02d}:{segundos:02d}')
        if self.contador == self.tempo:
            logging.info("Tempo chegou ao limite definido.")
            self.timer.stop()
            self.alert_pop()
            self.contador = 0
            self.lbl.setText("Time  :  00:00")
            self.btn_parar.hide()
            self.btn.show()
            self.showNormal()
            self.activateWindow()
            self.raise_()

    def minimizar_depois(self, milissegundos=4000):
        self.showNormal()
        self.timer_minimizar.stop()
        self.timer_minimizar.start(milissegundos)

# Execução
app = QApplication(sys.argv)
window = MainWindow()
app.exec()
