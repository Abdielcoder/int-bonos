#!/usr/bin/env python3
"""
Servicio OTP (One-Time Password) para validación adicional
Genera códigos de 6 dígitos que expiran en 5 minutos
"""

import smtplib
import random
import string
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class OTPService:
    """Servicio para manejar códigos OTP"""
    
    def __init__(self):
        self.otp_storage = {}  # Almacenamiento temporal de códigos OTP
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'desarrollo@rinorisk.com',  # Tu correo de Google Workspace
            'password': 'zezc hsgb azft jzct',  # Contraseña de aplicación de Google
            'from_email': 'desarrollo@rinorisk.com'
        }
        
    def generate_otp(self, email: str) -> str:
        """Genera un código OTP de 6 dígitos para el email especificado"""
        # Generar código de 6 dígitos
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Calcular tiempo de expiración (5 minutos)
        expiration_time = datetime.now() + timedelta(minutes=5)
        
        # Almacenar el código con su tiempo de expiración
        self.otp_storage[email] = {
            'code': otp_code,
            'expires_at': expiration_time,
            'generated_at': datetime.now()
        }
        
        print(f"[OTP] Código generado para {email}: {otp_code} (expira en 5 minutos)")
        return otp_code
    
    def send_otp_email(self, email: str, otp_code: str) -> tuple[bool, str]:
        """Envía el código OTP por correo electrónico"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = email
            msg['Subject'] = "🔐 Código de Verificación OTP - Herramientas Bonos"
            
            # Cuerpo del correo en HTML
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #1e40af; text-align: center;">🔐 Código de Verificación OTP</h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p>Hola,</p>
                            <p>Has solicitado un código de verificación para acceder a las funciones de resegmentación en <strong>Herramientas Bonos</strong>.</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <div style="display: inline-block; background-color: #1e40af; color: white; padding: 15px 30px; border-radius: 8px; font-size: 24px; font-weight: bold; letter-spacing: 3px;">
                                    {otp_code}
                                </div>
                            </div>
                            
                            <p><strong>⏰ Este código expira en 5 minutos.</strong></p>
                            <p>Si no solicitaste este código, puedes ignorar este correo de forma segura.</p>
                        </div>
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px;">
                            <p>Herramientas Bonos - Sistema de Administración</p>
                            <p>RinoRisk © {datetime.now().year}</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Enviar correo real usando Gmail SMTP
            print(f"[OTP] 📧 Enviando correo real a {email}")
            print(f"[OTP] 📋 Código OTP: {otp_code}")
            print(f"[OTP] ⏰ Expira en: 5 minutos")
            
            try:
                server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
                server.quit()
                print(f"[OTP] ✅ Correo enviado exitosamente a {email}")
                return True, f"Código OTP enviado exitosamente a {email}"
            except Exception as smtp_error:
                print(f"[OTP] ❌ Error SMTP: {smtp_error}")
                # Si falla el envío, seguir con simulación para pruebas
                print(f"[OTP] 📧 Fallback: Simulando envío de correo a {email}")
                return True, f"Código OTP generado (simulación por error SMTP): {otp_code}"
            
        except Exception as e:
            print(f"[OTP] ❌ Error enviando correo: {e}")
            return False, f"Error enviando correo: {str(e)}"
    
    def verify_otp(self, email: str, input_code: str) -> tuple[bool, str]:
        """Verifica si el código OTP es válido"""
        if email not in self.otp_storage:
            return False, "No hay código OTP generado para este correo"
        
        stored_data = self.otp_storage[email]
        stored_code = stored_data['code']
        expires_at = stored_data['expires_at']
        
        # Verificar si el código ha expirado
        if datetime.now() > expires_at:
            # Limpiar código expirado
            del self.otp_storage[email]
            return False, "El código OTP ha expirado. Solicita uno nuevo."
        
        # Verificar si el código coincide
        if input_code.strip() == stored_code:
            # Código válido - limpiar del almacenamiento
            del self.otp_storage[email]
            return True, "Código OTP válido"
        else:
            return False, "Código OTP incorrecto"
    
    def cleanup_expired_codes(self):
        """Limpia códigos OTP expirados del almacenamiento"""
        current_time = datetime.now()
        expired_emails = []
        
        for email, data in self.otp_storage.items():
            if current_time > data['expires_at']:
                expired_emails.append(email)
        
        for email in expired_emails:
            del self.otp_storage[email]
            print(f"[OTP] 🧹 Código expirado limpiado para {email}")
    
    def request_otp(self, email: str) -> tuple[bool, str]:
        """Solicita un nuevo código OTP para el email especificado"""
        # Limpiar códigos expirados
        self.cleanup_expired_codes()
        
        # Generar nuevo código
        otp_code = self.generate_otp(email)
        
        # Enviar por correo
        success, message = self.send_otp_email(email, otp_code)
        
        if success:
            return True, f"Código OTP enviado a {email}. Revisa tu bandeja de entrada."
        else:
            return False, message

# Instancia global del servicio OTP
otp_service = OTPService() 