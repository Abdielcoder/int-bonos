#!/usr/bin/env python3
"""
Interfaz Principal - Herramientas Bonos con PyQt/PySide
Aplicación con tabs para Cotejamiento y Resegmentación
"""

import sys
import os
import json
import csv
import io
import tempfile
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Importar Qt con compatibilidad PySide6/PyQt6 (PySide6 primero para macOS)
try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QTabWidget, QPushButton, QFrame, QScrollArea,
                                 QTableWidget, QTableWidgetItem, QHeaderView,
                                 QFileDialog, QMessageBox, QProgressBar,
                                 QLineEdit, QTextEdit, QGroupBox, QGridLayout,
                                 QSplitter, QComboBox, QSpinBox, QCheckBox,
                                 QApplication, QProgressDialog, QDialog, QDialogButtonBox,
                                 QSizePolicy)
    from PySide6.QtCore import Qt, Signal as pyqtSignal, QThread, QTimer, QSize, QRect
    from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QBrush
    QT_VARIANT = "PySide6"
except ImportError:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QTabWidget, QPushButton, QFrame, QScrollArea,
                                QTableWidget, QTableWidgetItem, QHeaderView,
                                QFileDialog, QMessageBox, QProgressBar,
                                QLineEdit, QTextEdit, QGroupBox, QGridLayout,
                                QSplitter, QComboBox, QSpinBox, QCheckBox,
                                QApplication, QProgressDialog, QDialog, QDialogButtonBox,
                                QSizePolicy)
    from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize, QRect
    from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QBrush
    QT_VARIANT = "PyQt6"

import requests
import pandas as pd
from resegmentacion_db import ResegmentacionDB
from resegmentacion_details_dialog import ResegmentacionDetailsDialog

def get_terminal_style():
    """Retorna el estilo CSS para terminal profesional estilo CIA"""
    return """
        QTextEdit {
            font-size: 13px;
            font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
            font-weight: 500;
            padding: 20px;
            border: 2px solid #00ff41;
            border-radius: 6px;
            background-color: #0a0a0a;
            color: #00ff41;
            line-height: 1.4;
            selection-background-color: #003d0f;
            selection-color: #ffffff;
        }
        QTextEdit:focus {
            border: 2px solid #00ff80;
        }
        QScrollBar:vertical {
            background-color: #1a1a1a;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #00ff41;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #00ff80;
        }
    """

class APIWorker(QThread):
    """Worker thread para operaciones de API"""
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self, operation_type: str, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        
    def run(self):
        """Ejecuta la operación de API en background"""
        try:
            if self.operation_type == "login":
                self.perform_login()
            elif self.operation_type == "fetch_data":
                self.perform_data_fetch()
            else:
                self.error_occurred.emit(f"Operación no reconocida: {self.operation_type}")
        except Exception as e:
            self.error_occurred.emit(f"Error en {self.operation_type}: {str(e)}")
            
    def perform_login(self):
        """Realiza login API"""
        url = self.kwargs.get('url', '')
        username = self.kwargs.get('username', '')
        password = self.kwargs.get('password', '')
        
        self.progress_updated.emit(25, "Conectando con API...")
        
        response = requests.post(url, json={
            'correo': username,
            'password': password
        }, timeout=10)
        
        self.progress_updated.emit(75, "Procesando respuesta...")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            if token:
                self.progress_updated.emit(100, "Login exitoso")
                self.data_received.emit({'token': token, 'result': result})
            else:
                self.error_occurred.emit("Token no encontrado en respuesta")
        else:
            self.error_occurred.emit(f"Login falló: {response.status_code}")
            
    def perform_data_fetch(self):
        """Obtiene datos de la API"""
        url = self.kwargs.get('url', '')
        headers = self.kwargs.get('headers', {})
        
        self.progress_updated.emit(30, "Consultando datos...")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        self.progress_updated.emit(80, "Procesando datos...")
        
        if response.status_code == 200:
            data = response.json()
            self.progress_updated.emit(100, "Datos obtenidos exitosamente")
            self.data_received.emit(data)
        else:
            self.error_occurred.emit(f"Consulta falló: {response.status_code}")

