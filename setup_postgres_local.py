#!/usr/bin/env python3
"""
Script para configurar PostgreSQL localmente para desenvolvimento
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        if result.stdout:
            print(f"📝 Saída: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro!")
        print(f"📝 Erro: {e.stderr.strip()}")
        return False

def check_postgres_installed():
    """Verifica se PostgreSQL está instalado"""
    print("🔍 Verificando se PostgreSQL está instalado...")
    
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL não encontrado")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL não está no PATH")
        return False

def create_database_and_user():
    """Cria o banco e usuário para o projeto"""
    print("🗄️ Configurando banco de dados...")
    
    # Criar usuário
    if not run_command(
        "sudo -u postgres createuser --interactive --pwprompt escola_user",
        "Criando usuário escola_user"
    ):
        print("⚠️  Usuário já existe ou erro na criação")
    
    # Criar banco
    if not run_command(
        "sudo -u postgres createdb -O escola_user escola_para_todos",
        "Criando banco escola_para_todos"
    ):
        print("⚠️  Banco já existe ou erro na criação")
    
    # Conceder privilégios
    run_command(
        "sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE escola_para_todos TO escola_user;'",
        "Concedendo privilégios ao usuário"
    )

def install_requirements():
    """Instala as dependências Python"""
    print("📦 Instalando dependências Python...")
    run_command("pip install -r requirements.txt", "Instalando requirements.txt")

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Arquivo {env_file} já existe")
        return
    
    print("📝 Criando arquivo .env...")
    env_content = """# Configurações para PostgreSQL - Escola para Todos

# Configurações da Aplicação
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Configurações do Banco PostgreSQL Local
DB_HOST=localhost
DB_NAME=escola_para_todos
DB_USER=escola_user
DB_PASSWORD=escola123
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")

def main():
    """Função principal"""
    print("🚀 Configurando PostgreSQL para Escola para Todos")
    print("=" * 50)
    
    # Verificar se PostgreSQL está instalado
    if not check_postgres_installed():
        print("\n❌ PostgreSQL não está instalado!")
        print("📋 Para instalar no Windows:")
        print("   1. Baixe em: https://www.postgresql.org/download/windows/")
        print("   2. Execute o instalador")
        print("   3. Execute este script novamente")
        return
    
    # Criar banco e usuário
    create_database_and_user()
    
    # Instalar dependências
    install_requirements()
    
    # Criar arquivo .env
    create_env_file()
    
    print("\n🎉 Configuração concluída!")
    print("📋 Próximos passos:")
    print("   1. Ajuste a senha no arquivo .env se necessário")
    print("   2. Execute: python init_db_postgres.py")
    print("   3. Execute: python app_postgres.py")
    print("\n🌐 Para produção no Render:")
    print("   1. Faça push para o repositório")
    print("   2. O Render configurará automaticamente")

if __name__ == "__main__":
    main()
