#!/usr/bin/env python3
"""
Versión corregida de main.py que importa principal.py de manera segura
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
            
    except ImportError:
        print("❌ Error: No se encontró PyQt6 ni PySide6. Instala uno de ellos:")
        print("   pip install PySide6  o  pip install PyQt6")
        sys.exit(1)

# Usuarios válidos (en un caso real, esto estaría en una base de datos segura)
USUARIOS_VALIDOS = {
    "sofia": "Sofia2024!",
    "evelyn": "Evelyn2024#", 
    "carlos": "Carlos2024$",
    "abdiel": "123"
}

# Mapeo de usuarios a sus correos correspondientes
USUARIO_CORREOS = {
    "carlos": "carlos@rinorisk.com",
    "sofia": "sofia@rinorisk.com", 
    "evelyn": "analista.financiero@rinorisk.com",
    "abdiel": "desarrollo@rinorisk.com"
}

class LoginWindow(QWidget):
    """Ventana de login moderna con diseño Admin Panel"""
    
    login_successful = pyqtSignal(dict)  # Pasar información del usuario
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configura la interfaz de usuario del login minimalista"""
        self.setWindowTitle("Admin Bonos - Login")
        # No establecer tamaño fijo para permitir que se adapte al contenedor
        
        # Layout principal que ocupa todo el espacio disponible
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)  # Márgenes mínimos
        
        # Widget contenedor para centrado perfecto
        center_widget = QWidget()
        center_widget.setMaximumSize(460, 520)  # Tamaño máximo del formulario
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame de login compacto
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        login_frame.setFixedSize(360, 380)
        
        # Layout del frame de login
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(16)
        frame_layout.setContentsMargins(25, 30, 25, 30)
        
        # Logo/Icono minimalista
        icon_label = QLabel("●")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 32px; 
            color: #1e40af;
            font-weight: bold;
            margin-bottom: 15px;
        """)
        frame_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel("ADMIN BONOS")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Campo usuario
        self.username_input = QLineEdit()
        self.username_input.setObjectName("simpleInput")
        self.username_input.setPlaceholderText("Usuario")
        # Campo de usuario vacío para que el usuario ingrese sus credenciales
        frame_layout.addWidget(self.username_input)
        
        # Campo contraseña
        self.password_input = QLineEdit()
        self.password_input.setObjectName("simpleInput")
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        # Campo de contraseña vacío para que el usuario ingrese sus credenciales
        frame_layout.addWidget(self.password_input)
        
        # Label de error
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        frame_layout.addWidget(self.error_label)
        
        # Botón login
        self.login_button = QPushButton("INICIAR SESIÓN")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        frame_layout.addWidget(self.login_button)
        
        # Configurar eventos
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Agregar el frame al layout del contenedor
        center_layout.addWidget(login_frame)
        
        # Agregar el widget contenedor al layout principal
        main_layout.addWidget(center_widget)
        
    def setup_styles(self):
        """Configura los estilos del login minimalista"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: 'SF Pro Display', 'Segoe UI', Arial, sans-serif;
            }
            #loginFrame {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            #titleLabel {
                color: #1a202c;
                font-size: 18px;
                font-weight: 500;
                margin: 8px 0;
            }
            #simpleInput {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 14px 16px;
                font-size: 15px;
                color: #2d3748;
                min-height: 20px;
            }
            #simpleInput:focus {
                border-color: #1e40af;
                outline: none;
            }
            #simpleInput::placeholder {
                color: #a0aec0;
            }
            #loginButton {
                background-color: #1e40af;
                border: none;
                color: white;
                padding: 16px 24px;
                font-size: 15px;
                font-weight: 500;
                border-radius: 8px;
                min-height: 24px;
            }
            #loginButton:hover {
                background-color: #1d4ed8;
            }
            #loginButton:pressed {
                background-color: #1e3a8a;
            }
            #loginButton:disabled {
                background-color: #cbd5e0;
                color: #a0aec0;
            }
            #errorLabel {
                color: #e53e3e;
                font-size: 13px;
                font-weight: 400;
                margin: 4px 0;
            }
        """)
        
    def handle_login(self):
        """Maneja el proceso de login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Deshabilitar botón
        self.login_button.setEnabled(False)
        self.login_button.setText("Verificando...")
        
        # Limpiar errores previos
        self.clear_error()
        
        # Validar campos
        if not username or not password:
            self.show_error("Por favor, complete todos los campos")
            self.login_button.setEnabled(True)
            self.login_button.setText("INICIAR SESIÓN")
            return
            
        # Validar credenciales
        if username in USUARIOS_VALIDOS and USUARIOS_VALIDOS[username] == password:
            # Guardar información del usuario autenticado
            self.usuario_autenticado = {
                'username': username,
                'email': USUARIO_CORREOS.get(username, 'desarrollo@rinorisk.com'),
                'nombre': username.title()  # Capitalizar primera letra
            }
            self.show_success("✅ Login exitoso, cargando...")
            # Usar QTimer para evitar bloquear la UI
            QTimer.singleShot(500, lambda: self.login_successful.emit(self.usuario_autenticado))
        else:
            self.show_error("Credenciales incorrectas")
            self.login_button.setEnabled(True)
            self.login_button.setText("INICIAR SESIÓN")
            
    def show_error(self, message):
        """Muestra un mensaje de error"""
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: #dc2626;")
        
    def show_success(self, message):
        """Muestra un mensaje de éxito"""
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: #059669;")
        
    def clear_error(self):
        """Limpia el mensaje de error"""
        self.error_label.setText("")
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

