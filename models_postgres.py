from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg
from psycopg.rows import dict_row
from datetime import datetime

class User(UserMixin):
    """Modelo de usuário com PostgreSQL"""
    
    def __init__(self, id, username, email, first_name, last_name, user_type, is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.user_type = user_type
        self._is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    @property
    def is_active(self):
        """Status ativo/inativo do usuário"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Setter para is_active"""
        self._is_active = value
    
    @property
    def full_name(self):
        """Nome completo do usuário"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.user_type == 'admin'
    
    @property
    def is_professor(self):
        """Verifica se o usuário é professor"""
        return self.user_type == 'professor'
    
    @property
    def is_aluno(self):
        """Verifica se o usuário é aluno"""
        return self.user_type == 'aluno'
    
    def can_access_admin_panel(self):
        """Verifica se o usuário pode acessar o painel administrativo"""
        return self.is_admin
    
    def can_create_content(self):
        """Verifica se o usuário pode criar conteúdo (aulas, exercícios)"""
        return self.is_admin or self.is_professor
    
    def can_manage_users(self):
        """Verifica se o usuário pode gerenciar outros usuários"""
        return self.is_admin
    
    def can_view_analytics(self):
        """Verifica se o usuário pode visualizar analytics"""
        return self.is_admin or self.is_professor
    
    def get_required_permissions(self):
        """Retorna as permissões necessárias para o usuário"""
        permissions = ['view_content']
        
        if self.is_aluno:
            permissions.extend(['view_own_progress', 'take_exercises'])
        elif self.is_professor:
            permissions.extend(['create_content', 'view_analytics', 'manage_own_content'])
        elif self.is_admin:
            permissions.extend(['create_content', 'view_analytics', 'manage_users', 'manage_all_content', 'system_admin'])
        
        return permissions
    
    @staticmethod
    def get_by_id(user_id, db):
        """Busca usuário por ID"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at
            FROM users WHERE id = %s
        ''', (user_id,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_username(username, db):
        """Busca usuário por username"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at
            FROM users WHERE id = %s
        ''', (username,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_email(email, db):
        """Busca usuário por email"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at
            FROM users WHERE id = %s
        ''', (email,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def authenticate(username, password, db):
        """Autentica usuário"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at, password_hash
            FROM users WHERE username = %s
        ''', (username,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            # Remover password_hash dos dados do usuário
            user_dict = dict(user_data)
            del user_dict['password_hash']
            return User(**user_dict)
        return None
    
    @staticmethod
    def create_user(username, email, password, first_name, last_name, user_type, db):
        """Cria novo usuário"""
        password_hash = generate_password_hash(password)
        now = datetime.utcnow()
        
        cur = db.cursor()
        cur.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, user_type, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, email, password_hash, first_name, last_name, user_type, True, now, now))
        
        user_id = cur.fetchone()['id']
        db.commit()
        cur.close()
        
        return User(user_id, username, email, first_name, last_name, user_type, True, now, now)
    
    @staticmethod
    def get_all_users(db):
        """Busca todos os usuários"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at
            FROM users ORDER BY created_at DESC
        ''')
        users_data = cur.fetchall()
        cur.close()
        
        return [User(*user_data) for user_data in users_data]
    
    def update_profile(self, first_name, last_name, email, db):
        """Atualiza perfil do usuário"""
        cur = db.cursor()
        cur.execute('''
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, updated_at = %s
            WHERE id = %s
        ''', (first_name, last_name, email, datetime.utcnow(), self.id))
        
        db.commit()
        cur.close()
        
        # Atualizar atributos locais
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.updated_at = datetime.utcnow()
    
    def change_password(self, new_password, db):
        """Altera senha do usuário"""
        password_hash = generate_password_hash(new_password)
        
        cur = db.cursor()
        cur.execute('''
            UPDATE users 
            SET password_hash = %s, updated_at = %s
            WHERE id = %s
        ''', (password_hash, datetime.utcnow(), self.id))
        
        db.commit()
        cur.close()
    
    def deactivate(self, db):
        """Desativa usuário"""
        cur = db.cursor()
        cur.execute('''
            UPDATE users 
            SET is_active = %s, updated_at = %s
            WHERE id = %s
        ''', (False, datetime.utcnow(), self.id))
        
        db.commit()
        cur.close()
        
        self._is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self, db):
        """Ativa usuário"""
        cur = db.cursor()
        cur.execute('''
            UPDATE users 
            SET is_active = %s, updated_at = %s
            WHERE id = %s
        ''', (True, datetime.utcnow(), self.id))
        
        db.commit()
        cur.close()
        
        self._is_active = True
        self.updated_at = datetime.utcnow()
