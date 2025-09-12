"""
Documentação Swagger/OpenAPI para a API REST
"""
from flask import Blueprint, render_template, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# Configuração do Swagger UI
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

# Blueprint para o Swagger UI
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Aqui se Ensina - API"
    }
)

# Especificação OpenAPI
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "Aqui se Ensina API",
        "description": "API REST para o sistema de educação Aqui se Ensina",
        "version": "1.0.0",
        "contact": {
            "name": "Equipe de Desenvolvimento",
            "email": "dev@escolaparatodos.com"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Servidor de Desenvolvimento"
        }
    ],
    "paths": {
        "/api/turmas": {
            "get": {
                "summary": "Listar todas as turmas",
                "description": "Retorna lista de todas as turmas com estatísticas",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Lista de turmas retornada com sucesso",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Turma"
                                            }
                                        },
                                        "total": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Não autorizado"
                    },
                    "500": {
                        "description": "Erro interno do servidor"
                    }
                }
            },
            "post": {
                "summary": "Criar nova turma",
                "description": "Cria uma nova turma no sistema",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["nome", "serie", "professor_id"],
                                "properties": {
                                    "nome": {
                                        "type": "string",
                                        "description": "Nome da turma"
                                    },
                                    "serie": {
                                        "type": "integer",
                                        "description": "Série/ano da turma"
                                    },
                                    "professor_id": {
                                        "type": "integer",
                                        "description": "ID do professor responsável"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Turma criada com sucesso",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                        "turma_id": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Dados inválidos"
                    },
                    "401": {
                        "description": "Não autorizado"
                    },
                    "403": {
                        "description": "Acesso negado - requer admin"
                    }
                }
            }
        },
        "/api/turmas/{turma_id}": {
            "parameters": [
                {
                    "name": "turma_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "ID da turma"
                }
            ],
            "get": {
                "summary": "Obter turma por ID",
                "description": "Retorna detalhes de uma turma específica",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Detalhes da turma",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {"$ref": "#/components/schemas/TurmaDetalhada"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Turma não encontrada"
                    }
                }
            },
            "put": {
                "summary": "Atualizar turma",
                "description": "Atualiza dados de uma turma existente",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "nome": {"type": "string"},
                                    "serie": {"type": "integer"},
                                    "professor_id": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Turma atualizada com sucesso"
                    },
                    "404": {
                        "description": "Turma não encontrada"
                    }
                }
            },
            "delete": {
                "summary": "Remover turma",
                "description": "Remove uma turma (soft delete)",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Turma removida com sucesso"
                    },
                    "404": {
                        "description": "Turma não encontrada"
                    }
                }
            }
        },
        "/api/turmas/{turma_id}/alunos": {
            "parameters": [
                {
                    "name": "turma_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "ID da turma"
                }
            ],
            "get": {
                "summary": "Listar alunos da turma",
                "description": "Retorna lista de todos os alunos de uma turma",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Lista de alunos",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Aluno"}
                                        },
                                        "total": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/turmas/{turma_id}/progresso": {
            "parameters": [
                {
                    "name": "turma_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "ID da turma"
                }
            ],
            "get": {
                "summary": "Estatísticas de progresso",
                "description": "Retorna estatísticas de progresso de uma turma",
                "tags": ["Turmas"],
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Estatísticas de progresso",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {"$ref": "#/components/schemas/ProgressoTurma"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "Turma": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nome": {"type": "string"},
                    "serie": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "professor": {"type": "string"},
                    "total_alunos": {"type": "integer"},
                    "total_aulas": {"type": "integer"},
                    "media_progresso": {"type": "number"}
                }
            },
            "TurmaDetalhada": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nome": {"type": "string"},
                    "serie": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "professor_id": {"type": "integer"},
                    "professor_nome": {"type": "string"},
                    "professor_email": {"type": "string"}
                }
            },
            "Aluno": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "nome": {"type": "string"},
                    "email": {"type": "string"},
                    "status": {"type": "string"},
                    "inscricao_data": {"type": "string", "format": "date-time"}
                }
            },
            "ProgressoTurma": {
                "type": "object",
                "properties": {
                    "turma_id": {"type": "integer"},
                    "turma_nome": {"type": "string"},
                    "media_geral": {"type": "number"},
                    "alunos_com_progresso": {"type": "integer"},
                    "total_exercicios": {"type": "integer"},
                    "ultima_atividade": {"type": "string", "format": "date-time"},
                    "data_calculo": {"type": "string", "format": "date-time"}
                }
            }
        }
    },
    "tags": [
        {
            "name": "Turmas",
            "description": "Operações relacionadas às turmas"
        }
    ]
}


def get_swagger_spec():
    """
    Retorna a especificação OpenAPI
    
    Returns:
        dict: Especificação OpenAPI completa
    """
    return openapi_spec


def create_swagger_blueprint():
    """
    Cria e retorna o blueprint do Swagger
    
    Returns:
        Blueprint: Blueprint configurado do Swagger
    """
    return swagger_ui_blueprint
