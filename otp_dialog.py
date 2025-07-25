#!/usr/bin/env python3
"""
Diálogo de validación OTP para Herramientas Bonos
"""

import sys
from datetime import datetime, timedelta

# Importar Qt con compatibilidad
try:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QLineEdit, QFrame, QMessageBox,
                                 QProgressBar, QTextEdit, QSpacerItem, QSizePolicy)
    from PySide6.QtCore import Qt, QTimer, Signal as pyqtSignal
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QLineEdit, QFrame, QMessageBox,
                                QProgressBar, QTextEdit, QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QFont, QIcon

from otp_service import otp_service

class OTPDialog(QDialog):
    """Diálogo para validación OTP"""
    
    otp_validated = pyqtSignal()  # Señal emitida cuando el OTP es válido
    
    def __init__(self, parent=None, email="sofia@rinorisk.com"):
        super().__init__(parent)
        self.email = email
        self.countdown_timer = QTimer()
        self.countdown_seconds = 300  # 5 minutos = 300 segundos
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo OTP minimalista"""
        self.setWindowTitle("Verificación OTP")
        self.setFixedSize(532, 448)  # Ventana 40% más grande (380*1.4, 320*1.4)
        self.setModal(True)
        
        # Layout principal centrado
        layout = QVBoxLayout(self)
        layout.setSpacing(30)  # Más espacio entre elementos
        layout.setContentsMargins(60, 60, 60, 60)  # Márgenes más amplios para la ventana más grande
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título simple y grande
        title_label = QLabel("Verificación de Seguridad")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción clara
        desc_label = QLabel(f"Se enviará un código al correo:\n{self.email}")
        desc_label.setObjectName("descLabel")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Botón para enviar código
        self.request_otp_btn = QPushButton("Enviar Código")
        self.request_otp_btn.setObjectName("primaryBtn")
        self.request_otp_btn.clicked.connect(self.request_otp)
        layout.addWidget(self.request_otp_btn)
        
        # Campo de entrada del código
        otp_label = QLabel("Ingresa el código de 6 dígitos:")
        otp_label.setObjectName("inputLabel")
        layout.addWidget(otp_label)
        
        self.otp_input = QLineEdit()
        self.otp_input.setObjectName("otpInput")
        self.otp_input.setPlaceholderText("123456")
        self.otp_input.setMaxLength(6)
        self.otp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_input.setEnabled(False)
        self.otp_input.returnPressed.connect(self.verify_otp)
        layout.addWidget(self.otp_input)
        
        # Estado/contador
        self.countdown_label = QLabel("Presiona 'Enviar Código' para comenzar")
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.verify_btn = QPushButton("Verificar")
        self.verify_btn.setObjectName("primaryBtn")
        self.verify_btn.clicked.connect(self.verify_otp)
        self.verify_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.verify_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Configurar timer de cuenta regresiva
        self.countdown_timer.timeout.connect(self.update_countdown)
        
    def setup_styles(self):
        """Configura los estilos del diálogo minimalista"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #titleLabel {
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
                margin: 10px 0 15px 0;
                padding: 5px 10px;
                min-height: 25px;
            }
            
            #descLabel {
                font-size: 12px;
                color: #6b7280;
                line-height: 1.6;
                margin: 0 0 18px 0;
                padding: 8px 15px;
                min-height: 35px;
            }
            
            #inputLabel {
                font-size: 12px;
                font-weight: 500;
                color: #374151;
                margin: 15px 0 8px 0;
                padding: 5px 10px;
                min-height: 20px;
            }
            
            #otpInput {
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                padding: 8px;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                background-color: #f9fafb;
                letter-spacing: 4px;
                min-height: 14px;
                margin: 3px 0 8px 0;
                max-width: 180px;
            }
            
            #otpInput:focus {
                border-color: #3b82f6;
                background-color: #ffffff;
                outline: none;
            }
            
            #otpInput:disabled {
                background-color: #f3f4f6;
                color: #9ca3af;
                border-color: #d1d5db;
            }
            
            #countdownLabel {
                font-size: 11px;
                font-weight: 500;
                color: #dc2626;
                margin: 8px 0 18px 0;
                padding: 5px 10px;
                min-height: 25px;
                line-height: 1.5;
            }
            
            #primaryBtn {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                border-radius: 6px;
                min-height: 28px;
                margin: 3px 0;
            }
            
            #primaryBtn:hover {
                background-color: #2563eb;
            }
            
            #primaryBtn:pressed {
                background-color: #1d4ed8;
            }
            
            #primaryBtn:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }
            
            #secondaryBtn {
                background-color: #f3f4f6;
                color: #6b7280;
                border: 1px solid #d1d5db;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 6px;
                min-height: 28px;
                margin: 3px 0;
            }
            
            #secondaryBtn:hover {
                background-color: #e5e7eb;
                color: #4b5563;
            }
        """)
        
    def request_otp(self):
        """Solicita un nuevo código OTP"""
        self.request_otp_btn.setEnabled(False)
        self.request_otp_btn.setText("Enviando...")
        self.countdown_label.setText("📧 Enviando código al correo...")
        
        # Solicitar OTP del servicio
        success, message = otp_service.request_otp(self.email)
        
        if success:
            # Habilitar campos de entrada
            self.otp_input.setEnabled(True)
            self.verify_btn.setEnabled(True)
            
            # Iniciar cuenta regresiva
            self.countdown_seconds = 300  # 5 minutos
            self.countdown_timer.start(1000)  # Actualizar cada segundo
            self.update_countdown()
            
            # Enfocar campo de entrada
            self.otp_input.setFocus()
            
            # Cambiar texto del botón
            self.request_otp_btn.setText("✅ Código Enviado")
            self.request_otp_btn.setEnabled(False)
            
            # Mensaje más discreto en la etiqueta
            self.countdown_label.setText("✅ Código enviado. Revisa tu correo electrónico.")
        else:
            QMessageBox.critical(self, "Error", f"Error al enviar código OTP:\n{message}")
            self.request_otp_btn.setEnabled(True)
            self.request_otp_btn.setText("Enviar Código")
            self.countdown_label.setText("❌ Error al enviar. Intenta nuevamente.")
    
    def verify_otp(self):
        """Verifica el código OTP ingresado"""
        otp_code = self.otp_input.text().strip()
        
        if len(otp_code) != 6:
            QMessageBox.warning(self, "Error", "El código debe tener exactamente 6 dígitos")
            return
        
        if not otp_code.isdigit():
            QMessageBox.warning(self, "Error", "El código debe contener solo números")
            return
        
        # Mostrar estado de procesamiento
        self.verify_btn.setEnabled(False)
        self.verify_btn.setText("Verificando...")
        self.countdown_label.setText("🔄 Verificando código...")
        
        # Verificar con el servicio OTP
        success, message = otp_service.verify_otp(self.email, otp_code)
        
        if success:
            # Mostrar éxito
            self.verify_btn.setText("✅ Verificado")
            self.countdown_label.setText("✅ Código verificado correctamente")
            self.countdown_timer.stop()
            
            # Cerrar diálogo después de un breve delay para mostrar el éxito
            QTimer.singleShot(800, self._complete_verification)
        else:
            # Restaurar estado en caso de error
            self.verify_btn.setEnabled(True)
            self.verify_btn.setText("Verificar")
            self.countdown_label.setText("❌ Código incorrecto. Intenta nuevamente.")
            QMessageBox.critical(self, "Error de Verificación", message)
            self.otp_input.clear()
            self.otp_input.setFocus()
    
    def _complete_verification(self):
        """Completa la verificación y cierra el diálogo"""
        self.otp_validated.emit()
        self.accept()
    
    def update_countdown(self):
        """Actualiza la cuenta regresiva"""
        if self.countdown_seconds <= 0:
            self.countdown_timer.stop()
            self.countdown_label.setText("⏰ El código ha expirado. Solicita uno nuevo.")
            self.verify_btn.setEnabled(False)
            self.otp_input.setEnabled(False)
            return
        
        minutes = self.countdown_seconds // 60
        seconds = self.countdown_seconds % 60
        self.countdown_label.setText(f"⏰ Código expira en: {minutes:02d}:{seconds:02d}")
        self.countdown_seconds -= 1
    
    def center_dialog(self):
        """Centra el diálogo en la pantalla"""
        if self.parent():
            # Centrar respecto al padre
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            # Centrar en pantalla
            screen = self.screen().availableGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def showEvent(self, event):
        """Se ejecuta cuando se muestra el diálogo"""
        super().showEvent(event)
        self.center_dialog()

def show_otp_dialog(parent=None, email="sofia@rinorisk.com") -> bool:
    """Función helper para mostrar el diálogo OTP y retornar si fue validado"""
    dialog = OTPDialog(parent, email)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted 