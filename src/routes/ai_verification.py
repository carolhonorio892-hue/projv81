#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - AI Verification Routes
Rotas para verificação AI - Etapa 2.5 do fluxo principal
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from pathlib import Path

from services.ai_verification_service import AIVerificationService

# Instanciar o serviço
ai_verification_service = AIVerificationService()
from services.realtime_logger import realtime_logger, log_info, log_success, log_error
from services.session_persistence import session_persistence

logger = logging.getLogger(__name__)

# Criar blueprint
ai_verification_bp = Blueprint('ai_verification', __name__)

@ai_verification_bp.route('/ai-verification/start', methods=['POST'])
def start_ai_verification():
    """Inicia processo de verificação AI"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID é obrigatório'
            }), 400
        
        log_info(f"🚀 Iniciando verificação AI para sessão: {session_id}")
        
        # Verificar se a sessão existe
        if not session_persistence.session_exists(session_id):
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # Carregar dados da sessão para verificação
        session_data = _load_session_data(session_id)
        
        if not session_data:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado encontrado para verificação. Execute as etapas anteriores primeiro.'
            }), 400
        
        # Processar verificação AI
        verification_result = ai_verification_service.process_session_data(session_id, session_data)
        
        # Atualizar status da sessão
        session_persistence.update_session_status(session_id, 'ai_verification_completed')
        
        log_success(f"✅ Verificação AI concluída para sessão: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'verification_result': verification_result,
            'message': 'Verificação AI concluída com sucesso'
        })
        
    except Exception as e:
        log_error(f"❌ Erro na verificação AI: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@ai_verification_bp.route('/ai-verification/status/<session_id>', methods=['GET'])
def get_verification_status(session_id: str):
    """Obtém status da verificação AI"""
    try:
        # Verificar se existe resultado de verificação
        base_dir = Path(os.path.dirname(__file__)).parent.parent / "analyses_data"
        result_file = base_dir / session_id / "modules" / "ai_verification.json"
        
        if not result_file.exists():
            return jsonify({
                'success': True,
                'status': 'not_started',
                'message': 'Verificação AI não foi executada ainda'
            })
        
        # Carregar resultado
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify({
            'success': True,
            'status': 'completed',
            'verification_result': result,
            'message': 'Verificação AI encontrada'
        })
        
    except Exception as e:
        log_error(f"❌ Erro ao obter status da verificação: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@ai_verification_bp.route('/ai-verification/summary/<session_id>', methods=['GET'])
def get_verification_summary(session_id: str):
    """Obtém resumo da verificação AI"""
    try:
        # Carregar resumo
        base_dir = Path(os.path.dirname(__file__)).parent.parent / "analyses_data"
        summary_file = base_dir / session_id / "modules" / "ai_verification_summary.json"
        
        if not summary_file.exists():
            return jsonify({
                'success': False,
                'error': 'Resumo da verificação não encontrado'
            }), 404
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        log_error(f"❌ Erro ao obter resumo da verificação: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@ai_verification_bp.route('/ai-verification/detailed-results/<session_id>', methods=['GET'])
def get_detailed_results(session_id: str):
    """Obtém resultados detalhados da verificação AI"""
    try:
        # Carregar resultado completo
        base_dir = Path(os.path.dirname(__file__)).parent.parent / "analyses_data"
        result_file = base_dir / session_id / "modules" / "ai_verification.json"
        
        if not result_file.exists():
            return jsonify({
                'success': False,
                'error': 'Resultados detalhados não encontrados'
            }), 404
        
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # Retornar apenas os resultados detalhados (sem dados originais para economizar bandwidth)
        detailed_results = result.get('detailed_results', [])
        
        # Limpar dados originais dos resultados para reduzir tamanho
        cleaned_results = []
        for item in detailed_results:
            cleaned_item = item.copy()
            if 'original_item' in cleaned_item:
                del cleaned_item['original_item']  # Remove dados originais grandes
            cleaned_results.append(cleaned_item)
        
        return jsonify({
            'success': True,
            'detailed_results': cleaned_results,
            'total_items': len(cleaned_results)
        })
        
    except Exception as e:
        log_error(f"❌ Erro ao obter resultados detalhados: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@ai_verification_bp.route('/ai-verification/stats', methods=['GET'])
def get_verification_stats():
    """Obtém estatísticas do serviço de verificação"""
    try:
        stats = ai_verification_service.get_session_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        log_error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

def _load_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    """Carrega dados da sessão para verificação"""
    try:
        # USAR APENAS CAMINHO RELATIVO - sem caminhos absolutos que criam pastas no C:
        
        # Caminho relativo simples: analyses_data/session_id
        base_dir = "analyses_data"
        session_dir = os.path.join(base_dir, session_id)
        
        # Se não existe diretório de análise, criar estrutura básica
        if not os.path.exists(session_dir):
            log_info(f"📁 Criando estrutura de diretórios para sessão: {session_id}")
            os.makedirs(session_dir, exist_ok=True)
            os.makedirs(os.path.join(session_dir, "modules"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "reports"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "raw_data"), exist_ok=True)
            
            # Carregar dados básicos da sessão do session_persistence
            session_data_basic = session_persistence._load_session_data(session_id)
            if session_data_basic:
                # Criar dados básicos para verificação
                basic_data = {
                    'session_info': session_data_basic,
                    'created_at': datetime.now().isoformat(),
                    'status': 'ready_for_verification'
                }
                
                # Salvar dados básicos
                basic_file = os.path.join(session_dir, "modules", "session_basic.json")
                with open(basic_file, 'w', encoding='utf-8') as f:
                    json.dump(basic_data, f, ensure_ascii=False, indent=2)
                
                log_info(f"📊 Estrutura básica criada para verificação da sessão: {session_id}")
            else:
                log_error(f"❌ Dados da sessão não encontrados no session_persistence: {session_id}")
                return None
        
        session_data = {}
        
        # Carregar dados de diferentes fontes
        data_sources = [
            ('modules', 'modules'),
            ('reports', 'reports'),
            ('raw_data', 'raw_data')
        ]
        
        for source_dir, key in data_sources:
            source_path = os.path.join(session_dir, source_dir)
            if os.path.exists(source_path):
                source_data = {}
                
                # Carregar arquivos JSON da fonte
                for json_file in os.listdir(source_path):
                    if json_file.endswith('.json'):
                        json_file_path = os.path.join(source_path, json_file)
                        try:
                            with open(json_file_path, 'r', encoding='utf-8') as f:
                                file_data = json.load(f)
                                file_name = os.path.splitext(json_file)[0]  # Remove .json extension
                                source_data[file_name] = file_data
                        except Exception as e:
                            log_error(f"❌ Erro ao carregar {json_file_path}: {str(e)}")
                            continue
                
                if source_data:
                    session_data[key] = source_data
        
        # Verificar se encontrou dados
        if not session_data:
            log_error(f"❌ Nenhum dado encontrado para sessão: {session_id}")
            return None
        
        log_info(f"📊 Dados carregados para verificação: {list(session_data.keys())}")
        return session_data
        
    except Exception as e:
        log_error(f"❌ Erro ao carregar dados da sessão: {str(e)}")
        return None