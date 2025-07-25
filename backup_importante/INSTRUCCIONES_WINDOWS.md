# 🪟 Crear Ejecutable bonosAlfa para Windows

Este documento explica cómo crear el ejecutable `bonosAlfa.exe` para Windows.

## ⚠️ Requisitos Previos

### 1. Sistema Windows
- Windows 10 o superior
- Arquitectura x64 (recomendado)

### 2. Python Instalado
```bash
# Verificar que Python está instalado
python --version
# Debe mostrar: Python 3.8 o superior
```

**Si no tienes Python:**
1. Descarga desde: https://python.org
2. **IMPORTANTE:** Marcar "Add Python to PATH" durante la instalación
3. Reiniciar el símbolo del sistema

### 3. Archivos del Proyecto
Asegúrate de tener estos archivos en la carpeta:
- `main.py`
- `principal.py`  
- `assets/` (carpeta con imágenes)
- Uno de los scripts de compilación (ver abajo)

## 🚀 Métodos de Compilación

### Método 1: Script Batch (.bat)
**Más simple y compatible**

1. Copia el archivo `crear_bonos_alfa_windows.bat` a tu carpeta del proyecto
2. Abre el símbolo del sistema (cmd) en la carpeta del proyecto
3. Ejecuta:
```cmd
crear_bonos_alfa_windows.bat
```

### Método 2: Script PowerShell (.ps1)
**Más moderno y con mejor información**

1. Copia el archivo `crear_bonos_alfa_windows.ps1` a tu carpeta del proyecto
2. Abre PowerShell como administrador
3. Permite la ejecución de scripts (solo la primera vez):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
4. Navega a tu carpeta del proyecto y ejecuta:
```powershell
.\crear_bonos_alfa_windows.ps1
```

## 📁 Resultado Esperado

Después de ejecutar cualquiera de los scripts, encontrarás:

```
tu-proyecto/
├── dist/
│   └── bonosAlfa.exe    ← ¡Tu ejecutable!
├── main.py
├── principal.py
└── assets/
```

## 🔧 Solución de Problemas

### Error: "Python no está instalado"
**Solución:**
1. Instala Python desde https://python.org
2. Asegúrate de marcar "Add Python to PATH"
3. Reinicia el símbolo del sistema

### Error: "pip no está disponible"
**Solución:**
```cmd
python -m ensurepip --upgrade
```

### Error: "No module named 'principal'"
**Solución:**
- Verifica que `principal.py` esté en la misma carpeta que `main.py`
- Verifica que no haya errores de sintaxis en `principal.py`

### Error durante la compilación
**Solución:**
1. Elimina las carpetas `build` y `dist`
2. Ejecuta el script nuevamente
3. Si persiste, instala las dependencias manualmente:
```cmd
pip install pyinstaller PySide6 pandas requests openpyxl xlsxwriter
```

### Ejecutable muy grande
**Esto es normal.** El ejecutable incluye:
- Python completo
- PySide6 (interface gráfica)
- pandas (procesamiento de datos)
- Todas las dependencias

Tamaño esperado: **80-150 MB**

## 🎯 Distribución

### Para uso personal:
- Simplemente ejecuta `dist\bonosAlfa.exe`

### Para distribuir a otros:
1. Copia el archivo `bonosAlfa.exe` 
2. **No necesitas** copiar nada más
3. El ejecutable funciona en cualquier Windows sin Python instalado

### Crear instalador (Opcional):
Puedes usar herramientas como:
- **Inno Setup** (gratis): https://jrsoftware.org/isinfo.php
- **NSIS** (gratis): https://nsis.sourceforge.io/
- **Advanced Installer** (comercial)

## 📋 Lista de Verificación

- [ ] Python 3.8+ instalado y en PATH
- [ ] Archivos `main.py` y `principal.py` presentes
- [ ] Carpeta `assets/` presente
- [ ] Script de compilación ejecutado sin errores
- [ ] Archivo `bonosAlfa.exe` creado en `dist/`
- [ ] Ejecutable probado y funcionando

## 🆘 Soporte

Si tienes problemas:

1. **Verifica los requisitos** de la sección anterior
2. **Lee los mensajes de error** completos
3. **Prueba instalar dependencias manualmente**:
```cmd
pip install --upgrade pip
pip install pyinstaller PySide6 pandas requests openpyxl xlsxwriter Pillow
```

## 📝 Notas Adicionales

- El ejecutable solo funciona en Windows
- Para macOS usa el script `crear_bonos_alfa_corregido.sh`
- Para Linux necesitarías adaptar el script de macOS
- El primer arranque puede ser lento (normal)
- Windows Defender puede escanear el ejecutable (normal)

---
✅ **¡Listo!** Ahora tienes `bonosAlfa.exe` funcionando en Windows. 