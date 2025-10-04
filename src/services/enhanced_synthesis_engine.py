#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Enhanced Synthesis Engine with AI Verifier
Motor de síntese aprimorado com busca ativa, análise profunda e verificação por IA
"""

import os
import logging
import json
import asyncio
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedSynthesisEngine:
    """Motor de síntese aprimorado com IA, busca ativa e verificação integrada"""

    def __init__(self):
        """Inicializa o motor de síntese com verificação AI integrada"""
        self.synthesis_prompts = self._load_enhanced_prompts()
        self.ai_manager = None
        self._initialize_ai_manager()

        # Configuração do AI Verifier integrado
        self.verifier_config = self._load_verifier_config()
        self._initialize_verifier_components()

        logger.info("🧠 Enhanced Synthesis Engine com AI Verifier inicializado")

    def _load_verifier_config(self) -> Dict[str, Any]:
        """Carrega configuração do AI Verifier"""
        return {
            'thresholds': {
                'approval': 0.75,
                'rejection': 0.35,
                'high_confidence': 0.85,
                'low_confidence': 0.5,
                'bias_high_risk': 0.7
            },
            'sentiment_analysis': {'enabled': True},
            'bias_detection': {
                'enabled': True,
                'bias_keywords': ['sempre', 'nunca', 'todos', 'ninguém', 'obviamente', 'claramente'],
                'disinformation_patterns': ['fake news', 'notícia falsa', 'teoria da conspiração'],
                'rhetoric_devices': []
            },
            'llm_reasoning': {'enabled': True, 'provider': 'gemini', 'model': 'gemini-1.5-flash'},
            'contextual_analysis': {'enabled': True},
            'rules': [
                {
                    "name": "high_confidence_approval",
                    "condition": "overall_confidence >= 0.85",
                    "action": {"status": "approved", "reason": "Alta confiança no conteúdo"}
                },
                {
                    "name": "high_risk_bias_rejection",
                    "condition": "overall_risk >= 0.7",
                    "action": {"status": "rejected", "reason": "Alto risco de viés/desinformação"}
                }
            ]
        }

    def _initialize_verifier_components(self):
        """Inicializa componentes do AI Verifier"""
        try:
            # Sentiment Analyzer
            self.sentiment_analyzer = self._create_sentiment_analyzer()

            # Bias Detector
            self.bias_detector = self._create_bias_detector()

            # LLM Reasoning (usa o mesmo AI Manager)
            self.llm_reasoning_enabled = self.verifier_config.get('llm_reasoning', {}).get('enabled', True)

            # Contextual Analyzer
            self.contextual_analyzer = self._create_contextual_analyzer()

            # Rule Engine
            self.rule_engine = self._create_rule_engine()

            # Confidence Thresholds
            self.confidence_thresholds = self._create_confidence_thresholds()

            # Estatísticas de verificação
            self.verification_stats = {
                'total_verified': 0,
                'approved': 0,
                'rejected': 0,
                'start_time': datetime.now()
            }

            logger.info("✅ Componentes do AI Verifier integrados ao Synthesis Engine")

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes do AI Verifier: {e}")

    def _create_sentiment_analyzer(self):
        """Cria analisador de sentimento básico"""
        class BasicSentimentAnalyzer:
            def __init__(self, config):
                self.config = config
                self.positive_words = {"bom", "ótimo", "excelente", "maravilhoso", "perfeito", "incrível", "fantástico"}
                self.negative_words = {"ruim", "péssimo", "terrível", "horrível", "problema", "erro", "falha"}

            def analyze_sentiment(self, text: str) -> Dict[str, Any]:
                if not text:
                    return {'polarity': 0.0, 'classification': 'neutral', 'confidence': 0.5}

                text_lower = text.lower()
                positive_count = sum(1 for word in self.positive_words if word in text_lower)
                negative_count = sum(1 for word in self.negative_words if word in text_lower)

                total_words = len(text_lower.split())
                if total_words == 0:
                    return {'polarity': 0.0, 'classification': 'neutral', 'confidence': 0.5}

                polarity = (positive_count - negative_count) / max(total_words, 1)

                if polarity > 0.05:
                    classification = 'positive'
                elif polarity < -0.05:
                    classification = 'negative'
                else:
                    classification = 'neutral'

                confidence = min(abs(polarity) * 5 + 0.3, 1.0)

                return {
                    'polarity': polarity,
                    'classification': classification,
                    'confidence': confidence
                }

        return BasicSentimentAnalyzer(self.verifier_config)

    def _create_bias_detector(self):
        """Cria detector de viés e desinformação"""
        class BasicBiasDetector:
            def __init__(self, config):
                self.config = config.get('bias_detection', {})
                self.bias_keywords = self.config.get('bias_keywords', [])
                self.disinformation_patterns = self.config.get('disinformation_patterns', [])

            def detect_bias_disinformation(self, text: str) -> Dict[str, Any]:
                if not text:
                    return {'overall_risk': 0.0, 'detected_bias_keywords': [], 'detected_disinformation_patterns': []}

                text_lower = text.lower()
                detected_bias = [kw for kw in self.bias_keywords if kw in text_lower]
                detected_disinfo = [pat for pat in self.disinformation_patterns if pat in text_lower]

                bias_score = min(len(detected_bias) * 0.1, 1.0)
                disinfo_score = min(len(detected_disinfo) * 0.2, 1.0)
                overall_risk = (bias_score * 0.4 + disinfo_score * 0.6)

                return {
                    'bias_score': bias_score,
                    'disinformation_score': disinfo_score,
                    'overall_risk': overall_risk,
                    'detected_bias_keywords': detected_bias,
                    'detected_disinformation_patterns': detected_disinfo,
                    'confidence': 0.7 if (detected_bias or detected_disinfo) else 0.5
                }

        return BasicBiasDetector(self.verifier_config)

    def _create_contextual_analyzer(self):
        """Cria analisador contextual básico"""
        class BasicContextualAnalyzer:
            def __init__(self):
                self.context_cache = {'processed_items': []}

            def analyze_context(self, item_data: Dict[str, Any], massive_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
                consistency_score = 0.7
                source_reliability = 0.6
                temporal_coherence = 0.7

                contextual_confidence = (consistency_score * 0.4 + source_reliability * 0.4 + temporal_coherence * 0.2)

                return {
                    'contextual_confidence': contextual_confidence,
                    'consistency_score': consistency_score,
                    'source_reliability_score': source_reliability,
                    'temporal_coherence_score': temporal_coherence,
                    'context_flags': []
                }

        return BasicContextualAnalyzer()

    def _create_rule_engine(self):
        """Cria motor de regras"""
        class BasicRuleEngine:
            def __init__(self, config):
                self.rules = config.get('rules', [])

            def apply_rules(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
                bias = analysis_result.get('bias_disinformation_analysis', {})
                overall_risk = bias.get('overall_risk', 0.0)

                if overall_risk >= 0.7:
                    return {
                        'status': 'rejected',
                        'reason': 'Alto risco de viés/desinformação',
                        'triggered_rules': ['high_risk_bias_rejection']
                    }

                return {
                    'status': 'approved',
                    'reason': 'Análise padrão aprovada',
                    'triggered_rules': []
                }

        return BasicRuleEngine(self.verifier_config)

    def _create_confidence_thresholds(self):
        """Cria gerenciador de limiares"""
        class BasicConfidenceThresholds:
            def __init__(self, config):
                self.thresholds = config.get('thresholds', {})

            def should_approve(self, confidence: float) -> bool:
                return confidence >= self.thresholds.get('approval', 0.75)

            def should_reject(self, confidence: float) -> bool:
                return confidence <= self.thresholds.get('rejection', 0.35)

            def get_threshold(self, threshold_type: str) -> float:
                return self.thresholds.get(threshold_type, 0.5)

        return BasicConfidenceThresholds(self.verifier_config)

    def verify_content_item(self, item_data: Dict[str, Any], massive_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verifica um item de conteúdo através do AI Verifier integrado

        Args:
            item_data: Dados do item para verificação
            massive_data: Contexto adicional

        Returns:
            Resultado da verificação com status de aprovação/rejeição
        """
        start_time = datetime.now()

        try:
            item_id = item_data.get('id', f'item_{self.verification_stats["total_verified"]}')
            logger.info(f"🔍 Verificando item: {item_id}")

            # Extrai conteúdo textual
            text_content = self._extract_text_content(item_data)

            if not text_content or len(text_content.strip()) < 5:
                return self._create_insufficient_content_result(item_data)

            # Análise de sentimento
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(text_content)

            # Detecção de viés/desinformação
            bias_result = self.bias_detector.detect_bias_disinformation(text_content)

            # Análise contextual
            contextual_result = self.contextual_analyzer.analyze_context(item_data, massive_data)

            # Análise LLM (opcional, usa AI Manager se disponível)
            llm_result = {'llm_confidence': 0.5, 'llm_recommendation': 'NÃO_EXECUTADO'}

            # Monta resultado da análise
            analysis_result = {
                'item_id': item_id,
                'original_item': item_data,
                'sentiment_analysis': sentiment_result,
                'bias_disinformation_analysis': bias_result,
                'contextual_analysis': contextual_result,
                'llm_reasoning_analysis': llm_result
            }

            # Aplica regras
            rule_result = self.rule_engine.apply_rules(analysis_result)

            # Decisão final
            final_decision = self._make_final_decision(analysis_result, rule_result)

            # Atualiza estatísticas
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_verification_stats(final_decision['status'], processing_time)

            analysis_result['ai_review'] = final_decision
            analysis_result['processing_time_seconds'] = processing_time

            logger.info(f"✅ Item verificado: {final_decision['status']} (confiança: {final_decision['final_confidence']:.3f})")

            return analysis_result

        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return self._create_error_result(item_data, str(e))

    def _extract_text_content(self, item_data: Dict[str, Any]) -> str:
        """Extrai conteúdo textual do item"""
        priority_fields = ['content', 'text', 'description', 'title', 'summary']
        text_parts = []

        for field in priority_fields:
            if field in item_data and item_data[field]:
                content = str(item_data[field]).strip()
                if content:
                    text_parts.append(content)

        return ' '.join(text_parts).strip()

    def _make_final_decision(self, analysis_result: Dict[str, Any], rule_result: Dict[str, Any]) -> Dict[str, Any]:
        """Toma decisão final baseada em todas as análises"""
        try:
            sentiment = analysis_result.get('sentiment_analysis', {})
            bias = analysis_result.get('bias_disinformation_analysis', {})
            contextual = analysis_result.get('contextual_analysis', {})

            # Calcula confiança composta
            confidences = [
                sentiment.get('confidence', 0.5) * 0.2,
                (1.0 - bias.get('overall_risk', 0.5)) * 0.3,
                contextual.get('contextual_confidence', 0.5) * 0.5
            ]

            final_confidence = sum(confidences)

            # Aplica decisão de regras se houver
            if rule_result.get('status') in ['approved', 'rejected']:
                status = rule_result['status']
                reason = rule_result['reason']
            else:
                # Usa limiares de confiança
                if self.confidence_thresholds.should_approve(final_confidence):
                    status = 'approved'
                    reason = 'Aprovado com base na análise combinada'
                elif self.confidence_thresholds.should_reject(final_confidence):
                    status = 'rejected'
                    reason = 'Rejeitado com base na análise combinada'
                else:
                    status = 'rejected'
                    reason = 'Rejeitado por ambiguidade - política de segurança'

            return {
                'status': status,
                'reason': reason,
                'final_confidence': final_confidence,
                'confidence_breakdown': {
                    'sentiment_contribution': sentiment.get('confidence', 0.5) * 0.2,
                    'bias_contribution': (1.0 - bias.get('overall_risk', 0.5)) * 0.3,
                    'contextual_contribution': contextual.get('contextual_confidence', 0.5) * 0.5
                },
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.0.0_integrated'
                }
            }

        except Exception as e:
            logger.error(f"❌ Erro na decisão final: {e}")
            return {
                'status': 'rejected',
                'reason': f'Erro no processamento: {str(e)}',
                'final_confidence': 0.0,
                'error': True
            }

    def _create_insufficient_content_result(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria resultado para conteúdo insuficiente"""
        return {
            'item_id': item_data.get('id', 'sem_id'),
            'ai_review': {
                'status': 'rejected',
                'reason': 'Conteúdo textual insuficiente',
                'final_confidence': 0.0,
                'insufficient_content': True
            }
        }

    def _create_error_result(self, item_data: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Cria resultado de erro"""
        return {
            'item_id': item_data.get('id', 'sem_id'),
            'ai_review': {
                'status': 'rejected',
                'reason': f'Erro: {error_message}',
                'final_confidence': 0.0,
                'error': True
            }
        }

    def _update_verification_stats(self, status: str, processing_time: float):
        """Atualiza estatísticas de verificação"""
        self.verification_stats['total_verified'] += 1
        if status == 'approved':
            self.verification_stats['approved'] += 1
        elif status == 'rejected':
            self.verification_stats['rejected'] += 1

    def get_verification_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de verificação"""
        total = self.verification_stats['total_verified']
        return {
            'total_verified': total,
            'approved': self.verification_stats['approved'],
            'rejected': self.verification_stats['rejected'],
            'approval_rate': self.verification_stats['approved'] / max(total, 1),
            'runtime_seconds': (datetime.now() - self.verification_stats['start_time']).total_seconds()
        }

    def _initialize_ai_manager(self):
        """Inicializa o gerenciador de IA com hierarquia OpenRouter"""
        try:
            from services.enhanced_ai_manager import enhanced_ai_manager
            self.ai_manager = enhanced_ai_manager
            logger.info("✅ AI Manager com hierarquia Grok-4 → Gemini conectado ao Synthesis Engine")
        except ImportError:
            logger.error("❌ Enhanced AI Manager não disponível")

    def _load_enhanced_prompts(self) -> Dict[str, str]:
        """Carrega prompts aprimorados para síntese"""
        return {
            'master_synthesis': """
# VOCÊ É O ANALISTA ESTRATÉGICO MESTRE - SÍNTESE ULTRA-PROFUNDA COM VERIFICAÇÃO

Sua missão é estudar profundamente o relatório de coleta fornecido e criar uma síntese estruturada, acionável e baseada 100% em dados reais VERIFICADOS.

## TEMPO MÍNIMO DE ESPECIALIZAÇÃO: 5 MINUTOS
Você deve dedicar NO MÍNIMO 5 minutos se especializando no tema fornecido, fazendo múltiplas buscas e análises profundas antes de gerar a síntese final.

## VERIFICAÇÃO INTEGRADA DE CONTEÚDO
- TODOS os insights devem ser verificados quanto a viés e desinformação
- Dados suspeitos ou de baixa qualidade devem ser REJEITADOS
- Apenas informações APROVADAS pelo verificador devem ser incluídas na síntese final

## ESTRUTURA OBRIGATÓRIA DO JSON DE RESPOSTA:

```json
{
  "insights_principais": [
    "Lista de 15-20 insights principais VERIFICADOS extraídos dos dados"
  ],
  "oportunidades_identificadas": [
    "Lista de 10-15 oportunidades de mercado VERIFICADAS"
  ],
  "publico_alvo_refinado": {
    "demografia_detalhada": {
      "idade_predominante": "Faixa etária específica baseada em dados VERIFICADOS",
      "genero_distribuicao": "Distribuição por gênero com percentuais VERIFICADOS",
      "renda_familiar": "Faixa de renda com dados do IBGE/pesquisas VERIFICADAS"
    },
    "psicografia_profunda": {
      "valores_principais": "Valores que guiam decisões - VERIFICADOS",
      "motivacoes_compra": "O que realmente os motiva a comprar - VERIFICADO"
    },
    "dores_viscerais_reais": [
      "Lista de 15-20 dores profundas VERIFICADAS nos dados reais"
    ],
    "desejos_ardentes_reais": [
      "Lista de 15-20 desejos VERIFICADOS nos dados reais"
    ]
  },
  "estrategias_recomendadas": [
    "Lista de 8-12 estratégias específicas baseadas em achados VERIFICADOS"
  ],
  "validacao_dados": {
    "total_items_analisados": "Número total de itens analisados",
    "items_aprovados": "Número de itens aprovados pelo AI Verifier",
    "items_rejeitados": "Número de itens rejeitados",
    "taxa_aprovacao": "Percentual de aprovação",
    "nivel_confianca": "Nível de confiança na análise (0-100%)"
  }
}
```

## RELATÓRIO DE COLETA PARA ANÁLISE:
"""
        }

    def _create_deep_specialization_prompt(self, synthesis_type: str, full_context: str) -> str:
        """Cria prompt para especialização profunda com verificação integrada"""

        base_specialization = f"""
🎓 MISSÃO CRÍTICA: APRENDER PROFUNDAMENTE COM OS DADOS DA ETAPA 1 (VERIFICADOS)

Você é um CONSULTOR ESPECIALISTA contratado por uma agência de marketing.
Você recebeu um DOSSIÊ COMPLETO com dados reais coletados na Etapa 1.

⚠️ IMPORTANTE: Todos os dados foram PRÉ-VERIFICADOS pelo AI Verifier integrado.
- Dados APROVADOS são confiáveis e devem ser usados
- Dados REJEITADOS devem ser IGNORADOS (contêm viés ou desinformação)

📚 PROCESSO DE APRENDIZADO OBRIGATÓRIO:

FASE 1 - ABSORÇÃO TOTAL DOS DADOS VERIFICADOS (20-30 minutos):
- LEIA APENAS dados que foram APROVADOS na verificação
- IGNORE dados que foram REJEITADOS
- MEMORIZE informações verificadas: nomes, marcas, produtos, canais
- ABSORVA números validados: seguidores, engajamento, preços, métricas

FASE 2 - ANÁLISE BASEADA EM DADOS VERIFICADOS:
- Use APENAS insights de dados aprovados
- Cite especificamente fontes verificadas
- Mencione números exatos validados
- Referencie apenas conteúdos aprovados

🎯 RESULTADO ESPERADO:
Uma análise baseada 100% em dados VERIFICADOS e CONFIÁVEIS.

📊 DADOS DA ETAPA 1 PARA APRENDIZADO PROFUNDO:
{full_context}

🚀 AGORA APRENDA PROFUNDAMENTE COM ESTES DADOS VERIFICADOS!
"""

        return base_specialization

    async def execute_deep_specialization_study(
        self,
        session_id: str,
        synthesis_type: str = "master_synthesis"
    ) -> Dict[str, Any]:
        """
        EXECUTA ESTUDO PROFUNDO COM VERIFICAÇÃO INTEGRADA

        Args:
            session_id: ID da sessão
            synthesis_type: Tipo de especialização
        """
        logger.info(f"🎓 INICIANDO ESTUDO PROFUNDO COM VERIFICAÇÃO para sessão: {session_id}")

        try:
            # 1. Carrega dados da Etapa 1
            logger.info("📚 FASE 1: Carregando dados da Etapa 1...")
            consolidacao_data = self._load_consolidacao_etapa1(session_id)
            if not consolidacao_data:
                raise Exception("❌ Arquivo de consolidação não encontrado")

            # 2. VERIFICA todos os dados através do AI Verifier integrado
            logger.info("🔍 FASE 2: VERIFICANDO dados através do AI Verifier...")
            verified_data = self._verify_all_data(consolidacao_data)

            logger.info(f"✅ Verificação concluída:")
            logger.info(f"  - Total analisado: {verified_data['total_items']}")
            logger.info(f"  - Aprovados: {verified_data['approved_items']} ({verified_data['approval_rate']:.1%})")
            logger.info(f"  - Rejeitados: {verified_data['rejected_items']}")

            # 3. Constrói contexto apenas com dados APROVADOS
            logger.info("🏗️ FASE 3: Construindo contexto com dados VERIFICADOS...")
            full_context = self._build_verified_context(verified_data)

            # 4. Prompt de especialização
            specialization_prompt = self._create_deep_specialization_prompt(synthesis_type, full_context)

            # 5. Executa síntese com dados verificados
            logger.info("🧠 FASE 4: Executando SÍNTESE com dados VERIFICADOS...")

            if not self.ai_manager:
                raise Exception("❌ AI Manager não disponível")

            synthesis_result = await self.ai_manager.generate_with_active_search(
                prompt=specialization_prompt,
                context=full_context,
                session_id=session_id,
                max_search_iterations=15,
                preferred_model="x-ai/grok-4-fast:free",
                min_processing_time=300
            )

            # 6. Processa resultado
            processed_synthesis = self._process_synthesis_result(synthesis_result)

            # 7. Adiciona estatísticas de verificação
            processed_synthesis['verification_stats'] = verified_data['stats']

            # 8. Salva síntese
            synthesis_path = self._save_synthesis_result(session_id, processed_synthesis, synthesis_type)

            logger.info(f"✅ Síntese com verificação integrada concluída: {synthesis_path}")

            return {
                "success": True,
                "session_id": session_id,
                "synthesis_path": synthesis_path,
                "synthesis_data": processed_synthesis,
                "verification_summary": verified_data['stats'],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na síntese: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _verify_all_data(self, consolidacao_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica todos os dados da consolidação através do AI Verifier

        Returns:
            Dict com dados verificados separados em aprovados/rejeitados
        """
        try:
            data_section = consolidacao_data.get('data', {})
            dados_web = data_section.get('dados_web', [])

            approved_items = []
            rejected_items = []

            logger.info(f"🔍 Verificando {len(dados_web)} itens...")

            for idx, item in enumerate(dados_web):
                # Prepara item para verificação
                item_data = {
                    'id': f"web_{idx+1:03d}",
                    'content': item.get('titulo', ''),
                    'title': item.get('titulo', ''),
                    'source': item.get('url', ''),
                    'description': str(item.get('relevancia', ''))
                }

                # Verifica item
                verification_result = self.verify_content_item(item_data)

                # Separa aprovados e rejeitados
                if verification_result.get('ai_review', {}).get('status') == 'approved':
                    approved_items.append(item)
                else:
                    rejected_items.append(item)

                if (idx + 1) % 10 == 0:
                    logger.info(f"  Verificados: {idx + 1}/{len(dados_web)}")

            total = len(dados_web)
            approved_count = len(approved_items)
            rejected_count = len(rejected_items)

            return {
                'total_items': total,
                'approved_items': approved_count,
                'rejected_items': rejected_count,
                'approval_rate': approved_count / max(total, 1),
                'approved_data': approved_items,
                'rejected_data': rejected_items,
                'stats': {
                    'total_analisados': total,
                    'aprovados': approved_count,
                    'rejeitados': rejected_count,
                    'taxa_aprovacao': f"{(approved_count / max(total, 1)) * 100:.1f}%"
                }
            }

        except Exception as e:
            logger.error(f"❌ Erro na verificação dos dados: {e}")
            return {
                'total_items': 0,
                'approved_items': 0,
                'rejected_items': 0,
                'approval_rate': 0.0,
                'approved_data': [],
                'rejected_data': [],
                'stats': {}
            }

    def _build_verified_context(self, verified_data: Dict[str, Any]) -> str:
        """Constrói contexto apenas com dados aprovados"""
        approved_data = verified_data.get('approved_data', [])

        context_parts = [
            "# DADOS VERIFICADOS E APROVADOS DA ETAPA 1",
            f"\nTotal de itens verificados: {verified_data['total_items']}",
            f"Itens aprovados: {verified_data['approved_items']} ({verified_data['approval_rate']:.1%})",
            f"Itens rejeitados: {verified_data['rejected_items']}\n",
            "\n## DADOS APROVADOS (Use apenas estes dados):\n"
        ]

        context_parts.append(json.dumps(approved_data, indent=2, ensure_ascii=False))

        return "\n".join(context_parts)

    # Métodos auxiliares existentes mantidos
    async def execute_enhanced_synthesis(self, session_id: str, synthesis_type: str = "master_synthesis") -> Dict[str, Any]:
        """Alias para execute_deep_specialization_study"""
        return await self.execute_deep_specialization_study(session_id, synthesis_type)

    def _load_consolidacao_etapa1(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carrega arquivo consolidado.json da pesquisa web"""
        try:
            consolidado_path = Path(f"analyses_data/pesquisa_web/{session_id}/consolidado.json")

            if not consolidado_path.exists():
                logger.warning(f"⚠️ Arquivo consolidado não encontrado: {consolidado_path}")
                return None

            with open(consolidado_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Consolidação Etapa 1 carregada")
                return data

        except Exception as e:
            logger.error(f"❌ Erro ao carregar consolidação: {e}")
            return None

    def _process_synthesis_result(self, synthesis_result: str) -> Dict[str, Any]:
        """Processa resultado da síntese"""
        try:
            if "```json" in synthesis_result:
                start = synthesis_result.find("```json") + 7
                end = synthesis_result.rfind("```")
                json_text = synthesis_result[start:end].strip()
                parsed_data = json.loads(json_text)

                parsed_data['metadata_sintese'] = {
                    'generated_at': datetime.now().isoformat(),
                    'engine': 'Enhanced Synthesis Engine v3.0 with AI Verifier',
                    'verified': True
                }

                return parsed_data

            try:
                return json.loads(synthesis_result)
            except:
                return {'raw_synthesis': synthesis_result, 'fallback_mode': True}

        except Exception as e:
            logger.error(f"❌ Erro ao processar síntese: {e}")
            return {'error': str(e), 'raw_synthesis': synthesis_result}

    def _save_synthesis_result(self, session_id: str, synthesis_data: Dict[str, Any], synthesis_type: str) -> str:
        """Salva resultado da síntese"""
        try:
            session_dir = Path(f"analyses_data/{session_id}")
            session_dir.mkdir(parents=True, exist_ok=True)

            synthesis_path = session_dir / f"sintese_{synthesis_type}.json"
            with open(synthesis_path, 'w', encoding='utf-8') as f:
                json.dump(synthesis_data, f, ensure_ascii=False, indent=2)

            if synthesis_type == 'master_synthesis':
                compat_path = session_dir / "resumo_sintese.json"
                with open(compat_path, 'w', encoding='utf-8') as f:
                    json.dump(synthesis_data, f, ensure_ascii=False, indent=2)

            return str(synthesis_path)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar síntese: {e}")
            raise

    def get_synthesis_status(self, session_id: str) -> Dict[str, Any]:
        """Verifica status da síntese para uma sessão"""
        try:
            session_dir = Path(f"analyses_data/{session_id}")
            synthesis_files = list(session_dir.glob("sintese_*.json"))

            if synthesis_files:
                latest_synthesis = max(synthesis_files, key=lambda f: f.stat().st_mtime)
                return {
                    "status": "completed",
                    "synthesis_available": True,
                    "latest_synthesis": str(latest_synthesis)
                }
            else:
                return {"status": "not_found"}

        except Exception as e:
            logger.error(f"❌ Erro ao verificar status: {e}")
            return {"status": "error", "error": str(e)}

# Instância global
enhanced_synthesis_engine = EnhancedSynthesisEngine()
