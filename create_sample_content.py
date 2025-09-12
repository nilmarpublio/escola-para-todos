#!/usr/bin/env python3
"""
Script para criar conteúdo de exemplo no banco de dados
"""

import psycopg
from psycopg.rows import dict_row
from datetime import datetime
import json

def create_sample_content():
    """Criar conteúdo de exemplo no banco"""
    
    try:
        # Conectar ao banco
        db = psycopg.connect(
            host='localhost',
            dbname='escola_para_todos',
            user='postgres',
            password='postgres',
            row_factory=dict_row
        )
        
        print("🎬 Criando conteúdo de exemplo...")
        
        cur = db.cursor()
        
        # 1. Criar turmas de exemplo
        print("\n1️⃣ Criando turmas...")
        cur.execute('''
            INSERT INTO turmas (nome, descricao, professor_id, max_alunos, is_active, created_at)
            VALUES 
            ('Matemática Básica', 'Fundamentos da matemática para iniciantes', 2, 30, true, NOW()),
            ('Português Infantil', 'Alfabetização e linguagem para crianças', 2, 25, true, NOW()),
            ('Ciências Divertidas', 'Explorando o mundo das ciências', 2, 28, true, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        ''')
        
        turma_ids = [row['id'] for row in cur.fetchall()]
        print(f"   Turmas criadas com IDs: {turma_ids}")
        
        # 2. Criar aulas com conteúdo
        print("2️⃣ Criando aulas...")
        cur.execute('''
            INSERT INTO aulas (titulo, descricao, conteudo, turma_id, professor_id, ordem, is_active, created_at)
            VALUES 
            (%s, 'Aprenda a contar de 1 a 10 de forma divertida!', 'Nesta aula você vai aprender a contar de 1 a 10 através de músicas e brincadeiras. Vamos usar objetos do dia a dia para praticar!', %s, 2, 1, true, NOW()),
            (%s, 'Conheça as vogais através de músicas e histórias', 'Vamos descobrir as vogais de forma divertida! Cada vogal tem sua música especial e vamos praticar com palavras simples.', %s, 2, 1, true, NOW()),
            (%s, 'Descubra os animais e seus sons', 'Nesta aula vamos conhecer os animais da fazenda: vaca, galinha, porco, cavalo e muito mais! Cada animal tem seu som característico.', %s, 2, 1, true, NOW()),
            (%s, 'Aprenda a somar números pequenos', 'Vamos aprender a somar números de 1 a 10 usando objetos visuais e exercícios práticos.', %s, 2, 2, true, NOW()),
            (%s, 'Vermelho, azul e amarelo - as cores básicas', 'Descubra as cores primárias e como elas se misturam para formar outras cores! Vamos pintar e brincar muito!', %s, 2, 2, true, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        ''', 
        ('Contando até 10', turma_ids[0],
         'Vogais A, E, I, O, U', turma_ids[1],
         'Animais da Fazenda', turma_ids[2],
         'Soma Simples', turma_ids[0],
         'Cores Primárias', turma_ids[1]))
        
        aula_ids = [row['id'] for row in cur.fetchall()]
        print(f"   Aulas criadas com IDs: {aula_ids}")
        
        # 3. Criar exercícios
        print("3️⃣ Criando exercícios...")
        
        # Exercício 1: Contando até 10
        opcoes1 = {
            "A": "3 dedos",
            "B": "5 dedos", 
            "C": "7 dedos",
            "D": "10 dedos"
        }
        
        # Exercício 2: Vogais
        opcoes2 = {
            "A": "3 vogais",
            "B": "5 vogais",
            "C": "7 vogais", 
            "D": "26 vogais"
        }
        
        # Exercício 3: Animais
        opcoes3 = {
            "A": "Cachorro",
            "B": "Gato", 
            "C": "Vaca",
            "D": "Galinha"
        }
        
        cur.execute('''
            INSERT INTO exercicios (titulo, pergunta, opcoes, resposta_correta, tipo, aula_id, pontos, is_active, created_at)
            VALUES 
            (%s, 'Quantos dedos você tem em uma mão?', %s, 'B', 'multipla_escolha', %s, 10, true, NOW()),
            (%s, 'Quantas vogais existem no alfabeto?', %s, 'B', 'multipla_escolha', %s, 15, true, NOW()),
            (%s, 'Qual animal faz "muuu"?', %s, 'C', 'multipla_escolha', %s, 10, true, NOW()),
            (%s, 'Quanto é 2 + 3?', '{"A": "4", "B": "5", "C": "6", "D": "7"}', 'B', 'multipla_escolha', %s, 10, true, NOW()),
            (%s, 'Qual cor é a mistura de azul e amarelo?', '{"A": "Vermelho", "B": "Verde", "C": "Roxo", "D": "Laranja"}', 'B', 'multipla_escolha', %s, 15, true, NOW())
            ON CONFLICT DO NOTHING
        ''', 
        ('Contando Dedos', json.dumps(opcoes1), aula_ids[0],
         'Vogais do Alfabeto', json.dumps(opcoes2), aula_ids[1],
         'Sons dos Animais', json.dumps(opcoes3), aula_ids[2],
         'Soma Simples', aula_ids[3],
         'Cores Primárias', aula_ids[4]))
        
        # 4. Matricular alunos nas turmas
        print("4️⃣ Matriculando alunos...")
        cur.execute('''
            INSERT INTO matriculas (aluno_id, turma_id, data_matricula, status)
            VALUES 
            (3, %s, NOW(), 'ativa'),
            (3, %s, NOW(), 'ativa'),
            (3, %s, NOW(), 'ativa')
            ON CONFLICT DO NOTHING
        ''', (turma_ids[0], turma_ids[1], turma_ids[2]))
        
        # 5. Criar progresso inicial
        print("5️⃣ Criando progresso inicial...")
        cur.execute('''
            INSERT INTO progresso_alunos (aluno_id, aula_id, status, data_inicio, created_at)
            VALUES 
            (3, %s, 'iniciada', NOW(), NOW()),
            (3, %s, 'em_progresso', NOW(), NOW()),
            (3, %s, 'concluida', NOW(), NOW())
            ON CONFLICT DO NOTHING
        ''', (aula_ids[0], aula_ids[1], aula_ids[2]))
        
        db.commit()
        cur.close()
        db.close()
        
        print("✅ Conteúdo de exemplo criado com sucesso!")
        print("🎬 Aulas com vídeos criadas")
        print("📝 Exercícios interativos adicionados")
        print("👥 Alunos matriculados")
        print("📊 Progresso inicial configurado")
        
    except Exception as e:
        print(f"❌ Erro ao criar conteúdo: {e}")

if __name__ == '__main__':
    create_sample_content()
