#!/usr/bin/env python3
"""
Herramientas Bonos - Aplicación PyQt/PySide
Sistema de autenticación y navegación principal
"""

import sys
import os
from pathlib import Path

# Configuración específica para macOS para solucionar problemas con plugins Qt
if sys.platform == 'darwin':  # macOS
    # Asegurar que las variables de entorno estén configuradas correctamente
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
    os.environ['QT_PLUGIN_PATH'] = ''

# Forzar el uso de PySide6 en macOS para mejor compatibilidad
try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QFrame, QStackedWidget, QMessageBox, QTabWidget,
                                 QScrollArea, QSizePolicy)
    from PySide6.QtCore import Qt, Signal as pyqtSignal, QTimer, QSize, QRect
    from PySide6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QFontDatabase
    QT_VARIANT = "PySide6"
    print(f"✅ Usando {QT_VARIANT}")
    
    # Importar LoadingModal y PrincipalWindow al inicio para evitar problemas con imports dinámicos
    try:
        from principal import LoadingModal, PrincipalWindow
        LOADING_MODAL_AVAILABLE = True
        PRINCIPAL_WINDOW_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ No se pudo importar módulos de principal: {e}")
        LoadingModal = None
        PrincipalWindow = None
        LOADING_MODAL_AVAILABLE = False
        PRINCIPAL_WINDOW_AVAILABLE = False
        
except ImportError:
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                    QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                    QFrame, QStackedWidget, QMessageBox, QTabWidget,
                                    QScrollArea, QSizePolicy)
        from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QRect
        from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QFontDatabase
        QT_VARIANT = "PyQt6"
        print(f"✅ Usando {QT_VARIANT}")
        
        # Importar LoadingModal y PrincipalWindow al inicio para evitar problemas con imports dinámicos
        try:
            from principal import LoadingModal, PrincipalWindow
            LOADING_MODAL_AVAILABLE = True
            PRINCIPAL_WINDOW_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ No se pudo importar módulos de principal: {e}")
            LoadingModal = None
            PrincipalWindow = None
            LOADING_MODAL_AVAILABLE = False
            PRINCIPAL_WINDOW_AVAILABLE = False
            
    except ImportError:
        print("❌ Error: No se encontró PyQt6 ni PySide6. Instala uno de ellos:")
        print("   pip install PySide6  o  pip install PyQt6")
        sys.exit(1)

# Credenciales hardcodeadas
USUARIO_VALIDO = "abdiel"
PASSWORD_VALIDO = "123"

