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
    
    # Tentar diferentes comandos para Windows
    commands = ['psql', 'psql.exe', 'C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe', 'C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe']
    
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
                return cmd
        except FileNotFoundError:
            continue
    
    print("❌ PostgreSQL não encontrado no PATH")
    return None

def create_database_and_user(psql_cmd):
    """Cria o banco e usuário para o projeto"""
    print("🗄️ Configurando banco de dados...")
    
    # Criar usuário (Windows - sem sudo)
    print("📝 Criando usuário escola_user...")
    create_user_cmd = f'"{psql_cmd}" -U postgres -c "CREATE USER escola_user WITH PASSWORD \'escola123\';"'
    
    if not run_command(create_user_cmd, "Criando usuário escola_user"):
        print("⚠️  Usuário já existe ou erro na criação")
    
    # Criar banco
    print("📝 Criando banco escola_para_todos...")
    create_db_cmd = f'"{psql_cmd}" -U postgres -c "CREATE DATABASE escola_para_todos OWNER escola_user;"'
    
    if not run_command(create_db_cmd, "Criando banco escola_para_todos"):
        print("⚠️  Banco já existe ou erro na criação")
    
    # Conceder privilégios
    grant_cmd = f'"{psql_cmd}" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE escola_para_todos TO escola_user;"'
    run_command(grant_cmd, "Concedendo privilégios ao usuário")
    
    # Conceder privilégios no schema public
    grant_schema_cmd = f'"{psql_cmd}" -U postgres -d escola_para_todos -c "GRANT ALL ON SCHEMA public TO escola_user;"'
    run_command(grant_schema_cmd, "Concedendo privilégios no schema")

def test_connection():
    """Testa a conexão com o banco"""
    print("🔍 Testando conexão com PostgreSQL...")
    
    test_script = """
import psycopg
import os

try:
    conn = psycopg.connect(
        host='localhost',
        dbname='escola_para_todos',
        user='escola_user',
        password='escola123',
        port=5432
    )
    print('✅ Conexão PostgreSQL funcionando!')
    conn.close()
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
"""
    
    with open('test_connection.py', 'w') as f:
        f.write(test_script)
    
    if run_command("python test_connection.py", "Testando conexão"):
        os.remove('test_connection.py')
        return True
    return False

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
DB_PORT=5432
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")

def show_postgres_commands(psql_cmd):
    """Mostra comandos úteis do PostgreSQL"""
    print("\n🗄️ Comandos PostgreSQL úteis:")
    print(f"   Conectar como postgres: {psql_cmd} -U postgres")
    print(f"   Conectar ao banco: {psql_cmd} -U escola_user -d escola_para_todos")
    print("   Listar bancos: \\l")
    print("   Listar tabelas: \\dt")
    print("   Sair: \\q")

def main():
    """Função principal"""
    print("🚀 Configurando PostgreSQL para Escola para Todos")
    print("=" * 50)
    
    # Verificar se PostgreSQL está instalado
    psql_cmd = check_postgres_installed()
    if not psql_cmd:
        print("\n❌ PostgreSQL não está instalado ou não está no PATH!")
        print("📋 Para instalar no Windows:")
        print("   1. Baixe em: https://www.postgresql.org/download/windows/")
        print("   2. Execute o instalador")
        print("   3. Adicione o binário ao PATH")
        print("   4. Execute este script novamente")
        return
    
    # Criar banco e usuário
    create_database_and_user(psql_cmd)
    
    # Instalar dependências
    install_requirements()
    
    # Testar conexão
    if not test_connection():
        print("❌ Erro na conexão com PostgreSQL")
        print("📋 Verifique se:")
        print("   1. PostgreSQL está rodando")
        print("   2. A senha do usuário postgres está correta")
        print("   3. A porta 5432 está disponível")
        return
    
    # Criar arquivo .env
    create_env_file()
    
    # Mostrar comandos úteis
    show_postgres_commands(psql_cmd)
    
    print("\n🎉 Configuração concluída!")
    print("📋 Próximos passos:")
    print("   1. Execute: python init_db_postgres.py")
    print("   2. Execute: python app_postgres.py")
    print("\n🌐 Para produção no Render:")
    print("   1. O Render configurará automaticamente")
    print("   2. Não precisa de configuração local")

if __name__ == "__main__":
    main()
