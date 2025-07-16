
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

        self.estado_janela = "normal"  # ou "maximized"


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
        self.contador_aviso = 0
        self.tempo = 0

    def bloqueia_teclado(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                print("Emergência ativada!")
                return False  # Permite o ESC
            return True  # Bloqueia outras teclas
        return False
    
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


    def aviso_tempo(self):
        notification.notify(
            title='Tempo Finalizado!',
            message='Hora de descansar. Levante-se e alongue-se por 1 minuto.',
            timeout=10
        )

        # 🪟 Caixa de diálogo PySide
        msg_aviso = QMessageBox(self)
        msg_aviso.setWindowTitle('Tempo Finalizado!')
        msg_aviso.setText('Hora de descansar. Levante-se e alongue-se por ')
        self.timer_aviso()
        msg_aviso.exec()

    def timer_aviso(self):

        logging.info('Começou tempo de descanso')
        self.contador_aviso = 0
        self.tempo_pausa = 60  # tempo de pausa em segundos

        # Cria um novo timer para pausa
        self.timer_pausa = QTimer(self)
        self.timer_pausa.setInterval(1000)
        self.timer_pausa.timeout.connect(self.contador_pausa)
        self.timer_pausa.start()

    def contador_pausa(self):
        self.contador_aviso +=1
        tempo_pausa = 100
        self.lbl.setText(f'Time  :  {tempo_pausa}')


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

    def contar_tempo(self):
        self.contador += 1
        minutos = self.contador // 60
        segundos = self.contador % 60
        tempo_iniciar = f"{minutos:02d}:{segundos:02d}"
        self.lbl.setText(f'Time  :  {tempo_iniciar}')
        if self.contador == self.tempo:
            self.showNormal()  # Traz a janela de volta
            self.chegou_tempo()
            self.aviso_tempo()
            self.contador = 0
            self.lbl.setText(f'Time  :  00:00 ')
            self.btn_parar.hide()
            self.btn.show()
            self.activateWindow()     # garante que ela receba foco
            self.raise_()             # traz para 
            fake_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
            self.bloqueia_teclado(fake_event)
        
    def minimizar_depois(self, milissegundos=3000):
        self.showNormal()
        QTimer.singleShot(milissegundos, self.showMinimized)
                
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()