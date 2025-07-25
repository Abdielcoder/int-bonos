# Herramientas Bonos

Aplicación de escritorio desarrollada con Python y PyQt/PySide que proporciona una interfaz nativa para gestión de bonos con funcionalidades de cotejamiento y resegmentación.

## Características

- **Sistema de autenticación**: Pantalla de login moderna con diseño Admin Panel
- **Interfaz nativa**: Aplicación de escritorio nativa usando PyQt/PySide
- **Interfaz con tabs**: Dos pestañas principales:
  - **Cotejamiento** (seleccionada por defecto) - Análisis y comparación de datos
  - **Resegmentación** - Herramientas de procesamiento de pólizas
- **API Integration**: Conexión con APIs externas para obtención de datos
- **Exportación de datos**: Capacidad de exportar resultados en formato CSV
- **Búsqueda y filtrado**: Herramientas avanzadas de búsqueda en tablas
- **Diseño moderno**: Interfaz limpia y moderna con tema claro

## Credenciales de Acceso (Hardcodeadas)

Para acceder al sistema utiliza las siguientes credenciales:

- **Usuario**: `abdiel`
- **Contraseña**: `123`

## Requisitos del Sistema

- Python 3.8 o superior
- PyQt6 6.6.0+ o PySide6 6.6.0+
- Sistema operativo: Windows, macOS, o Linux

## Instalación

### Opción 1: Instalación desde código fuente

1. Clona o descarga el proyecto
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Opción 2: Usar ejecutable (Recomendado para usuarios finales)

Descarga el ejecutable precompilado desde la sección de releases. No requiere instalación de Python.

## Ejecución

### Desde código fuente

Para ejecutar la aplicación:

```bash
python main.py
```

### Desde ejecutable

Simplemente ejecuta el archivo descargado:

- **Windows**: `HerramientasBonos.exe`
- **macOS**: `HerramientasBonos.app`
- **Linux**: `./HerramientasBonos`

## Funcionalidades

### Tab de Cotejamiento

- **Configuración de API**: Interfaz para configurar conexiones con APIs externas
- **Login automático**: Sistema de autenticación con APIs
- **Carga de datos**: Importación desde archivos JSON o APIs directas
- **Análisis estadístico**: Visualización de métricas clave en tarjetas informativas
- **Tabla interactiva**: Visualización detallada de datos con capacidades de búsqueda y filtrado
- **Exportación**: Descarga de resultados en formato CSV

### Tab de Resegmentación

- **Procesamiento de pólizas**: Herramientas para resegmentación
- **Formularios dinámicos**: Interfaz intuitiva para ingreso de datos
- **Tipos de procesamiento**: Múltiples opciones de resegmentación (Automática, Manual, Por Criterios)
- **Resultados en tiempo real**: Visualización inmediata de resultados del procesamiento

## Estructura del Proyecto

```
Interfaz_bonos/
├── main.py                    # Archivo principal con login y navegación
├── principal.py               # Ventana principal con tabs de funcionalidades
├── requirements.txt           # Dependencias del proyecto
├── build_requirements.txt     # Dependencias para compilación
├── build_executable.py        # Script para crear ejecutable
├── assets/                    # Recursos de la aplicación
│   └── img/
│       └── rino.png          # Logo de la aplicación
├── test_api*.py              # Scripts de prueba de APIs
└── README.md                 # Este archivo
```

## Compilación de Ejecutable

### Opción 1: Script Automático (Recomendado)

Para crear un ejecutable nativo:

```bash
python build_executable.py
```

Este script:
- Detecta automáticamente PyQt6 o PySide6
- Configura todas las dependencias necesarias
- Optimiza el tamaño del ejecutable
- Genera ejecutables para el sistema operativo actual

### Opción 2: PyInstaller Manual

1. Instala PyInstaller:
```bash
pip install pyinstaller
```

2. Crea el ejecutable:
```bash
pyinstaller --onefile --windowed --name=HerramientasBonos main.py
```

### Distribución

El ejecutable se genera en la carpeta `dist/`:
- **Windows**: `dist/HerramientasBonos.exe`
- **macOS**: `dist/HerramientasBonos.app`
- **Linux**: `dist/HerramientasBonos`

## Dependencias

### Principales
- **PyQt6/PySide6**: Framework de interfaz gráfica
- **requests**: Cliente HTTP para APIs
- **pandas**: Manipulación y análisis de datos

### Opcionales
- **openpyxl**: Soporte para archivos Excel
- **xlsxwriter**: Generación de archivos Excel avanzados

## Configuración

### APIs
La aplicación se conecta con APIs externas. Configura las URLs y credenciales en el tab de Cotejamiento:

- **URL Login**: Endpoint de autenticación
- **URL Consulta**: Endpoint de obtención de datos
- **Credenciales**: Usuario y contraseña de la API

### Archivos JSON
También puedes cargar datos desde archivos JSON locales usando el botón "Cargar Archivo JSON".

## Desarrollo

### Arquitectura

La aplicación está estructurada con el patrón MVC:

- **main.py**: Controlador principal y sistema de login
- **principal.py**: Vista principal con componentes de interfaz
- **Clases Qt**: Modelos de datos y workers para operaciones asíncronas

### Estilos

La aplicación usa QSS (Qt Style Sheets) para un diseño moderno y consistente. Los estilos están integrados en los componentes para facilitar el mantenimiento.

### Threads

Las operaciones de API se ejecutan en threads separados usando `QThread` para mantener la interfaz responsiva.

## Migración desde NiceGUI

Esta aplicación fue migrada desde NiceGUI a PyQt/PySide para:

- **Mejor rendimiento**: Aplicación nativa más rápida
- **Mejor integración**: Mejor integración con el sistema operativo
- **Distribución simplificada**: Ejecutables independientes sin dependencias web
- **Funcionalidades nativas**: Acceso completo a funcionalidades del sistema

## Soporte

Para reportar problemas o solicitar funcionalidades:

1. Verifica que tengas las dependencias correctas instaladas
2. Revisa los logs de debug en la consola
3. Proporciona información del sistema operativo y versión de Python

## Licencia

Aplicación desarrollada para uso interno de RinoRisk.

---

**Versión**: 2.0.0 (PyQt/PySide)  
**Última actualización**: 2025  
**Desarrollado por**: RinoRisk Development Team 