class PaymentDetailsDialog(QDialog):
    """Diálogo para mostrar detalles de pagos"""
    
    def __init__(self, payment_details: List[dict], poliza_info: dict, parent=None):
        super().__init__(parent)
        self.payment_details = payment_details
        self.poliza_info = poliza_info
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        poliza_num = self.poliza_info.get('Núm. Póliza') or self.poliza_info.get('numPoliza', 'N/A')
        self.setWindowTitle(f"Detalles de Pagos - {poliza_num}")
        self.setModal(True)
        self.resize(1300, 650)  # Más grande para personas mayores
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Información básica de la póliza - más grande para personas mayores
        info_text = f"Póliza: {poliza_num} | Agente: {self.poliza_info.get('Agente', self.poliza_info.get('agente', 'N/A'))}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 18px; font-weight: 500; color: #374151; padding: 15px 0;")
        layout.addWidget(info_label)
        
        # Tabla de detalles de pagos
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # Botón de cerrar - más grande para personas mayores
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        close_button.setFixedSize(160, 60)  # Botón aún más grande
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #d1d5db;
                border-radius: 10px;
                font-weight: 600;
                font-size: 18px;
                color: #374151;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Estilos minimalistas para personas mayores
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
                background-color: white;
                alternate-background-color: #fafafa;
                font-size: 15px;
            }
            QTableWidget::item {
                padding: 15px 12px;
                border: none;
                min-height: 20px;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 18px 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: normal;
                color: #374151;
                font-size: 15px;
                min-height: 25px;
            }
        """)
    
    def setup_table(self):
        """Configura la tabla de detalles de pagos"""
        if not self.payment_details:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Información"])
            self.table.setItem(0, 0, QTableWidgetItem("No hay detalles de pagos disponibles"))
            return
        
        # Definir columnas basadas en el primer elemento
        first_payment = self.payment_details[0]
        all_columns = list(first_payment.keys())
        
        # Filtrar columnas - eliminar subramoId
        internal_columns = [col for col in all_columns if col != 'subramoId']
        
        # Mapear nombres internos a nombres legibles en español
        column_names = {
            '_id': 'ID PAGO',
            'claveAgente': 'Clave Agente',
            'fechaPago': 'Fecha de Pago',
            'isPrimerAnio': '¿Primer Año?',
            'numPoliza': 'Núm. Póliza',
            'primaNeta': 'Prima Neta'
        }
        
        # Crear lista de nombres mostrados
        display_columns = [column_names.get(col, col) for col in internal_columns]
        
        self.table.setRowCount(len(self.payment_details))
        self.table.setColumnCount(len(internal_columns))
        self.table.setHorizontalHeaderLabels(display_columns)
        
        # Llenar datos
        for row, payment in enumerate(self.payment_details):
            for col, key in enumerate(internal_columns):
                value = payment.get(key, '')
                
                # Formatear valores especiales
                if key == 'primaNeta' and value:
                    try:
                        value = f"${float(value):,.2f}"
                    except (ValueError, TypeError):
                        pass
                elif key == 'fechaPago' and value:
                    try:
                        # Convertir fecha si es necesario
                        if 'T' in str(value):
                            date_part = str(value).split('T')[0]
                            value = date_part
                    except:
                        pass
                elif key == 'isPrimerAnio':
                    # Convertir valores booleanos a texto legible
                    if value is None:
                        value = "No especificado"
                    elif value is True:
                        value = "Sí"
                    elif value is False:
                        value = "No"
                
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
        
        # Configurar tabla con diseño limpio
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)  # Ocultar números de fila
        
        # Configurar header
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Ajustar tamaño de la tabla para personas mayores
        self.table.setMinimumHeight(400)
        
        # Configurar altura de filas más grande
        self.table.verticalHeader().setDefaultSectionSize(45)
        
        # Auto-ajustar columnas
        self.table.resizeColumnsToContents()

class StatCardWidget(QFrame):
    """Widget de tarjeta de estadísticas"""
    
    def __init__(self, title: str, value: str, icon: str = "📊", color: str = "#1565C0"):
        super().__init__()
        self.setup_ui(title, value, icon, color)
        
    def setup_ui(self, title: str, value: str, icon: str, color: str):
        """Configura la UI de la tarjeta"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(180, 100)  # Tamaño más compacto
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        
        # Icono - tamaño compacto
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 20px; color: {color};")
        layout.addWidget(icon_label)
        
        # Valor - tamaño compacto
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        layout.addWidget(self.value_label)
        
        # Título - tamaño compacto
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 12px; color: #666; font-weight: 500;")
        layout.addWidget(title_label)
        
        self.setLayout(layout)
        
        # Estilo del frame
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: #f9fafb;
            }}
        """)
        
    def update_value(self, new_value: str):
        """Actualiza el valor mostrado"""
        self.value_label.setText(new_value)

class DataTableWidget(QWidget):
    """Widget de tabla de datos con funcionalidades avanzadas"""
    
    def __init__(self):
        super().__init__()
        self.current_data = []
        self.original_data = []  # Para almacenar datos originales con detalles de pagos
        self.filtered_data = []  # Para datos filtrados por búsqueda
        
        # Variables de paginación
        self.page_size = 100  # Registros por página
        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0
        
        # Base de datos de resegmentaciones
        self.resegmentacion_db = ResegmentacionDB()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de la tabla"""
        layout = QVBoxLayout()
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        # Búsqueda
        search_label = QLabel("🔍 Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en tabla...")
        self.search_input.textChanged.connect(self.filter_table)
        
        # Botón limpiar filtros
        clear_filters_btn = QPushButton("🧹 Limpiar Filtros")
        clear_filters_btn.clicked.connect(self.clear_filters)
        clear_filters_btn.setMinimumSize(140, 40)  # Botón más conservador
        clear_filters_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                background-color: #6b7280;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        

        
        # Botón exportar - más grande para personas mayores
        export_btn = QPushButton("📊 Exportar CSV")
        export_btn.clicked.connect(self.export_to_csv)
        export_btn.setMinimumSize(140, 40)  # Botón más conservador
        export_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                background-color: #1e40af;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        # Botón reporte aclaración - inicialmente oculto
        self.aclaracion_btn = QPushButton("📋 Reporte Aclaración")
        self.aclaracion_btn.clicked.connect(self.export_aclaracion)
        self.aclaracion_btn.setMinimumSize(180, 50)  # Botón más grande
        self.aclaracion_btn.setVisible(False)  # Oculto inicialmente
        self.aclaracion_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                background-color: #d97706;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #b45309;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        # Info de registros
        self.info_label = QLabel("0 registros")
        
        toolbar.addWidget(search_label)
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(clear_filters_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.info_label)
        toolbar.addWidget(export_btn)
        toolbar.addWidget(self.aclaracion_btn)
        
        layout.addLayout(toolbar)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Habilitar ordenamiento pero manejar manualmente para preservar todos los datos
        self.table.setSortingEnabled(True)
        
        # Configurar header
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Conectar señal de ordenamiento personalizado
        header.sectionClicked.connect(self.handle_column_sort)
        
        # Conectar evento de click en celda
        self.table.cellClicked.connect(self.on_cell_clicked)
        
        # Establecer tamaño mínimo para la tabla
        self.table.setMinimumHeight(400)
        self.table.setMinimumWidth(1000)
        
        # Configurar altura de filas más grande para personas mayores
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        layout.addWidget(self.table)
        
        # Controles de paginación
        pagination_layout = QHBoxLayout()
        
        # Información de página
        self.page_info_label = QLabel("Página 1 de 1")
        self.page_info_label.setStyleSheet("font-weight: normal; color: #374151; font-size: 13px;")
        
        # Selector de registros por página
        page_size_label = QLabel("Registros por página:")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500", "Todos"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        self.page_size_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                min-width: 80px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #1e40af;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        # Botones de navegación
        self.first_page_btn = QPushButton("⏮️ Primera")
        self.first_page_btn.clicked.connect(self.go_to_first_page)
        self.first_page_btn.setMaximumSize(120, 40)
        
        self.prev_page_btn = QPushButton("⬅️ Anterior")
        self.prev_page_btn.clicked.connect(self.go_to_previous_page)
        self.prev_page_btn.setMaximumSize(120, 40)
        
        self.next_page_btn = QPushButton("Siguiente ➡️")
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        self.next_page_btn.setMaximumSize(120, 40)
        
        self.last_page_btn = QPushButton("Última ⏭️")
        self.last_page_btn.clicked.connect(self.go_to_last_page)
        self.last_page_btn.setMaximumSize(120, 40)
        
        # Estilo para botones de paginación
        pagination_btn_style = """
            QPushButton {
                font-size: 12px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:disabled {
                background-color: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """
        
        self.first_page_btn.setStyleSheet(pagination_btn_style)
        self.prev_page_btn.setStyleSheet(pagination_btn_style)
        self.next_page_btn.setStyleSheet(pagination_btn_style)
        self.last_page_btn.setStyleSheet(pagination_btn_style)
        
        # Añadir elementos al layout de paginación
        pagination_layout.addWidget(page_size_label)
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.first_page_btn)
        pagination_layout.addWidget(self.prev_page_btn)
        pagination_layout.addWidget(self.next_page_btn)
        pagination_layout.addWidget(self.last_page_btn)
        
        layout.addLayout(pagination_layout)
        
        # Configurar política de tamaño para expansión
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.setLayout(layout)
        
        # Estilos
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #e5e7eb;
                background-color: white;
                alternate-background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border: none;
                min-height: 16px;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 12px 10px;
                border: none;
                border-bottom: 1px solid #d1d5db;
                font-weight: normal;
                color: #374151;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit {
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                min-height: 18px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1e40af;
                outline: none;
            }
            QPushButton {
                padding: 12px 20px;
                background-color: #1e40af;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                min-height: 40px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
    def load_data(self, data: List[Dict], columns: List[str], column_mapping: Dict[str, str] = None):
        """Carga datos en la tabla con paginación - Optimizado para memoria"""
        import gc
        
        # Preparar datos para uso con paginación
        self.column_mapping = column_mapping or {}
        
        # Convertir datos usando el mapeo de columnas si es necesario - optimizado
        if self.column_mapping:
            # Solo convertir si hay mapeo real
            converted_data = [
                {display_column: row_data.get(self.column_mapping.get(display_column, display_column), '')
                 for display_column in columns}
                for row_data in data
            ]
        else:
            # Sin mapeo, usar datos originales directamente
            converted_data = data
        
        print(f"[DEBUG] load_data - Procesando {len(data)} registros con mapeo de columnas")
        print(f"[DEBUG] Mapeo de columnas: {self.column_mapping}")
        
        # Usar load_data_simple para manejar la paginación
        self.load_data_simple(converted_data, columns, data)
        
        # Limpiar variables temporales
        if 'converted_data' in locals() and converted_data is not data:
            del converted_data
        gc.collect()
    
    def load_data_simple(self, data: List[Dict], columns: List[str], original_data: List[Dict]):
        """Carga datos en la tabla de forma simple sin mapeo con paginación - Optimizado para memoria"""
        import gc
        
        # Liberar datos anteriores explícitamente
        if hasattr(self, 'current_data'):
            del self.current_data
        if hasattr(self, 'filtered_data'):
            del self.filtered_data
        if hasattr(self, 'original_data'):
            del self.original_data
        gc.collect()
        
        # Validar datos de entrada
        if not isinstance(data, list):
            data = []
        if not isinstance(columns, list):
            columns = []
        if not isinstance(original_data, list):
            original_data = []
            
        # Guardar todos los datos - COPIAR para evitar modificaciones accidentales
        self.current_data = data.copy() if data else []
        self.original_data = original_data.copy() if original_data else []
        self.filtered_data = data.copy() if data else []  # Copiar en lugar de referenciar
        self.columns = columns.copy() if columns else []
        
        print(f"[DEBUG] Datos guardados - current_data: {len(self.current_data)}, original_data: {len(self.original_data)}")
        
        # Inicializar página actual si no existe
        if not hasattr(self, 'current_page'):
            self.current_page = 1
        
        # Calcular paginación
        self.total_records = len(self.filtered_data)
        self.calculate_pagination()
        
        print(f"[DEBUG] load_data_simple - Total registros: {self.total_records}, Página: {self.current_page}/{self.total_pages}")
        
        # Mostrar solo los datos de la página actual
        self.display_current_page()
        
    def cleanup_memory(self):
        """Función auxiliar para limpiar memoria explícitamente"""
        import gc
        
        # Liberar datos temporales si existen
        temp_vars = ['converted_data', 'temp_data', 'filtered_results', 'page_data', 'data_to_show']
        for var_name in temp_vars:
            if hasattr(self, var_name):
                delattr(self, var_name)
        
        # Forzar garbage collection
        gc.collect()
        
    def force_memory_cleanup(self):
        """Función para forzar una limpieza completa de memoria"""
        import gc
        
        print("[DEBUG] Iniciando limpieza forzada de memoria...")
        
        # Limpiar contenido de la tabla
        if hasattr(self, 'table'):
            self.table.clearContents()
        
        # Si hay filtros aplicados diferentes a los datos originales, liberarlos
        if hasattr(self, 'filtered_data') and hasattr(self, 'current_data'):
            if self.filtered_data is not self.current_data:
                del self.filtered_data
                self.filtered_data = self.current_data
        
        # Limpiar variables temporales
        self.cleanup_memory()
        
        # Múltiples llamadas a garbage collection para asegurar limpieza
        for i in range(3):
            gc.collect()
        
        print("[DEBUG] Limpieza de memoria completada")
        
    def calculate_pagination(self):
        """Calcula la información de paginación"""
        # Obtener datos para cálculo
        data_length = len(self.filtered_data) if hasattr(self, 'filtered_data') else len(self.current_data) if hasattr(self, 'current_data') else 0
        
        if data_length == 0:
            self.total_pages = 1
            self.current_page = 1
            self.total_records = 0
        elif self.page_size == 0 or (hasattr(self, 'page_size_combo') and self.page_size_combo.currentText() == "Todos"):
            self.page_size = max(1, data_length)
            self.total_pages = 1
            self.total_records = data_length
        else:
            self.total_pages = max(1, (data_length + self.page_size - 1) // self.page_size)
            self.total_records = data_length
        
        # Asegurar que la página actual esté en rango válido
        self.current_page = max(1, min(self.current_page, self.total_pages))
        
        # Actualizar interfaz
        self.update_pagination_controls()
        

        
    def display_current_page(self):
        """Muestra solo los datos de la página actual - Optimizado para memoria"""
        import gc
        
        if not hasattr(self, 'columns') or not hasattr(self, 'table'):
            return
        
        # Limpiar widgets anteriores de la tabla para liberar memoria
        self.table.clearContents()
        gc.collect()
            
        # Obtener datos a mostrar
        data_to_show = self.filtered_data if hasattr(self, 'filtered_data') else self.current_data if hasattr(self, 'current_data') else []
        
        if not data_to_show:
            # Sin datos, limpiar tabla
            self.table.setRowCount(0)
            self.table.setColumnCount(len(self.columns) if hasattr(self, 'columns') else 0)
            if hasattr(self, 'columns'):
                self.table.setHorizontalHeaderLabels(self.columns)
            self.update_info()
            return
            
        # Calcular rango de datos para la página actual - usar slicing eficiente
        if hasattr(self, 'page_size_combo') and self.page_size_combo.currentText() == "Todos":
            page_data = data_to_show
        else:
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = min(start_idx + self.page_size, len(data_to_show))
            # Usar slice directo en lugar de lista intermedia
            page_data = data_to_show[start_idx:end_idx]
        
        print(f"[DEBUG] Mostrando {len(page_data)} registros de la página {self.current_page}")
        
        # Configurar tabla
        self.table.setRowCount(len(page_data))
        self.table.setColumnCount(len(self.columns))
        
        # Configurar headers
        self.table.setHorizontalHeaderLabels(self.columns)
        
        # Llenar datos
        for row_idx, row_data in enumerate(page_data):
            # Verificar si esta fila tiene resegmentación
            agente = row_data.get('Agente', '')
            subramo = row_data.get('Subramo', '')
            num_poliza = row_data.get('Núm. Póliza', '')
            
            # Verificación simple y directa: buscar en la base de datos
            tiene_resegmentacion = False
            fecha_resegmentacion = None
            fecha_primer_pago_resegmentado = None
            
            # Verificación de resegmentación - DINÁMICA Y EN TIEMPO REAL
            reseg_data = self.verificar_resegmentacion_dinamica(agente, subramo, num_poliza)
            if reseg_data:
                tiene_resegmentacion = True
                fecha_resegmentacion = reseg_data.get('fecha_resegmentacion', '')
                fecha_primer_pago_resegmentado = reseg_data.get('fecha_primer_pago', '')
                tipo_resegmentacion = reseg_data.get('tipo_resegmentacion', '')
                print(f"[DEBUG] ✅ RESEGMENTACIÓN ENCONTRADA para {num_poliza} - Tipo: {tipo_resegmentacion}")
            else:
                tiene_resegmentacion = False
            

            
            for col_idx, column in enumerate(self.columns):
                if column == 'Aclaración':
                    # Crear checkbox para la columna Aclaración
                    checkbox = QCheckBox()
                    checkbox.setChecked(row_data.get(column, False))
                    checkbox.stateChanged.connect(self.check_aclaracion_buttons)
                    
                    # Centrar el checkbox
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    layout.addWidget(checkbox)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.setContentsMargins(0, 0, 0, 0)
                    
                    self.table.setCellWidget(row_idx, col_idx, widget)
                
                elif column == 'Resegmentación':
                    # Columna de resegmentación
                    if tiene_resegmentacion:
                        try:
                            # Mostrar la fecha del primer pago resegmentado (más relevante para el usuario)
                            if fecha_primer_pago_resegmentado:
                                from datetime import datetime
                                # Intentar parsear diferentes formatos de fecha
                                fecha_display = fecha_primer_pago_resegmentado
                                try:
                                    # Si es formato ISO
                                    if 'T' in fecha_primer_pago_resegmentado:
                                        dt = datetime.fromisoformat(fecha_primer_pago_resegmentado.replace('Z', '+00:00'))
                                        fecha_display = dt.strftime("%d/%m/%Y")
                                    # Si ya está en formato DD/MM/YYYY o similar
                                    elif '/' in fecha_primer_pago_resegmentado or '-' in fecha_primer_pago_resegmentado:
                                        fecha_display = fecha_primer_pago_resegmentado
                                except:
                                    fecha_display = fecha_primer_pago_resegmentado
                                
                                item = QTableWidgetItem(f"📅 {fecha_display}")
                                item.setToolTip(f"Primer pago resegmentado: {fecha_display}\nHaz clic para ver detalles de resegmentación")
                            else:
                                item = QTableWidgetItem("✅ Resegmentada")
                                item.setToolTip("Haz clic para ver detalles de resegmentación")
                            
                            item.setBackground(QColor(80, 80, 80))  # Gris oscuro para resegmentadas
                            item.setForeground(QColor(255, 255, 255))  # Texto blanco
                        except Exception as e:
                            print(f"[ERROR] Error formateando fecha resegmentación: {e}")
                            item = QTableWidgetItem("✅ Resegmentada")
                            item.setBackground(QColor(80, 80, 80))
                            item.setForeground(QColor(255, 255, 255))
                    else:
                        item = QTableWidgetItem("")
                    
                    self.table.setItem(row_idx, col_idx, item)
                
                else:
                    value = row_data.get(column, '')
                    item = QTableWidgetItem(str(value))
                    
                    # Aplicar sombreado base si la fila tiene resegmentación
                    if tiene_resegmentacion:
                        item.setBackground(QColor(64, 64, 64))  # Gris oscuro para toda la fila
                        item.setForeground(QColor(255, 255, 255))  # Texto blanco
                        print(f"[DEBUG] 🎨 APLICANDO gris oscuro a {num_poliza} columna {column}")
                    
                    # Colorear celdas especiales (pueden sobrescribir el color base)
                    if 'diferencia' in column.lower():
                        try:
                            # Extraer valor numérico de strings como "$-123.45"
                            numeric_value = float(str(value).replace('$', '').replace(',', '').replace('+', ''))
                            if numeric_value > 0:
                                if tiene_resegmentacion:
                                    item.setBackground(QColor(34, 139, 34))  # Verde oscuro para resegmentadas
                                    item.setForeground(QColor(255, 255, 255))  # Texto blanco
                                else:
                                    item.setBackground(QColor(220, 252, 231))  # Verde claro para normales
                            elif numeric_value < 0:
                                if tiene_resegmentacion:
                                    item.setBackground(QColor(139, 34, 34))  # Rojo oscuro para resegmentadas
                                    item.setForeground(QColor(255, 255, 255))  # Texto blanco
                                else:
                                    item.setBackground(QColor(254, 226, 226))  # Rojo claro para normales
                        except (ValueError, TypeError):
                            pass
                    
                    # Hacer clickeable la columna Detalles Pagos si tiene pagos
                    elif column == 'Detalles Pagos' and value and str(value).isdigit() and int(value) > 0:
                        if tiene_resegmentacion:
                            item.setBackground(QColor(30, 144, 255))  # Azul oscuro para resegmentadas
                            item.setForeground(QColor(255, 255, 255))  # Texto blanco
                        else:
                            item.setBackground(QColor(173, 216, 230))  # Azul claro para normales
                        item.setToolTip("Haz clic para ver detalles de pagos")
                            
                    self.table.setItem(row_idx, col_idx, item)
        
        # Ajustar columnas
        self.table.resizeColumnsToContents()
        
        # Actualizar info y controles de paginación
        self.update_info()
        self.update_pagination_controls()
        
        # Liberar memoria de variables temporales
        if 'page_data' in locals():
            del page_data
        if 'data_to_show' in locals() and data_to_show is not self.filtered_data and data_to_show is not self.current_data:
            del data_to_show
        gc.collect()
        
    def update_pagination_controls(self):
        """Actualiza los controles de paginación"""
        # Verificar que los controles existen
        if not hasattr(self, 'page_info_label'):
            return
            
        # Actualizar información de página
        if hasattr(self, 'page_size_combo') and self.page_size_combo.currentText() == "Todos":
            text = f"Mostrando todos los {self.total_records} registros"
        else:
            if self.total_records > 0:
                start_record = (self.current_page - 1) * self.page_size + 1
                end_record = min(self.current_page * self.page_size, self.total_records)
                text = f"Página {self.current_page} de {self.total_pages} ({start_record}-{end_record} de {self.total_records})"
            else:
                text = "Sin registros"
        
        # Actualizar el texto del label
        self.page_info_label.setText(text)
        
        # Habilitar/deshabilitar botones si existen
        if hasattr(self, 'first_page_btn'):
            self.first_page_btn.setEnabled(self.current_page > 1)
        if hasattr(self, 'prev_page_btn'):
            self.prev_page_btn.setEnabled(self.current_page > 1)
        if hasattr(self, 'next_page_btn'):
            self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        if hasattr(self, 'last_page_btn'):
            self.last_page_btn.setEnabled(self.current_page < self.total_pages)
            
        # Forzar actualización visual de los controles
        if hasattr(self, 'page_info_label'):
            self.page_info_label.update()
        if hasattr(self, 'first_page_btn'):
            self.first_page_btn.update()
        if hasattr(self, 'prev_page_btn'):
            self.prev_page_btn.update()
        if hasattr(self, 'next_page_btn'):
            self.next_page_btn.update()
        if hasattr(self, 'last_page_btn'):
            self.last_page_btn.update()
        
    # Métodos de navegación de paginación - Optimizados para memoria
    def go_to_first_page(self):
        """Va a la primera página"""
        if self.total_pages > 0:
            self.cleanup_memory()  # Limpiar antes de cambiar
            self.current_page = 1
            self.display_current_page()
            self.update_pagination_controls()
        
    def go_to_previous_page(self):
        """Va a la página anterior"""
        if self.current_page > 1:
            self.cleanup_memory()  # Limpiar antes de cambiar
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination_controls()
            
    def go_to_next_page(self):
        """Va a la página siguiente"""
        if self.current_page < self.total_pages:
            self.cleanup_memory()  # Limpiar antes de cambiar
            self.current_page += 1
            self.display_current_page()
            self.update_pagination_controls()
            
    def go_to_last_page(self):
        """Va a la última página"""
        if self.total_pages > 0:
            self.cleanup_memory()  # Limpiar antes de cambiar
            self.current_page = self.total_pages
            self.display_current_page()
            self.update_pagination_controls()
        
    def change_page_size(self, new_size_text):
        """Cambia el tamaño de página"""
        if new_size_text == "Todos":
            # Usar filtered_data si existe, sino current_data
            data_length = len(self.filtered_data) if hasattr(self, 'filtered_data') else len(self.current_data) if hasattr(self, 'current_data') else 0
            self.page_size = max(1, data_length)  # Evitar división por cero
        else:
            self.page_size = int(new_size_text)
        
        # Resetear a primera página
        self.current_page = 1
        self.calculate_pagination()
        self.display_current_page()
    
    def check_aclaracion_buttons(self):
        """Verifica si hay checkboxes seleccionados y muestra/oculta el botón de aclaración"""
        selected_count = 0
        
        for row in range(self.table.rowCount()):
            # Buscar la columna de Aclaración
            aclaracion_col = -1
            for col in range(self.table.columnCount()):
                if self.table.horizontalHeaderItem(col).text() == 'Aclaración':
                    aclaracion_col = col
                    break
            
            if aclaracion_col >= 0:
                widget = self.table.cellWidget(row, aclaracion_col)
                if widget:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        selected_count += 1
        
        # Mostrar/ocultar botón según si hay selecciones
        self.aclaracion_btn.setVisible(selected_count > 0)
        
        # Actualizar texto del botón con la cantidad
        if selected_count > 0:
            self.aclaracion_btn.setText(f"📋 Reporte Aclaración ({selected_count})")
        else:
            self.aclaracion_btn.setText("📋 Reporte Aclaración")
    
    def export_aclaracion(self):
        """Exporta solo los registros marcados para aclaración"""
        try:
            selected_data = []
            
            for row in range(self.table.rowCount()):
                # Buscar la columna de Aclaración
                aclaracion_col = -1
                for col in range(self.table.columnCount()):
                    if self.table.horizontalHeaderItem(col).text() == 'Aclaración':
                        aclaracion_col = col
                        break
                
                if aclaracion_col >= 0:
                    widget = self.table.cellWidget(row, aclaracion_col)
                    if widget:
                        checkbox = widget.findChild(QCheckBox)
                        if checkbox and checkbox.isChecked():
                            # Obtener datos de la fila
                            row_data = {}
                            for col in range(self.table.columnCount()):
                                header = self.table.horizontalHeaderItem(col).text()
                                if header != 'Aclaración':  # Excluir la columna de checkbox
                                    item = self.table.item(row, col)
                                    if item:
                                        row_data[header] = item.text()
                                    else:
                                        row_data[header] = ''
                            selected_data.append(row_data)
            
            if not selected_data:
                QMessageBox.warning(self, "Advertencia", "No hay registros seleccionados para aclaración")
                return
            
            # Diálogo para guardar archivo
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Reporte de Aclaración", 
                f"reporte_aclaracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV files (*.csv)"
            )
            
            if filename:
                # Escribir CSV
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    if selected_data:
                        fieldnames = list(selected_data[0].keys())
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(selected_data)
                
                QMessageBox.information(self, "Éxito", 
                                      f"Reporte de aclaración exportado exitosamente.\nArchivo: {filename}\nRegistros: {len(selected_data)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar reporte de aclaración: {str(e)}")
    
    def clear_filters(self):
        """Limpia todos los filtros de la tabla con paginación - Corregido para sorting"""
        import gc
        
        try:
            print("[DEBUG] Iniciando clear_filters...")
            print(f"[DEBUG] Datos antes de limpiar - current_data: {len(self.current_data) if hasattr(self, 'current_data') else 0}")
            print(f"[DEBUG] Datos antes de limpiar - filtered_data: {len(self.filtered_data) if hasattr(self, 'filtered_data') else 0}")
            
            # Limpiar campo de búsqueda
            self.search_input.clear()
            
            # IMPORTANTE: Desactivar temporalmente el sorting para evitar conflictos
            sorting_was_enabled = self.table.isSortingEnabled()
            if sorting_was_enabled:
                self.table.setSortingEnabled(False)
                print("[DEBUG] Sorting desactivado temporalmente")
            
            # Limpiar estado de sorting visual
            horizontal_header = self.table.horizontalHeader()
            horizontal_header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            
            # Liberar memoria de datos filtrados anteriores
            if hasattr(self, 'filtered_data') and self.filtered_data is not self.current_data:
                del self.filtered_data
                gc.collect()
            
            # Verificar que tenemos datos originales
            if not hasattr(self, 'current_data') or not self.current_data:
                print("[ERROR] No hay current_data para restaurar!")
                QMessageBox.warning(self, "Advertencia", "No hay datos para restaurar.")
                return
            
            # Limpiar checkboxes de aclaración en todos los datos originales
            for item in self.current_data:
                if 'Aclaración' in item:
                    item['Aclaración'] = False
            
            # Usar función auxiliar para restaurar tabla completamente
            if not self.restore_table_to_original_state():
                print("[ERROR] Falló la restauración de la tabla")
                return
            
            # Reactivar sorting si estaba activado
            if sorting_was_enabled:
                self.table.setSortingEnabled(True)
                print("[DEBUG] Sorting reactivado")
            
            # Actualizar botones de aclaración
            if hasattr(self, 'check_aclaracion_buttons'):
                self.check_aclaracion_buttons()
            
            # Forzar liberación de memoria
            gc.collect()
            
            print("[DEBUG] clear_filters completado exitosamente")
            QMessageBox.information(self, "Filtros Limpiados", 
                                  "Se han limpiado todos los filtros y selecciones de la tabla.")
            
        except Exception as e:
            print(f"[ERROR] Error en clear_filters: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al limpiar filtros: {str(e)}")
    
    def set_original_data(self, original_data: List[Dict]):
        """Configura los datos originales con detalles de pagos"""
        self.original_data = original_data
    
    def restore_table_to_original_state(self):
        """Restaura la tabla completamente a su estado original sin filtros ni sorting"""
        print("[DEBUG] Restaurando tabla a estado original...")
        
        if not hasattr(self, 'current_data') or not self.current_data:
            print("[ERROR] No hay datos originales para restaurar")
            return False
        
        try:
            # Desactivar sorting temporalmente
            self.table.setSortingEnabled(False)
            
            # Limpiar completamente la tabla
            self.table.clearContents()
            self.table.setRowCount(0)
            
            # Restaurar datos filtrados
            self.filtered_data = self.current_data.copy()
            self.total_records = len(self.filtered_data)
            
            # Resetear paginación
            self.current_page = 1
            self.calculate_pagination()
            
            # Recargar tabla completamente
            self.display_current_page()
            
            # Reactivar sorting
            self.table.setSortingEnabled(True)
            
            print(f"[DEBUG] Tabla restaurada exitosamente con {len(self.filtered_data)} registros")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error restaurando tabla: {str(e)}")
            return False
    
    def on_cell_clicked(self, row: int, column: int):
        """Maneja el click en una celda"""
        # Obtener el nombre de la columna
        column_name = self.table.horizontalHeaderItem(column).text()
        
        # Obtener datos de la fila
        row_data = {}
        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item:
                key = header_item.text()
                item = self.table.item(row, col)
                if item:
                    row_data[key] = item.text()
        
        # Obtener información básica de la fila
        agente = row_data.get('Agente', '')
        subramo = row_data.get('Subramo', '')
        num_poliza = row_data.get('Núm. Póliza', '')
        
        # Verificar si tiene resegmentación (primero por póliza, luego por pago_id)
        tiene_resegmentacion = self.resegmentacion_db.verificar_resegmentacion_existe(agente, subramo, num_poliza)
        resegmentacion_data = None
        
        if tiene_resegmentacion:
            resegmentacion_data = self.resegmentacion_db.obtener_resegmentacion(agente, subramo, num_poliza)
        else:
            # Verificar resegmentación por pago_id en detalles de pagos
            payment_details = self.find_payment_details_specific(agente, subramo, num_poliza)
            for pago in payment_details:
                pago_id = pago.get('idPago', '')
                if pago_id and self.resegmentacion_db.verificar_resegmentacion_por_pago_id(pago_id):
                    resegmentacion_data = self.resegmentacion_db.obtener_resegmentacion_por_pago_id(pago_id)
                    tiene_resegmentacion = True
                    break
        
        # Si la fila tiene resegmentación, mostrar detalles de resegmentación
        if tiene_resegmentacion and resegmentacion_data:
            dialog = ResegmentacionDetailsDialog(resegmentacion_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refrescar la tabla después de posibles cambios
                self.display_current_page()
            return
        
        # Si no tiene resegmentación, procesar clicks normales
        if column_name == 'Detalles Pagos':
            # Buscar los detalles de pagos originales usando Agente, Subramo y Núm. Póliza
            payment_details = self.find_payment_details_specific(agente, subramo, num_poliza)
            
            if payment_details:
                # Mostrar diálogo con detalles
                dialog = PaymentDetailsDialog(payment_details, row_data, self)
                dialog.exec()
            else:
                QMessageBox.information(self, "Información", 
                                      "No hay detalles de pagos disponibles para esta póliza.")
    
    def find_payment_details_specific(self, agente_buscado: str, subramo_buscado: str, num_poliza: str) -> List[Dict]:
        """Busca los detalles de pagos para una póliza específica usando agente, subramo y número de póliza"""
        for item in self.original_data:
            agente = item.get('agente', '')
            subramos = item.get('subramos', [])
            
            # Verificar que coincida el agente
            if agente != agente_buscado:
                continue
                
            for subramo_data in subramos:
                subramo_nombre = subramo_data.get('subramo', '')
                
                # Verificar que coincida el subramo
                if subramo_nombre != subramo_buscado:
                    continue
                    
                polizas = subramo_data.get('polizas', [])
                for poliza in polizas:
                    if poliza.get('numPoliza') == num_poliza:
                        prima_proyectada = poliza.get('primaProyectada', {})
                        return prima_proyectada.get('detallePagos', [])
        
        return []

    def find_payment_details(self, num_poliza: str) -> List[Dict]:
        """Busca los detalles de pagos para una póliza específica (método original mantenido para compatibilidad)"""
        for item in self.original_data:
            agente = item.get('agente', '')
            subramos = item.get('subramos', [])
            
            for subramo in subramos:
                polizas = subramo.get('polizas', [])
                for poliza in polizas:
                    if poliza.get('numPoliza') == num_poliza:
                        prima_proyectada = poliza.get('primaProyectada', {})
                        return prima_proyectada.get('detallePagos', [])
        
        return []
    

    def verificar_resegmentacion_dinamica(self, agente: str, subramo: str, num_poliza: str) -> Optional[Dict]:
        """
        Verifica dinámicamente si una póliza tiene resegmentación.
        SOLO busca en la base de datos SQLite, sin comparaciones parciales.
        Retorna los datos de la resegmentación si existe, None si no existe.
        """
        try:
            # Método 1: Búsqueda directa por póliza
            reseg_data = self.resegmentacion_db.obtener_resegmentacion(agente, subramo, num_poliza)
            if reseg_data and reseg_data.get('estado', 'ACTIVO').upper() == 'ACTIVO':
                return reseg_data
            
            # Método 2: Búsqueda por número de póliza exacto (para casos de nuevo negocio)
            all_resegmentaciones = self.resegmentacion_db.obtener_todas_resegmentaciones()
            for reseg in all_resegmentaciones:
                if reseg.get('estado', 'ACTIVO').upper() == 'ACTIVO':
                    # Comparación EXACTA de números de póliza
                    poliza_db = str(reseg.get('num_poliza', '')).strip().upper()
                    poliza_actual = str(num_poliza).strip().upper()
                    
                    # Verificar póliza de nuevo negocio registrada
                    poliza_nuevo_negocio = str(reseg.get('num_poliza_nuevo_negocio', '')).strip().upper()
                    
                    # SOLO comparaciones exactas
                    if poliza_db == poliza_actual or (poliza_nuevo_negocio and poliza_nuevo_negocio == poliza_actual):
                        return reseg
            
            # Método 3: Búsqueda por pago_id (solo para resegmentaciones Prima)
            payment_details = self.find_payment_details(num_poliza)
            for pago in payment_details:
                pago_id = pago.get('idPago', '')
                if pago_id:
                    reseg_data = self.resegmentacion_db.obtener_resegmentacion_por_pago_id(pago_id)
                    if reseg_data and reseg_data.get('estado', 'ACTIVO').upper() == 'ACTIVO':
                        return reseg_data
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Error verificando resegmentación dinámica para {num_poliza}: {e}")
            return None

    def handle_column_sort(self, logical_index):
        """Maneja el ordenamiento personalizado de columnas preservando todos los datos"""
        try:
            if not hasattr(self, 'filtered_data') or not self.filtered_data:
                return
            
            if not hasattr(self, 'columns') or logical_index >= len(self.columns):
                return
                
            column_name = self.columns[logical_index]
            
            # Determinar el orden de ordenamiento
            header = self.table.horizontalHeader()
            current_sort_order = header.sortIndicatorOrder()
            
            # Alternar entre ascendente y descendente
            if current_sort_order == Qt.SortOrder.AscendingOrder:
                sort_order = Qt.SortOrder.DescendingOrder
                reverse = True
            else:
                sort_order = Qt.SortOrder.AscendingOrder
                reverse = False
            
            print(f"[DEBUG] Ordenando por columna: {column_name}, orden: {'DESC' if reverse else 'ASC'}")
            
            # Desactivar temporalmente el ordenamiento automático para evitar conflictos
            self.table.setSortingEnabled(False)
            
            # Ordenar todos los datos filtrados
            def sort_key(item):
                value = item.get(column_name, '')
                # Manejar diferentes tipos de datos
                if isinstance(value, str):
                    # Intentar convertir a número si parece numérico
                    if value.replace('.', '').replace(',', '').replace('-', '').replace('+', '').replace('$', '').isdigit():
                        try:
                            return float(value.replace('$', '').replace(',', '').replace('+', ''))
                        except:
                            return value.lower()
                    return value.lower()
                elif isinstance(value, (int, float)):
                    return value
                else:
                    return str(value).lower()
            
            # Ordenar los datos
            self.filtered_data.sort(key=sort_key, reverse=reverse)
            
            # Resetear a la primera página después del ordenamiento
            self.current_page = 1
            self.calculate_pagination()
            
            # Mostrar los datos ordenados
            self.display_current_page()
            
            # Reactivar el ordenamiento y establecer el indicador visual
            self.table.setSortingEnabled(True)
            header.setSortIndicator(logical_index, sort_order)
            
            print(f"[DEBUG] Ordenamiento completado. Mostrando página 1 de {self.total_pages}")
            
        except Exception as e:
            print(f"[ERROR] Error en ordenamiento personalizado: {e}")
            # Reactivar el ordenamiento en caso de error
            self.table.setSortingEnabled(True)

    def actualizar_visualizacion_resegmentaciones(self):
        """
        Actualiza la visualización de la tabla para reflejar nuevas resegmentaciones.
        Debe llamarse después de completar una resegmentación.
        """
        try:
            print("[DEBUG] 🔄 Actualizando visualización de resegmentaciones...")
            
            # Simplemente volver a mostrar la página actual
            # Esto forzará la consulta dinámica de resegmentaciones
            self.display_current_page()
            
            # Opcional: mostrar mensaje de actualización
            print("[DEBUG] ✅ Visualización de resegmentaciones actualizada")
            
        except Exception as e:
            print(f"[ERROR] Error actualizando visualización de resegmentaciones: {e}")

    def buscar_poliza_por_pago_id(self, pago_id: str) -> Optional[Dict]:
        """Busca la póliza que contiene un pago_id específico en los datos originales"""
        try:
            for item in self.original_data:
                agente = item.get('agente', '')
                subramos = item.get('subramos', [])
                
                for subramo_data in subramos:
                    subramo = subramo_data.get('subramo', '')
                    polizas = subramo_data.get('polizas', [])
                    
                    for poliza in polizas:
                        num_poliza = poliza.get('numPoliza', '')
                        prima_proyectada = poliza.get('primaProyectada', {})
                        detalle_pagos = prima_proyectada.get('detallePagos', [])
                        
                        # Buscar el pago_id en los detalles de pagos
                        for pago in detalle_pagos:
                            if pago.get('idPago', '') == pago_id:
                                return {
                                    'agente': agente,
                                    'subramo': subramo,
                                    'num_poliza': num_poliza,
                                    'pago_details': pago
                                }
            
            print(f"[DEBUG] No se encontró póliza para pago_id: {pago_id}")
            return None
            
        except Exception as e:
            print(f"[ERROR] Error buscando póliza por pago_id {pago_id}: {str(e)}")
            return None
    
    def asociar_poliza_con_respuesta_api(self, respuesta_api: Dict, pago_id: str) -> Optional[Dict]:
        """
        Asocia la póliza de la tabla con la respuesta de la API usando diferentes estrategias
        """
        try:
            # Extraer número de póliza de la respuesta API
            poliza_api = None
            if 'data' in respuesta_api and 'ajustes' in respuesta_api['data']:
                ajustes = respuesta_api['data']['ajustes']
                if ajustes and len(ajustes) > 0:
                    poliza_api = ajustes[0].get('ajuste', {}).get('numPoliza', '')
            
            if not poliza_api:
                print(f"[DEBUG] No se pudo extraer numPoliza de la respuesta API")
                return None
            
            print(f"[DEBUG] Buscando asociación para póliza API: {poliza_api}")
            
            # Estrategia 1: Buscar directamente por número de póliza de la API
            for row in self.current_data:
                if row.get('Núm. Póliza', '') == poliza_api:
                    print(f"[DEBUG] Asociación directa encontrada: {poliza_api}")
                    return {
                        'agente': row.get('Agente', ''),
                        'subramo': row.get('Subramo', ''),
                        'num_poliza': row.get('Núm. Póliza', '')
                    }
            
            # Estrategia 2: Buscar por pago_id en los datos originales y asociar con current_data
            poliza_original = self.buscar_poliza_por_pago_id(pago_id)
            if poliza_original:
                agente_original = poliza_original.get('agente', '')
                subramo_original = poliza_original.get('subramo', '')
                
                # Buscar en current_data por agente y subramo
                for row in self.current_data:
                    if (row.get('Agente', '') == agente_original and 
                        row.get('Subramo', '') == subramo_original):
                        print(f"[DEBUG] Asociación por agente/subramo: {row.get('Núm. Póliza', '')}")
                        return {
                            'agente': row.get('Agente', ''),
                            'subramo': row.get('Subramo', ''),
                            'num_poliza': row.get('Núm. Póliza', '')
                        }
            
            print(f"[DEBUG] No se pudo asociar póliza API {poliza_api} con datos de la tabla")
            return None
            
        except Exception as e:
            print(f"[ERROR] Error asociando póliza con respuesta API: {str(e)}")
            return None
    
    def agregar_resegmentacion(self, resegmentacion_data: Dict) -> bool:
        """Agrega una nueva resegmentación a la base de datos"""
        try:
            success = self.resegmentacion_db.guardar_resegmentacion(resegmentacion_data)
            if success:
                # Refrescar la tabla para mostrar los cambios
                self.display_current_page()
                print(f"[DEBUG] Resegmentación agregada: {resegmentacion_data.get('num_poliza', '')}")
            return success
        except Exception as e:
            print(f"[ERROR] Error agregando resegmentación: {str(e)}")
            return False
    
    def actualizar_resegmentaciones(self):
        """Actualiza la visualización de resegmentaciones en la tabla"""
        try:
            self.display_current_page()
            print("[DEBUG] Resegmentaciones actualizadas en la tabla")
        except Exception as e:
            print(f"[ERROR] Error actualizando resegmentaciones: {str(e)}")
        
    def filter_table(self):
        """Filtra la tabla basado en la búsqueda con paginación - Optimizado para memoria"""
        import gc  # Garbage collector para liberar memoria
        
        search_text = self.search_input.text().lower()
        
        if not hasattr(self, 'current_data'):
            return
        
        # Liberar memoria de filtros anteriores explícitamente
        if hasattr(self, 'filtered_data'):
            del self.filtered_data
            gc.collect()  # Forzar garbage collection
            
        # Filtrar los datos usando generador para optimizar memoria
        if not search_text:
            # Sin filtro, referenciar datos originales sin copiar
            self.filtered_data = self.current_data
        else:
            # Aplicar filtro usando list comprehension optimizada
            columns_to_search = self.columns if hasattr(self, 'columns') else []
            
            def row_matches_filter(row_data):
                """Función auxiliar para verificar si una fila coincide con el filtro"""
                for column in (columns_to_search if columns_to_search else row_data.keys()):
                    value = str(row_data.get(column, ''))
                    if search_text in value.lower():
                        return True
                return False
            
            # Usar list comprehension para mejor rendimiento de memoria
            self.filtered_data = [row for row in self.current_data if row_matches_filter(row)]
            
            # Debug: verificar que los datos filtrados tengan las columnas necesarias
            if self.filtered_data:
                sample_row = self.filtered_data[0]
                print(f"[DEBUG] Filtrado - Columnas en primera fila: {list(sample_row.keys())}")
                print(f"[DEBUG] Filtrado - Prima ADM: {sample_row.get('Prima ADM', 'NO ENCONTRADA')}")
            
            # Liberar variables temporales
            del columns_to_search
            del row_matches_filter
        
        # Recalcular paginación y mostrar primera página
        self.current_page = 1
        self.total_records = len(self.filtered_data)
        self.calculate_pagination()
        self.display_current_page()
        
        # Forzar liberación de memoria después del filtrado
        gc.collect()
        
    def update_info(self):
        """Actualiza la información de registros con paginación"""
        if not hasattr(self, 'total_records'):
            # Fallback para compatibilidad
            visible_rows = sum(1 for row in range(self.table.rowCount()) 
                              if not self.table.isRowHidden(row))
            total_rows = self.table.rowCount()
            
            if visible_rows == total_rows:
                self.info_label.setText(f"{total_rows} registros")
            else:
                self.info_label.setText(f"{visible_rows} de {total_rows} registros")
        else:
            # Con paginación
            current_page_size = self.table.rowCount()
            if hasattr(self, 'filtered_data') and len(self.filtered_data) != len(self.current_data):
                # Hay filtros aplicados
                if current_page_size == self.total_records:
                    self.info_label.setText(f"{self.total_records} registros (filtrados)")
                else:
                    start_record = (self.current_page - 1) * self.page_size + 1
                    end_record = min(self.current_page * self.page_size, self.total_records)
                    self.info_label.setText(f"Mostrando {start_record}-{end_record} de {self.total_records} registros (filtrados)")
            else:
                # Sin filtros
                if current_page_size == self.total_records:
                    self.info_label.setText(f"{self.total_records} registros")
                else:
                    start_record = (self.current_page - 1) * self.page_size + 1
                    end_record = min(self.current_page * self.page_size, self.total_records)
                    self.info_label.setText(f"Mostrando {start_record}-{end_record} de {self.total_records} registros")
            
    def export_to_csv(self):
        """Exporta los datos visibles a CSV"""
        if not self.current_data:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", f"datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv)"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.current_data)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, "Éxito", f"Datos exportados a {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")

class CotejamientoTab(QWidget):
    """Tab de cotejamiento con funcionalidad completa"""
    
    token_updated = pyqtSignal(str)
    user_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.api_token = None
        self.current_data = None
        self.user_info = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del tab de cotejamiento"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Logo de RinoRisk
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/img/rino.png")
        if not logo_pixmap.isNull():
            # Escalar el logo manteniendo proporción
            scaled_pixmap = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # Fallback si no se puede cargar la imagen
            logo_label.setText("🏢")
            logo_label.setStyleSheet("font-size: 32px;")
        
        title_label = QLabel("Sistema de Cotejamiento de Bonos")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1f2937;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Configuración de API (oculta, solo para uso interno)
        api_group = QGroupBox("Configuración de API")
        api_group.setVisible(False)  # Ocultar toda la sección
        api_layout = QGridLayout()
        
        # URL de login
        api_layout.addWidget(QLabel("URL Login:"), 0, 0)
        self.login_url_input = QLineEdit("https://condicionesrino.com/api/core/auth/login")
        api_layout.addWidget(self.login_url_input, 0, 1)
        
        # Usuario
        api_layout.addWidget(QLabel("Usuario:"), 1, 0)
        self.username_input = QLineEdit("desarrollo-general@rinorisk.com")
        api_layout.addWidget(self.username_input, 1, 1)
        
        # Contraseña
        api_layout.addWidget(QLabel("Contraseña:"), 2, 0)
        self.password_input = QLineEdit("$QV@Rj4m66b")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.password_input, 2, 1)
        
        # URL de consulta
        api_layout.addWidget(QLabel("URL Consulta:"), 3, 0)
        self.query_url_input = QLineEdit("https://condicionesrino.com/api/comparacion-adm")
        api_layout.addWidget(self.query_url_input, 3, 1)
        
        # Botones principales (visibles)
        buttons_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("🔐 Iniciar Sesión API")
        self.login_btn.clicked.connect(self.perform_api_login)
        self.login_btn.setVisible(False)  # Oculto por defecto, se ejecuta automáticamente
        
        # Botón Cargar ADM - prerequisito para consultar datos
        self.load_adm_btn = QPushButton("💾 Cargar ADM")
        self.load_adm_btn.clicked.connect(self.load_adm_data)
        self.load_adm_btn.setMinimumSize(250, 60)  # Botón más conservador
        self.load_adm_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #1e40af;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        self.query_btn = QPushButton("📊 Consultar Datos")
        self.query_btn.clicked.connect(self.perform_data_query)
        self.query_btn.setEnabled(False)  # Deshabilitado hasta que se cargue ADM
        self.query_btn.setMinimumSize(250, 60)  # Botón más conservador
        self.query_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #1e40af;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        

        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.load_adm_btn)
        buttons_layout.addWidget(self.query_btn)
        buttons_layout.addStretch()
        
        # Ejecutar login automáticamente al cargar la interfaz
        QTimer.singleShot(1000, self.auto_api_login)
        
        api_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Área de controles principales (visible)
        controls_group = QGroupBox("Controles Principales")
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(self.load_adm_btn)  # Agregar botón Cargar ADM
        controls_layout.addWidget(self.query_btn)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Estado
        self.status_label = QLabel("Listo para iniciar")
        self.status_label.setStyleSheet("color: #6b7280; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Área de estadísticas
        self.stats_layout = QHBoxLayout()
        layout.addLayout(self.stats_layout)
        
        # Área de resultados
        results_group = QGroupBox("Resultados del Análisis")
        results_layout = QVBoxLayout()
        
        # Tabla de datos
        self.data_table = DataTableWidget()
        results_layout.addWidget(self.data_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
        
    def auto_api_login(self):
        """Ejecuta el login API automáticamente al iniciar la aplicación"""
        print("[DEBUG] Ejecutando login API automático...")
        self.status_label.setText("🔐 Conectando automáticamente con la API...")
        
        # Mostrar modal de carga simple
        self.loading_modal = SimpleProgressDialog(self, "Conectando con API...")
        self.loading_modal.update_message("Inicializando conexión...")
        self.loading_modal.show_progress()
        
        # Verificar que tenemos las credenciales configuradas
        if not self.login_url_input.text() or not self.username_input.text() or not self.password_input.text():
            self.status_label.setText("⚠️ Credenciales API configuradas, iniciando sesión...")
        
        # Ejecutar el login automáticamente
        self.perform_api_login()
        
    def perform_api_login(self):
        """Realiza login en la API"""
        if not self.login_url_input.text() or not self.username_input.text() or not self.password_input.text():
            # Si es llamada automática, solo mostrar en status, no error popup
            if not self.login_btn.isVisible():
                if hasattr(self, 'loading_modal'):
                    self.loading_modal.hide_progress()
                self.status_label.setText("✅ Listo para cargar ADM")
                return
            else:
                if hasattr(self, 'loading_modal'):
                    self.loading_modal.hide_progress()
                QMessageBox.warning(self, "Error", "Complete todos los campos de autenticación")
                return
            
        # Si no hay modal de carga (login manual), crear uno
        if not hasattr(self, 'loading_modal') or not self.loading_modal.isVisible():
            self.loading_modal = SimpleProgressDialog(self, "Autenticando...")
            self.loading_modal.update_message("Verificando credenciales...")
            self.loading_modal.show_progress()
            
        self.status_label.setText("Conectando con API...")
        self.login_btn.setEnabled(False)
        
        # Crear worker para login
        self.api_worker = APIWorker(
            "login",
            url=self.login_url_input.text(),
            username=self.username_input.text(),
            password=self.password_input.text()
        )
        
        self.api_worker.data_received.connect(self.on_login_success)
        self.api_worker.error_occurred.connect(self.on_login_error)
        self.api_worker.progress_updated.connect(self.update_status_with_modal)
        self.api_worker.start()
        
    def decode_jwt_payload(self, token):
        """Decodifica el payload de un JWT token sin verificar la firma"""
        try:
            # Los JWT tienen 3 partes separadas por puntos: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                return {}
                
            # Decodificar el payload (segunda parte)
            payload = parts[1]
            
            # Agregar padding si es necesario
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
                
            # Decodificar base64
            decoded = base64.b64decode(payload)
            return json.loads(decoded.decode('utf-8'))
            
        except Exception as e:
            print(f"[DEBUG] Error decodificando JWT: {e}")
            return {}
    
    def on_login_success(self, data: dict):
        """Maneja login exitoso"""
        # Cerrar modal de carga
        if hasattr(self, 'loading_modal'):
            self.loading_modal.hide_progress()
            
        self.api_token = data['token']
        
        # Extraer información del usuario de la respuesta o del JWT
        usuario_response = data.get('usuario', {})  # Cambiado de 'user' a 'usuario'
        
        if usuario_response:
            # Usar datos de la respuesta del login
            self.user_info = {
                'name': usuario_response.get('nombre', 'Usuario Sistema'),
                'email': usuario_response.get('correo', 'desarrollo-general@rinorisk.com'),
                'shortName': usuario_response.get('uidCartera', ''),
                'role': usuario_response.get('rol', '')
            }
        else:
            # Fallback: extraer del JWT
            jwt_payload = self.decode_jwt_payload(self.api_token)
            self.user_info = {
                'name': jwt_payload.get('name', 'Usuario Sistema'),
                'email': jwt_payload.get('email', 'desarrollo-general@rinorisk.com'),
                'shortName': jwt_payload.get('shortName', ''),
                'role': jwt_payload.get('role', '')
            }
        
        user_name = self.user_info.get('name', 'Usuario Sistema')
        
        print(f"[DEBUG] Respuesta completa del login: {data}")
        print(f"[DEBUG] Información del usuario extraída: {self.user_info}")
        print(f"[DEBUG] Nombre del usuario: {user_name}")
        
        self.status_label.setText("✅ Sesión API iniciada - Cargar ADM para continuar")
        self.login_btn.setEnabled(True)
        # No habilitar consultar datos hasta que se cargue ADM
        
        # Emitir signals para compartir token y usuario con otras tabs
        self.token_updated.emit(self.api_token)
        self.user_updated.emit(self.user_info)
        print(f"[DEBUG] Token compartido con otras tabs: {self.api_token[:20]}...")
        print(f"[DEBUG] Usuario compartido con otras tabs: {user_name}")
        
        # Solo mostrar mensaje si el botón es visible (no automático)
        if self.login_btn.isVisible():
            QMessageBox.information(self, "Éxito", "Login exitoso. Ahora cargue los datos ADM.")
        else:
            print("[DEBUG] ✅ Login API automático exitoso")
    
    def load_adm_data(self):
        """Carga archivo ADM y extrae año/mes del nombre"""
        try:
            if not self.api_token:
                QMessageBox.warning(self, "Advertencia", "Debe iniciar sesión API primero")
                return
            
            # Diálogo para seleccionar archivo ADM
            filename, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleccionar Archivo ADM", 
                "", 
                "Archivos ADM (*.csv *.xlsx *.xls);;Todos los archivos (*)"
            )
            
            if not filename:
                return  # Usuario canceló
            
            # Extraer nombre del archivo sin ruta
            import os
            file_basename = os.path.basename(filename)
            
            # Extraer año y mes del formato: pb_2025_01_cca_77293_DIR_NOROESTE
            year, month = self.extract_year_month_from_filename(file_basename)
            
            if not year or not month:
                QMessageBox.warning(self, "Formato Inválido", 
                                  f"El archivo no tiene el formato esperado.\n"
                                  f"Formato esperado: pb_YYYY_MM_cca_xxxxx_DIR_xxxxx\n"
                                  f"Archivo seleccionado: {file_basename}")
                return
            
            # Deshabilitar botón durante la carga
            self.load_adm_btn.setEnabled(False)
            self.load_adm_btn.setText("💾 Cargando ADM...")
            self.status_label.setText(f"🔄 Cargando ADM {year}/{month}...")
            
            # Mostrar modal de carga para ADM
            self.adm_loading_modal = SimpleProgressDialog(self, "Cargando Archivo ADM")
            self.adm_loading_modal.update_message(f"Procesando: {file_basename}")
            self.adm_loading_modal.show_progress()
            
            # Almacenar información del archivo
            self.adm_file_info = {
                'filename': filename,
                'year': year,
                'month': month,
                'basename': file_basename
            }
            
            # Simular proceso de carga con QTimer y actualizar progreso
            self.adm_timer = QTimer()
            self.adm_timer.timeout.connect(self.update_adm_progress)
            self.adm_progress = 0
            self.adm_timer.start(200)  # Actualizar cada 200ms
            
        except Exception as e:
            if hasattr(self, 'adm_loading_modal'):
                self.adm_loading_modal.hide_progress()
            QMessageBox.critical(self, "Error", f"Error al cargar datos ADM: {str(e)}")
            self.load_adm_btn.setEnabled(True)
            self.load_adm_btn.setText("💾 Cargar ADM")
    
    def update_adm_progress(self):
        """Actualiza el progreso de carga del ADM"""
        self.adm_progress += 10
        
        if hasattr(self, 'adm_loading_modal'):
            if self.adm_progress <= 30:
                self.adm_loading_modal.update_message("Leyendo archivo...")
            elif self.adm_progress <= 60:
                self.adm_loading_modal.update_message("Validando formato...")
            elif self.adm_progress <= 90:
                self.adm_loading_modal.update_message("Procesando datos...")
            else:
                self.adm_loading_modal.update_message("Finalizando carga...")
                
        if self.adm_progress >= 100:
            self.adm_timer.stop()
            QTimer.singleShot(500, self.on_adm_loaded)  # Pequeña pausa antes de finalizar
    
    def extract_year_month_from_filename(self, filename):
        """Extrae año y mes del nombre del archivo ADM"""
        try:
            import re
            
            # Patrón para: pb_YYYY_MM_cca_xxxxx_DIR_xxxxx
            pattern = r'pb_(\d{4})_(\d{2})_cca_.*_DIR_.*'
            match = re.match(pattern, filename)
            
            if match:
                year = match.group(1)
                month = match.group(2)
                
                # Validar que el mes esté en rango válido
                if 1 <= int(month) <= 12:
                    return year, month
                else:
                    print(f"[DEBUG] Mes inválido: {month}")
                    return None, None
            else:
                print(f"[DEBUG] Patrón no coincide para: {filename}")
                return None, None
                
        except Exception as e:
            print(f"[DEBUG] Error extrayendo año/mes: {e}")
            return None, None
    
    def on_adm_loaded(self):
        """Maneja la finalización de la carga ADM"""
        try:
            # Cerrar modal de carga ADM
            if hasattr(self, 'adm_loading_modal'):
                self.adm_loading_modal.hide_progress()
                
            # Obtener información del archivo cargado
            file_info = getattr(self, 'adm_file_info', {})
            year = file_info.get('year', 'N/A')
            month = file_info.get('month', 'N/A')
            basename = file_info.get('basename', 'N/A')
            
            # Actualizar interfaz
            self.load_adm_btn.setText(f"✅ ADM {year}/{month}")
            self.load_adm_btn.setEnabled(False)  # Mantener deshabilitado una vez cargado
            self.load_adm_btn.setStyleSheet("""
                QPushButton {
                    font-size: 22px;
                    font-weight: 700;
                    padding: 20px 35px;
                    border-radius: 12px;
                    background-color: #10b981;
                    color: white;
                    border: none;
                }
            """)
            
            # Habilitar botón de consultar datos
            self.query_btn.setEnabled(True)
            self.status_label.setText(f"✅ ADM {year}/{month} cargado - Listo para consultar datos")
            
            # Mostrar información detallada del archivo cargado
            QMessageBox.information(self, "ADM Cargado Exitosamente", 
                                  f"Archivo ADM cargado correctamente:\n\n"
                                  f"📁 Archivo: {basename}\n"
                                  f"📅 Año: {year}\n"
                                  f"📆 Mes: {month}\n\n"
                                  f"Ahora puede consultar datos.")
            
        except Exception as e:
            if hasattr(self, 'adm_loading_modal'):
                self.adm_loading_modal.hide_progress()
            QMessageBox.critical(self, "Error", f"Error al finalizar carga ADM: {str(e)}")
        
    def on_login_error(self, error: str):
        """Maneja error de login"""
        # Cerrar modal de carga
        if hasattr(self, 'loading_modal'):
            self.loading_modal.hide_progress()
            
        self.status_label.setText("⚠️ Listo para cargar ADM - configurar API manualmente si es necesario")
        self.login_btn.setEnabled(True)
        
        # Solo mostrar mensaje de error si el botón es visible (no automático)
        if self.login_btn.isVisible():
            QMessageBox.critical(self, "Error de Login", error)
        else:
            print(f"[DEBUG] ⚠️ Login API automático falló: {error}")
            # Hacer visible el botón para login manual si el automático falla
            self.login_btn.setVisible(True)
        
    def perform_data_query(self):
        """Consulta datos de la API"""
        if not self.api_token:
            QMessageBox.warning(self, "Error", "Debe iniciar sesión primero")
            return
        
        # Verificar que se haya cargado ADM y obtener fecha dinámica
        if not hasattr(self, 'adm_file_info') or not self.adm_file_info:
            QMessageBox.warning(self, "Error", "Debe cargar el archivo ADM primero")
            return
            
        # Extraer año y mes del ADM cargado y formar la fecha dinámica
        year = self.adm_file_info.get('year')
        month = self.adm_file_info.get('month')
        
        if not year or not month:
            QMessageBox.warning(self, "Error", "No se pudo obtener fecha del archivo ADM")
            return
            
        # Construir fecha dinámica: YYYY-MM-01
        dynamic_period = f"{year}-{month}-01"
        
        print(f"[DEBUG] Construyendo consulta API con fecha dinámica: {dynamic_period}")
        print(f"[DEBUG] Basado en ADM: año={year}, mes={month}")
        
        self.status_label.setText(f"Consultando datos para {dynamic_period}...")
        self.query_btn.setEnabled(False)
        
        # Mostrar modal de carga para consulta de datos
        self.query_loading_modal = SimpleProgressDialog(self, "Consultando Datos")
        self.query_loading_modal.update_message(f"Obteniendo información para {dynamic_period}...")
        self.query_loading_modal.show_progress()
        
        headers = {
            'x-token': self.api_token,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.query_url_input.text()}?periodo[]={dynamic_period}"
        
        print(f"[DEBUG] URL completa de la API: {url}")
        
        # Crear worker para consulta
        self.api_worker = APIWorker(
            "fetch_data",
            url=url,
            headers=headers
        )
        
        self.api_worker.data_received.connect(self.on_data_received)
        self.api_worker.error_occurred.connect(self.on_query_error)
        self.api_worker.progress_updated.connect(self.update_query_status_with_modal)
        self.api_worker.start()
        
    def on_data_received(self, data: dict):
        """Procesa datos recibidos de la API"""
        # Cerrar modal de carga de consulta
        if hasattr(self, 'query_loading_modal'):
            self.query_loading_modal.hide_progress()
            
        self.current_data = data
        self.process_api_data(data)
        self.status_label.setText("✅ Datos cargados exitosamente")
        self.query_btn.setEnabled(True)
        
    def on_query_error(self, error: str):
        """Maneja error de consulta"""
        # Cerrar modal de carga de consulta
        if hasattr(self, 'query_loading_modal'):
            self.query_loading_modal.hide_progress()
            
        self.status_label.setText(f"❌ Error en consulta: {error}")
        self.query_btn.setEnabled(True)
        QMessageBox.critical(self, "Error de Consulta", error)
        
    def update_status(self, progress: int, message: str):
        """Actualiza el estado del progreso"""
        self.status_label.setText(message)
        
    def update_status_with_modal(self, progress: int, message: str):
        """Actualiza el estado del progreso incluyendo el modal de carga"""
        self.status_label.setText(message)
        if hasattr(self, 'loading_modal') and self.loading_modal.isVisible():
            self.loading_modal.update_message(message)
            
    def update_query_status_with_modal(self, progress: int, message: str):
        """Actualiza el estado del progreso para consulta de datos incluyendo el modal de carga"""
        self.status_label.setText(message)
        if hasattr(self, 'query_loading_modal') and self.query_loading_modal.isVisible():
            self.query_loading_modal.update_message(message)
        

    def process_api_data(self, data: dict):
        """Procesa los datos de la API y actualiza la interfaz"""
        try:
            # Mostrar modal de procesamiento
            process_modal = SimpleProgressDialog(self, "Procesando Datos")
            process_modal.update_message("Analizando información...")
            process_modal.show_progress()
            
            # Simular progreso de procesamiento
            process_modal.update_message("Limpiando datos anteriores...")
            
            # Limpiar estadísticas anteriores
            self.clear_stats()
            
            process_modal.update_message("Extrayendo datos principales...")
            
            # Extraer datos principales
            data_list = data.get('data', [])
            
            if not data_list:
                process_modal.hide_progress()
                QMessageBox.warning(self, "Advertencia", "No se encontraron datos en la respuesta")
                return
                
            primer_registro = data_list[0]
            resumen = primer_registro.get('resumenComparacion', {})
            detalle = primer_registro.get('detalleComparacion', [])
            
            process_modal.update_message("Generando estadísticas...")
            
            # Mostrar estadísticas
            self.show_statistics(resumen)
            
            process_modal.update_message("Procesando datos de la tabla...")
            
            # Procesar datos para la tabla
            table_data = self.process_table_data(detalle)
            
            # Cambiar los nombres de las claves directamente en los datos
            display_table_data = []
            for row in table_data:
                new_row = {
                    'Agente': row.get('agente', ''),
                    'Subramo': row.get('subramo', ''),
                    'Núm. Póliza': row.get('numPoliza', ''),
                    'Prima ADM': row.get('primaADM', ''),
                    'Total Prima': row.get('totalPrima', ''),
                    'Cantidad Pagos': row.get('cantidadPagos', ''),
                    'Detalles Pagos': row.get('detallePagos', ''),
                    'Diferencia': row.get('diferencia', ''),
                    'Resegmentación': '',  # Se llenará dinámicamente según la base de datos
                    'Aclaración': False  # Checkbox inicialmente no seleccionado
                }
                display_table_data.append(new_row)
            
            process_modal.update_message("Configurando tabla de resultados...")
            
            # Configurar columnas con nombres descriptivos (agregada columna Resegmentación)
            columns = [
                'Agente', 'Subramo', 'Núm. Póliza', 'Prima ADM', 'Total Prima', 
                'Cantidad Pagos', 'Detalles Pagos', 'Diferencia', 'Resegmentación', 'Aclaración'
            ]
            
            # Cargar datos en tabla (sin mapeo ya que los datos tienen las claves correctas)
            self.data_table.load_data_simple(display_table_data, columns, detalle)
            
            process_modal.update_message("Procesamiento completado")
            
            # Pequeña pausa para mostrar el progreso completo
            QTimer.singleShot(500, process_modal.hide_progress)
            
        except Exception as e:
            if 'process_modal' in locals():
                process_modal.hide_progress()
            QMessageBox.critical(self, "Error", f"Error procesando datos: {str(e)}")
            
    def clear_stats(self):
        """Limpia las estadísticas anteriores"""
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
            
    def show_statistics(self, resumen: dict):
        """Muestra estadísticas en tarjetas simples"""
        # Datos para mostrar
        stats_data = [
            ("👥 Agentes", f"{resumen.get('agentes', 0):,}"),
            ("💰 Total Prima ADM", f"${resumen.get('totalPrimaADM', 0):,.2f}"),
            ("📈 Prima Proyectada", f"${resumen.get('totalPrimaProyectada', 0):,.2f}"),
            ("⚖️ Diferencia Total", f"${resumen.get('totalPrimaDiferencia', 0):+,.2f}"),
            ("📄 Cantidad Pólizas", f"{resumen.get('cantidadPolizas', 0):,}"),
            ("⚠️ Diferencias Pólizas", f"{resumen.get('cantidadPolizasDiferencia', 0):,}"),
            ("🔴 Diferencias >$50", f"{resumen.get('cantidadPolizasDiferenciasMayorA50', 0):,}")
        ]
        
        # Crear cards simples usando QLabel en lugar de widgets complejos
        for title, value in stats_data:
            card_widget = QFrame()
            card_widget.setFrameStyle(QFrame.Shape.StyledPanel)
            card_widget.setFixedSize(200, 85)
            
            # Layout del card
            card_layout = QVBoxLayout(card_widget)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.setSpacing(5)
            
            # Título
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    font-weight: normal;
                    color: #374151;
                    margin: 0;
                    padding: 2px;
                }
            """)
            
            # Valor
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #1e40af;
                    margin: 0;
                    padding: 2px;
                }
            """)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            # Estilo del card
            card_widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    margin: 3px;
                }
                QFrame:hover {
                    border-color: #1e40af;
                    background-color: #f9fafb;
                }
            """)
            
            self.stats_layout.addWidget(card_widget)
            
        self.stats_layout.addStretch()
        
    def process_table_data(self, detalle: List[dict]) -> List[dict]:
        """Procesa los datos de detalle para la tabla"""
        table_data = []
        
        for agente_item in detalle:
            agente_id = agente_item.get('agente', 'N/A')
            subramos = agente_item.get('subramos', [])
            
            # Procesar cada subramo del agente
            for subramo_data in subramos:
                subramo_nombre = subramo_data.get('subramo', 'N/A')
                polizas = subramo_data.get('polizas', [])
                
                # Procesar cada póliza del subramo
                for poliza in polizas:
                    num_poliza = poliza.get('numPoliza', 'N/A')
                    prima_adm = poliza.get('primaADM', 0)
                    prima_proyectada = poliza.get('primaProyectada', {})
                    diferencia = poliza.get('diferencia', 0)
                    
                    # Extraer datos de prima proyectada
                    total_prima = prima_proyectada.get('totalPrima', 0) if isinstance(prima_proyectada, dict) else 0
                    cantidad_pagos = prima_proyectada.get('cantidadPagos', 0) if isinstance(prima_proyectada, dict) else 0
                    detalle_pagos = prima_proyectada.get('detallePagos', []) if isinstance(prima_proyectada, dict) else []
                    
                    # Formatear valores
                    try:
                        prima_adm_formatted = f"${float(prima_adm):,.2f}" if prima_adm != "N/A" and prima_adm is not None else "N/A"
                    except (ValueError, TypeError):
                        prima_adm_formatted = "N/A"
                    
                    try:
                        total_prima_formatted = f"${float(total_prima):,.2f}" if total_prima else "$0.00"
                    except (ValueError, TypeError):
                        total_prima_formatted = "$0.00"
                    
                    try:
                        diferencia_formatted = f"${float(diferencia):+,.2f}" if diferencia else "$0.00"
                    except (ValueError, TypeError):
                        diferencia_formatted = "$0.00"
                    
                    table_data.append({
                        'agente': agente_id,
                        'subramo': subramo_nombre,
                        'numPoliza': num_poliza,
                        'primaADM': prima_adm_formatted,
                        'totalPrima': total_prima_formatted,
                        'cantidadPagos': cantidad_pagos,
                        'detallePagos': len(detalle_pagos),  # Número de detalles de pago
                        'diferencia': diferencia_formatted
                    })
        
        # Ordenar por diferencia absoluta
        table_data.sort(key=lambda x: abs(float(x['diferencia'].replace('$', '').replace(',', '').replace('+', ''))), reverse=True)
        
        return table_data

class ResegmentacionPrimaTab(QWidget):
    """Tab de resegmentación prima"""
    
    # Señal para notificar cuando se completa una resegmentación
    resegmentacion_completada = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.api_token = None  # Token para API
        self.user_info = {}  # Información del usuario
        self.usuario_local = None  # Información del usuario logueado localmente
        self.setup_ui()
        
    def set_api_token(self, token):
        """Establece el token de API obtenido del tab de Cotejamiento"""
        self.api_token = token
        print(f"[DEBUG] Token API establecido en ResegmentacionPrimaTab: {token[:20] if token else 'None'}...")
        
    def set_user_info(self, user_info):
        """Establece la información del usuario obtenida del tab de Cotejamiento"""
        self.user_info = user_info
        user_name = user_info.get('name', 'Usuario Sistema')
        print(f"[DEBUG] Información de usuario establecida en ResegmentacionPrimaTab: {user_name}")
        
    def set_usuario_local(self, usuario_info):
        """Establece la información del usuario logueado localmente"""
        self.usuario_local = usuario_info
        print(f"[DEBUG] Usuario local establecido en ResegmentacionPrimaTab: {usuario_info}")
        
    def setup_ui(self):
        """Configura la interfaz del tab de resegmentación prima"""
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header distintivo para Prima
        header_layout = QHBoxLayout()
        
        header_icon = QLabel("💰")
        header_icon.setStyleSheet("font-size: 32px; margin-right: 10px;")
        
        header_title = QLabel("RESEGMENTACIÓN PRIMA")
        header_title.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151; margin-bottom: 20px;")
        
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Formulario de resegmentación con colores distintivos para Prima
        form_group = QGroupBox("💰 Configuración Prima")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #ffffff;
                color: #374151;
            }
        """)
        form_layout = QGridLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 25, 20, 20)
        
        # Campos del formulario
        # Pago ID
        pago_id_label = QLabel("Pago ID:")
        pago_id_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(pago_id_label, 0, 0)
        
        self.pago_id_input = QLineEdit()
        self.pago_id_input.setPlaceholderText("Ingrese el ID del pago")
        self.pago_id_input.setMinimumHeight(50)
        self.pago_id_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addWidget(self.pago_id_input, 0, 1)
        
        # Fecha primer pago con botón de calendario
        fecha_label = QLabel("Fecha primer pago:")
        fecha_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(fecha_label, 1, 0)
        
        fecha_layout = QHBoxLayout()
        self.fecha_primer_pago_input = QLineEdit()
        self.fecha_primer_pago_input.setPlaceholderText("YYYY-MM-DD")
        self.fecha_primer_pago_input.setReadOnly(True)
        self.fecha_primer_pago_input.setMinimumHeight(50)
        self.fecha_primer_pago_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: #f9fafb;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: white;
            }
        """)
        
        self.calendario_btn = QPushButton("📅")
        self.calendario_btn.setMinimumSize(50, 50)
        self.calendario_btn.setMaximumWidth(60)
        self.calendario_btn.clicked.connect(self.mostrar_calendario)
        self.calendario_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        fecha_layout.addWidget(self.fecha_primer_pago_input)
        fecha_layout.addWidget(self.calendario_btn)
        form_layout.addLayout(fecha_layout, 1, 1)
        
        # Motivo como input de texto
        motivo_label = QLabel("Motivo:")
        motivo_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(motivo_label, 2, 0)
        
        self.motivo_input = QLineEdit()
        self.motivo_input.setPlaceholderText("Ingrese el motivo del ajuste")
        self.motivo_input.setText("Ajuste")  # Valor por defecto
        self.motivo_input.setMinimumHeight(50)
        self.motivo_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addWidget(self.motivo_input, 2, 1)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.procesar_btn = QPushButton("💰 Procesar Prima")
        self.procesar_btn.clicked.connect(self.procesar_resegmentacion)
        self.procesar_btn.setMinimumSize(250, 60)
        self.procesar_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #1e40af;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        self.limpiar_btn = QPushButton("🧹 Limpiar Formulario")
        self.limpiar_btn.clicked.connect(self.limpiar_formulario)
        self.limpiar_btn.setMinimumSize(200, 60)
        self.limpiar_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #6b7280;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        buttons_layout.addWidget(self.procesar_btn)
        buttons_layout.addWidget(self.limpiar_btn)
        buttons_layout.addStretch()
        
        form_layout.addLayout(buttons_layout, 3, 0, 1, 2)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Área de resultados
        results_group = QGroupBox("Resultados de Resegmentación")
        results_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #f9fafb;
            }
        """)
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText(">>> SISTEMA DE ANÁLISIS RINORISK - TERMINAL PRIMA INICIADA <<<")
        self.results_text.setMinimumHeight(200)
        self.results_text.setStyleSheet(get_terminal_style())
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def mostrar_calendario(self):
        """Muestra un modal con calendario para seleccionar la fecha de primer pago"""
        from datetime import datetime
        
        try:
            # Importar el widget de calendario y clases de fecha según la versión de Qt
            if QT_VARIANT == "PySide6":
                from PySide6.QtWidgets import QCalendarWidget
                from PySide6.QtCore import QDate
            else:
                from PyQt6.QtWidgets import QCalendarWidget
                from PyQt6.QtCore import QDate
                
            # Crear el diálogo del calendario
            dialog = QDialog(self)
            dialog.setWindowTitle("Seleccionar Fecha de Primer Pago")
            dialog.setModal(True)
            dialog.resize(500, 450)
            
            # Layout del diálogo
            layout = QVBoxLayout(dialog)
            
            # Widget de calendario
            calendar = QCalendarWidget()
            
            # Configurar fechas mínima y máxima usando QDate
            min_date = QDate(2020, 1, 1)
            max_date = QDate(2030, 12, 31)
            calendar.setMinimumDate(min_date)
            calendar.setMaximumDate(max_date)
            
            # Habilitar navegación por año y mes
            calendar.setNavigationBarVisible(True)
            calendar.setDateEditEnabled(True)
            calendar.setSelectedDate(QDate.currentDate())
            calendar.setMinimumSize(400, 300)
            
            layout.addWidget(calendar)
            
            # Botones
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)
            
            ok_button = QPushButton("Aceptar")
            cancel_button = QPushButton("Cancelar")
            
            ok_button.setMinimumSize(120, 45)
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            
            cancel_button.setMinimumSize(120, 45)
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(cancel_button)
            buttons_layout.addWidget(ok_button)
            layout.addLayout(buttons_layout)
            
            # Conectar eventos
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # Mostrar diálogo y procesar resultado
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_date = calendar.selectedDate()
                date_string = selected_date.toString("yyyy-MM-dd")
                self.fecha_primer_pago_input.clear()
                self.fecha_primer_pago_input.setText(date_string)
                self.fecha_primer_pago_input.update()
                
        except ImportError:
            QMessageBox.information(self, "Información", "Por favor ingrese la fecha manualmente en formato YYYY-MM-DD")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al mostrar calendario: {str(e)}")
            
    def llamar_api_ajuste(self, pago_id, fecha_primer_pago, motivo):
        """Realiza la llamada a la API de ajuste manual"""
        try:
            url = f"https://condicionesrino.com/api/ajuste-manual/prima-pagada/{pago_id}"
            headers = {
                'x-token': self.api_token,
                'Content-Type': 'application/json'
            }
            # Usar el correo del usuario local como identificador del ajustador
            if self.usuario_local:
                user_email = self.usuario_local.get('email', 'desarrollo-general@rinorisk.com')
            else:
                user_email = 'desarrollo-general@rinorisk.com'  # Fallback
                
            body = {
                "ajuste": {
                    "fechaPago": fecha_primer_pago
                },
                "motivoAjuste": f"{motivo} - pagoId: {pago_id}",
                "nombreAjustador": user_email
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                return False, f"Error {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
        
    def procesar_resegmentacion(self):
        """Procesa la resegmentación usando la API real"""
        pago_id = self.pago_id_input.text().strip()
        fecha_primer_pago = self.fecha_primer_pago_input.text().strip()
        motivo = self.motivo_input.text().strip()
        
        if not pago_id:
            QMessageBox.warning(self, "Error", "Debe ingresar el Pago ID")
            return
            
        if not fecha_primer_pago:
            QMessageBox.warning(self, "Error", "Debe seleccionar la fecha de primer pago")
            return
            
        if not motivo:
            QMessageBox.warning(self, "Error", "Debe ingresar un motivo")
            return
            
        if not self.api_token:
            QMessageBox.warning(self, "Error", "No hay sesión API activa. Vaya a la pestaña Cotejamiento para iniciar sesión.")
            return
        
        # ========================= VALIDACIÓN OTP =========================
        print(f"[OTP] Iniciando validación OTP para resegmentación Prima")
        try:
            from otp_dialog import show_otp_dialog
            
            # Mostrar diálogo OTP y esperar validación
            otp_validated = show_otp_dialog(self, "sofia@rinorisk.com")
            
            if not otp_validated:
                print(f"[OTP] Validación OTP cancelada o fallida")
                QMessageBox.warning(self, "Operación Cancelada", 
                                  "Se requiere validación OTP para ejecutar operaciones de resegmentación.")
                return
            
            print(f"[OTP] ✅ Validación OTP exitosa. Procediendo con resegmentación.")
            
        except Exception as e:
            print(f"[OTP] ❌ Error en validación OTP: {e}")
            QMessageBox.critical(self, "Error OTP", 
                               f"Error en el sistema de validación OTP:\n{str(e)}")
            return
        # ================================================================
            
        self.procesar_btn.setEnabled(False)
        self.procesar_btn.setText("⏳ Procesando...")
        
        # Mostrar modal de carga para resegmentación prima
        self.reseg_loading_modal = SimpleProgressDialog(
            self, 
            "Procesando Resegmentación Prima"
        )
        self.reseg_loading_modal.update_message(f"Aplicando ajuste para el Pago ID: {pago_id}...")
        self.reseg_loading_modal.show_progress()
        
        resultado_inicial = f"""
<span style="color: #00ff41; font-weight: bold;">╔══════════════════════════════════════════════════════════════════╗</span>
<span style="color: #00ff41; font-weight: bold;">║                   RINORISK SECURITY TERMINAL                     ║</span>
<span style="color: #00ff41; font-weight: bold;">║                RESEGMENTACIÓN PRIMA - OPERACIÓN INICIADA         ║</span>
<span style="color: #00ff41; font-weight: bold;">╚══════════════════════════════════════════════════════════════════╝</span>

<span style="color: #ffff00; font-weight: bold;">[CLASIFICADO] DATOS DE OPERACIÓN:</span>
<span style="color: #00ffff;">PAGO_ID:</span> <span style="color: #ffffff;">{pago_id}</span>
<span style="color: #00ffff;">FECHA_TARGET:</span> <span style="color: #ffffff;">{fecha_primer_pago}</span>
<span style="color: #00ffff;">MOTIVO_OPS:</span> <span style="color: #ffffff;">{motivo}</span>

<span style="color: #ff6600; font-weight: bold;">[STATUS]</span> <span style="color: #ffff00;">Estableciendo conexión segura con API...</span>
<span style="color: #ff6600; font-weight: bold;">[STATUS]</span> <span style="color: #ffff00;">Autenticación en progreso...</span>
        """
        self.results_text.setHtml(resultado_inicial)
        
        try:
            # Actualizar progreso del modal
            self.reseg_loading_modal.update_message("Preparando solicitud API...")
            success, response = self.llamar_api_ajuste(pago_id, fecha_primer_pago, motivo)
            
            if success:
                # Actualizar progreso del modal
                self.reseg_loading_modal.update_message("Procesando respuesta del servidor...")
                QTimer.singleShot(500, lambda: self.reseg_loading_modal.update_message("Resegmentación completada"))
                
                resultado = f"""
<span style="color: #00ff41; font-weight: bold;">╔══════════════════════════════════════════════════════════════════╗</span>
<span style="color: #00ff41; font-weight: bold;">║                   RINORISK SECURITY TERMINAL                     ║</span>
<span style="color: #00ff41; font-weight: bold;">║                RESEGMENTACIÓN PRIMA - COMPLETADA                 ║</span>
<span style="color: #00ff41; font-weight: bold;">╚══════════════════════════════════════════════════════════════════╝</span>

<span style="color: #ffff00; font-weight: bold;">[CLASIFICADO] DATOS DE OPERACIÓN:</span>
<span style="color: #00ffff;">PAGO_ID:</span> <span style="color: #ffffff;">{pago_id}</span>
<span style="color: #00ffff;">FECHA_TARGET:</span> <span style="color: #ffffff;">{fecha_primer_pago}</span>
<span style="color: #00ffff;">MOTIVO_OPS:</span> <span style="color: #ffffff;">{motivo}</span>

<span style="color: #00ff00; font-weight: bold;">[SUCCESS] OPERACIÓN COMPLETADA EXITOSAMENTE</span>

<span style="color: #00ffff; font-weight: bold;">RESPUESTA DEL SERVIDOR CENTRAL:</span>
<pre style="color: #ffffff; font-family: monospace; background-color: #1a1a1a; padding: 10px; border-left: 3px solid #00ff41;">
{json.dumps(response, indent=2, ensure_ascii=False)}
</pre>

<span style="color: #ffff00;">TIMESTAMP:</span> <span style="color: #ffffff;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
<span style="color: #ffff00;">STATUS:</span> <span style="color: #00ff00;">OPERACIÓN AUTORIZADA Y EJECUTADA</span>

<span style="color: #00ff00; font-weight: bold;">[CONFIRMED] CAMBIOS APLICADOS EN EL SISTEMA CENTRAL</span>
                """
                
                # Guardar resegmentación en la base de datos
                try:
                    # Obtener información del usuario responsable
                    usuario_responsable = getattr(self, 'usuario_info', {}).get('nombre', 'Usuario Desconocido')
                    
                    # Crear datos de resegmentación
                    resegmentacion_data = {
                        'agente': '',  # Se puede obtener del contexto si está disponible
                        'subramo': '',  # Se puede obtener del contexto si está disponible  
                        'num_poliza': '',  # Se puede obtener del contexto si está disponible
                        'tipo_resegmentacion': 'PRIMA',
                        'fecha_resegmentacion': datetime.now().isoformat(),
                        'usuario_responsable': usuario_responsable,
                        'pago_id': pago_id,
                        'fecha_primer_pago': fecha_primer_pago,
                        'motivo_resegmentacion': motivo,
                        'num_poliza_nuevo_negocio': '',
                        'datos_originales': {
                            'pago_id': pago_id,
                            'fecha_primer_pago': fecha_primer_pago,
                            'motivo': motivo,
                            'timestamp': datetime.now().isoformat()
                        },
                        'respuesta_api': response
                    }
                    
                    # Intentar guardar en la base de datos
                    from resegmentacion_db import ResegmentacionDB
                    db = ResegmentacionDB()
                    
                    # Si tenemos contexto de la tabla de cotejamiento, buscar los datos
                    if hasattr(self.parent(), 'data_table'):
                        # Usar la nueva función de asociación mejorada
                        poliza_encontrada = self.parent().data_table.asociar_poliza_con_respuesta_api(response, pago_id)
                        if poliza_encontrada:
                            resegmentacion_data['agente'] = poliza_encontrada.get('agente', '')
                            resegmentacion_data['subramo'] = poliza_encontrada.get('subramo', '')
                            resegmentacion_data['num_poliza'] = poliza_encontrada.get('num_poliza', '')
                            print(f"[DB] Póliza asociada para pago_id {pago_id}: {poliza_encontrada.get('num_poliza', '')}")
                        else:
                            # Fallback: intentar la búsqueda original
                            poliza_encontrada = self.parent().data_table.buscar_poliza_por_pago_id(pago_id)
                            if poliza_encontrada:
                                resegmentacion_data['agente'] = poliza_encontrada.get('agente', '')
                                resegmentacion_data['subramo'] = poliza_encontrada.get('subramo', '')
                                resegmentacion_data['num_poliza'] = poliza_encontrada.get('num_poliza', '')
                                print(f"[DB] Póliza encontrada (fallback) para pago_id {pago_id}: {poliza_encontrada.get('num_poliza', '')}")
                    
                    success = db.guardar_resegmentacion(resegmentacion_data)
                    if success:
                        print(f"[DB] ✅ Resegmentación Prima guardada en base de datos")
                        # Actualizar la tabla de cotejamiento si está disponible
                        if hasattr(self.parent(), 'data_table'):
                            self.parent().data_table.actualizar_resegmentaciones()
                    else:
                        print(f"[DB] ❌ Error guardando resegmentación Prima en base de datos")
                        
                except Exception as db_error:
                    print(f"[DB] ❌ Error de base de datos: {str(db_error)}")
                
                QMessageBox.information(self, "Éxito", "Resegmentación procesada exitosamente")
                
                # Emitir señal de resegmentación completada
                print(f"[SIGNAL] Emitiendo señal de resegmentación completada (Prima)")
                self.resegmentacion_completada.emit()
            else:
                resultado = f"""
🔄 PROCESAMIENTO DE RESEGMENTACIÓN INICIADO
═══════════════════════════════════════════

🆔 Pago ID: {pago_id}
📅 Fecha primer pago: {fecha_primer_pago}
🔧 Motivo: {motivo}

❌ ERROR EN EL PROCESAMIENTO

📋 Detalles del error:
{response}

- Fecha de intento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Estado: Error al comunicarse con la API

⚠️ Por favor revise los datos e intente nuevamente.
                """
                QMessageBox.critical(self, "Error", f"Error al procesar resegmentación:\n{response}")
                
        except Exception as e:
            resultado = f"""
🔄 PROCESAMIENTO DE RESEGMENTACIÓN INICIADO
═══════════════════════════════════════════

🆔 Pago ID: {pago_id}
📅 Fecha primer pago: {fecha_primer_pago}
🔧 Motivo: {motivo}

💥 ERROR INESPERADO

📋 Detalles del error:
{str(e)}

- Fecha de intento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Estado: Error inesperado en el sistema

⚠️ Por favor contacte al administrador del sistema.
            """
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
        
        finally:
            # Cerrar modal de carga de resegmentación
            if hasattr(self, 'reseg_loading_modal'):
                self.reseg_loading_modal.hide_progress()
            self.procesar_btn.setEnabled(True)
            self.procesar_btn.setText("💰 Procesar Prima")
        
        self.results_text.setHtml(resultado)
        
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.pago_id_input.clear()
        self.fecha_primer_pago_input.clear()
        self.motivo_input.setText("Ajuste")
        self.results_text.clear()

class ResegmentacionNuevoNegocioTab(QWidget):
    """Tab de resegmentación nuevo negocio"""
    
    # Señal para notificar cuando se completa una resegmentación
    resegmentacion_completada = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.api_token = None  # Token para API
        self.user_info = {}  # Información del usuario
        self.usuario_local = None  # Información del usuario logueado localmente
        self.setup_ui()
        
    def set_api_token(self, token):
        """Establece el token de API obtenido del tab de Cotejamiento"""
        self.api_token = token
        print(f"[DEBUG] Token API establecido en ResegmentacionNuevoNegocioTab: {token[:20] if token else 'None'}...")
        
    def set_user_info(self, user_info):
        """Establece la información del usuario obtenida del tab de Cotejamiento"""
        self.user_info = user_info
        user_name = user_info.get('name', 'Usuario Sistema')
        print(f"[DEBUG] Información de usuario establecida en ResegmentacionNuevoNegocioTab: {user_name}")
        
    def set_usuario_local(self, usuario_info):
        """Establece la información del usuario logueado localmente"""
        self.usuario_local = usuario_info
        print(f"[DEBUG] Usuario local establecido en ResegmentacionNuevoNegocioTab: {usuario_info}")
        
    def setup_ui(self):
        """Configura la interfaz del tab de resegmentación nuevo negocio"""
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header distintivo para Nuevo Negocio
        header_layout = QHBoxLayout()
        
        header_icon = QLabel("🚀")
        header_icon.setStyleSheet("font-size: 32px; margin-right: 10px;")
        
        header_title = QLabel("RESEGMENTACIÓN NUEVO NEGOCIO")
        header_title.setStyleSheet("font-size: 22px; font-weight: 600; color: #374151; margin-bottom: 20px;")
        
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Formulario de resegmentación con colores distintivos para Nuevo Negocio
        form_group = QGroupBox("🚀 Configuración Nuevo Negocio")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #ffffff;
                color: #374151;
            }
        """)
        form_layout = QGridLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 25, 20, 20)
        
        # Campos del formulario
        # Número de Póliza
        pago_id_label = QLabel("Número de Póliza:")
        pago_id_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(pago_id_label, 0, 0)
        
        self.pago_id_input = QLineEdit()
        self.pago_id_input.setPlaceholderText("Ingrese el número de póliza")
        self.pago_id_input.setMinimumHeight(50)
        self.pago_id_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addWidget(self.pago_id_input, 0, 1)
        
        # Mover a: con botón de calendario
        fecha_label = QLabel("Mover a:")
        fecha_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(fecha_label, 1, 0)
        
        fecha_layout = QHBoxLayout()
        self.fecha_primer_pago_input = QLineEdit()
        self.fecha_primer_pago_input.setPlaceholderText("YYYY-MM-DD")
        self.fecha_primer_pago_input.setReadOnly(True)
        self.fecha_primer_pago_input.setMinimumHeight(50)
        self.fecha_primer_pago_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: #f9fafb;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: white;
            }
        """)
        
        self.calendario_btn = QPushButton("📅")
        self.calendario_btn.setMinimumSize(50, 50)
        self.calendario_btn.setMaximumWidth(60)
        self.calendario_btn.clicked.connect(self.mostrar_calendario)
        self.calendario_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        fecha_layout.addWidget(self.fecha_primer_pago_input)
        fecha_layout.addWidget(self.calendario_btn)
        form_layout.addLayout(fecha_layout, 1, 1)
        
        # Motivo como input de texto
        motivo_label = QLabel("Motivo:")
        motivo_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                padding: 8px 0px;
            }
        """)
        form_layout.addWidget(motivo_label, 2, 0)
        
        self.motivo_input = QLineEdit()
        self.motivo_input.setPlaceholderText("Ingrese el motivo del ajuste")
        self.motivo_input.setText("Ajuste")  # Valor por defecto
        self.motivo_input.setMinimumHeight(50)
        self.motivo_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 12px 15px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: white;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addWidget(self.motivo_input, 2, 1)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.procesar_btn = QPushButton("🚀 Procesar Nuevo Negocio")
        self.procesar_btn.clicked.connect(self.procesar_resegmentacion)
        self.procesar_btn.setMinimumSize(280, 60)
        self.procesar_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #1e40af;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        self.limpiar_btn = QPushButton("🧹 Limpiar Formulario")
        self.limpiar_btn.clicked.connect(self.limpiar_formulario)
        self.limpiar_btn.setMinimumSize(200, 60)
        self.limpiar_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 6px;
                background-color: #6b7280;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        
        buttons_layout.addWidget(self.procesar_btn)
        buttons_layout.addWidget(self.limpiar_btn)
        buttons_layout.addStretch()
        
        form_layout.addLayout(buttons_layout, 3, 0, 1, 2)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Área de resultados
        results_group = QGroupBox("Resultados de Resegmentación")
        results_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #f9fafb;
            }
        """)
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText(">>> SISTEMA DE ANÁLISIS RINORISK - TERMINAL NUEVO NEGOCIO INICIADA <<<")
        self.results_text.setMinimumHeight(200)
        self.results_text.setStyleSheet(get_terminal_style())
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def mostrar_calendario(self):
        """Muestra un modal con calendario para seleccionar la fecha de primer pago"""
        from datetime import datetime
        
        try:
            # Importar el widget de calendario y clases de fecha según la versión de Qt
            if QT_VARIANT == "PySide6":
                from PySide6.QtWidgets import QCalendarWidget
                from PySide6.QtCore import QDate
            else:
                from PyQt6.QtWidgets import QCalendarWidget
                from PyQt6.QtCore import QDate
                
            # Crear el diálogo del calendario
            dialog = QDialog(self)
            dialog.setWindowTitle("Seleccionar Fecha de Primer Pago")
            dialog.setModal(True)
            dialog.resize(500, 450)
            
            # Layout del diálogo
            layout = QVBoxLayout(dialog)
            
            # Widget de calendario
            calendar = QCalendarWidget()
            
            # Configurar fechas mínima y máxima usando QDate
            min_date = QDate(2020, 1, 1)
            max_date = QDate(2030, 12, 31)
            calendar.setMinimumDate(min_date)
            calendar.setMaximumDate(max_date)
            
            # Habilitar navegación por año y mes
            calendar.setNavigationBarVisible(True)
            calendar.setDateEditEnabled(True)
            calendar.setSelectedDate(QDate.currentDate())
            calendar.setMinimumSize(400, 300)
            
            layout.addWidget(calendar)
            
            # Botones
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)
            
            ok_button = QPushButton("Aceptar")
            cancel_button = QPushButton("Cancelar")
            
            ok_button.setMinimumSize(120, 45)
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            
            cancel_button.setMinimumSize(120, 45)
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #6b7280;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
            """)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(cancel_button)
            buttons_layout.addWidget(ok_button)
            layout.addLayout(buttons_layout)
            
            # Conectar eventos
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # Mostrar diálogo y procesar resultado
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_date = calendar.selectedDate()
                date_string = selected_date.toString("yyyy-MM-dd")
                self.fecha_primer_pago_input.clear()
                self.fecha_primer_pago_input.setText(date_string)
                self.fecha_primer_pago_input.update()
                
        except ImportError:
            QMessageBox.information(self, "Información", "Por favor ingrese la fecha manualmente en formato YYYY-MM-DD")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al mostrar calendario: {str(e)}")
            
    def llamar_api_ajuste(self, numero_poliza, fecha_primer_pago, motivo):
        """Realiza la llamada a la API de ajuste manual para nuevo negocio"""
        print(f"\n{'='*80}")
        print(f"[RESEGMENTACIÓN NUEVO NEGOCIO] INICIANDO PETICIÓN API")
        print(f"{'='*80}")
        
        try:
            url = f"https://condicionesrino.com/api/ajuste-manual/nuevo-negocio/{numero_poliza}"
            headers = {
                'x-token': self.api_token,
                'Content-Type': 'application/json'
            }
            # Usar el correo del usuario local como identificador del ajustador
            if self.usuario_local:
                user_email = self.usuario_local.get('email', 'desarrollo-general@rinorisk.com')
            else:
                user_email = 'desarrollo-general@rinorisk.com'  # Fallback
                
            body = {
                "ajuste": {
                    "fechaPrimerPago": fecha_primer_pago
                },
                "motivoAjuste": f"{motivo}",
                "nombreAjustador": user_email
            }
            
            # LOGS DETALLADOS DE LA PETICIÓN
            print(f"[REQUEST] URL: {url}")
            print(f"[REQUEST] Método: POST")
            print(f"[REQUEST] Headers:")
            for header_key, header_value in headers.items():
                if header_key == 'x-token':
                    print(f"  {header_key}: {header_value[:20]}...{header_value[-10:] if len(header_value) > 30 else header_value}")
                else:
                    print(f"  {header_key}: {header_value}")
            
            print(f"[REQUEST] Body (JSON):")
            import json
            print(json.dumps(body, indent=2, ensure_ascii=False))
            
            print(f"\n[API] Enviando petición...")
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            # LOGS DE LA RESPUESTA
            print(f"[RESPONSE] Status Code: {response.status_code}")
            print(f"[RESPONSE] Headers:")
            for header_key, header_value in response.headers.items():
                print(f"  {header_key}: {header_value}")
            
            print(f"[RESPONSE] Raw Text: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[RESPONSE] JSON Parsed Successfully:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    print(f"[SUCCESS] ✅ Petición exitosa - Status 200")
                    return True, result
                except json.JSONDecodeError as json_error:
                    print(f"[ERROR] ❌ Error parseando JSON: {json_error}")
                    print(f"[ERROR] Raw response: {response.text}")
                    return False, f"Error parseando JSON: {json_error}"
            else:
                print(f"[ERROR] ❌ Error HTTP {response.status_code}")
                print(f"[ERROR] Response text: {response.text}")
                return False, f"Error {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout as timeout_error:
            print(f"[ERROR] ❌ Timeout (30s): {timeout_error}")
            return False, f"Timeout después de 30 segundos: {str(timeout_error)}"
        except requests.exceptions.ConnectionError as conn_error:
            print(f"[ERROR] ❌ Error de conexión: {conn_error}")
            return False, f"Error de conexión: {str(conn_error)}"
        except requests.exceptions.RequestException as req_error:
            print(f"[ERROR] ❌ Error de petición: {req_error}")
            return False, f"Error de petición: {str(req_error)}"
        except Exception as e:
            print(f"[ERROR] ❌ Error inesperado: {e}")
            import traceback
            print(f"[ERROR] Traceback completo:")
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}"
        finally:
            print(f"{'='*80}")
            print(f"[RESEGMENTACIÓN NUEVO NEGOCIO] PETICIÓN API FINALIZADA")
            print(f"{'='*80}\n")
        
    def procesar_resegmentacion(self):
        """Procesa la resegmentación usando la API real"""
        print(f"\n🚀 [NUEVO NEGOCIO] INICIANDO PROCESO DE RESEGMENTACIÓN")
        print(f"{'='*60}")
        
        numero_poliza = self.pago_id_input.text().strip()
        fecha_primer_pago = self.fecha_primer_pago_input.text().strip()
        motivo = self.motivo_input.text().strip()
        
        print(f"[INPUT] Número de Póliza: '{numero_poliza}'")
        print(f"[INPUT] Mover a (fecha): '{fecha_primer_pago}'")
        print(f"[INPUT] Motivo: '{motivo}'")
        print(f"[INPUT] Token API disponible: {'Sí' if self.api_token else 'No'}")
        if self.api_token:
            print(f"[INPUT] Token (parcial): {self.api_token[:20]}...{self.api_token[-10:]}")
        print(f"[INPUT] Usuario logueado: {self.user_info.get('name', 'N/A')}")
        
        # Validaciones con logs
        if not numero_poliza:
            print(f"[ERROR] ❌ Validación fallida: Número de Póliza vacío")
            QMessageBox.warning(self, "Error", "Debe ingresar el Número de Póliza")
            return
            
        if not fecha_primer_pago:
            print(f"[ERROR] ❌ Validación fallida: Fecha vacía")
            QMessageBox.warning(self, "Error", "Debe seleccionar la fecha de mover a")
            return
            
        if not motivo:
            print(f"[ERROR] ❌ Validación fallida: Motivo vacío")
            QMessageBox.warning(self, "Error", "Debe ingresar un motivo")
            return
            
        if not self.api_token:
            print(f"[ERROR] ❌ Validación fallida: Token API no disponible")
            QMessageBox.warning(self, "Error", "No hay sesión API activa. Vaya a la pestaña Cotejamiento para iniciar sesión.")
            return
            
        print(f"[VALIDATION] ✅ Todas las validaciones pasaron exitosamente")
        
        # ========================= VALIDACIÓN OTP =========================
        print(f"[OTP] Iniciando validación OTP para resegmentación Nuevo Negocio")
        try:
            from otp_dialog import show_otp_dialog
            
            # Mostrar diálogo OTP y esperar validacióndesarrollo@rinorisk.com
            otp_validated = show_otp_dialog(self, "")
            
            if not otp_validated:
                print(f"[OTP] Validación OTP cancelada o fallida")
                QMessageBox.warning(self, "Operación Cancelada", 
                                  "Se requiere validación OTP para ejecutar operaciones de resegmentación.")
                return
            
            print(f"[OTP] ✅ Validación OTP exitosa. Procediendo con resegmentación.")
            
        except Exception as e:
            print(f"[OTP] ❌ Error en validación OTP: {e}")
            QMessageBox.critical(self, "Error OTP", 
                               f"Error en el sistema de validación OTP:\n{str(e)}")
            return
        # ================================================================
            
        print(f"[UI] Deshabilitando botón y mostrando modal de carga")
        self.procesar_btn.setEnabled(False)
        self.procesar_btn.setText("⏳ Procesando...")
        
        # Mostrar modal de carga para resegmentación nuevo negocio
        self.reseg_loading_modal = SimpleProgressDialog(
            self, 
            "Procesando Resegmentación Nuevo Negocio"
        )
        self.reseg_loading_modal.update_message(f"Aplicando ajuste para la Póliza: {numero_poliza}...")
        self.reseg_loading_modal.show_progress()
        print(f"[UI] Modal de carga mostrado")
        
        resultado_inicial = f"""
