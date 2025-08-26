import sqlite3

print("INICIANDO TESTE...")

try:
    db = sqlite3.connect('escola_para_todos.db')
    cursor = db.cursor()
    
    print("1. Testando niveis_aluno...")
    cursor.execute("SELECT * FROM niveis_aluno LIMIT 1")
    nivel = cursor.fetchone()
    print(f"Resultado: {nivel}")
    print(f"Tipo: {type(nivel)}")
    
    print("2. Testando metas_semanais...")
    cursor.execute("SELECT * FROM metas_semanais LIMIT 1")
    meta = cursor.fetchone()
    print(f"Resultado: {meta}")
    print(f"Tipo: {type(meta)}")
    
    cursor.close()
    db.close()
    print("TESTE CONCLUIDO!")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
