#!/usr/bin/env python3
"""
Base de datos SQLite para gestionar resegmentaciones
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class ResegmentacionDB:
    """Clase para manejar la base de datos de resegmentaciones"""
    
    def __init__(self, db_path: str = "resegmentaciones.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla de resegmentaciones
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resegmentaciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agente TEXT NOT NULL,
                        subramo TEXT NOT NULL,
                        num_poliza TEXT NOT NULL,
                        tipo_resegmentacion TEXT NOT NULL,  -- 'PRIMA' o 'NUEVO_NEGOCIO'
                        fecha_resegmentacion DATETIME NOT NULL,
                        usuario_responsable TEXT NOT NULL,
                        pago_id TEXT,
                        fecha_primer_pago TEXT,
                        motivo_resegmentacion TEXT,
                        num_poliza_nuevo_negocio TEXT,
                        datos_originales TEXT,  -- JSON con datos originales
                        respuesta_api TEXT,     -- JSON con respuesta de la API
                        estado TEXT DEFAULT 'ACTIVO',  -- 'ACTIVO', 'REVERTIDO'
                        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(agente, subramo, num_poliza, tipo_resegmentacion)
                    )
                ''')
                
                # Crear índices para consultas rápidas
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reseg_poliza 
                    ON resegmentaciones(num_poliza)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reseg_agente_subramo 
                    ON resegmentaciones(agente, subramo)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reseg_fecha 
                    ON resegmentaciones(fecha_resegmentacion)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reseg_pago_id 
                    ON resegmentaciones(pago_id)
                ''')
                
                conn.commit()
                print("[DEBUG] Base de datos de resegmentaciones inicializada correctamente")
                
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {str(e)}")
            raise
    
    def guardar_resegmentacion(self, resegmentacion_data: Dict) -> bool:
        """
        Guarda una resegmentación en la base de datos
        
        Args:
            resegmentacion_data: Diccionario con los datos de la resegmentación
            
        Returns:
            bool: True si se guardó exitosamente, False en caso contrario
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Preparar datos
                agente = resegmentacion_data.get('agente', '')
                subramo = resegmentacion_data.get('subramo', '')
                num_poliza = resegmentacion_data.get('num_poliza', '')
                tipo_resegmentacion = resegmentacion_data.get('tipo_resegmentacion', '')
                fecha_resegmentacion = resegmentacion_data.get('fecha_resegmentacion', datetime.now().isoformat())
                usuario_responsable = resegmentacion_data.get('usuario_responsable', '')
                pago_id = resegmentacion_data.get('pago_id', '')
                fecha_primer_pago = resegmentacion_data.get('fecha_primer_pago', '')
                motivo_resegmentacion = resegmentacion_data.get('motivo_resegmentacion', '')
                num_poliza_nuevo_negocio = resegmentacion_data.get('num_poliza_nuevo_negocio', '')
                datos_originales = json.dumps(resegmentacion_data.get('datos_originales', {}))
                respuesta_api = json.dumps(resegmentacion_data.get('respuesta_api', {}))
                
                # Insertar o actualizar
                cursor.execute('''
                    INSERT OR REPLACE INTO resegmentaciones 
                    (agente, subramo, num_poliza, tipo_resegmentacion, fecha_resegmentacion,
                     usuario_responsable, pago_id, fecha_primer_pago, motivo_resegmentacion,
                     num_poliza_nuevo_negocio, datos_originales, respuesta_api)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agente, subramo, num_poliza, tipo_resegmentacion, fecha_resegmentacion,
                    usuario_responsable, pago_id, fecha_primer_pago, motivo_resegmentacion,
                    num_poliza_nuevo_negocio, datos_originales, respuesta_api
                ))
                
                conn.commit()
                print(f"[DEBUG] Resegmentación guardada: {agente} - {subramo} - {num_poliza}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error guardando resegmentación: {str(e)}")
            return False
    
    def obtener_resegmentacion(self, agente: str, subramo: str, num_poliza: str) -> Optional[Dict]:
        """
        Obtiene una resegmentación específica por agente, subramo y número de póliza
        
        Returns:
            Dict con los datos de la resegmentación o None si no existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Para acceder por nombres de columna
                cursor = conn.cursor()
                
                # Búsqueda exacta primero
                cursor.execute('''
                    SELECT * FROM resegmentaciones 
                    WHERE agente = ? AND subramo = ? AND num_poliza = ? 
                    AND estado = 'ACTIVO'
                    ORDER BY fecha_resegmentacion DESC
                    LIMIT 1
                ''', (agente, subramo, num_poliza))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                
                # Si no encuentra, búsqueda flexible (limpiar espacios y comparar)
                cursor.execute('''
                    SELECT * FROM resegmentaciones 
                    WHERE TRIM(UPPER(agente)) = TRIM(UPPER(?)) 
                    AND TRIM(UPPER(subramo)) = TRIM(UPPER(?)) 
                    AND TRIM(UPPER(num_poliza)) = TRIM(UPPER(?))
                    AND estado = 'ACTIVO'
                    ORDER BY fecha_resegmentacion DESC
                    LIMIT 1
                ''', (agente, subramo, num_poliza))
                
                row = cursor.fetchone()
                if row:
                    print(f"[DEBUG] Resegmentación encontrada con búsqueda flexible: {agente}-{subramo}-{num_poliza}")
                    return dict(row)
                
                return None
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo resegmentación: {str(e)}")
            return None
    
    def obtener_todas_resegmentaciones(self) -> List[Dict]:
        """Obtiene todas las resegmentaciones activas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM resegmentaciones 
                    WHERE estado = 'ACTIVO'
                    ORDER BY fecha_resegmentacion DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo resegmentaciones: {str(e)}")
            return []
    
    def verificar_resegmentacion_existe(self, agente: str, subramo: str, num_poliza: str) -> bool:
        """Verifica si existe una resegmentación para los datos dados"""
        resegmentacion = self.obtener_resegmentacion(agente, subramo, num_poliza)
        return resegmentacion is not None
    
    def obtener_fecha_resegmentacion(self, agente: str, subramo: str, num_poliza: str) -> Optional[str]:
        """Obtiene la fecha de resegmentación si existe"""
        resegmentacion = self.obtener_resegmentacion(agente, subramo, num_poliza)
        if resegmentacion:
            return resegmentacion.get('fecha_resegmentacion', '')
        return None
    
    def obtener_resegmentacion_por_pago_id(self, pago_id: str) -> Optional[Dict]:
        """Obtiene una resegmentación específica por pago_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM resegmentaciones 
                    WHERE pago_id = ? AND estado = 'ACTIVO'
                    ORDER BY fecha_resegmentacion DESC
                    LIMIT 1
                ''', (pago_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo resegmentación por pago_id: {str(e)}")
            return None
    
    def verificar_resegmentacion_por_pago_id(self, pago_id: str) -> bool:
        """Verifica si existe una resegmentación para un pago_id dado"""
        resegmentacion = self.obtener_resegmentacion_por_pago_id(pago_id)
        return resegmentacion is not None
    
    def obtener_fecha_primer_pago_resegmentado(self, pago_id: str) -> Optional[str]:
        """Obtiene la fecha de primer pago resegmentado si existe"""
        resegmentacion = self.obtener_resegmentacion_por_pago_id(pago_id)
        if resegmentacion:
            return resegmentacion.get('fecha_primer_pago', '')
        return None
    
    def revertir_resegmentacion(self, agente: str, subramo: str, num_poliza: str) -> bool:
        """Marca una resegmentación como revertida"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE resegmentaciones 
                    SET estado = 'REVERTIDO' 
                    WHERE agente = ? AND subramo = ? AND num_poliza = ? AND estado = 'ACTIVO'
                ''', (agente, subramo, num_poliza))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"[ERROR] Error revirtiendo resegmentación: {str(e)}")
            return False
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de resegmentaciones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de resegmentaciones activas
                cursor.execute('SELECT COUNT(*) FROM resegmentaciones WHERE estado = "ACTIVO"')
                total_activas = cursor.fetchone()[0]
                
                # Resegmentaciones por tipo
                cursor.execute('''
                    SELECT tipo_resegmentacion, COUNT(*) 
                    FROM resegmentaciones 
                    WHERE estado = "ACTIVO" 
                    GROUP BY tipo_resegmentacion
                ''')
                por_tipo = dict(cursor.fetchall())
                
                # Resegmentaciones por fecha (últimos 30 días)
                cursor.execute('''
                    SELECT DATE(fecha_resegmentacion) as fecha, COUNT(*) 
                    FROM resegmentaciones 
                    WHERE estado = "ACTIVO" 
                    AND fecha_resegmentacion >= datetime('now', '-30 days')
                    GROUP BY DATE(fecha_resegmentacion)
                    ORDER BY fecha DESC
                ''')
                por_fecha = dict(cursor.fetchall())
                
                return {
                    'total_activas': total_activas,
                    'por_tipo': por_tipo,
                    'por_fecha': por_fecha
                }
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo estadísticas: {str(e)}")
            return {}
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        # SQLite se maneja automáticamente con context managers
        pass 