<span style="color: #00ff41; font-weight: bold;">╔══════════════════════════════════════════════════════════════════╗</span>
<span style="color: #00ff41; font-weight: bold;">║                   RINORISK SECURITY TERMINAL                     ║</span>
<span style="color: #00ff41; font-weight: bold;">║            RESEGMENTACIÓN NUEVO NEGOCIO - OPERACIÓN INICIADA     ║</span>
<span style="color: #00ff41; font-weight: bold;">╚══════════════════════════════════════════════════════════════════╝</span>

<span style="color: #ffff00; font-weight: bold;">[CLASIFICADO] DATOS DE OPERACIÓN:</span>
<span style="color: #00ffff;">POLIZA_ID:</span> <span style="color: #ffffff;">{numero_poliza}</span>
<span style="color: #00ffff;">FECHA_TARGET:</span> <span style="color: #ffffff;">{fecha_primer_pago}</span>
<span style="color: #00ffff;">MOTIVO_OPS:</span> <span style="color: #ffffff;">{motivo}</span>

<span style="color: #ff6600; font-weight: bold;">[STATUS]</span> <span style="color: #ffff00;">Iniciando protocolo de seguridad...</span>
<span style="color: #ff6600; font-weight: bold;">[STATUS]</span> <span style="color: #ffff00;">Estableciendo túnel cifrado con API...</span>
        """
        self.results_text.setHtml(resultado_inicial)
        print(f"[UI] Texto de resultado inicial establecido")
        
        try:
            print(f"[PROCESS] Iniciando proceso de llamada a API...")
            # Actualizar progreso del modal
            self.reseg_loading_modal.update_message("Preparando solicitud API...")
            print(f"[PROCESS] Progreso modal: 30% - Preparando solicitud API")
            
            success, response = self.llamar_api_ajuste(numero_poliza, fecha_primer_pago, motivo)
            print(f"[PROCESS] Llamada API completada - Success: {success}")
            
            if success:
                print(f"[SUCCESS] ✅ API respondió exitosamente")
                print(f"[SUCCESS] Respuesta recibida: {response}")
                # Actualizar progreso del modal
                self.reseg_loading_modal.update_message("Procesando respuesta del servidor...")
                print(f"[PROCESS] Progreso modal: 80% - Procesando respuesta")
                QTimer.singleShot(500, lambda: self.reseg_loading_modal.update_message("Resegmentación completada"))
                
                resultado = f"""
