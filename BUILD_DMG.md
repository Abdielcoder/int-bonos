# 📦 Guía para Crear Instalador DMG - Admin Bonos

Esta guía explica cómo crear un instalador DMG profesional para **Admin Bonos** en macOS.

## 🎯 Requisitos Previos

### 📋 Sistema
- **macOS** (cualquier versión moderna)
- **Python 3.8+** instalado
- **Homebrew** (recomendado para herramientas adicionales)

### 📦 Dependencias Python
```bash
pip3 install pyinstaller
```

### 🛠️ Herramientas Opcionales (Recomendadas)
```bash
# Para DMG con diseño avanzado
brew install create-dmg
```

## 🚀 Métodos de Construcción

### 🔥 Método Rápido (Recomendado)

**Script automático en Bash:**
```bash
# Dar permisos de ejecución
chmod +x setup_dmg.sh

# Ejecutar
./setup_dmg.sh
```

### 🐍 Método Avanzado (Python)

**Script completo en Python:**
```bash
python3 build_dmg.py
```

### ⚡ Método Manual

**Construcción paso a paso:**

1. **Limpiar builds anteriores:**
   ```bash
   rm -rf build dist *.spec
   ```

2. **Convertir icono:**
   ```bash
   # Crear iconset
   mkdir -p assets/img/logo.iconset
   
   # Generar tamaños múltiples
   for size in 16 32 64 128 256 512 1024; do
       sips -z $size $size assets/img/logo.png \
            --out "assets/img/logo.iconset/icon_${size}x${size}.png"
   done
   
   # Convertir a ICNS
   iconutil -c icns assets/img/logo.iconset -o assets/img/logo.icns
   rm -rf assets/img/logo.iconset
   ```

3. **Construir aplicación:**
   ```bash
   python3 -m PyInstaller \
       --onedir \
       --windowed \
       --noconfirm \
       --clean \
       --name "Admin Bonos" \
       --osx-bundle-identifier "com.rinorisk.adminbonos" \
       --icon "assets/img/logo.icns" \
       --add-data "assets:assets" \
       --add-data "requirements.txt:." \
       main.py
   ```

4. **Crear DMG (con create-dmg):**
   ```bash
   create-dmg \
       --volname "Admin Bonos" \
       --volicon "assets/img/logo.png" \
       --window-pos 200 120 \
       --window-size 600 400 \
       --icon-size 100 \
       --icon "Admin Bonos.app" 175 190 \
       --hide-extension "Admin Bonos.app" \
       --app-drop-link 425 190 \
       --no-internet-enable \
       "dist/AdminBonos-1.0.0-macOS.dmg" \
       "dist/Admin Bonos.app"
   ```

5. **Crear DMG (método simple):**
   ```bash
   # Crear DMG temporal
   hdiutil create -size 200m -fs HFS+ -volname "Admin Bonos" "temp.dmg"
   
   # Montar
   MOUNT_POINT=$(hdiutil mount "temp.dmg" | grep "/Volumes/" | awk '{print $3}')
   
   # Copiar aplicación
   cp -R "dist/Admin Bonos.app" "$MOUNT_POINT/"
   ln -s /Applications "$MOUNT_POINT/Applications"
   
   # Desmontar y comprimir
   hdiutil unmount "$MOUNT_POINT"
   hdiutil convert "temp.dmg" -format UDZO -o "dist/AdminBonos-1.0.0-macOS.dmg"
   rm "temp.dmg"
   ```

## 📁 Estructura de Archivos Resultante

```
Interfaz_bonos/
├── dist/
│   ├── Admin Bonos.app          # Aplicación macOS
│   └── AdminBonos-1.0.0-macOS.dmg # Instalador DMG
├── build/                       # Archivos temporales (se pueden eliminar)
├── assets/
│   └── img/
│       ├── logo.png            # Icono original
│       └── logo.icns           # Icono convertido (temporal)
├── build_dmg.py                # Script Python avanzado
├── setup_dmg.sh                # Script Bash rápido
└── BUILD_DMG.md                # Esta documentación
```

## 🎨 Características del Instalador

### ✨ Diseño Profesional
- **Icono personalizado** usando `assets/img/logo.png`
- **Ventana de instalación** con diseño corporativo
- **Drag & Drop** intuitivo hacia Applications
- **Tamaño optimizado** con compresión UDZO

### 🔒 Compatibilidad
- **Bundle ID:** `com.rinorisk.adminbonos`
- **Arquitectura:** Universal (Intel + Apple Silicon)
- **macOS:** 10.14+ (Mojave y posteriores)

### 📦 Contenido Incluido
- ✅ Aplicación principal (`Admin Bonos.app`)
- ✅ Assets y recursos (`assets/`)
- ✅ Dependencias Python embebidas
- ✅ Requirements para referencia

## 🐛 Solución de Problemas

### ❌ Error: "PyInstaller no encontrado"
```bash
pip3 install pyinstaller
# o si usas conda:
conda install pyinstaller
```

### ❌ Error: "create-dmg no encontrado"
```bash
# Instalar con Homebrew
brew install create-dmg

# O usar método simple (automático fallback)
```

### ❌ Error: "Permission denied"
```bash
# Dar permisos al script
chmod +x setup_dmg.sh
```

### ❌ Error: "Icon not found"
```bash
# Verificar que existe el icono
ls -la assets/img/logo.png

# O usar icono alternativo
cp assets/img/rino.png assets/img/logo.png
```

### ❌ Error de construcción de PyInstaller
```bash
# Limpiar caché y rebuilds
rm -rf build dist *.spec __pycache__
pip3 install --upgrade pyinstaller
```

## 📋 Lista de Verificación

Antes de crear el DMG, asegúrate de que:

- [ ] ✅ El archivo `main.py` existe y funciona
- [ ] ✅ El archivo `requirements.txt` está actualizado
- [ ] ✅ La carpeta `assets/` contiene todos los recursos
- [ ] ✅ El icono `assets/img/logo.png` existe
- [ ] ✅ PyInstaller está instalado (`pip3 install pyinstaller`)
- [ ] ✅ Tienes permisos de escritura en el directorio
- [ ] ✅ Hay suficiente espacio en disco (>500MB)

## 🚀 Comandos Rápidos

**Todo en uno:**
```bash
# Preparar y ejecutar
chmod +x setup_dmg.sh && ./setup_dmg.sh
```

**Solo construcción:**
```bash
python3 build_dmg.py
```

**Limpiar todo:**
```bash
rm -rf build dist *.spec assets/img/*.icns
```

## 📞 Resultado Final

Después de ejecutar cualquiera de los métodos, tendrás:

```
📦 dist/AdminBonos-1.0.0-macOS.dmg (Instalador listo para distribuir)
📁 dist/Admin Bonos.app (Aplicación ejecutable)
```

**Para instalar:**
1. Abre el archivo `.dmg`
2. Arrastra `Admin Bonos.app` a la carpeta `Applications`
3. Ejecuta desde Launchpad o Applications

---

**¡Listo!** 🎉 Tu instalador DMG profesional está creado y listo para distribuir. 