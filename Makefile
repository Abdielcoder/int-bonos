# Makefile para Admin Bonos - Construcción de Instalador DMG

# Variables
APP_NAME = Admin Bonos
APP_VERSION = 1.0.0
DMG_NAME = AdminBonos-$(APP_VERSION)-macOS

# Colores para output
GREEN = \033[0;32m
BLUE = \033[0;34m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: all help clean dmg app icon install-deps test

# Target por defecto
all: dmg

help:
	@echo "$(BLUE)📦 Admin Bonos - Sistema de Construcción DMG$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponibles:$(NC)"
	@echo "  $(GREEN)make dmg$(NC)         - Crear instalador DMG completo"
	@echo "  $(GREEN)make app$(NC)         - Solo construir aplicación .app"
	@echo "  $(GREEN)make icon$(NC)        - Solo convertir icono PNG a ICNS"
	@echo "  $(GREEN)make install-deps$(NC) - Instalar dependencias necesarias"
	@echo "  $(GREEN)make clean$(NC)       - Limpiar archivos de construcción"
	@echo "  $(GREEN)make test$(NC)        - Probar la aplicación antes de empaquetar"
	@echo "  $(GREEN)make help$(NC)        - Mostrar esta ayuda"
	@echo ""
	@echo "$(YELLOW)Archivos resultado:$(NC)"
	@echo "  📦 dist/$(DMG_NAME).dmg"
	@echo "  📁 dist/$(APP_NAME).app"

# Crear DMG completo (método rápido)
dmg:
	@echo "$(BLUE)🚀 Creando instalador DMG para $(APP_NAME)$(NC)"
	@./setup_dmg.sh

# Crear DMG usando Python (método avanzado)
dmg-python:
	@echo "$(BLUE)🐍 Creando instalador DMG con Python$(NC)"
	@python3 build_dmg.py

# Solo construir aplicación
app: clean install-deps icon
	@echo "$(BLUE)🏗️ Construyendo aplicación $(APP_NAME)$(NC)"
	@python3 -m PyInstaller \
		--onedir \
		--windowed \
		--noconfirm \
		--clean \
		--name "$(APP_NAME)" \
		--osx-bundle-identifier "com.rinorisk.adminbonos" \
		--icon "assets/img/logo.icns" \
		--add-data "assets:assets" \
		--add-data "requirements.txt:." \
		main.py
	@echo "$(GREEN)✅ Aplicación construida: dist/$(APP_NAME).app$(NC)"

# Convertir icono
icon:
	@echo "$(BLUE)🎨 Convirtiendo icono PNG a ICNS$(NC)"
	@if [ -f "assets/img/logo.png" ]; then \
		mkdir -p assets/img/logo.iconset; \
		for size in 16 32 64 128 256 512 1024; do \
			sips -z $$size $$size assets/img/logo.png \
				--out "assets/img/logo.iconset/icon_$${size}x$${size}.png" > /dev/null 2>&1; \
			if [ $$size -le 512 ]; then \
				double_size=$$((size * 2)); \
				sips -z $$double_size $$double_size assets/img/logo.png \
					--out "assets/img/logo.iconset/icon_$${size}x$${size}@2x.png" > /dev/null 2>&1; \
			fi; \
		done; \
		iconutil -c icns assets/img/logo.iconset -o assets/img/logo.icns; \
		rm -rf assets/img/logo.iconset; \
		echo "$(GREEN)✅ Icono convertido: assets/img/logo.icns$(NC)"; \
	else \
		echo "$(RED)❌ No se encontró assets/img/logo.png$(NC)"; \
		exit 1; \
	fi

# Instalar dependencias
install-deps:
	@echo "$(BLUE)📦 Verificando dependencias$(NC)"
	@python3 -c "import PyInstaller" 2>/dev/null || pip3 install pyinstaller
	@command -v create-dmg >/dev/null 2>&1 || echo "$(YELLOW)⚠️ create-dmg no instalado. Opcional: brew install create-dmg$(NC)"
	@echo "$(GREEN)✅ Dependencias verificadas$(NC)"

# Probar aplicación
test:
	@echo "$(BLUE)🧪 Probando aplicación$(NC)"
	@python3 -c "import main; print('✅ main.py se puede importar')"
	@python3 -c "import principal; print('✅ principal.py se puede importar')"
	@test -f assets/img/logo.png && echo "$(GREEN)✅ Logo encontrado$(NC)" || echo "$(RED)❌ Logo no encontrado$(NC)"
	@test -f requirements.txt && echo "$(GREEN)✅ Requirements encontrado$(NC)" || echo "$(RED)❌ Requirements no encontrado$(NC)"

# Limpiar archivos de construcción
clean:
	@echo "$(BLUE)🧹 Limpiando archivos de construcción$(NC)"
	@rm -rf build dist *.spec __pycache__ assets/img/*.icns assets/img/*.iconset
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

# Limpiar todo (incluir dist)
clean-all: clean
	@echo "$(BLUE)🧹 Limpieza completa$(NC)"
	@rm -rf dist
	@echo "$(GREEN)✅ Limpieza completa finalizada$(NC)"

# Mostrar información del sistema
info:
	@echo "$(BLUE)📋 Información del Sistema$(NC)"
	@echo "OS: $$(uname -s)"
	@echo "Arch: $$(uname -m)"
	@echo "Python: $$(python3 --version)"
	@echo "PyInstaller: $$(python3 -c 'import PyInstaller; print(PyInstaller.__version__)' 2>/dev/null || echo 'No instalado')"
	@echo "create-dmg: $$(command -v create-dmg >/dev/null 2>&1 && echo 'Disponible' || echo 'No instalado')"

# Verificar estructura de proyecto
check:
	@echo "$(BLUE)🔍 Verificando estructura del proyecto$(NC)"
	@test -f main.py && echo "$(GREEN)✅ main.py$(NC)" || echo "$(RED)❌ main.py$(NC)"
	@test -f principal.py && echo "$(GREEN)✅ principal.py$(NC)" || echo "$(RED)❌ principal.py$(NC)"
	@test -f requirements.txt && echo "$(GREEN)✅ requirements.txt$(NC)" || echo "$(RED)❌ requirements.txt$(NC)"
	@test -d assets && echo "$(GREEN)✅ assets/$(NC)" || echo "$(RED)❌ assets/$(NC)"
	@test -f assets/img/logo.png && echo "$(GREEN)✅ assets/img/logo.png$(NC)" || echo "$(RED)❌ assets/img/logo.png$(NC)"
	@test -f setup_dmg.sh && echo "$(GREEN)✅ setup_dmg.sh$(NC)" || echo "$(RED)❌ setup_dmg.sh$(NC)"

# Crear release completo
release: clean check test dmg
	@echo "$(GREEN)🎉 Release creado exitosamente$(NC)"
	@ls -la dist/$(DMG_NAME).dmg
	@echo "$(BLUE)📦 Instalador listo: dist/$(DMG_NAME).dmg$(NC)" 