import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog)
import pandas as pd
import chardet
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Number Filter")
        self.setFixedSize(600, 400)
        
        # Variables para almacenar rutas de archivos
        self.bloctel_file = None
        self.fichier_file = None
        
        # Crear widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Etiquetas para mostrar archivos seleccionados
        self.label_bloctel = QLabel("Bloctel File: Not selected")
        self.label_fichier = QLabel("Fichier File: Not selected")
        
        # Botones de selección de archivo
        button_layout = QHBoxLayout()
        self.btn_bloctel = QPushButton("Select Bloctel.csv")
        self.btn_fichier = QPushButton("Select Fichier.csv")
        self.btn_bloctel.clicked.connect(self.pick_bloctel_file)
        self.btn_fichier.clicked.connect(self.pick_fichier_file)
        button_layout.addWidget(self.btn_bloctel)
        button_layout.addWidget(self.btn_fichier)
        
        # Botón de proceso
        self.btn_process = QPushButton("Process Files")
        self.btn_process.setEnabled(False)
        self.btn_process.clicked.connect(self.process_files)
        
        # Instrucciones
        instructions = QLabel("Two files will be saved: a .txt with deleted numbers and a .csv with the final filtered file.")
        instructions.setWordWrap(True)
        
        # Agregar widgets al layout
        layout.addWidget(self.label_bloctel)
        layout.addWidget(self.label_fichier)
        layout.addLayout(button_layout)
        layout.addWidget(self.btn_process)
        layout.addWidget(instructions)
        layout.addStretch()
        
    def pick_bloctel_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Bloctel File",
            "",
            "CSV Files (*.csv)"
        )
        if file_name:
            self.bloctel_file = file_name
            self.label_bloctel.setText(f"Bloctel: {os.path.basename(file_name)}")
            self.check_files()
            
    def pick_fichier_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Fichier File",
            "",
            "CSV Files (*.csv)"
        )
        if file_name:
            self.fichier_file = file_name
            self.label_fichier.setText(f"Fichier: {os.path.basename(file_name)}")
            self.check_files()
    
    def check_files(self):
        self.btn_process.setEnabled(bool(self.bloctel_file and self.fichier_file))
    
    def process_files(self):
        try:
            # Detectar codificación
            def detect_encoding(file):
                with open(file, 'rb') as f:
                    result = chardet.detect(f.read())
                return result['encoding']

            encoding_bloctel = detect_encoding(self.bloctel_file)
            encoding_fichier = detect_encoding(self.fichier_file)

            # Procesar archivos
            df_bloctel = pd.read_csv(self.bloctel_file, dtype=str, header=None, usecols=[0], encoding=encoding_bloctel)
            df_fichier = pd.read_csv(self.fichier_file, dtype=str, encoding=encoding_fichier)

            # Limpiar datos
            df_bloctel[0] = df_bloctel[0].str.replace(r'\s+', '', regex=True)
            df_fichier['telefono'] = df_fichier.iloc[:, 0].str.split(';').str[0]
            df_fichier['telefono'] = df_fichier['telefono'].str.replace(r'\s+', '', regex=True)
            
            df_bloctel[0] = df_bloctel[0].astype(str).str.replace('.0', '')
            df_fichier['telefono'] = df_fichier['telefono'].astype(str).str.replace('.0', '')

            # Filtrar números
            df_filtered = df_fichier[~df_fichier['telefono'].isin(df_bloctel[0])]
            deleted_numbers = df_fichier[df_fichier['telefono'].isin(df_bloctel[0])]['telefono']

            # Guardar archivos
            deleted_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save deleted numbers",
                "deleted_numbers.txt",
                "Text Files (*.txt)"
            )
            if deleted_file:
                with open(deleted_file, 'w') as f:
                    for number in deleted_numbers:
                        f.write(f"{number}\n")

            filtered_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save filtered data",
                "filtered_data.csv",
                "CSV Files (*.csv)"
            )
            if filtered_file:
                df_filtered.to_csv(filtered_file, index=False, encoding='utf-8')
                
            QMessageBox.information(self, "Success", "Files processed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()