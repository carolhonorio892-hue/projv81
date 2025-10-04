#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - AI Verification Service
Serviço integrado de verificação AI - Etapa 2.5 do fluxo principal
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .external_review_agent import ExternalReviewAgent
from .realtime_logger import realtime_logger, log_info, log_success, log_error

logger = logging.getLogger(__name__)

class AIVerificationService:
    """Serviço de verificação AI integrado ao fluxo principal"""

    def __init__(self):
        """Inicializa o serviço de verificação AI"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Inicializar o agente de revisão externa
        self.review_agent = ExternalReviewAgent()
        
        # Estatísticas da sessão
        self.session_stats = {
            'items_processed': 0,
            'items_approved': 0,
            'items_rejected': 0,
            'start_time': datetime.now(),
            'processing_times': []
        }
        
        log_info("✅ AI Verification Service inicializado")

    def process_session_data(self, session_id: str, data_to_verify: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados de uma sessão através da verificação AI
        
        Args:
            session_id (str): ID da sessão
            data_to_verify (Dict[str, Any]): Dados para verificação
            
        Returns:
            Dict[str, Any]: Resultado da verificação
        """
        start_time = datetime.now()
        
        try:
            log_info(f"🔍 Iniciando verificação AI para sessão: {session_id}")
            
            # Preparar dados para análise
            items_to_analyze = self._prepare_data_for_analysis(data_to_verify)
            
            if not items_to_analyze:
                log_error("❌ Nenhum item válido encontrado para análise")
                return self._create_empty_result(session_id)
            
            log_info(f"📊 Analisando {len(items_to_analyze)} itens")
            
            # Processar cada item
            verification_results = []
            for i, item in enumerate(items_to_analyze):
                log_info(f"🔍 Processando item {i+1}/{len(items_to_analyze)}")
                
                # Processar item através do agente de revisão
                result = self.review_agent.process_item(item, data_to_verify)
                verification_results.append(result)
                
                # Atualizar estatísticas
                status = result.get('ai_review', {}).get('status', 'error')
                if status == 'approved':
                    self.session_stats['items_approved'] += 1
                elif status == 'rejected':
                    self.session_stats['items_rejected'] += 1
                
                self.session_stats['items_processed'] += 1
            
            # Compilar resultado final
            final_result = self._compile_verification_result(
                session_id, verification_results, start_time
            )
            
            # Salvar resultado
            self._save_verification_result(session_id, final_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            log_success(f"✅ Verificação AI concluída em {processing_time:.2f}s")
            
            return final_result
            
        except Exception as e:
            log_error(f"❌ Erro na verificação AI: {str(e)}")
            return self._create_error_result(session_id, str(e))

    def _prepare_data_for_analysis(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara dados para análise"""
        items = []
        
        # Extrair de analysis_results (formato padrão)
        if 'analysis_results' in data:
            analysis_data = data['analysis_results']
            if isinstance(analysis_data, list):
                for i, item in enumerate(analysis_data):
                    if isinstance(item, dict) and item:
                        items.append({
                            'id': f'analysis_{i}',
                            'source': 'analysis_results',
                            'type': 'analysis_item',
                            'content': item.get('content', str(item)),
                            'title': item.get('title', f'Item {i+1}'),
                            'original_data': item
                        })
        
        # Extrair itens de diferentes fontes de dados
        if 'content_analysis' in data:
            content_data = data['content_analysis']
            if isinstance(content_data, dict):
                for key, value in content_data.items():
                    if isinstance(value, (str, dict)) and value:
                        items.append({
                            'id': f'content_{key}',
                            'source': 'content_analysis',
                            'type': key,
                            'content': str(value) if isinstance(value, str) else json.dumps(value),
                            'original_data': value
                        })
        
        # Extrair de análises de concorrência
        if 'competitor_analysis' in data:
            comp_data = data['competitor_analysis']
            if isinstance(comp_data, dict):
                for comp_name, comp_info in comp_data.items():
                    if isinstance(comp_info, dict) and comp_info:
                        items.append({
                            'id': f'competitor_{comp_name}',
                            'source': 'competitor_analysis',
                            'type': 'competitor_data',
                            'content': json.dumps(comp_info),
                            'title': comp_name,
                            'original_data': comp_info
                        })
        
        # Extrair de insights de mercado
        if 'market_insights' in data:
            insights = data['market_insights']
            if isinstance(insights, (list, dict)):
                if isinstance(insights, list):
                    for i, insight in enumerate(insights):
                        items.append({
                            'id': f'insight_{i}',
                            'source': 'market_insights',
                            'type': 'market_insight',
                            'content': str(insight),
                            'original_data': insight
                        })
                else:
                    for key, value in insights.items():
                        items.append({
                            'id': f'insight_{key}',
                            'source': 'market_insights',
                            'type': key,
                            'content': str(value),
                            'original_data': value
                        })
        
        # Extrair de dados de pesquisa web
        if 'web_research' in data:
            web_data = data['web_research']
            if isinstance(web_data, dict):
                for source, content in web_data.items():
                    if content:
                        items.append({
                            'id': f'web_{source}',
                            'source': 'web_research',
                            'type': 'web_content',
                            'content': str(content),
                            'title': source,
                            'original_data': content
                        })
        
        return items

    def _compile_verification_result(self, session_id: str, results: List[Dict[str, Any]], start_time: datetime) -> Dict[str, Any]:
        """Compila resultado final da verificação"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calcular estatísticas
        total_items = len(results)
        approved_items = sum(1 for r in results if r.get('ai_review', {}).get('status') == 'approved')
        rejected_items = sum(1 for r in results if r.get('ai_review', {}).get('status') == 'rejected')
        error_items = sum(1 for r in results if r.get('ai_review', {}).get('status') == 'error')
        
        # Calcular confiança média
        confidences = [r.get('ai_review', {}).get('final_confidence', 0.0) for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Identificar principais problemas
        main_issues = self._identify_main_issues(results)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(results)
        
        return {
            'session_id': session_id,
            'verification_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': processing_time,
            'statistics': {
                'total_items_analyzed': total_items,
                'items_approved': approved_items,
                'items_rejected': rejected_items,
                'items_with_errors': error_items,
                'approval_rate': (approved_items / total_items * 100) if total_items > 0 else 0,
                'average_confidence': avg_confidence
            },
            'main_issues': main_issues,
            'recommendations': recommendations,
            'detailed_results': results,
            'overall_status': 'approved' if approved_items > rejected_items else 'rejected',
            'quality_score': avg_confidence * 100,
            'verification_summary': {
                'high_confidence_items': sum(1 for r in results if r.get('ai_review', {}).get('final_confidence', 0) > 0.8),
                'medium_confidence_items': sum(1 for r in results if 0.5 <= r.get('ai_review', {}).get('final_confidence', 0) <= 0.8),
                'low_confidence_items': sum(1 for r in results if r.get('ai_review', {}).get('final_confidence', 0) < 0.5)
            }
        }

    def _identify_main_issues(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica principais problemas encontrados"""
        issues = []
        
        for result in results:
            ai_review = result.get('ai_review', {})
            if ai_review.get('status') == 'rejected':
                issues.append({
                    'item_id': result.get('item_id'),
                    'issue_type': 'rejection',
                    'reason': ai_review.get('reason', 'Motivo não especificado'),
                    'confidence': ai_review.get('final_confidence', 0.0)
                })
            
            # Verificar problemas de viés
            bias_analysis = result.get('bias_disinformation_analysis', {})
            if bias_analysis.get('overall_risk', 0) > 0.6:
                issues.append({
                    'item_id': result.get('item_id'),
                    'issue_type': 'high_bias_risk',
                    'reason': f"Alto risco de viés detectado: {bias_analysis.get('overall_risk', 0):.2f}",
                    'details': bias_analysis.get('detected_bias_keywords', [])
                })
        
        return issues[:10]  # Limitar a 10 principais problemas

    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Analisar padrões nos resultados
        rejected_count = sum(1 for r in results if r.get('ai_review', {}).get('status') == 'rejected')
        total_count = len(results)
        
        if rejected_count > total_count * 0.5:
            recommendations.append("⚠️ Alta taxa de rejeição detectada. Revisar qualidade dos dados coletados.")
        
        # Verificar problemas de sentimento
        negative_sentiment_count = sum(1 for r in results 
                                     if r.get('sentiment_analysis', {}).get('classification') == 'negative')
        
        if negative_sentiment_count > total_count * 0.3:
            recommendations.append("📊 Alto volume de conteúdo com sentimento negativo. Considerar ajustar estratégia de coleta.")
        
        # Verificar problemas de viés
        high_bias_count = sum(1 for r in results 
                            if r.get('bias_disinformation_analysis', {}).get('overall_risk', 0) > 0.6)
        
        if high_bias_count > 0:
            recommendations.append(f"🎯 {high_bias_count} itens com alto risco de viés detectados. Revisar fontes de dados.")
        
        # Recomendações de confiança
        low_confidence_count = sum(1 for r in results 
                                 if r.get('ai_review', {}).get('final_confidence', 0) < 0.5)
        
        if low_confidence_count > total_count * 0.3:
            recommendations.append("🔍 Muitos itens com baixa confiança. Considerar coleta de dados adicionais.")
        
        if not recommendations:
            recommendations.append("✅ Dados aprovados na verificação AI. Qualidade adequada para prosseguir.")
        
        return recommendations

    def _save_verification_result(self, session_id: str, result: Dict[str, Any]):
        """Salva resultado da verificação"""
        try:
            # Definir caminho de salvamento
            base_dir = Path(os.path.dirname(__file__)).parent.parent / "analyses_data"
            session_dir = base_dir / session_id / "modules"
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar resultado completo
            result_file = session_dir / "ai_verification.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Salvar resumo executivo
            summary = {
                'module': 'ai_verification',
                'title': 'Verificação AI - Etapa 2.5',
                'timestamp': result['verification_timestamp'],
                'status': result['overall_status'],
                'quality_score': result['quality_score'],
                'statistics': result['statistics'],
                'main_issues': result['main_issues'][:3],  # Top 3 issues
                'recommendations': result['recommendations'][:3]  # Top 3 recommendations
            }
            
            summary_file = session_dir / "ai_verification_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            log_success(f"💾 Resultado da verificação AI salvo: {result_file}")
            
        except Exception as e:
            log_error(f"❌ Erro ao salvar resultado da verificação: {str(e)}")

    def _create_empty_result(self, session_id: str) -> Dict[str, Any]:
        """Cria resultado vazio quando não há dados para analisar"""
        return {
            'session_id': session_id,
            'verification_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': 0.0,
            'statistics': {
                'total_items_analyzed': 0,
                'items_approved': 0,
                'items_rejected': 0,
                'items_with_errors': 0,
                'approval_rate': 0,
                'average_confidence': 0.0
            },
            'main_issues': [],
            'recommendations': ['⚠️ Nenhum dado encontrado para verificação. Execute as etapas anteriores primeiro.'],
            'detailed_results': [],
            'overall_status': 'no_data',
            'quality_score': 0.0,
            'verification_summary': {
                'high_confidence_items': 0,
                'medium_confidence_items': 0,
                'low_confidence_items': 0
            }
        }

    def _create_error_result(self, session_id: str, error_message: str) -> Dict[str, Any]:
        """Cria resultado de erro"""
        return {
            'session_id': session_id,
            'verification_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': 0.0,
            'error': error_message,
            'statistics': {
                'total_items_analyzed': 0,
                'items_approved': 0,
                'items_rejected': 0,
                'items_with_errors': 1,
                'approval_rate': 0,
                'average_confidence': 0.0
            },
            'main_issues': [{'issue_type': 'system_error', 'reason': error_message}],
            'recommendations': ['❌ Erro no sistema de verificação. Contate o suporte técnico.'],
            'detailed_results': [],
            'overall_status': 'error',
            'quality_score': 0.0,
            'verification_summary': {
                'high_confidence_items': 0,
                'medium_confidence_items': 0,
                'low_confidence_items': 0
            }
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão atual"""
        return self.session_stats.copy()

# Instância global do serviço
ai_verification_service = AIVerificationService()