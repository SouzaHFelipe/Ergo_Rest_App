
import sys
import logging
from plyer import notification  # coloque isso no topo do arquivo
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import QTimer , QObject , QEvent ,Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox)

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


        self.timer_alert = QTimer(self)
        self.timer_alert.setInterval(1000)
        self.timer_alert.timeout.connect(self.contar_alert)


        # Variáveis de tempo
        self.contador = 0
        self.contador_alert = 0
        self.tempo = 0

    def atualizar_contador(self):
        self.contador += 1
        self.lbl_pop.setText(f"Contador: {self.contador} segundos")

    def alert_pop(self):
        self.contador_alert = 0  # reinicia contagem de descanso

        self.pop_up = QWidget()
        self.pop_up.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pop_up.setStyleSheet("""
            border-radius: 12px;
        """)

        self.lbl_pop = QLabel(f'Tempo de descanso iniciado!\n Time: 00:00')
        self.lbl_pop.setAlignment(Qt.AlignCenter)
        self.lbl_pop.setStyleSheet("color: black; font-size: 16px; padding: 10px;")

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_pop)
        self.pop_up.setLayout(layout)
        self.timer_alert.start()

        self.pop_up.resize(300, 100)
        self.pop_up.show()

        QTimer.singleShot(6000, self.fechar_pop)

    def fechar_pop(self):
        self.timer_alert.stop()
        self.pop_up.close()

    def libera_teclado(self,event):
        if event.type() == QEvent.KeyPress:
            return False  
        return True
    
    def adicionar_tempo(self):
        try:
            self.tempo = int(self.txt_tempo.text())
            logging.info(f"Tempo definido: {self.tempo} segundos.")
        except ValueError:
            logging.warning('Valor inválido digitado.')
            self.tempo = 0
        return self.tempo

    def iniciador_tempo(self):
        logging.info("Comecou o tempo.")
        self.adicionar_tempo()
        self.contador = 0
        self.timer.start()

        # Visibilidade correta
        self.btn.hide()
        self.btn_parar.show()
        self.reiniciar_tempo.hide()
        self.btn_continuar_tempo.hide()
        self.minimizar_depois()

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

    def chegou_tempo(self):
        if self.contador == self.tempo:
            logging.info("Tempo chegou ao limite definido.")
            self.timer.stop()

    def contar_alert(self):
        self.contador_alert += 1
        self.minutos = self.contador_alert // 60
        self.segundos = self.contador_alert % 60
        self.tempo_iniciar = f"{self.minutos:02d}:{self.segundos:02d}"
        self.lbl_pop.setText(f'Tempo de descanso iniciado!\n Time: {self.tempo_iniciar}')

    def contar_tempo(self):
        self.contador += 1
        minutos = self.contador // 60
        segundos = self.contador % 60
        tempo_iniciar = f"{minutos:02d}:{segundos:02d}"
        self.lbl.setText(f'Time  :  {tempo_iniciar}')
        if self.contador == self.tempo:
            self.showNormal()  # Traz a janela de volta
            self.chegou_tempo()
            self.alert_pop()
            self.contador = 0
            self.lbl.setText(f'Time  :  00:00 ')
            self.btn_parar.hide()
            self.btn.show()
            self.activateWindow()     # garante que ela receba foco
            self.raise_()             # traz para 

    def minimizar_depois(self, milissegundos=3000):
        self.showNormal()
        QTimer.singleShot(milissegundos, self.showMinimized)
                
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()