🔄 PROCESAMIENTO DE RESEGMENTACIÓN INICIADO
═══════════════════════════════════════════

🆔 Número de Póliza: {numero_poliza}
📅 Mover a: {fecha_primer_pago}
🔧 Motivo: {motivo}

⏳ Procesando con API...

✅ RESEGMENTACIÓN COMPLETADA EXITOSAMENTE

📊 Resultados de la API:
{json.dumps(response, indent=2, ensure_ascii=False)}

- Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Estado: Enviado exitosamente a la API

💾 Cambios aplicados en el sistema.
                """
                
                # Guardar resegmentación en la base de datos
                try:
                    # Obtener información del usuario responsable
                    usuario_responsable = getattr(self, 'user_info', {}).get('name', 'Usuario Desconocido')
                    
                    # Crear datos de resegmentación
                    resegmentacion_data = {
                        'agente': '',  # Se puede obtener del contexto si está disponible
                        'subramo': '',  # Se puede obtener del contexto si está disponible  
                        'num_poliza': numero_poliza,  # Tenemos el número de póliza directamente
                        'tipo_resegmentacion': 'NUEVO_NEGOCIO',
                        'fecha_resegmentacion': datetime.now().isoformat(),
                        'usuario_responsable': usuario_responsable,
                        'pago_id': '',
                        'fecha_primer_pago': fecha_primer_pago,
                        'motivo_resegmentacion': motivo,
                        'num_poliza_nuevo_negocio': numero_poliza,
                        'datos_originales': {
                            'numero_poliza': numero_poliza,
                            'fecha_primer_pago': fecha_primer_pago,
                            'motivo': motivo,
                            'timestamp': datetime.now().isoformat()
                        },
                        'respuesta_api': response
                    }
                    
                    # Intentar guardar en la base de datos
                    from resegmentacion_db import ResegmentacionDB
                    db = ResegmentacionDB()
                    
                    # Si tenemos contexto de la tabla de cotejamiento, buscar los datos
                    if hasattr(self.parent(), 'data_table') and hasattr(self.parent().data_table, 'current_data'):
                        # Buscar la póliza en los datos actuales
                        for row in self.parent().data_table.current_data:
                            if row.get('Núm. Póliza', '') == numero_poliza:
                                resegmentacion_data['agente'] = row.get('Agente', '')
                                resegmentacion_data['subramo'] = row.get('Subramo', '')
                                break
                    
                    success = db.guardar_resegmentacion(resegmentacion_data)
                    if success:
                        print(f"[DB] ✅ Resegmentación Nuevo Negocio guardada en base de datos")
                        # Actualizar la tabla de cotejamiento si está disponible
                        if hasattr(self.parent(), 'data_table'):
                            self.parent().data_table.actualizar_resegmentaciones()
                    else:
                        print(f"[DB] ❌ Error guardando resegmentación Nuevo Negocio en base de datos")
                        
                except Exception as db_error:
                    print(f"[DB] ❌ Error de base de datos: {str(db_error)}")
                
                print(f"[UI] Mostrando mensaje de éxito al usuario")
                QMessageBox.information(self, "Éxito", "Resegmentación procesada exitosamente")
                
                # Emitir señal de resegmentación completada
                print(f"[SIGNAL] Emitiendo señal de resegmentación completada")
                self.resegmentacion_completada.emit()
            else:
                print(f"[ERROR] ❌ API falló")
                print(f"[ERROR] Respuesta de error: {response}")
                resultado = f"""
