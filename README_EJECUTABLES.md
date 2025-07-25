# 🚀 Ejecutables bonosAlfa - Guía Completa

Esta guía explica cómo crear y usar los ejecutables de **bonosAlfa** para diferentes sistemas operativos.

## 📋 Resumen de Archivos Creados

### 🍎 **Para macOS**
- **`crear_bonos_alfa_compatible.sh`** - Script principal (recomendado)
- **`crear_bonos_alfa_universal.sh`** - Script universal (experimental)
- **`crear_bonos_alfa_corregido.sh`** - Script con correcciones básicas
- **`abrir_bonos_alfa.sh`** - Script de ayuda para problemas de seguridad

### 🪟 **Para Windows**
- **`crear_bonos_alfa_windows.bat`** - Script Batch (simple)
- **`crear_bonos_alfa_windows.ps1`** - Script PowerShell (moderno)
- **`INSTRUCCIONES_WINDOWS.md`** - Guía detallada para Windows

## 🍎 Ejecutables para macOS

### ✅ **Script Recomendado: `crear_bonos_alfa_compatible.sh`**

**Este es el script que funciona mejor y soluciona todos los problemas conocidos:**

```bash
# Hacer ejecutable y usar
chmod +x crear_bonos_alfa_compatible.sh
./crear_bonos_alfa_compatible.sh
```

**Características:**
- ✅ Compatible con Intel Mac y Apple Silicon (M1/M2/M3)
- ✅ Soluciona problemas de encodings
- ✅ Incluye firma de código adhoc
- ✅ Crea ejecutables específicos para cada arquitectura
- ✅ Genera DMG instalador automaticamente
- ✅ Incluye script de ayuda para problemas de seguridad

**Archivos generados:**
```
dist/
├── bonosAlfa.app                           # Aplicación macOS
├── bonosAlfa_AppleSilicon                  # Ejecutable directo (M1/M2/M3)
├── bonosAlfa-1.0.0-AppleSilicon.dmg       # Instalador DMG
└── abrir_bonos_alfa.sh                    # Script de ayuda
```

### 🔒 **Solución de Problemas de Seguridad en macOS**

Si aparece el mensaje **"No se puede abrir la aplicación"**:

#### **Método 1: Script de Ayuda (Más Fácil)**
```bash
./abrir_bonos_alfa.sh
```

#### **Método 2: Click Derecho**
1. Click derecho en `bonosAlfa.app`
2. Selecciona "Abrir"
3. Confirma "Abrir" en el diálogo

#### **Método 3: Terminal**
```bash
# Remover restricciones
xattr -d com.apple.quarantine "dist/bonosAlfa.app"

# O si está en Applications
xattr -d com.apple.quarantine "/Applications/bonosAlfa.app"
```

#### **Método 4: Preferencias del Sistema**
1. Ve a **Preferencias del Sistema** > **Seguridad y Privacidad**
2. En la pestaña **General**
3. Haz clic en **"Abrir de todas formas"**

### 📦 **Instalación en macOS**

1. **Desde DMG:**
   - Abre `bonosAlfa-1.0.0-AppleSilicon.dmg`
   - Arrastra `bonosAlfa.app` a la carpeta **Applications**
   - Ejecuta desde Launchpad

2. **Ejecutable directo:**
   ```bash
   ./dist/bonosAlfa_AppleSilicon
   ```

## 🪟 Ejecutables para Windows

### 📝 **Requisitos Previos**
- Windows 10 o superior
- Python 3.8+ instalado con "Add Python to PATH"
- PowerShell o Command Prompt

### **Método 1: Script Batch (Más Simple)**
```cmd
# Copiar crear_bonos_alfa_windows.bat al proyecto
# Abrir cmd en la carpeta del proyecto
crear_bonos_alfa_windows.bat
```

### **Método 2: Script PowerShell (Recomendado)**
```powershell
# Permitir ejecución de scripts (primera vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ejecutar script
.\crear_bonos_alfa_windows.ps1
```

**Resultado esperado:**
```
dist/
└── bonosAlfa.exe    # Ejecutable para Windows
```

