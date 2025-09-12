#!/usr/bin/env python3
"""
Script para configurar PostgreSQL usando Docker
"""

import os
import subprocess
import sys
import time
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

def check_docker_installed():
    """Verifica se Docker está instalado"""
    print("🔍 Verificando se Docker está instalado...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Docker não está no PATH")
        return False

def check_docker_running():
    """Verifica se Docker está rodando"""
    print("🔍 Verificando se Docker está rodando...")
    
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker está rodando!")
            return True
        else:
            print("❌ Docker não está rodando")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar Docker: {e}")
        return False

def start_postgres_container():
    """Inicia o container PostgreSQL"""
    print("🐳 Iniciando container PostgreSQL...")
    
    # Parar container existente se houver
    run_command("docker stop escola-postgres", "Parando container existente")
    run_command("docker rm escola-postgres", "Removendo container existente")
    
    # Iniciar novo container
    if run_command(
        'docker run --name escola-postgres -e POSTGRES_DB=escola_para_todos -e POSTGRES_USER=escola_user -e POSTGRES_PASSWORD=escola123 -p 5432:5432 -d postgres:15',
        "Iniciando container PostgreSQL"
    ):
        print("⏳ Aguardando PostgreSQL inicializar...")
        time.sleep(10)  # Aguardar inicialização
        return True
    return False

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

def create_env_file():
    """Cria arquivo .env se não existir"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Arquivo {env_file} já existe")
        return
    
    print("📝 Criando arquivo .env...")
    env_content = """# Configurações para PostgreSQL - Aqui se Ensina

# Configurações da Aplicação
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Configurações do Banco PostgreSQL Local (Docker)
DB_HOST=localhost
DB_NAME=escola_para_todos
DB_USER=escola_user
DB_PASSWORD=escola123
DB_PORT=5432
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")

def show_docker_commands():
    """Mostra comandos úteis do Docker"""
    print("\n🐳 Comandos Docker úteis:")
    print("   Parar PostgreSQL: docker stop escola-postgres")
    print("   Iniciar PostgreSQL: docker start escola-postgres")
    print("   Ver logs: docker logs escola-postgres")
    print("   Conectar ao banco: docker exec -it escola-postgres psql -U escola_user -d escola_para_todos")
    print("   Parar e remover: docker stop escola-postgres && docker rm escola-postgres")

def main():
    """Função principal"""
    print("🚀 Configurando PostgreSQL com Docker para Aqui se Ensina")
    print("=" * 60)
    
    # Verificar se Docker está instalado
    if not check_docker_installed():
        print("\n❌ Docker não está instalado!")
        print("📋 Para instalar no Windows:")
        print("   1. Baixe Docker Desktop: https://www.docker.com/products/docker-desktop/")
        print("   2. Execute o instalador")
        print("   3. Reinicie o computador")
        print("   4. Execute este script novamente")
        return
    
    # Verificar se Docker está rodando
    if not check_docker_running():
        print("\n❌ Docker não está rodando!")
        print("📋 Inicie o Docker Desktop e tente novamente")
        return
    
    # Iniciar container PostgreSQL
    if not start_postgres_container():
        print("❌ Erro ao iniciar container PostgreSQL")
        return
    
    # Testar conexão
    if not test_connection():
        print("❌ Erro na conexão com PostgreSQL")
        return
    
    # Criar arquivo .env
    create_env_file()
    
    # Mostrar comandos úteis
    show_docker_commands()
    
    print("\n🎉 Configuração concluída!")
    print("📋 Próximos passos:")
    print("   1. Execute: python init_db_postgres.py")
    print("   2. Execute: python app_postgres.py")
    print("\n🌐 Para produção no Render:")
    print("   1. O Render configurará automaticamente")
    print("   2. Não precisa do Docker em produção")

if __name__ == "__main__":
    main()