🔄 PROCESAMIENTO DE RESEGMENTACIÓN INICIADO
═══════════════════════════════════════════

🆔 Número de Póliza: {numero_poliza}
📅 Mover a: {fecha_primer_pago}
🔧 Motivo: {motivo}

❌ ERROR EN EL PROCESAMIENTO

📋 Detalles del error:
{response}

- Fecha de intento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Estado: Error al comunicarse con la API

⚠️ Por favor revise los datos e intente nuevamente.
                """
                print(f"[UI] Mostrando mensaje de error al usuario")
                QMessageBox.critical(self, "Error", f"Error al procesar resegmentación:\n{response}")
                
        except Exception as e:
            print(f"[EXCEPTION] ❌ Error inesperado en procesar_resegmentacion: {e}")
            import traceback
            print(f"[EXCEPTION] Traceback completo:")
            traceback.print_exc()
            resultado = f"""
🔄 PROCESAMIENTO DE RESEGMENTACIÓN INICIADO
═══════════════════════════════════════════

🆔 Número de Póliza: {numero_poliza}
📅 Mover a: {fecha_primer_pago}
🔧 Motivo: {motivo}

💥 ERROR INESPERADO

📋 Detalles del error:
{str(e)}

- Fecha de intento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Estado: Error inesperado en el sistema

