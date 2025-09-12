#!/usr/bin/env python3
"""
Script para configurar PostgreSQL no Windows
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_psql_command(command, description, user="postgres", database="postgres"):
    """Executa um comando psql"""
    print(f"🔧 {description}...")
    
    psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
    
    # Comando completo
    full_command = [
        psql_path,
        "-U", user,
        "-d", database,
        "-c", command
    ]
    
    try:
        # Executar com variáveis de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = 'postgres'  # Senha padrão, ajuste se necessário
        
        result = subprocess.run(
            full_command, 
            env=env,
            capture_output=True, 
            text=True,
            check=True
        )
        
        print(f"✅ {description} - Sucesso!")
        if result.stdout:
            print(f"📝 Saída: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro!")
        print(f"📝 Erro: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def create_database_and_user():
    """Cria o banco e usuário para o projeto"""
    print("🗄️ Configurando banco de dados...")
    
    # Criar usuário
    if not run_psql_command(
        "CREATE USER escola_user WITH PASSWORD 'escola123';",
        "Criando usuário escola_user"
    ):
        print("⚠️  Usuário já existe ou erro na criação")
    
    # Criar banco
    if not run_psql_command(
        "CREATE DATABASE escola_para_todos OWNER escola_user;",
        "Criando banco escola_para_todos"
    ):
        print("⚠️  Banco já existe ou erro na criação")
    
    # Conceder privilégios
    run_psql_command(
        "GRANT ALL PRIVILEGES ON DATABASE escola_para_todos TO escola_user;",
        "Concedendo privilégios ao usuário"
    )
    
    # Conceder privilégios no schema public
    run_psql_command(
        "GRANT ALL ON SCHEMA public TO escola_user;",
        "Concedendo privilégios no schema",
        user="escola_user",
        database="escola_para_todos"
    )

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

def run_command(command, description):
    """Executa um comando Python"""
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

def show_postgres_commands():
    """Mostra comandos úteis do PostgreSQL"""
    psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
    
    print("\n🗄️ Comandos PostgreSQL úteis:")
    print(f"   Conectar como postgres: \"{psql_path}\" -U postgres")
    print(f"   Conectar ao banco: \"{psql_path}\" -U escola_user -d escola_para_todos")
    print("   Listar bancos: \\l")
    print("   Listar tabelas: \\dt")
    print("   Sair: \\q")
    print("\n💡 Dica: Se pedir senha, use 'postgres' para usuário postgres")

def main():
    """Função principal"""
    print("🚀 Configurando PostgreSQL para Escola para Todos (Windows)")
    print("=" * 60)
    
    print("📋 IMPORTANTE: Este script assume que:")
    print("   1. PostgreSQL está instalado em C:\\Program Files\\PostgreSQL\\17\\")
    print("   2. A senha do usuário 'postgres' é 'postgres'")
    print("   3. Se a senha for diferente, edite o script e altere PGPASSWORD")
    print()
    
    # Verificar se PostgreSQL está instalado
    psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
    if not os.path.exists(psql_path):
        print(f"❌ PostgreSQL não encontrado em {psql_path}")
        print("📋 Verifique o caminho de instalação")
        return
    
    print(f"✅ PostgreSQL encontrado em {psql_path}")
    
    # Criar banco e usuário
    create_database_and_user()
    
    # Instalar dependências
    install_requirements()
    
    # Criar arquivo .env
    create_env_file()
    
    # Mostrar comandos úteis
    show_postgres_commands()
    
    print("\n🎉 Configuração concluída!")
    print("📋 Próximos passos:")
    print("   1. Execute: python init_db_postgres.py")
    print("   2. Execute: python app_postgres.py")
    print("\n🌐 Para produção no Render:")
    print("   1. O Render configurará automaticamente")
    print("   2. Não precisa de configuração local")
    
    print("\n⚠️  Se houver erro de senha:")
    print("   1. Edite este script")
    print("   2. Altere a linha: env['PGPASSWORD'] = 'sua_senha_real'")
    print("   3. Execute novamente")

if __name__ == "__main__":
    main()
