#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar especificamente a função de gamificação
"""

import sqlite3
import sys
import os

# Adicionar o diretório atual ao path para importar o app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gamificacao_function():
    """Testar a função de gamificação diretamente"""
    print("🔍 TESTANDO FUNÇÃO DE GAMIFICAÇÃO")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db = sqlite3.connect('escola_para_todos.db')
        cursor = db.cursor()
        
        # Simular o que a função faz
        print("1. Testando consulta de níveis...")
        cursor.execute("""
            SELECT nivel_atual, pontos_totais, pontos_nivel_atual, pontos_proximo_nivel, 
                   titulo_nivel, cor_nivel, icone_nivel
            FROM niveis_aluno 
            WHERE aluno_id = 1
        """)
        nivel_info = cursor.fetchone()
        print(f"   nivel_info: {nivel_info}")
        print(f"   tipo: {type(nivel_info)}")
        
        if nivel_info:
            print(f"   é iterável: {hasattr(nivel_info, '__iter__')}")
            print(f"   tem __len__: {hasattr(nivel_info, '__len__')}")
            if hasattr(nivel_info, '__len__'):
                print(f"   comprimento: {len(nivel_info)}")
        
        print("\n2. Testando consulta de metas...")
        cursor.execute("""
            SELECT m.id, m.nome, m.descricao, m.tipo, m.valor_meta, m.pontos_recompensa, 
                   m.recompensa_virtual, m.data_inicio, m.data_fim,
                   COALESCE(pm.valor_atual, 0) as valor_atual,
                   COALESCE(pm.concluida, 0) as concluida,
                   COALESCE(pm.recompensa_coletada, 0) as recompensa_coletada
            FROM metas_semanais m
            LEFT JOIN progresso_metas pm ON m.id = pm.meta_id AND pm.aluno_id = 1
            WHERE m.ativa = 1 AND m.data_fim >= date('now')
            ORDER BY m.data_fim ASC
        """)
        metas_semanais = cursor.fetchall()
        print(f"   metas_semanais: {metas_semanais}")
        print(f"   tipo: {type(metas_semanais)}")
        print(f"   é iterável: {hasattr(metas_semanais, '__iter__')}")
        
        print("\n3. Testando consulta de conquistas...")
        cursor.execute("""
            SELECT c.nome, c.descricao, c.pontos, c.icone, ac.data_conquista
            FROM aluno_conquista ac
            JOIN conquistas c ON ac.conquista_id = c.id
            WHERE ac.aluno_id = 1
            ORDER BY ac.data_conquista DESC
            LIMIT 5
        """)
        conquistas_recentes = cursor.fetchall()
        print(f"   conquistas_recentes: {conquistas_recentes}")
        print(f"   tipo: {type(conquistas_recentes)}")
        
        print("\n4. Testando consulta de histórico...")
        cursor.execute("""
            SELECT pontos, tipo, descricao, data_ganho
            FROM historico_pontos
            WHERE aluno_id = 1 AND data_ganho >= date('now', 'weekday 0', '-6 days')
            ORDER BY data_ganho DESC
            LIMIT 10
        """)
        historico_semana = cursor.fetchall()
        print(f"   historico_semana: {historico_semana}")
        print(f"   tipo: {type(historico_semana)}")
        
        print("\n5. Testando cálculo de progresso...")
        progresso_nivel = 0
        if nivel_info and isinstance(nivel_info, (list, tuple)) and len(nivel_info) >= 4:
            try:
                pontos_totais = float(nivel_info[2]) if nivel_info[2] is not None else 0
                pontos_proximo = float(nivel_info[3]) if nivel_info[3] is not None else 100
                if pontos_proximo > 0:
                    progresso_nivel = (pontos_totais / pontos_proximo) * 100
                print(f"   progresso_nivel calculado: {progresso_nivel}")
            except (TypeError, ValueError, ZeroDivisionError) as e:
                print(f"   erro ao calcular progresso: {e}")
                progresso_nivel = 0
        else:
            print(f"   nivel_info não é válido para cálculo")
        
        print("\n6. Testando conversão para listas...")
        metas_semanais = metas_semanais if isinstance(metas_semanais, list) else []
        conquistas_recentes = conquistas_recentes if isinstance(conquistas_recentes, list) else []
        historico_semana = historico_semana if isinstance(historico_semana, list) else []
        
        print(f"   metas_semanais final: {type(metas_semanais)}")
        print(f"   conquistas_recentes final: {type(conquistas_recentes)}")
        print(f"   historico_semana final: {type(historico_semana)}")
        
        cursor.close()
        db.close()
        
        print("\n✅ TESTE CONCLUÍDO SEM ERROS!")
        
    except Exception as e:
        print(f"\n❌ ERRO ENCONTRADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gamificacao_function()