⚠️ Por favor contacte al administrador del sistema.
            """
            print(f"[UI] Mostrando mensaje de error inesperado al usuario")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
        
        finally:
            print(f"[CLEANUP] Iniciando limpieza final...")
            # Cerrar modal de carga de resegmentación
            if hasattr(self, 'reseg_loading_modal'):
                self.reseg_loading_modal.hide_progress()
                print(f"[CLEANUP] Modal de carga cerrado")
            self.procesar_btn.setEnabled(True)
            self.procesar_btn.setText("🚀 Procesar Nuevo Negocio")
            print(f"[CLEANUP] Botón restaurado y habilitado")
        
        self.results_text.setHtml(resultado)
        print(f"[UI] Texto de resultado final establecido")
        print(f"🚀 [NUEVO NEGOCIO] PROCESO DE RESEGMENTACIÓN FINALIZADO")
        print(f"{'='*60}\n")
        
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.pago_id_input.clear()
        self.fecha_primer_pago_input.clear()
        self.motivo_input.setText("Ajuste")
        self.results_text.clear()

class ResegmentacionTab(QWidget):
    """Tab de resegmentación con sub-tabs"""
    
    def __init__(self):
        super().__init__()
        self.api_token = None  # Token para API
        self.user_info = {}  # Información del usuario
        self.usuario_local = None  # Información del usuario logueado localmente
        self.setup_ui()
        
    def set_api_token(self, token):
        """Establece el token de API obtenido del tab de Cotejamiento"""
        self.api_token = token
        print(f"[DEBUG] Token API establecido en ResegmentacionTab: {token[:20] if token else 'None'}...")
        
    def set_user_info(self, user_info):
        """Establece la información del usuario obtenida del tab de Cotejamiento"""
        self.user_info = user_info
        user_name = user_info.get('name', 'Usuario Sistema')
        print(f"[DEBUG] Información de usuario establecida en ResegmentacionTab: {user_name}")
        
    def set_usuario_local(self, usuario_info):
        """Establece la información del usuario logueado localmente"""
        self.usuario_local = usuario_info
        print(f"[DEBUG] Usuario local establecido en ResegmentacionTab: {usuario_info}")
        
        # Pasar la información a los sub-tabs
        if hasattr(self, 'resegmentacion_prima_tab'):
            self.resegmentacion_prima_tab.set_usuario_local(usuario_info)
        if hasattr(self, 'resegmentacion_nuevo_negocio_tab'):
            self.resegmentacion_nuevo_negocio_tab.set_usuario_local(usuario_info)
        
    def setup_ui(self):
        """Configura la interfaz del tab de resegmentación con sub-tabs"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sub-tabs widget
        self.sub_tab_widget = QTabWidget()
        self.sub_tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Crear sub-tabs
        self.resegmentacion_prima_tab = ResegmentacionPrimaTab()
        self.resegmentacion_nuevo_negocio_tab = ResegmentacionNuevoNegocioTab()
        
        # Conectar señales de resegmentación completada
        self.resegmentacion_prima_tab.resegmentacion_completada.connect(self.on_resegmentacion_completada)
        self.resegmentacion_nuevo_negocio_tab.resegmentacion_completada.connect(self.on_resegmentacion_completada)
        
        # Agregar sub-tabs
        self.sub_tab_widget.addTab(self.resegmentacion_prima_tab, "💰 Resegmentación Prima")
        self.sub_tab_widget.addTab(self.resegmentacion_nuevo_negocio_tab, "🚀 Resegmentación Nuevo Negocio")
        
        layout.addWidget(self.sub_tab_widget)
        self.setLayout(layout)
        
        # Si ya tenemos información del usuario local, pasarla a los sub-tabs
        if self.usuario_local:
            self.resegmentacion_prima_tab.set_usuario_local(self.usuario_local)
            self.resegmentacion_nuevo_negocio_tab.set_usuario_local(self.usuario_local)
    
    def on_resegmentacion_completada(self):
        """Manejador para cuando se completa una resegmentación en cualquier sub-tab"""
        try:
            print("[DEBUG] 🔄 Resegmentación completada, actualizando visualización...")
            
            # Buscar la tabla principal (CotejamientoTab)
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'cotejamiento_tab'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'cotejamiento_tab'):
                cotejamiento_tab = parent_window.cotejamiento_tab
                if hasattr(cotejamiento_tab, 'data_table'):
                    print("[DEBUG] 📊 Actualizando tabla de cotejamiento...")
                    cotejamiento_tab.data_table.actualizar_visualizacion_resegmentaciones()
                    print("[DEBUG] ✅ Tabla actualizada exitosamente")
                else:
                    print("[DEBUG] ⚠️ No se encontró data_table en cotejamiento_tab")
            else:
                print("[DEBUG] ⚠️ No se encontró cotejamiento_tab para actualizar")
                
        except Exception as e:
            print(f"[ERROR] Error actualizando visualización tras resegmentación: {e}")
        
    def set_api_token(self, token):
        """Establece el token de API para todos los sub-tabs de resegmentación"""
        self.api_token = token
        self.resegmentacion_prima_tab.set_api_token(token)
        self.resegmentacion_nuevo_negocio_tab.set_api_token(token)
        
    def set_user_info(self, user_info):
        """Establece la información del usuario para todos los sub-tabs de resegmentación"""
        self.user_info = user_info
        self.resegmentacion_prima_tab.set_user_info(user_info)
        self.resegmentacion_nuevo_negocio_tab.set_user_info(user_info)