def apply_fixed_global_styles(app):
    """
    Aplica estilos globales fijos que NO se adaptan al sistema operativo.
    
    Esta función asegura que la aplicación mantenga siempre los mismos colores
    independientemente de si el usuario tiene activado el modo oscuro/claro
    en su sistema operativo (macOS, Windows, Linux).
    
    Utiliza !important en CSS para sobrescribir cualquier estilo del sistema.
    """
    global_style = """
        /* ESTILOS GLOBALES FIJOS - NO SE ADAPTAN AL SISTEMA */
        
        QWidget {
            background-color: #f9fafb !important;
            color: #1f2937 !important;
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
        }
        
        QMainWindow {
            background-color: #f9fafb !important;
        }
        
        QDialog {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        
        QLabel {
            background-color: transparent !important;
            color: #374151 !important;
        }
        
        QLineEdit {
            background-color: #ffffff !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
        }
        
        QPushButton {
            background-color: #1e40af !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 6px !important;
        }
        
        QPushButton:hover {
            background-color: #1d4ed8 !important;
        }
        
        QPushButton:disabled {
            background-color: #9ca3af !important;
            color: #f3f4f6 !important;
        }
        
        QTableWidget {
            background-color: #ffffff !important;
            color: #374151 !important;
            gridline-color: #e5e7eb !important;
            border: 1px solid #d1d5db !important;
        }
        
        QTableWidget::item {
            background-color: #ffffff !important;
            color: #374151 !important;
        }
        
        QTableWidget::item:selected {
            background-color: #dbeafe !important;
            color: #1e40af !important;
        }
        
        QHeaderView::section {
            background-color: #f9fafb !important;
            color: #374151 !important;
            border: none !important;
            border-bottom: 1px solid #d1d5db !important;
            font-weight: normal !important;
            font-size: 13px !important;
        }
        
        QTabWidget::pane {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
        }
        
        QTabBar::tab {
            background-color: #f3f4f6 !important;
            color: #6b7280 !important;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        
        QGroupBox {
            background-color: #ffffff !important;
            color: #374151 !important;
            border: 2px solid #e5e7eb !important;
        }
        
        QTextEdit {
            background-color: #ffffff !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
        }
        
        QComboBox {
            background-color: #ffffff !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
        }
        
        QScrollBar:vertical {
            background-color: #f3f4f6 !important;
        }
        
        QScrollBar::handle:vertical {
            background-color: #d1d5db !important;
        }
        
        /* Asegurar que elementos específicos mantengan colores fijos */
        QStackedWidget {
            background-color: #f9fafb !important;
        }
        
        QFrame {
            background-color: transparent !important;
        }
    """
    
    # Aplicar estilos globales con !important para sobrescribir cualquier tema del sistema
    app.setStyleSheet(global_style)
    print("🎨 Estilos globales fijos aplicados - inmunes al modo oscuro")

