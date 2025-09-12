#!/usr/bin/env python3
"""
Arquivo que força o uso do startCommand no render.yaml
"""

import os
import subprocess
import sys

def main():
    """Função principal que executa o startCommand"""
    print("🚀 Iniciando Aqui se Aprende via startCommand...")
    
    # Verificar se estamos no Render
    if os.getenv('RENDER'):
        print("✅ Detectado ambiente Render")
        
        # Executar o startCommand do render.yaml
        start_command = "python init_db_postgres.py && gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app_postgres:app"
        
        print(f"🚀 Executando: {start_command}")
        
        try:
            # Executar o comando
            result = subprocess.run(start_command, shell=True, check=True)
            print("✅ startCommand executado com sucesso!")
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar startCommand: {e}")
            return e.returncode
    else:
        print("❌ Não estamos no Render, usando app_postgres.py diretamente")
        # Importar e executar app_postgres.py
        from app_postgres import app
        app.run()

if __name__ == '__main__':
    sys.exit(main())
