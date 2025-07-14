import sys
import logging
import keyboard as key
from pynput.keyboard import Key , Listener
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit)

# 📋 Configura o log: em arquivo e console
logging.basicConfig(
    filename='Rest_App_Log.log',
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

        # Campo de entrada de tempo
        self.txt_tempo = QLineEdit()
        self.txt_tempo.setPlaceholderText('Digite o tempo para descanso (em segundos)')
        self.lyt.addWidget(self.txt_tempo)

        # Label do tempo formatado
        self.lbl = QLabel("Time  :  00:00")
        self.lyt.addWidget(self.lbl)

        # Botão para iniciar
        self.btn = QPushButton('Clique para iniciar')
        self.lyt.addWidget(self.btn)
        self.btn.clicked.connect(self.iniciador_tempo)

        # Botão para pausar
        self.btn_parar = QPushButton('Clique para parar')
        self.btn_parar.hide()
        self.lyt.addWidget(self.btn_parar)
        self.btn_parar.clicked.connect(self.para_tempo)

        # Botão para continuar
        self.btn_continuar_tempo = QPushButton('Continuar Tempo')
        self.btn_continuar_tempo.hide()
        self.lyt.addWidget(self.btn_continuar_tempo)
        self.btn_continuar_tempo.clicked.connect(self.continuar_tempo)

        # Botão para reiniciar
        self.reiniciar_tempo = QPushButton('Reiniciar Tempo')
        self.reiniciar_tempo.hide()
        self.lyt.addWidget(self.reiniciar_tempo)
        self.reiniciar_tempo.clicked.connect(self.reiniciar_timer)

        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.contar_tempo)

        # Variáveis de tempo
        self.contador = 0
        self.tempo = 0

    def adicionar_tempo(self):
        try:
            self.tempo = int(self.txt_tempo.text())
            logging.info(f"Tempo definido: {self.tempo} segundos.")
        except ValueError:
            logging.warning('Valor inválido digitado.')
            self.tempo = 0
        return self.tempo

    def travar_teclado(self):
        for i in range(150):
            key.block_key(i)

    def liberar_teclado(self):
        for i in range(150):
            key.unblock_key(i)


    def chegou_tempo(self):
        if self.contador == self.tempo:
            logging.info("Tempo chegou ao limite definido.")
            self.timer.stop()
            self.travar_teclado()

    def iniciador_tempo(self):
        logging.info("Começou o tempo.")
        self.adicionar_tempo()
        self.contador = 0
        self.timer.start()

        # Visibilidade correta
        self.btn.hide()
        self.btn_parar.show()
        self.reiniciar_tempo.hide()
        self.btn_continuar_tempo.hide()

    def para_tempo(self):
        self.timer.stop()
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

    def reiniciar_timer(self):
        self.timer.stop()
        self.contador = 0
        self.lbl.setText("Time  :  00:00")
        self.timer.start()
        logging.info("Timer reiniciado!")

        self.btn_continuar_tempo.hide()
        self.reiniciar_tempo.hide()
        self.btn_parar.show()

    def contar_tempo(self):
        self.contador += 1
        minutos = self.contador // 60
        segundos = self.contador % 60
        tempo = f"{minutos:02d}:{segundos:02d}"
        self.lbl.setText(f'Time  :  {tempo}')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()