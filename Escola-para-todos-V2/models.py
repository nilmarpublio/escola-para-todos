from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

class User(UserMixin):
    """Modelo de usuário com Flask-Login"""
    
    def __init__(self, id, username, email, first_name, last_name, user_type, is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.user_type = user_type
        self._is_active = is_active  # Usar atributo privado
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
            FROM users WHERE id = ?
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
            FROM users WHERE username = ?
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
            FROM users WHERE email = ?
        ''', (email,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def authenticate(username, password, db):
        """Autentica usuário com username e senha"""
        cur = db.cursor()
        cur.execute('''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at, password_hash
            FROM users WHERE username = ? AND is_active = 1
        ''', (username,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data and check_password_hash(user_data[9], password):
            # Remove password_hash dos dados do usuário
            return User(*user_data[:9])
        return None
    
    @staticmethod
    def create_user(username, email, password, first_name, last_name, user_type, db):
        """Cria um novo usuário"""
        try:
            password_hash = generate_password_hash(password)
            cur = db.cursor()
            cur.execute('''
                INSERT INTO users (username, email, password_hash, first_name, last_name, user_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, first_name, last_name, user_type))
            
            user_id = cur.lastrowid
            db.commit()
            cur.close()
            
            return User.get_by_id(user_id, db)
        except Exception as e:
            db.rollback()
            raise e
    
    def update_profile(self, first_name, last_name, email, db):
        """Atualiza perfil do usuário"""
        try:
            cur = db.cursor()
            cur.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (first_name, last_name, email, self.id))
            
            db.commit()
            cur.close()
            
            # Atualiza o objeto local
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.updated_at = datetime.now()
            
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def change_password(self, new_password, db):
        """Altera a senha do usuário"""
        try:
            password_hash = generate_password_hash(new_password)
            cur = db.cursor()
            cur.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (password_hash, self.id))
            
            db.commit()
            cur.close()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def deactivate(self, db):
        """Desativa o usuário"""
        try:
            cur = db.cursor()
            cur.execute('''
                UPDATE users 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (self.id,))
            
            db.commit()
            cur.close()
            
            self._is_active = False  # Usar atributo privado
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def activate(self, db):
        """Ativa o usuário"""
        try:
            cur = db.cursor()
            cur.execute('''
                UPDATE users 
                SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (self.id,))
            
            db.commit()
            cur.close()
            
            self._is_active = True  # Usar atributo privado
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_all_users(db, user_type=None, is_active=None):
        """Lista todos os usuários com filtros opcionais"""
        query = '''
            SELECT id, username, email, first_name, last_name, user_type, is_active, created_at, updated_at
            FROM users
        '''
        params = []
        
        if user_type or is_active is not None:
            query += ' WHERE'
            if user_type:
                query += ' user_type = ?'
                params.append(user_type)
            if is_active is not None:
                if user_type:
                    query += ' AND'
                query += ' is_active = ?'
                params.append(1 if is_active else 0)
        
        query += ' ORDER BY created_at DESC'
        
        cur = db.cursor()
        cur.execute(query, params)
        users_data = cur.fetchall()
        cur.close()
        
        return [User(*user_data) for user_data in users_data]
    
    def to_dict(self):
        """Converte usuário para dicionário (sem dados sensíveis)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'full_name': self.full_name,
            'permissions': self.get_required_permissions()
        }
    
    def __repr__(self):
        return f'<User {self.username}:{self.user_type}>'
