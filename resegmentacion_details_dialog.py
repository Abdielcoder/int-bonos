#!/usr/bin/env python3
"""
Diálogo para mostrar detalles de resegmentación
"""

import json
from datetime import datetime
from typing import Dict, Optional

try:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QTextEdit, QGroupBox, QGridLayout,
                                 QScrollArea, QWidget, QFrame, QMessageBox)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont, QPixmap, QIcon
except ImportError:
    try:
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QTextEdit, QGroupBox, QGridLayout,
                                   QScrollArea, QWidget, QFrame, QMessageBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont, QPixmap, QIcon
    except ImportError:
        print("❌ Error: No se encontró PyQt6 ni PySide6")
        exit(1)

class ResegmentacionDetailsDialog(QDialog):
    """Diálogo para mostrar detalles completos de una resegmentación"""
    
    def __init__(self, resegmentacion_data: Dict, parent=None):
        super().__init__(parent)
        self.resegmentacion_data = resegmentacion_data
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("Detalles de Resegmentación")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con título
        header_layout = QHBoxLayout()
        
        # Icono según tipo de resegmentación
        tipo = self.resegmentacion_data.get('tipo_resegmentacion', '')
        if tipo == 'PRIMA':
            icon_text = "💰"
            title_text = "RESEGMENTACIÓN PRIMA"
            color = "#d97706"
        else:
            icon_text = "🚀"
            title_text = "RESEGMENTACIÓN NUEVO NEGOCIO"
            color = "#1e40af"
        
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 32px; margin-right: 10px;")
        
        title_label = QLabel(title_text)
        title_label.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {color};")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Área de contenido con scroll
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Información básica
        basic_info_group = self.create_basic_info_group()
        scroll_layout.addWidget(basic_info_group)
        
        # Información de resegmentación
        reseg_info_group = self.create_resegmentation_info_group()
        scroll_layout.addWidget(reseg_info_group)
        
        # Datos originales
        original_data_group = self.create_original_data_group()
        scroll_layout.addWidget(original_data_group)
        
        # Respuesta de la API
        api_response_group = self.create_api_response_group()
        scroll_layout.addWidget(api_response_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Botón revertir (si es posible)
        if self.resegmentacion_data.get('estado', '') == 'ACTIVO':
            revert_btn = QPushButton("🔄 Revertir Resegmentación")
            revert_btn.clicked.connect(self.revertir_resegmentacion)
            revert_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: white;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    margin-right: 10px;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
            """)
            buttons_layout.addWidget(revert_btn)
        
        close_btn = QPushButton("✕ Cerrar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        buttons_layout.addWidget(close_btn)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
    
    def create_basic_info_group(self) -> QGroupBox:
        """Crea el grupo de información básica"""
        group = QGroupBox("📋 Información Básica")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # Información básica
        fields = [
            ("Agente:", self.resegmentacion_data.get('agente', 'N/A')),
            ("Subramo:", self.resegmentacion_data.get('subramo', 'N/A')),
            ("Número de Póliza:", self.resegmentacion_data.get('num_poliza', 'N/A')),
            ("Estado:", self.resegmentacion_data.get('estado', 'N/A')),
        ]
        
        for i, (label_text, value_text) in enumerate(fields):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; color: #374151;")
            
            value = QLabel(str(value_text))
            value.setStyleSheet("color: #6b7280; background-color: #f9fafb; padding: 5px; border-radius: 4px;")
            
            layout.addWidget(label, i, 0)
            layout.addWidget(value, i, 1)
        
        group.setLayout(layout)
        return group
    
    def create_resegmentation_info_group(self) -> QGroupBox:
        """Crea el grupo de información de resegmentación"""
        group = QGroupBox("🔄 Información de Resegmentación")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # Formatear fecha
        fecha_reseg = self.resegmentacion_data.get('fecha_resegmentacion', '')
        if fecha_reseg:
            try:
                dt = datetime.fromisoformat(fecha_reseg.replace('Z', '+00:00'))
                fecha_formatted = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                fecha_formatted = fecha_reseg
        else:
            fecha_formatted = 'N/A'
        
        fields = [
            ("Tipo de Resegmentación:", self.resegmentacion_data.get('tipo_resegmentacion', 'N/A')),
            ("Fecha de Resegmentación:", fecha_formatted),
            ("Usuario Responsable:", self.resegmentacion_data.get('usuario_responsable', 'N/A')),
            ("Pago ID:", self.resegmentacion_data.get('pago_id', 'N/A')),
            ("Fecha Primer Pago:", self.resegmentacion_data.get('fecha_primer_pago', 'N/A')),
            ("Número Póliza Nuevo Negocio:", self.resegmentacion_data.get('num_poliza_nuevo_negocio', 'N/A')),
        ]
        
        for i, (label_text, value_text) in enumerate(fields):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; color: #374151;")
            
            value = QLabel(str(value_text))
            value.setStyleSheet("color: #6b7280; background-color: #f9fafb; padding: 5px; border-radius: 4px;")
            value.setWordWrap(True)
            
            layout.addWidget(label, i, 0)
            layout.addWidget(value, i, 1)
        
        # Motivo en área de texto separada
        motivo = self.resegmentacion_data.get('motivo_resegmentacion', '')
        if motivo:
            motivo_label = QLabel("Motivo de Resegmentación:")
            motivo_label.setStyleSheet("font-weight: 600; color: #374151;")
            
            motivo_text = QTextEdit()
            motivo_text.setPlainText(motivo)
            motivo_text.setMaximumHeight(100)
            motivo_text.setReadOnly(True)
            motivo_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f9fafb;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 5px;
                    color: #6b7280;
                }
            """)
            
            layout.addWidget(motivo_label, len(fields), 0)
            layout.addWidget(motivo_text, len(fields), 1)
        
        group.setLayout(layout)
        return group
    
    def create_original_data_group(self) -> QGroupBox:
        """Crea el grupo de datos originales"""
        group = QGroupBox("📊 Datos Originales")
        layout = QVBoxLayout()
        
        datos_originales_str = self.resegmentacion_data.get('datos_originales', '{}')
        try:
            datos_originales = json.loads(datos_originales_str) if isinstance(datos_originales_str, str) else datos_originales_str
            formatted_data = json.dumps(datos_originales, indent=2, ensure_ascii=False)
        except:
            formatted_data = str(datos_originales_str)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(formatted_data)
        text_edit.setMaximumHeight(200)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_edit)
        group.setLayout(layout)
        return group
    
    def create_api_response_group(self) -> QGroupBox:
        """Crea el grupo de respuesta de la API"""
        group = QGroupBox("🌐 Respuesta de la API")
        layout = QVBoxLayout()
        
        respuesta_api_str = self.resegmentacion_data.get('respuesta_api', '{}')
        try:
            respuesta_api = json.loads(respuesta_api_str) if isinstance(respuesta_api_str, str) else respuesta_api_str
            formatted_response = json.dumps(respuesta_api, indent=2, ensure_ascii=False)
        except:
            formatted_response = str(respuesta_api_str)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(formatted_response)
        text_edit.setMaximumHeight(200)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_edit)
        group.setLayout(layout)
        return group
    
    def revertir_resegmentacion(self):
        """Revierte una resegmentación"""
        reply = QMessageBox.question(
            self, 
            "Confirmar Reversión",
            "¿Está seguro de que desea revertir esta resegmentación?\n\nEsta acción marcará la resegmentación como revertida.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from resegmentacion_db import ResegmentacionDB
                
                db = ResegmentacionDB()
                success = db.revertir_resegmentacion(
                    self.resegmentacion_data.get('agente', ''),
                    self.resegmentacion_data.get('subramo', ''),
                    self.resegmentacion_data.get('num_poliza', '')
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Reversión Exitosa",
                        "La resegmentación ha sido revertida exitosamente."
                    )
                    self.accept()  # Cerrar el diálogo
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se pudo revertir la resegmentación. Intente nuevamente."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al revertir resegmentación: {str(e)}"
                )
    
    def setup_styles(self):
        """Configura los estilos del diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #374151;
            }
            
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
        """) 