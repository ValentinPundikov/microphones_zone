import sys  # Импортируем модуль sys для работы с системными параметрами
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel, QPushButton, QFileDialog, QMessageBox  # Импортируем нужные виджеты из PyQt5
from PyQt5.QtCore import Qt, QTimer  # Импортируем классы Qt и QTimer из PyQt5 для работы с событиями и таймерами
import vlc  # Импортируем модуль vlc для работы с мультимедиа

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AZS01')  # Устанавливаем заголовок окна
        self.setFixedSize(250, 250)  # Устанавливаем фиксированный размер окна
        self.setStyleSheet('background-color: #f0f0f0;')  # Устанавливаем цвет фона окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # Устанавливаем флаг поверх всех окон
        self.init_ui()  # Инициализируем пользовательский интерфейс
        self.timer = QTimer(self)  # Создаем таймер
        self.timer.timeout.connect(self.show_connection_error)  # Подключаем обработчик события таймера
        self.instance = vlc.Instance('--no-xlib')  # Создаем экземпляр VLC для воспроизведения мультимедиа
        self.stations = {}  # Словарь для хранения зон и соответствующих им ссылок на RTSP-потоки

    def init_ui(self):
        layout = QVBoxLayout()  # Создаем вертикальный макет
        layout.setAlignment(Qt.AlignCenter)  # Выравниваем элементы по центру

        # Добавляем метку для отображения номера станции
        self.station_label = QLabel("Номер станции: ")
        layout.addWidget(self.station_label)

        # Добавляем метку для разделения
        layout.addWidget(QLabel("--------------------"))

        # Добавляем метку для отображения зон
        layout.addWidget(QLabel("Зоны:"))

        # Создаем радиокнопки для выбора зоны
        self.radio_buttons = []

        # Добавляем кнопку для выбора файла
        self.select_file_button = QPushButton("Выбрать файл")
        self.select_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_button)

        self.setLayout(layout)

    def select_file(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("INI files (*.ini)")
        file_dialog.selectNameFilter("INI files (*.ini)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.load_stations_from_file(file_path)

    def load_stations_from_file(self, file_path):
        self.stations.clear()
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                self.stations[key] = value

        # Отображаем номер станции
        self.station_label.setText("Номер станции: " + self.stations.get('AZS', ''))

        # Удаляем предыдущие радиокнопки
        for button in self.radio_buttons:
            button.setParent(None)

        # Отображаем радиокнопки для зон
        for key, value in self.stations.items():
            if key.startswith('Zona') and value:
                zone_name = key.split('=')[1]  # Извлекаем название зоны из ключа
                radio_button = QRadioButton(zone_name)
                radio_button.setChecked(False)
                radio_button.toggled.connect(lambda checked, button=radio_button: self.toggle_radio_button(button, checked))
                self.layout().addWidget(radio_button)
                self.radio_buttons.append(radio_button)

    def toggle_radio_button(self, button, checked):
        if checked:
            try:
                self.start_rtsp_stream(self.stations['Zona='+button.text()])
                self.timer.start(10000)  # Запускаем таймер на 10 секунд
            except Exception as e:
                self.show_connection_error()

    def start_rtsp_stream(self, rtsp_url):
        media = self.instance.media_new(rtsp_url)
        if hasattr(self, 'player'):
            self.player.stop()  # Остановка предыдущего воспроизведения
            self.player.set_media(media)
        else:
            self.player = self.instance.media_player_new()
            self.player.set_media(media)

        if self.player.play() == -1:
            raise Exception("Ошибка при воспроизведении потока RTSP")

    def show_connection_error(self):
        self.timer.stop()  # Останавливаем таймер
        QMessageBox.warning(self, "Ошибка", "Ошибка при воспроизведении потока RTSP: Нет соединения", QMessageBox.Ok)

# Основная часть программы
if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создаем объект приложения
    player = AudioPlayer()  # Создаем объект класса AudioPlayer
    player.show()  # Отображаем окно приложения
    sys.exit(app.exec_())  # Запускаем цикл обработки событий
