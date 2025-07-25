# 🚀 Generación de Ejecutables - Herramientas Bonos

Este documento explica cómo generar ejecutables independientes para macOS y Windows desde cero, garantizando compatibilidad y funcionamiento correcto.

## 📋 Requisitos Previos

### Para macOS:
- Python 3.9+ instalado
- Terminal con acceso a comandos
- Conexión a internet para descargar dependencias

### Para Windows:
- Python 3.9+ instalado
- Command Prompt o PowerShell
- Conexión a internet para descargar dependencias

## 🛠️ Scripts de Construcción

Se han creado 4 scripts específicos para garantizar la construcción exitosa:

### 1. `build_all.py` - Script Principal (Recomendado)
```bash
# macOS
python3 build_all.py

# Windows
python build_all.py
```

**Características:**
- Detecta automáticamente el sistema operativo
- Ejecuta el script correspondiente
- Manejo de errores integrado
- Instrucciones claras

### 2. `build_macos.py` - Solo para macOS
```bash
python3 build_macos.py
```

**Características:**
- Usa solo PySide6 (evita conflictos con PyQt6)
- Genera un bundle `.app` nativo de macOS
- Incluye todas las dependencias
- Optimizado para Apple Silicon e Intel

### 3. `build_windows.py` - Solo para Windows
```bash
python build_windows.py
```

**Características:**
- Usa solo PySide6 (evita conflictos con PyQt6)
- Genera un archivo `.exe` ejecutable
- Incluye todas las dependencias
- Compatible con Windows 10/11

### 4. `build_windows_wine.py` - Windows desde macOS (Experimental)
```bash
python3 build_windows_wine.py
```

**Características:**
- Usa Wine para generar .exe desde macOS
- Requiere Wine instalado (`./install_wine.sh`)
- **Nota:** Puede tener problemas en macOS 26+
- Alternativa: Usar máquina virtual Windows

## 🔧 Proceso de Construcción

### Paso 1: Preparación
Los scripts automáticamente:
- ✅ Desinstalan PyQt6 para evitar conflictos
- ✅ Instalan PySide6 como framework Qt
- ✅ Instalan PyInstaller para crear ejecutables
- ✅ Instalan todas las dependencias necesarias

### Paso 2: Configuración
Los scripts crean archivos `.spec` optimizados que incluyen:
- 📁 Todos los archivos Python necesarios
- 📁 Carpeta `assets` con imágenes y recursos
- 📁 Base de datos SQLite
- 📦 Todas las dependencias Python

### Paso 3: Construcción
- 🔨 PyInstaller compila el código
- 📦 Empaqueta todas las dependencias
- 🎯 Genera el ejecutable final

## 📁 Resultados

### macOS
- **Ubicación:** `dist/HerramientasBonos.app`
- **Tipo:** Bundle de aplicación nativo
- **Ejecución:** Doble clic en Finder
- **Distribución:** Comprimir la carpeta `.app`

### Windows
- **Ubicación:** `dist/HerramientasBonos.exe`
- **Tipo:** Archivo ejecutable
- **Ejecución:** Doble clic en Explorer
- **Distribución:** Compartir el archivo `.exe`

## 🎯 Características de los Ejecutables

### ✅ Ventajas
- **Independientes:** No requieren Python instalado
- **Completos:** Incluyen todas las dependencias
- **Nativos:** Interfaz gráfica sin consola
- **Optimizados:** Tamaño reducido sin módulos innecesarios
- **Compatibles:** Funcionan en sistemas sin desarrollo

### 🔒 Seguridad
- **macOS:** Bundle firmado y compatible con Gatekeeper
- **Windows:** Ejecutable estándar sin requerimientos especiales
- **Sin malware:** Código fuente transparente y verificable

## 🚨 Solución de Problemas

### Error: "PyQt6 y PySide6 conflict"
**Solución:** Los scripts automáticamente desinstalan PyQt6 y usan solo PySide6.

### Error: "No se encontró PyInstaller"
**Solución:** Los scripts instalan automáticamente PyInstaller.

### Error: "Faltan dependencias"
**Solución:** Los scripts instalan todas las dependencias necesarias.

### Error: "Permisos en macOS"
**Solución:** 
1. Ir a Preferencias del Sistema > Seguridad y Privacidad
2. Permitir la ejecución del archivo
3. O ejecutar: `xattr -cr dist/HerramientasBonos.app`

### Error: "Wine no funciona en macOS 26+"
**Solución:** 
1. Usar una máquina virtual Windows
2. Usar servicios en la nube (GitHub Actions, Azure Pipelines)
3. Usar Docker con Windows container
4. Compilar directamente en una máquina Windows

## 🍷 Instalación de Wine (Opcional)

Para generar ejecutables de Windows desde macOS:

```bash
# Instalar Wine automáticamente
./install_wine.sh

# O manualmente
brew install --cask wine-stable
softwareupdate --install-rosetta --agree-to-license
```

**Nota:** Wine puede tener problemas en versiones pre-release de macOS.

## 🖥️ Alternativas para Windows desde macOS

### 1. Máquina Virtual
- **Parallels Desktop** o **VMware Fusion**
- Instalar Windows 10/11
- Ejecutar `build_windows.py` dentro de la VM

### 2. GitHub Actions
- Crear workflow que compile en Windows
- Descargar el .exe generado

### 3. Docker
- Usar Windows container
- Compilar dentro del contenedor

### 4. Servicios en la Nube
- **Azure Pipelines**
- **GitLab CI/CD**
- **CircleCI**

## 📊 Comparación de Tamaños

| Sistema | Tamaño Aproximado | Tipo |
|---------|------------------|------|
| macOS   | 150-200 MB       | .app bundle |
| Windows | 100-150 MB       | .exe file |

## 🔄 Actualización de Ejecutables

Para actualizar los ejecutables:
1. Modificar el código fuente
2. Ejecutar el script de construcción correspondiente
3. Reemplazar el ejecutable anterior

## 📞 Soporte

Si encuentras problemas:
1. Verifica que Python esté instalado correctamente
2. Asegúrate de tener conexión a internet
3. Ejecuta el script con permisos de administrador si es necesario
4. Revisa los mensajes de error para identificar el problema específico
5. Para problemas con Wine, considera usar una máquina virtual

## 🎉 ¡Listo!

Una vez completado el proceso, tendrás ejecutables completamente funcionales que puedes distribuir a usuarios finales sin necesidad de que instalen Python o dependencias adicionales.

---

**Nota:** Estos scripts están optimizados para evitar los problemas comunes de construcción de ejecutables y garantizar la compatibilidad entre diferentes versiones de Python y sistemas operativos. 