class PrincipalWindow(QWidget):
    """Ventana principal con tabs de funcionalidades"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.usuario_local = None  # Información del usuario logueado localmente
        self.setup_ui()
        
    def set_usuario_autenticado(self, usuario_info):
        """Establece la información del usuario autenticado localmente"""
        self.usuario_local = usuario_info
        print(f"[DEBUG] Usuario local establecido: {usuario_info}")
        
        # Pasar la información del usuario local a los tabs que la necesiten
        if hasattr(self, 'resegmentacion_tab'):
            self.resegmentacion_tab.set_usuario_local(usuario_info)
        
    def setup_ui(self):
        """Configura la interfaz principal"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget con botón cerrar sesión
        tab_container = QWidget()
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Header con botón cerrar sesión
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        # Botón cerrar sesión
        logout_btn = QPushButton("🚪 Cerrar Sesión")
        logout_btn.clicked.connect(self.logout_requested.emit)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                color: #374151;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                border-color: #fca5a5;
                color: #dc2626;
            }
        """)
        top_bar.addWidget(logout_btn)
        
        tab_layout.addLayout(top_bar)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Crear tabs
        self.cotejamiento_tab = CotejamientoTab()
        self.resegmentacion_tab = ResegmentacionTab()
        
        # Conectar signals para compartir token y usuario entre tabs
        self.cotejamiento_tab.token_updated.connect(self.resegmentacion_tab.set_api_token)
        self.cotejamiento_tab.user_updated.connect(self.resegmentacion_tab.set_user_info)
        
        # Agregar tabs
        self.tab_widget.addTab(self.cotejamiento_tab, "📊 Cotejamiento")
        self.tab_widget.addTab(self.resegmentacion_tab, "🔄 Resegmentación")
        
        tab_layout.addWidget(self.tab_widget)
        layout.addWidget(tab_container)
        
        self.setLayout(layout)
        
        # Estilos
        self.setup_styles()
        
        # Si ya tenemos información del usuario local, pasarla a los tabs
        if self.usuario_local:
            self.resegmentacion_tab.set_usuario_local(self.usuario_local)
        

        
    def setup_styles(self):
        """Configura los estilos de la ventana principal"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                background-color: white;
                border-radius: 8px;
                margin-top: -1px;
            }
            
            QTabBar::tab {
                background-color: #f3f4f6;
                color: #6b7280;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #e5e7eb;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #1f2937;
                border-bottom-color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #e5e7eb;
                color: #374151;
            }
            
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f9fafb;
            }
        """)

# Función de compatibilidad (no se usa en PyQt pero se mantiene para compatibilidad)
def setup_inter_font():
    """Función de compatibilidad - no necesaria en PyQt"""
    pass

def create_cotejamiento_tab():
    """Función de compatibilidad - no se usa en PyQt"""
    pass

def create_resegmentacion_tab():
    """Función de compatibilidad - no se usa en PyQt"""
    pass 

class SimpleProgressDialog(QDialog):
    """Diálogo de progreso simple y liviano"""
    
    def __init__(self, parent=None, title="Procesando..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 120)
        self.setModal(True)
        
        # Layout simple
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Mensaje principal
        self.message_label = QLabel("Procesando...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Barra de progreso simple
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def update_message(self, message):
        """Actualiza el mensaje"""
        self.message_label.setText(message)
        
    def show_progress(self):
        """Muestra el diálogo"""
        self.show()
        
    def hide_progress(self):
        """Oculta el diálogo"""
        self.hide()