### 📋 **Instrucciones Detalladas para Windows**
Ver archivo: `INSTRUCCIONES_WINDOWS.md`

## 🛠️ Características Técnicas

### 🔧 **Dependencias Incluidas**
- **PySide6** - Framework de interfaz gráfica
- **pandas** - Procesamiento de datos
- **requests** - Cliente HTTP
- **openpyxl** - Manejo de archivos Excel
- **xlsxwriter** - Creación de archivos Excel
- **Todas las librerías estándar de Python**

### 📊 **Tamaños Aproximados**
- **macOS**: 50-70 MB (DMG), 130-150 MB (aplicación)
- **Windows**: 80-120 MB

### 🏗️ **Arquitecturas Soportadas**
- **macOS Intel** (x86_64)
- **macOS Apple Silicon** (M1/M2/M3 - arm64)
- **Windows x64**

## 🚨 Solución de Problemas Comunes

### **❌ "No se puede abrir la aplicación" (macOS)**
**Causa:** Restricciones de seguridad de macOS
**Solución:** Usar cualquiera de los métodos de seguridad descritos arriba

### **❌ "Python no está instalado" (Windows)**
**Causa:** Python no está en PATH
**Solución:** 
1. Instalar Python desde https://python.org
2. Marcar "Add Python to PATH" durante la instalación

### **❌ Aplicación se cierra inmediatamente**
**Causa:** Falta el módulo `encodings`
**Solución:** El script compatible ya incluye todos los módulos necesarios

### **❌ Error "No module named 'principal'"**
**Causa:** Archivos del proyecto no están en la misma carpeta
**Solución:** Verificar que `main.py` y `principal.py` estén presentes

### **❌ Ejecutable muy grande**
**Causa:** Normal - incluye Python completo y todas las dependencias
**Solución:** No es un problema, es esperado para aplicaciones standalone

## 📁 Estructura de Archivos del Proyecto

```
Interfaz_bonos/
├── main.py                              # Archivo principal
├── principal.py                         # Módulo principal
├── assets/                              # Recursos (imágenes, etc.)
│   └── img/
│       └── logo.png
├── crear_bonos_alfa_compatible.sh       # ✅ Script macOS recomendado
├── crear_bonos_alfa_windows.bat         # Script Windows (batch)
├── crear_bonos_alfa_windows.ps1         # Script Windows (PowerShell)
├── abrir_bonos_alfa.sh                  # Script ayuda macOS
├── INSTRUCCIONES_WINDOWS.md            # Guía Windows
├── README_EJECUTABLES.md               # Esta guía
└── dist/                               # Ejecutables generados
    ├── bonosAlfa.app                   # Aplicación macOS
    ├── bonosAlfa_AppleSilicon          # Ejecutable macOS directo
    ├── bonosAlfa-1.0.0-AppleSilicon.dmg # Instalador DMG
    └── bonosAlfa.exe                   # Ejecutable Windows (cuando se cree)
```

## 🎯 Distribución

### **Para Usuarios Finales:**
1. **macOS**: Comparte el archivo `.dmg`
2. **Windows**: Comparte el archivo `.exe`
3. **Ambos sistemas**: No requieren Python instalado

### **Para Desarrolladores:**
1. Clonar/descargar el proyecto completo
2. Ejecutar el script correspondiente al sistema operativo
3. Los ejecutables se generan en la carpeta `dist/`

## 📞 Soporte

Si tienes problemas:

1. **Lee esta guía completa**
2. **Verifica los requisitos previos**
3. **Usa los scripts de ayuda incluidos**
4. **Revisa la sección de solución de problemas**

## 📝 Notas Adicionales

- Los ejecutables son **standalone** (no requieren Python)
- El primer arranque puede ser **lento** (normal)
- **Windows Defender** puede escanear el ejecutable (normal)
- **macOS Gatekeeper** mostrará avisos de seguridad (usar métodos de solución)
- Los ejecutables funcionan **offline** sin conexión a internet

---

✅ **¡Listo!** Con esta guía puedes crear y distribuir **bonosAlfa** en macOS y Windows. 