class LoginWindow(QWidget):
    """Ventana de login moderna con diseño Admin Panel"""
    
    login_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz de usuario del login minimalista"""
        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Frame principal del login
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        login_frame.setFixedSize(400, 450)
        
        # Layout del frame de login
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo de RinoRisk
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_pixmap = QPixmap("assets/img/rino.png")
        if not logo_pixmap.isNull():
            # Escalar el logo manteniendo proporción
            scaled_pixmap = logo_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("margin-bottom: 10px;")
        else:
            # Fallback si no se puede cargar la imagen
            logo_label.setText("🔐")
            logo_label.setStyleSheet("font-size: 48px; color: #2563eb; margin-bottom: 10px;")
        frame_layout.addWidget(logo_label)
        
        # Título simple
        title_label = QLabel("ADMIN BONOS")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Espaciador
        frame_layout.addSpacing(20)
        
        # Campo de usuario directo
        self.username_input = QLineEdit()
        self.username_input.setObjectName("simpleInput")
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setMinimumHeight(45)
        frame_layout.addWidget(self.username_input)
        
        # Campo de contraseña directo
        self.password_input = QLineEdit()
        self.password_input.setObjectName("simpleInput")
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        frame_layout.addWidget(self.password_input)
        
        # Mensaje de error
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(30)
        frame_layout.addWidget(self.error_label)
        
        # Botón de login
        self.login_button = QPushButton("INICIAR SESIÓN")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setMinimumHeight(45)
        frame_layout.addWidget(self.login_button)
        
        # Conectar eventos
        self.login_button.clicked.connect(self.validate_login)
        self.username_input.returnPressed.connect(self.validate_login)
        self.password_input.returnPressed.connect(self.validate_login)
        
        # Agregar frame al layout principal
        layout.addWidget(login_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        
    def setup_styles(self):
        """Configura los estilos minimalistas de la ventana de login"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #loginFrame {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
            
            #titleLabel {
                color: #374151;
                font-size: 20px;
                font-weight: 600;
                margin: 10px 0;
            }
            
            #simpleInput {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: #374151;
            }
            
            #simpleInput:focus {
                border-color: #1e40af;
                background-color: white;
            }
            
            #simpleInput::placeholder {
                color: #9ca3af;
            }
            
            #loginButton {
                background-color: #1e40af;
                border: none;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
            }
            
            #loginButton:hover {
                background-color: #1d4ed8;
            }
            
            #loginButton:pressed {
                background-color: #1e3a8a;
            }
            
            #loginButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
            
            #errorLabel {
                color: #dc2626;
                font-size: 13px;
                font-weight: 500;
                margin: 5px 0;
            }
        """)
        
    def validate_login(self):
        """Valida las credenciales de login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("⚠️ Por favor ingrese usuario y contraseña")
            return
            
        if username == USUARIO_VALIDO and password == PASSWORD_VALIDO:
            self.error_label.setText("✅ Login exitoso, cargando...")
            self.error_label.setStyleSheet("color: #4CAF50; font-weight: 500;")
            
            # Simular un pequeño delay para mostrar el mensaje
            QTimer.singleShot(500, self.emit_login_success)
        else:
            self.show_error("❌ Credenciales incorrectas. Acceso denegado.")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()
            
    def emit_login_success(self):
        """Emite la señal de login exitoso"""
        self.login_successful.emit()
        
    def show_error(self, message):
        """Muestra un mensaje de error"""
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: #f44336; font-weight: 500;")
        
    def clear_error(self):
        """Limpia el mensaje de error"""
        self.error_label.setText("")