class MainApplication(QMainWindow):
    """Aplicación principal con gestión de ventanas"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("Herramientas Bonos - Sistema")
        self.setMinimumSize(1200, 800)
        
        # Widget central stackeado
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Crear ventana de login
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_interface)
        self.stacked_widget.addWidget(self.login_window)
        
        # Variables de transición
        self.transition_modal = None
        self.transition_timer = None
        self.transition_step = 0
        
        # Centrar ventana
        self.center_window()
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def show_main_interface(self, usuario_info):
        """Muestra la interfaz principal después del login exitoso"""
        print("[DEBUG] ===== CARGANDO INTERFAZ PRINCIPAL =====")
        print(f"[DEBUG] Usuario autenticado: {usuario_info}")
        
        # Guardar información del usuario para pasarla a la interfaz principal
        self.usuario_autenticado = usuario_info
        
        # Mostrar mensaje simple en lugar de modal complejo
        self.login_window.show_success("Cargando interfaz principal...")
        
        # Usar QTimer para cargar la interfaz de manera asíncrona
        QTimer.singleShot(1000, self.load_principal_interface)
        
    def load_principal_interface(self):
        """Carga la interfaz principal de manera segura"""
        try:
            print("[DEBUG] Importando módulo principal...")
            # Importar principal solo cuando es necesario
            from principal import PrincipalWindow
            
            print("[DEBUG] Creando ventana principal...")
            self.main_window = PrincipalWindow()
            
            print("[DEBUG] Configurando información del usuario...")
            # Pasar información del usuario autenticado a la ventana principal
            if hasattr(self, 'usuario_autenticado'):
                self.main_window.set_usuario_autenticado(self.usuario_autenticado)
            
            print("[DEBUG] Configurando conexiones...")
            self.main_window.logout_requested.connect(self.show_login)
            
            print("[DEBUG] Agregando a stack widget...")
            self.stacked_widget.addWidget(self.main_window)
            
            print("[DEBUG] Cambiando a interfaz principal...")
            self.stacked_widget.setCurrentWidget(self.main_window)
            
            print("[DEBUG] ✅ Interfaz principal cargada exitosamente")
            
        except Exception as e:
            print(f"❌ Error cargando interfaz principal: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar error al usuario
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo cargar la interfaz principal:\n\n{str(e)}\n\nLa aplicación se cerrará."
            )
            sys.exit(1)
        
    def show_login(self):
        """Vuelve a mostrar la pantalla de login"""
        self.login_window.clear_error()
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()
        self.login_window.login_button.setEnabled(True)
        self.login_window.login_button.setText("INICIAR SESIÓN")
        self.stacked_widget.setCurrentWidget(self.login_window)

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
        
        # 🎨 CONFIGURAR COLORES FIJOS - NO ADAPTAR AL SISTEMA
        print("🎨 Configurando colores fijos independientes del sistema...")
        
        # Configurar atributos Qt básicos para evitar adaptación al sistema
        try:
            # Atributos estándar disponibles en PySide6/PyQt6
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            
            # Verificar y aplicar atributos adicionales si están disponibles
            qt_attributes = [
                ('AA_DontCreateNativeWidgetSiblings', True),
                ('AA_DontUseNativeDialogs', True),
                ('AA_DisableNativeVirtualKeyboard', True)
            ]
            
            for attr_name, value in qt_attributes:
                if hasattr(Qt.ApplicationAttribute, attr_name):
                    attr = getattr(Qt.ApplicationAttribute, attr_name)
                    app.setAttribute(attr, value)
                    print(f"✅ Configurado: {attr_name}")
            
            print("✅ Atributos Qt configurados para evitar adaptación del sistema")
        except Exception as e:
            print(f"⚠️ Error configurando atributos Qt: {e}")
            print("✅ Continuando con configuración mínima...")
        
        # Configurar paleta de colores fija para evitar adaptación al modo oscuro
        fixed_palette = QPalette()
        
        # Colores de fondo principales (siempre claros)
        fixed_palette.setColor(QPalette.ColorRole.Window, QColor("#f9fafb"))           # Fondo ventana
        fixed_palette.setColor(QPalette.ColorRole.WindowText, QColor("#1f2937"))      # Texto ventana
        fixed_palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))            # Fondo campos entrada
        fixed_palette.setColor(QPalette.ColorRole.Text, QColor("#374151"))            # Texto campos entrada
        
        # Colores de botones (siempre consistentes)
        fixed_palette.setColor(QPalette.ColorRole.Button, QColor("#f3f4f6"))          # Fondo botón
        fixed_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#374151"))      # Texto botón
        
        # Colores de selección (siempre azul claro)
        fixed_palette.setColor(QPalette.ColorRole.Highlight, QColor("#dbeafe"))       # Selección
        fixed_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e40af")) # Texto seleccionado
        
        # Colores alternativos para tablas
        fixed_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f9fafb"))   # Filas alternas
        
        # Colores de tooltips
        fixed_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))     # Fondo tooltip
        fixed_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#374151"))     # Texto tooltip
        
        # Aplicar la paleta fija a la aplicación
        app.setPalette(fixed_palette)
        
        # Configurar atributos específicos para macOS y manejo de errores
        if sys.platform == 'darwin':
            try:
                # Configuraciones compatibles para macOS
                if hasattr(Qt.ApplicationAttribute, 'AA_DontShowIconsInMenus'):
                    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
                if hasattr(Qt.ApplicationAttribute, 'AA_NativeWindows'):
                    app.setAttribute(Qt.ApplicationAttribute.AA_NativeWindows, False)
                # Desactivar seguimiento automático del modo oscuro en macOS
                if hasattr(Qt.ApplicationAttribute, 'AA_DontUseNativeMenuBar'):
                    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, True)
                print("🍎 Configuraciones específicas de macOS aplicadas")
            except AttributeError as e:
                print(f"⚠️ Algunos atributos macOS no disponibles: {e}")
                print("✅ Continuando sin configuraciones específicas de macOS")
        
        # Configurar fuente por defecto con manejo de errores
        try:
            font = QFont("Arial", 10)  # Usar Arial que está disponible en macOS
            app.setFont(font)
        except Exception as e:
            print(f"⚠️ Error configurando fuente: {e}")
        
        print("✅ Colores fijos configurados - la app no se adaptará al modo oscuro")
        
        # Aplicar estilos globales fijos adicionales
        apply_fixed_global_styles(app)
        
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