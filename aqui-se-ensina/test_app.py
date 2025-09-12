#!/usr/bin/env python3
"""
Script de teste para verificar se a aplicação Flask pura está funcionando
"""

import requests
import time
import sys

def test_app():
    """Testar se a aplicação está rodando"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testando aplicação Flask Pura...")
    print("=" * 50)
    
    try:
        # Testar página inicial
        print("1. Testando página inicial...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Página inicial carregada com sucesso")
        else:
            print(f"   ❌ Erro na página inicial: {response.status_code}")
            return False
        
        # Testar página de login
        print("2. Testando página de login...")
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            print("   ✅ Página de login carregada com sucesso")
        else:
            print(f"   ❌ Erro na página de login: {response.status_code}")
            return False
        
        # Testar página de registro
        print("3. Testando página de registro...")
        response = requests.get(f"{base_url}/auth/register")
        if response.status_code == 200:
            print("   ✅ Página de registro carregada com sucesso")
        else:
            print(f"   ❌ Erro na página de registro: {response.status_code}")
            return False
        
        # Testar dashboard (deve redirecionar para login)
        print("4. Testando acesso ao dashboard...")
        response = requests.get(f"{base_url}/dashboard", allow_redirects=False)
        if response.status_code in [302, 401]:
            print("   ✅ Dashboard protegido corretamente (redirecionamento para login)")
        else:
            print(f"   ❌ Dashboard não está protegido: {response.status_code}")
            return False
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        print("✅ A aplicação Flask Pura está funcionando perfeitamente!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: A aplicação não está rodando")
        print("   Execute 'python app.py' primeiro")
        return False
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes da aplicação...")
    
    # Aguardar um pouco para a aplicação inicializar
    print("⏳ Aguardando aplicação inicializar...")
    time.sleep(2)
    
    success = test_app()
    
    if success:
        print("\n🎯 Aplicação pronta para uso!")
        print("📝 Próximos passos:")
        print("   1. Acesse http://localhost:5000")
        print("   2. Crie uma conta ou faça login")
        print("   3. Explore as funcionalidades")
    else:
        print("\n❌ Alguns testes falharam")
        print("📝 Verifique:")
        print("   1. Se a aplicação está rodando (python app.py)")
        print("   2. Se o banco foi inicializado (python init_db.py)")
        print("   3. Se as variáveis de ambiente estão configuradas")
        sys.exit(1)

if __name__ == '__main__':
    main()