class MainApplication(QMainWindow):
    """Aplicación principal que maneja login y ventana principal"""
    
    def __init__(self):
        super().__init__()
        self.setup_application()
        
    def setup_application(self):
        """Configura la aplicación principal"""
        self.setWindowTitle("Herramientas Bonos - Sistema")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        
        # Centrar ventana
        self.center_window()
        
        # Stack widget para cambiar entre login y principal
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Crear ventana de login
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_interface)
        self.stacked_widget.addWidget(self.login_window)
        
        # Cargar icono si existe
        self.setup_window_icon()
        
    def setup_window_icon(self):
        """Configura el icono de la ventana"""
        icon_path = Path("assets/img/rino.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            
    def center_window(self):
        """Centra la ventana en la pantalla"""
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def show_main_interface(self):
        """Muestra la interfaz principal después del login exitoso"""
        print("[DEBUG] ===== CARGANDO INTERFAZ PRINCIPAL =====")
        
        # Crear modal de carga de transición
        self.create_transition_loading()
        
        # Usar QTimer para simular la carga paso a paso
        self.transition_timer = QTimer()
        self.transition_step = 0
        self.transition_timer.timeout.connect(self.update_transition_progress)
        self.transition_timer.start(300)  # Actualizar cada 300ms
        
    def create_transition_loading(self):
        """Crea el modal de carga para la transición"""
        # Verificar si LoadingModal está disponible
        if not LOADING_MODAL_AVAILABLE or LoadingModal is None:
            print("⚠️ LoadingModal no disponible, continuando sin modal de carga")
            return
            
        try:
            self.transition_modal = LoadingModal(
                self, 
                "Cargando Sistema", 
                "Inicializando interfaz principal..."
            )
            self.transition_modal.center_on_parent()
            self.transition_modal.show_with_animation()
        except Exception as e:
            print(f"❌ Error creando modal de carga: {e}")
            self.transition_modal = None
        
    def update_transition_progress(self):
        """Actualiza el progreso de la transición"""
        self.transition_step += 1
        
        try:
            if self.transition_step == 1:
                if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                    self.transition_modal.update_progress(25, "Importando módulos...")
                else:
                    print("[Progreso] Importando módulos... (25%)")
            elif self.transition_step == 2:
                if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                    self.transition_modal.update_progress(50, "Configurando interfaz...")
                else:
                    print("[Progreso] Configurando interfaz... (50%)")
                # Crear la ventana principal con manejo de errores
                try:
                    if not PRINCIPAL_WINDOW_AVAILABLE or PrincipalWindow is None:
                        raise ImportError("PrincipalWindow no está disponible")
                    self.main_window = PrincipalWindow()
                except Exception as e:
                    print(f"❌ Error creando PrincipalWindow: {e}")
                    raise e
            elif self.transition_step == 3:
                if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                    self.transition_modal.update_progress(75, "Estableciendo conexiones...")
                else:
                    print("[Progreso] Estableciendo conexiones... (75%)")
                if hasattr(self, 'main_window'):
                    self.main_window.logout_requested.connect(self.show_login)
                    self.stacked_widget.addWidget(self.main_window)
            elif self.transition_step == 4:
                if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                    self.transition_modal.update_progress(100, "Finalizando carga...")
                else:
                    print("[Progreso] Finalizando carga... (100%)")
                if hasattr(self, 'main_window'):
                    self.stacked_widget.setCurrentWidget(self.main_window)
                    print("[DEBUG] ✅ Interfaz principal cargada exitosamente")
            else:
                self.transition_timer.stop()
                if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                    self.transition_modal.hide_with_animation()
                    # Limpiar referencias
                    self.transition_modal = None
        except Exception as e:
            print(f"❌ Error en transición paso {self.transition_step}: {e}")
            self.transition_timer.stop()
            if hasattr(self, 'transition_modal') and self.transition_modal is not None:
                self.transition_modal.hide_with_animation()
            QMessageBox.critical(self, "Error", f"Error cargando la aplicación:\n{str(e)}")
        
    def show_login(self):
        """Vuelve a mostrar la pantalla de login"""
        self.login_window.clear_error()
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()
        self.login_window.username_input.setFocus()
        self.stacked_widget.setCurrentWidget(self.login_window)
        
        # Limpiar la ventana principal
        if hasattr(self, 'main_window'):
            self.stacked_widget.removeWidget(self.main_window)
            self.main_window.deleteLater()
            delattr(self, 'main_window')

def main():
    """Función principal de la aplicación"""
    try:
        print("🚀 Iniciando Herramientas Bonos - PyQt/PySide")
        
        # Configurar variables de entorno específicas para Qt en macOS
        if sys.platform == 'darwin':
            # Limpiar variables de entorno problemáticas
            for env_var in ['QT_QPA_PLATFORM_PLUGIN_PATH', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM']:
                if env_var in os.environ:
                    del os.environ[env_var]
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Herramientas Bonos")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("RinoRisk")
        
        # Configurar atributos específicos para macOS y manejo de errores
        if sys.platform == 'darwin':
            app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
            app.setAttribute(Qt.ApplicationAttribute.AA_NativeWindows, False)
            # Nota: AA_DisableWindowContextHelpButton no está disponible en PySide6
        
        # Configurar fuente por defecto con manejo de errores
        try:
            font = QFont("Inter", 10)
            if not font.exactMatch():
                font = QFont("Segoe UI", 10)
                if not font.exactMatch():
                    font = QFont("Arial", 10)  # Fallback universal
            app.setFont(font)
        except Exception as e:
            print(f"⚠️ Error configurando fuente: {e}")
        
        # Crear y mostrar ventana principal
        window = MainApplication()
        window.show()
        
        print("✅ Aplicación iniciada exitosamente")
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error fatal en la aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 