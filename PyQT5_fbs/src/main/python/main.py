import sys

from PyQt5 import QtWidgets
from fbs_runtime.application_context import ApplicationContext, cached_property

from extractor2 import DataExtractor
from my_widgets import *
from uhslcdesign import Ui_MainWindow

# import darkdetect

if is_pyqt5():
    pass
else:
    pass


class AppContext(ApplicationContext):  # 1. Subclass ApplicationContext
    def run(self):  # 2. Implement run()
        version = self.build_settings["version"]
        name = self.build_settings["app_name"]
        # if sys.platform == 'darwin' and darkdetect.isDark():
        #     p = self.app.palette()
        #     p.setColor(QPalette.Base, QColor(101, 101, 101))
        #     p.setColor(QPalette.WindowText, QColor(231, 231, 231))
        #     p.setColor(QPalette.Text, QColor(231, 231, 231))
        #     self.app.setPalette(p)
        self.window.setWindowTitle(name + " v" + str(version))
        self.window.show()
        return self.app.exec_()  # 3. End run() with this line

    @cached_property
    def window(self):
        return ApplicationWindow()


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create Screen objects
        self.start_screen = Start(self.ui)
        self.help_screen = HelpScreen(self.ui)

        self.ui.actionInstructions.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.backButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))

        close_app = self.ui.actionQuit
        close_app.triggered.connect(self.close_application)

        open_file = self.ui.actionOpen
        open_file.triggered.connect(self.file_open)

        reload_file = self.ui.actionReload
        reload_file.triggered.connect(self.get_loaded_files)

        opents_file = self.ui.actionOpen_TS
        opents_file.triggered.connect(self.open_ts)

    def file_open(self, reload=False, ts=False):
        if not reload:
            # filters = "s*.dat;; ts*.dat"
            if ts:
                filters = "t*.dat"
            else:
                filters = "s*.dat"
            if ts:
                if st.get_path(st.SAVE_KEY):
                    path = st.get_path(st.SAVE_KEY)
                else:
                    # path = "C:\\Users\\komar\\OneDrive\\Desktop\\monp"
                    path = os.path.expanduser('~')
            else:
                if st.get_path(st.LOAD_KEY):
                    path = st.get_path(st.LOAD_KEY)
                else:
                    # path = "C:\\Users\\komar\\OneDrive\\Desktop\\monp"
                    path = os.path.expanduser('~')
            self.file_name = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open File', path, filters)
        # file_name = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open File', filter)

        # Validating files selected
        if self.is_valid_files(self.file_name):
            pass
        else:
            self.critical_dialog(title="ERROR",
                                 text="Warning, wrong files selected",
                                 info_text="The files need to belong to the adjacent months and the same station. Please select valid files to continue",
                                 details=''''MAC:
            The files are loaded in order in which they were selected. Select files from the oldest to the youngest.\nWINDOWS:
            The order is determined by the file order in the File Explorer. The files should be sorted by name before selecting them.
            ''')
            return

        try:
            # in_file = open(name[0],'r')
            self.month_count = len(self.file_name[0])
            print('FILENAME', self.file_name[0][0])

            self.ui.lineEdit_2.setText("Loaded: " + str(self.month_count) + " months")

            # data_collection = DataCollection()
            # Create DataExtractor for each month that was loaded into program
            months = []
            for j in range(self.month_count):
                month = DataExtractor(self.file_name[0][j])
                # An empty sensor, used to create "ALL" radio button in the GUI
                all_sensor = Sensor(None, None, 'ALL', None, None, None, None)
                month.sensors.add_sensor(all_sensor)
                # month = Month(month=month_int, sensors=month.sensors)
                months.append(month)

            # # The reason de[0] is used is because the program only allows to load
            # # multiple months for the same station, so the station sensors should be the same
            # # But what if a sensor is ever added to a station??? Check with fee it this ever happens
            name = months[0].headers[0][3:6]
            location = months[0].loc
            station_id = months[0].headers[0][:3]

            station = Station(name=name, location=location, station_id=station_id, month=months)
            self.start_screen.station = station
            self.start_screen.make_sensor_buttons(station.month_collection[0].sensor_collection.sensors)

        except (FileNotFoundError, IndexError) as e:
            print('Error:', e)

    def critical_dialog(self, title, text, info_text, details):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setInformativeText(info_text)
        msg_box.setDetailedText(str(details))
        msg_box.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()

    def pairwise_diff(self, lst):
        diff = 0
        result = []
        for i in range(len(lst) - 1):
            # subtracting the alternate numbers
            diff = lst[i] - lst[i + 1]
            result.append(diff)
        return result

    def is_valid_files(self, files):
        dates = []
        names = []
        result = []
        # extract dates and station 4 letter codes for every file that was loaded
        for file in files[0]:
            if file[-8:-4].isdigit():
                dates.append(int(file[-8:-4]))
                # check if monp file or a TS file
                if file.split("/")[-1][0] == "s":
                    names.append(file.split("/")[-1][1:5])
                else:
                    names.append(file.split("/")[-1][0:4])
        # check the difference between all dates
        for val in self.pairwise_diff(dates):
            if val != -1 and val != -89:
                result.append(val)
        # check if the files selected are all from the same station
        if names[1:] != names[:-1]:
            return False

        return len(result) == 0

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Warning', "Are you sure you want to quit?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def get_loaded_files(self):
        self.file_open(reload=True)

    def open_ts(self):
        self.file_open(reload=False, ts=True)
        # return self.file_name;


if __name__ == '__main__':
    appctxt = AppContext()  # 4. Instantiate the subclass
    exit_code = appctxt.run()  # 5. Invoke run()
    sys.exit(exit_code)
