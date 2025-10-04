'''
ARQV30 Enhanced v3.0 - Enhanced Module Processor
Processador aprimorado de módulos com IA e integração com Synthesis Engine
IMPLEMENTAÇÃO COMPLETA PARA RELATÓRIOS COERENTES E ESPECIALIZADOS
'''

import os
import logging
import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import do Enhanced AI Manager e Synthesis Engine
from services.enhanced_ai_manager import enhanced_ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

# Configuração do diretório base de forma mais robusta
# Idealmente, isso viria de uma configuração centralizada ou variável de ambiente
BASE_DATA_DIR = Path(os.getenv("ARQV30_DATA_DIR", Path(__file__).parent.parent / "analyses_data"))

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importação segura de módulos aprimorados
try:
    from services.cpl_devastador_protocol import CPLDevastadorProtocol
    from services.avatar_generation_system import AvatarGenerationSystem
    from services.visceral_leads_engineer import VisceralLeadsEngineer
    HAS_ENHANCED_MODULES = True
    logger.info("Módulos aprimorados (CPL, Avatar, Visceral) carregados com sucesso.")
except ImportError as e:
    logger.warning(f"Um ou mais módulos aprimorados não foram encontrados. O sistema operará em modo padrão. Detalhe: {e}")
    CPLDevastadorProtocol = None
    AvatarGenerationSystem = None
    VisceralLeadsEngineer = None
    HAS_ENHANCED_MODULES = False

logger.info("🚀 ARQV30 Enhanced v3.0 - Processador de Módulos Iniciado")

class EnhancedModuleProcessor:
    '''
    Processador aprimorado de módulos com foco em resultados precisos e coerentes
    INTEGRAÇÃO COMPLETA COM SYNTHESIS ENGINE PARA RELATÓRIOS ESPECIALIZADOS
    '''

    def __init__(self):
        '''Inicializa o processador com integração ao Synthesis Engine'''
        self.ai_manager = enhanced_ai_manager
        self.modules_config = self._get_consolidated_modules_config()
        
        # Integração com Synthesis Engine
        self.synthesis_integration = True
        self.content_quality_threshold = 0.8
        self.coherence_validation = True
        
        # Métricas de qualidade dos módulos
        self.module_quality_metrics = {
            'total_generated': 0,
            'high_quality_modules': 0,
            'coherence_score': 0.0,
            'synthesis_alignment': 0.0
        }
        
        logger.info("🚀 Enhanced Module Processor ULTRA-ROBUSTO inicializado")
        logger.info(f"📊 {len(self.modules_config)} módulos especializados configurados")
        logger.info("🔗 Integração com Synthesis Engine ativada")
        logger.info("✅ Validação de coerência habilitada")

    def _get_consolidated_modules_config(self) -> Dict[str, Any]:
        '''Retorna a configuração consolidada e sem duplicatas dos módulos.'''
        # Módulos foram revisados para eliminar redundâncias e melhorar a clareza.
        return {
            'sintese_master': {
                'title': 'Síntese Master do Projeto',
                'description': 'Visão geral consolidada do projeto, unificando os principais pontos do briefing e contexto estratégico.',
                'use_active_search': False,
                'type': 'core'
            },
            'avatares': {
                'title': 'Avatares Detalhados do Público-Alvo',
                'description': 'Criação de personas detalhadas do público-alvo, incluindo dores, desejos, demografia e comportamento.',
                'use_active_search': False,
                'type': 'core'
            },
            'analise_competitiva': {
                'title': 'Análise Competitiva Aprofundada',
                'description': 'Mapeamento e análise completa dos principais concorrentes diretos e indiretos.',
                'use_active_search': True,
                'type': 'research'
            },
            'insights_mercado': {
                'title': 'Insights Estratégicos de Mercado',
                'description': 'Análise de tendências, oportunidades, riscos e dinâmica do mercado para informar a estratégia.',
                'use_active_search': True,
                'type': 'research'
            },
            'posicionamento': {
                'title': 'Estratégia de Posicionamento e Diferenciação',
                'description': 'Definição do posicionamento único da marca/produto no mercado e seus principais diferenciais.',
                'use_active_search': False,
                'type': 'strategy'
            },
            'drivers_mentais': {
                'title': 'Drivers Mentais e Gatilhos Psicológicos',
                'description': 'Identificação dos principais gatilhos psicológicos e drivers de compra do público-alvo.',
                'use_active_search': False,
                'type': 'strategy'
            },
            'estrategia_conteudo': {
                'title': 'Estratégia de Marketing de Conteúdo',
                'description': 'Planejamento de conteúdo para atrair, engajar e converter o público-alvo em diferentes etapas do funil.',
                'use_active_search': True,
                'type': 'strategy'
            },
            'funil_vendas': {
                'title': 'Estrutura do Funil de Vendas',
                'description': 'Desenho da jornada do cliente e da estrutura completa do funil de vendas, da atração à conversão.',
                'use_active_search': False,
                'type': 'strategy'
            },
            'canais_aquisicao': {
                'title': 'Mapeamento de Canais de Aquisição',
                'description': 'Identificação e priorização dos canais de aquisição de clientes mais eficazes para o negócio.',
                'use_active_search': False,
                'type': 'strategy'
            },
            'estrategia_preco': {
                'title': 'Estratégia de Precificação e Monetização',
                'description': 'Definição de modelos de preço, propostas de valor e estratégias de monetização.',
                'use_active_search': False,
                'type': 'strategy'
            },
            'copy_devastadora': {
                'title': 'Diretrizes de Copywriting de Alta Conversão',
                'description': 'Criação de diretrizes e exemplos de copywriting com foco em persuasão e conversão.',
                'use_active_search': False,
                'type': 'execution'
            },
            'provas_visuais': {
                'title': 'Sistema de Provas Visuais e Sociais',
                'description': 'Estratégia para coletar e apresentar provas sociais e visuais para construir credibilidade.',
                'use_active_search': False,
                'type': 'execution'
            },
            'anti_objecao': {
                'title': 'Sistema Anti-Objeção',
                'description': 'Mapeamento de possíveis objeções e desenvolvimento de argumentos para neutralizá-las.',
                'use_active_search': False,
                'type': 'execution'
            },
            'plano_acao': {
                'title': 'Plano de Ação Executável',
                'description': 'Criação de um plano de ação detalhado com fases, tarefas e cronograma para implementação.',
                'use_active_search': False,
                'type': 'execution'
            },
            'metricas_kpis': {
                'title': 'Definição de Métricas e KPIs',
                'description': 'Seleção dos principais indicadores de desempenho (KPIs) para monitorar o sucesso do projeto.',
                'use_active_search': False,
                'type': 'execution'
            },
            'cronograma_lancamento': {
                'title': 'Cronograma Detalhado de Lançamento',
                'description': 'Elaboração de um cronograma detalhado para as fases de um lançamento de produto/serviço.',
                'use_active_search': False,
                'type': 'execution'
            },
            'cpl_completo': {
                'title': 'Protocolo Integrado de CPLs Devastadores',
                'description': 'Protocolo completo para criação de uma sequência de 4 CPLs (Conteúdo Pré-Lançamento) de alta performance.',
                'use_active_search': True,
                'type': 'specialized',
                'requires': ['sintese_master', 'avatares', 'posicionamento', 'insights_mercado']
            },
            'ai_verification': {
                'title': 'Verificação por IA - Etapa de Qualidade',
                'description': 'Verificação automática de qualidade, consistência e confiabilidade dos dados gerados.',
                'use_active_search': False,
                'type': 'verification'
            }
        }

    async def generate_modules_with_synthesis_integration(self, session_id: str, synthesis_data: Dict[str, Any] = None) -> Dict[str, Any]:
        '''
        Gera módulos com integração completa ao Synthesis Engine
        MÉTODO PRINCIPAL PARA GERAÇÃO DE RELATÓRIOS COERENTES
        '''
        logger.info(f"🧠 Iniciando geração de módulos com integração Synthesis Engine: {session_id}")
        
        try:
            # ETAPA 1: Carregar e validar dados base
            base_data = await self._load_and_validate_base_data(session_id, synthesis_data)
            if not base_data:
                return self._create_error_result(session_id, "Falha ao carregar dados base")
            
            # ETAPA 2: Análise de coerência dos dados
            coherence_analysis = await self._analyze_data_coherence(base_data, session_id)
            
            # ETAPA 3: Preparação do contexto especializado
            specialized_context = await self._prepare_specialized_context(base_data, coherence_analysis)
            
            # ETAPA 4: Geração sequencial de módulos com validação
            results = await self._generate_modules_with_validation(session_id, specialized_context)
            
            # ETAPA 5: Validação final de coerência entre módulos
            final_validation = await self._validate_module_coherence(session_id, results)
            
            # ETAPA 6: Aprimoramento baseado na validação
            if final_validation['needs_improvement']:
                results = await self._improve_module_quality(session_id, results, final_validation)
            
            # Atualizar métricas
            self._update_quality_metrics(results, final_validation)
            
            logger.info(f"✅ Geração completa para sessão {session_id}")
            logger.info(f"📊 Qualidade geral: {final_validation.get('overall_quality', 0):.1f}/100")
            
            return {
                **results,
                'synthesis_integration': True,
                'quality_metrics': final_validation,
                'coherence_score': coherence_analysis.get('coherence_score', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com integração Synthesis: {e}")
            salvar_erro("module_generation_synthesis_error", str(e), contexto={'session_id': session_id})
            return self._create_error_result(session_id, str(e))

    async def _load_and_validate_base_data(self, session_id: str, synthesis_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        '''Carrega e valida dados base com integração do Synthesis Engine'''
        try:
            logger.info("📊 Carregando e validando dados base")
            
            # Carregar dados tradicionais
            base_data = self._load_base_data(session_id)
            
            # Integrar dados do Synthesis Engine se disponíveis
            if synthesis_data:
                base_data = self._integrate_synthesis_data(base_data, synthesis_data)
                logger.info("🔗 Dados do Synthesis Engine integrados")
            
            # Validar qualidade dos dados
            validation_result = await self._validate_base_data_quality(base_data)
            
            if validation_result['is_valid']:
                logger.info(f"✅ Dados base validados - Qualidade: {validation_result['quality_score']:.2f}")
                base_data['validation_result'] = validation_result
                return base_data
            else:
                logger.error(f"❌ Dados base inválidos: {validation_result['issues']}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados base: {e}")
            return None

    def _integrate_synthesis_data(self, base_data: Dict[str, Any], synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        '''Integra dados do Synthesis Engine aos dados base'''
        try:
            if not base_data:
                base_data = {}
            
            # Integrar síntese principal
            if 'synthesis' in synthesis_data:
                base_data['synthesis_master'] = synthesis_data['synthesis']
            
            # Integrar métricas de qualidade
            if 'quality_metrics' in synthesis_data:
                base_data['quality_metrics'] = synthesis_data['quality_metrics']
            
            # Integrar query original
            if 'query_original' in synthesis_data:
                base_data['query_original'] = synthesis_data['query_original']
            
            # Marcar como integrado
            base_data['synthesis_integrated'] = True
            base_data['integration_timestamp'] = datetime.now().isoformat()
            
            return base_data
            
        except Exception as e:
            logger.error(f"❌ Erro na integração de dados: {e}")
            return base_data

    async def _validate_base_data_quality(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        '''Valida a qualidade dos dados base'''
        try:
            validation_result = {
                'is_valid': False,
                'quality_score': 0.0,
                'issues': [],
                'strengths': []
            }
            
            # Verificar presença de dados essenciais
            essential_fields = ['contexto_estrategico', 'sintese_master']
            missing_fields = [field for field in essential_fields if field not in base_data]
            
            if missing_fields:
                validation_result['issues'].append(f"Campos essenciais ausentes: {missing_fields}")
            else:
                validation_result['strengths'].append("Todos os campos essenciais presentes")
            
            # Verificar qualidade do contexto estratégico
            if 'contexto_estrategico' in base_data:
                context = base_data['contexto_estrategico']
                if context.get('tema') and context.get('segmento'):
                    validation_result['strengths'].append("Contexto estratégico bem definido")
                else:
                    validation_result['issues'].append("Contexto estratégico incompleto")
            
            # Verificar integração com Synthesis Engine
            if base_data.get('synthesis_integrated'):
                validation_result['strengths'].append("Integração com Synthesis Engine ativa")
            
            # Calcular pontuação de qualidade
            total_checks = len(essential_fields) + 2  # campos essenciais + contexto + synthesis
            passed_checks = len(validation_result['strengths'])
            validation_result['quality_score'] = passed_checks / total_checks
            
            # Determinar se é válido
            validation_result['is_valid'] = validation_result['quality_score'] >= 0.6
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de dados: {e}")
            return {'is_valid': False, 'quality_score': 0.0, 'issues': [str(e)]}

    async def _analyze_data_coherence(self, base_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        '''Analisa a coerência dos dados para geração de módulos'''
        try:
            logger.info("🔍 Analisando coerência dos dados")
            
            coherence_analysis = {
                'coherence_score': 0.0,
                'consistency_issues': [],
                'data_gaps': [],
                'recommendations': []
            }
            
            # Verificar consistência entre contexto e síntese
            context = base_data.get('contexto_estrategico', {})
            synthesis = base_data.get('sintese_master', {})
            
            # Verificar alinhamento de tema/segmento
            context_tema = context.get('tema', '').lower()
            synthesis_insights = str(synthesis.get('insights_principais', [])).lower()
            
            if context_tema and context_tema in synthesis_insights:
                coherence_analysis['coherence_score'] += 0.3
            else:
                coherence_analysis['consistency_issues'].append("Desalinhamento entre tema do contexto e insights")
            
            # Verificar presença de público-alvo
            if synthesis.get('publico_alvo_refinado'):
                coherence_analysis['coherence_score'] += 0.3
            else:
                coherence_analysis['data_gaps'].append("Público-alvo não definido na síntese")
            
            # Verificar oportunidades identificadas
            opportunities = synthesis.get('oportunidades_identificadas', [])
            if len(opportunities) >= 5:
                coherence_analysis['coherence_score'] += 0.4
            else:
                coherence_analysis['data_gaps'].append("Poucas oportunidades identificadas")
            
            # Gerar recomendações
            if coherence_analysis['coherence_score'] < 0.7:
                coherence_analysis['recommendations'].append("Enriquecer dados com busca ativa")
                coherence_analysis['recommendations'].append("Validar alinhamento entre contexto e síntese")
            
            logger.info(f"📊 Coerência dos dados: {coherence_analysis['coherence_score']:.2f}")
            return coherence_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de coerência: {e}")
            return {'coherence_score': 0.0, 'consistency_issues': [str(e)]}

    async def _prepare_specialized_context(self, base_data: Dict[str, Any], coherence_analysis: Dict[str, Any]) -> Dict[str, Any]:
        '''Prepara contexto especializado para geração de módulos'''
        try:
            logger.info("🎯 Preparando contexto especializado")
            
            specialized_context = {
                'base_data': base_data,
                'coherence_analysis': coherence_analysis,
                'module_guidelines': self._get_module_guidelines(),
                'quality_requirements': self._get_quality_requirements(),
                'cross_module_references': {}
            }
            
            # Extrair elementos-chave para referência cruzada
            synthesis = base_data.get('sintese_master', {})
            
            specialized_context['key_insights'] = synthesis.get('insights_principais', [])[:10]
            specialized_context['target_audience'] = synthesis.get('publico_alvo_refinado', {})
            specialized_context['market_opportunities'] = synthesis.get('oportunidades_identificadas', [])[:8]
            specialized_context['query_original'] = base_data.get('query_original', '')
            
            # Preparar diretrizes específicas por tipo de módulo
            specialized_context['module_specific_guidelines'] = {
                'avatar': self._get_avatar_guidelines(specialized_context),
                'competitive': self._get_competitive_guidelines(specialized_context),
                'strategy': self._get_strategy_guidelines(specialized_context),
                'content': self._get_content_guidelines(specialized_context)
            }
            
            logger.info("✅ Contexto especializado preparado")
            return specialized_context
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar contexto: {e}")
            return {'base_data': base_data, 'error': str(e)}

    def _get_module_guidelines(self) -> Dict[str, str]:
        '''Retorna diretrizes gerais para geração de módulos'''
        return {
            'focus_on_query': 'Mantenha foco absoluto na query original',
            'use_real_data': 'Use apenas dados reais extraídos da coleta',
            'be_specific': 'Seja específico e acionável em todas as recomendações',
            'maintain_coherence': 'Mantenha coerência com outros módulos',
            'validate_sources': 'Valide informações com fontes confiáveis'
        }

    def _get_quality_requirements(self) -> Dict[str, Any]:
        '''Retorna requisitos de qualidade para módulos'''
        return {
            'min_content_length': 800,
            'max_generic_content': 0.2,
            'required_specificity': 0.8,
            'coherence_threshold': 0.7,
            'actionability_score': 0.8
        }

    def _get_avatar_guidelines(self, context: Dict[str, Any]) -> str:
        '''Diretrizes específicas para módulos de avatar'''
        target_audience = context.get('target_audience', {})
        return f"""
        DIRETRIZES PARA AVATAR:
        - Base-se nos dados demográficos: {target_audience.get('demografia_detalhada', {})}
        - Use as dores viscerais identificadas: {target_audience.get('dores_viscerais_reais', [])}
        - Incorpore os desejos ardentes: {target_audience.get('desejos_ardentes_reais', [])}
        - Mantenha foco na query original: {context.get('query_original', '')}
        """

    def _get_competitive_guidelines(self, context: Dict[str, Any]) -> str:
        '''Diretrizes específicas para análise competitiva'''
        opportunities = context.get('market_opportunities', [])
        return f"""
        DIRETRIZES PARA ANÁLISE COMPETITIVA:
        - Explore as oportunidades identificadas: {opportunities}
        - Use dados reais de mercado da síntese
        - Identifique gaps competitivos específicos
        - Foque no contexto da query original
        """

    def _get_strategy_guidelines(self, context: Dict[str, Any]) -> str:
        '''Diretrizes específicas para estratégias'''
        insights = context.get('key_insights', [])
        return f"""
        DIRETRIZES PARA ESTRATÉGIAS:
        - Base estratégias nos insights principais: {insights}
        - Seja específico e acionável
        - Inclua métricas mensuráveis
        - Mantenha alinhamento com a query original
        """

    def _get_content_guidelines(self, context: Dict[str, Any]) -> str:
        '''Diretrizes específicas para conteúdo'''
        return f"""
        DIRETRIZES PARA CONTEÚDO:
        - Use linguagem do público-alvo identificado
        - Incorpore insights comportamentais da síntese
        - Seja específico ao contexto da query
        - Inclua exemplos práticos e acionáveis
        """

    def _create_error_result(self, session_id: str, error_message: str) -> Dict[str, Any]:
        '''Cria resultado de erro padronizado'''
        return {
            "session_id": session_id,
            "error": error_message,
            "successful_modules": 0,
            "failed_modules": len(self.modules_config),
            "modules_generated": [],
            "modules_failed": list(self.modules_config.keys()),
            "total_modules": len(self.modules_config),
            "synthesis_integration": False
        }

    async def generate_all_modules(self, session_id: str) -> Dict[str, Any]:
        '''Gera todos os módulos configurados de forma sequencial e robusta.'''
        logger.info(f"🚀 Iniciando geração de todos os módulos para a sessão: {session_id}")

        base_data = self._load_base_data(session_id)
        if not base_data:
            logger.error(f"Não foi possível carregar os dados base para a sessão {session_id}. Abortando a geração de módulos.")
            return {
                "session_id": session_id,
                "error": "Falha ao carregar dados base.",
                "successful_modules": 0,
                "failed_modules": len(self.modules_config),
                "modules_generated": [],
                "modules_failed": list(self.modules_config.keys()),
                "total_modules": len(self.modules_config)
            }

        results = {
            "session_id": session_id,
            "successful_modules": 0,
            "failed_modules": 0,
            "modules_generated": [],
            "modules_failed": [],
            "total_modules": len(self.modules_config)
        }

        modules_dir = BASE_DATA_DIR / session_id / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)

        for module_name, config in self.modules_config.items():
            try:
                logger.info(f"📝 Gerando módulo: {config['title']} ({module_name})")
                
                # Passa os dados já gerados como contexto para os módulos seguintes
                context_from_previous_modules = self._get_context_from_generated_modules(results['modules_generated'], modules_dir)

                if module_name == 'cpl_completo' and CPLDevastadorProtocol:
                    module_content = await self._generate_cpl_module(base_data, session_id)
                else:
                    module_content = await self._generate_standard_module(module_name, config, base_data, context_from_previous_modules, session_id)

                if module_content:
                    file_extension = "json" if module_name == 'cpl_completo' else "md"
                    module_path = modules_dir / f"{module_name}.{file_extension}"
                    with open(module_path, 'w', encoding='utf-8') as f:
                        if file_extension == "json":
                            json.dump(module_content, f, indent=4, ensure_ascii=False)
                        else:
                            f.write(module_content)
                    
                    results["successful_modules"] += 1
                    results["modules_generated"].append(module_name)
                    logger.info(f"✅ Módulo {module_name} gerado com sucesso.")
                    salvar_etapa(f"geracao_modulo_{module_name}", {"status": "sucesso", "path": str(module_path)})
                else:
                    raise ValueError("Conteúdo do módulo retornado como vazio.")

            except Exception as e:
                logger.error(f"❌ Erro ao gerar módulo {module_name}: {e}", exc_info=True)
                salvar_erro(f"geracao_modulo_{module_name}", str(e), contexto={"session_id": session_id})
                results["failed_modules"] += 1
                results["modules_failed"].append({"module": module_name, "error": str(e)})

        await self._generate_consolidated_report(session_id, results)
        logger.info(f"🏁 Processo finalizado para a sessão {session_id}. Sucesso: {results['successful_modules']}, Falhas: {results['failed_modules']}.")
        return results

    async def _generate_cpl_module(self, base_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        '''Gera o conteúdo para o módulo especializado CPL.'''
        if not CPLDevastadorProtocol:
            logger.warning("Protocolo CPL não disponível, usando conteúdo de fallback.")
            return {
                'titulo': 'Protocolo de CPLs Devastadores (Fallback)',
                'descricao': 'O módulo especializado para CPL não pôde ser carregado. Este é um conteúdo substituto.',
                'status': 'fallback'
            }

        cpl_protocol = CPLDevastadorProtocol()
        contexto = base_data.get('contexto_estrategico', {})
        
        return await cpl_protocol.executar_protocolo_completo(
            tema=contexto.get('tema', 'Não especificado'),
            segmento=contexto.get('segmento', 'Não especificado'),
            publico_alvo=contexto.get('publico_alvo', 'Não especificado'),
            session_id=session_id
        )

    async def _generate_standard_module(self, module_name: str, config: Dict[str, Any], base_data: Dict[str, Any], context_from_previous: str, session_id: str) -> str:
        '''Gera o conteúdo para um módulo padrão.'''
        prompt = self._get_module_prompt(module_name, config, base_data, context_from_previous)
        
        if config.get('use_active_search', False):
            # O contexto para a busca ativa deve ser conciso
            search_context = f"Projeto: {base_data.get('contexto_estrategico', {}).get('tema', '')}. Mercado: {base_data.get('contexto_estrategico', {}).get('segmento', '')}."
            content = await self.ai_manager.generate_with_active_search(
                prompt=prompt,
                context=search_context,
                session_id=session_id
            )
        else:
            content = await self.ai_manager.generate_text(prompt=prompt)

        if self._is_ai_refusal(content) or not content or len(content.strip()) < 150:
            logger.warning(f"⚠️ Conteúdo da IA insuficiente ou recusado para {module_name}. Gerando fallback robusto.")
            content = self._generate_fallback_content(module_name, config, base_data)
        
        return content

    def _load_base_data(self, session_id: str) -> Dict[str, Any]:
        '''Carrega os dados base da sessão (sintese_master, contexto_estrategico, etc.).'''
        try:
            sintese_master_path = BASE_DATA_DIR / session_id / "sintese_master.json"
            contexto_path = BASE_DATA_DIR / session_id / "contexto_estrategico.json"

            base_data = {}
            if sintese_master_path.exists():
                with open(sintese_master_path, 'r', encoding='utf-8') as f:
                    base_data['sintese_master'] = json.load(f)
            
            if contexto_path.exists():
                with open(contexto_path, 'r', encoding='utf-8') as f:
                    base_data['contexto_estrategico'] = json.load(f)

            if not base_data:
                logger.warning(f"Nenhum dado base (sintese_master, contexto_estrategico) encontrado para a sessão {session_id}.")
                return None

            logger.info(f"Dados base carregados para a sessão {session_id}.")
            return base_data
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados base para sessão {session_id}: {e}", exc_info=True)
            return None

    def _get_context_from_generated_modules(self, generated_modules: List[str], modules_dir: Path) -> str:
        '''Constrói um contexto com base nos resumos dos módulos já gerados.'''
        context = "\n\n---\nCONTEXTO DOS MÓDULOS ANTERIORES:\n"
        for module_name in generated_modules:
            try:
                module_file = modules_dir / f"{module_name}.md"
                if module_file.exists():
                    with open(module_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extrai o resumo executivo ou as primeiras linhas
                        summary = self._extract_summary(content)
                        context += f"\n### Resumo do Módulo: {self.modules_config[module_name]['title']}\n{summary}\n"
            except Exception as e:
                logger.warning(f"Não foi possível ler o módulo anterior {module_name} para gerar contexto: {e}")
        return context

    def _extract_summary(self, content: str) -> str:
        '''Extrai um resumo de um conteúdo de módulo.'''
        # Tenta encontrar um "Resumo Executivo"
        try:
            parts = content.split("## Resumo Executivo")
            if len(parts) > 1:
                summary_part = parts[1].split("## ")[0]
                return "\n".join(summary_part.strip().split('\n')[:5]) # Limita a 5 linhas
        except Exception:
            pass # Ignora erros e usa o método fallback
        
        # Se não encontrar, retorna as primeiras 7 linhas do arquivo
        return "\n".join(content.strip().split('\n')[:7])

    def _get_module_prompt(self, module_name: str, config: Dict[str, Any], base_data: Dict[str, Any], context_from_previous: str) -> str:
        '''Cria um prompt detalhado e focado para a IA, evitando alucinações.'''
        contexto_estrategico = base_data.get('contexto_estrategico', {})
        tema = contexto_estrategico.get('tema', 'o projeto')
        segmento = contexto_estrategico.get('segmento', 'o mercado')
        publico_alvo = contexto_estrategico.get('publico_alvo', 'o público-alvo')

        prompt = f'''
# INSTRUÇÃO PARA IA - ESPECIALISTA EM ESTRATÉGIA DE NEGÓCIOS

**TAREFA:** Gerar o conteúdo para o módulo "{config['title']}".

**OBJETIVO DO MÓDULO:** {config['description']}

**CONTEXTO DO PROJETO:**
- **Projeto/Produto:** {tema}
- **Mercado/Nicho:** {segmento}
- **Público-Alvo Principal:** {publico_alvo}
- **Contexto Estratégico Adicional:** {json.dumps(contexto_estrategico, ensure_ascii=False, indent=2)}

{context_from_previous}

**REGRAS DE GERAÇÃO:**
1.  **FOCO ABSOLUTO:** Mantenha-se estritamente no objetivo deste módulo. Não desvie para outros tópicos.
2.  **ESTRUTURA:** Organize o conteúdo de forma clara e lógica, usando Markdown. Comece com um `## Resumo Executivo` e depois desenvolva as seções principais.
3.  **PROFUNDIDADE E APLICABILIDADE:** Forneça análises aprofundadas, insights práticos e recomendações acionáveis. Evite generalidades.
4.  **LINGUAGEM:** Use uma linguagem profissional, direta e estratégica.
5.  **NÃO ALUCINE:** Se alguma informação crucial não estiver disponível no contexto fornecido, indique a necessidade de obter essa informação em vez de inventar dados.

**COMECE A GERAR O CONTEÚDO ABAIXO:**

# {config['title']}

## Resumo Executivo

'''
        return prompt

    def _is_ai_refusal(self, content: str) -> bool:
        '''Verifica se a resposta da IA é uma recusa em gerar o conteúdo.'''
        if not content or len(content.strip()) < 50:
            return True
        
        refusal_patterns = [
            "não posso criar", "não consigo gerar", "devo recusar", "não sou capaz de", "não posso fornecer", "não posso ajudar com",
            "i'm sorry, but i must decline", "i cannot provide", "i'm unable to", "i can't help with", "i must decline",
            "i cannot assist", "i'm not able to", "i cannot create", "i'm sorry, i cannot", "i cannot generate"
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in refusal_patterns)

    def _generate_fallback_content(self, module_name: str, config: Dict[str, Any], base_data: Dict[str, Any]) -> str:
        '''Gera conteúdo de fallback robusto quando a IA falha.'''
        context_data = base_data.get('contexto_estrategico', {})
        tema = context_data.get('tema', 'Produto/Serviço')
        segmento = context_data.get('segmento', 'Mercado')
        
        return f'''# {config['title']} (Conteúdo de Fallback)

## Aviso: Falha na Geração por IA

O conteúdo a seguir é um modelo genérico gerado como fallback, pois o sistema de IA não conseguiu produzir uma análise detalhada para este módulo. Recomenda-se uma análise manual ou uma nova tentativa de geração.

## Resumo Executivo

Este módulo deveria apresentar estratégias detalhadas para {config['description'].lower()} no segmento de {segmento}. Devido a uma falha na geração, apresentamos uma estrutura padrão que deve ser preenchida manualmente.

## Estrutura para Análise Manual

### 1. Contexto e Objetivos
- **Segmento de Mercado:** {segmento}
- **Produto/Serviço Foco:** {tema}
- **Objetivo Principal deste Módulo:** Descreva aqui o que se espera alcançar com a análise de '{config['title']}'.

### 2. Pontos-Chave de Análise
- **Ponto 1:** Descreva o primeiro aspecto a ser analisado.
- **Ponto 2:** Descreva o segundo aspecto a ser analisado.
- **Ponto 3:** Descreva o terceiro aspecto a ser analisado.

### 3. Estratégias Recomendadas
- **Estratégia A:** Baseado na análise, qual a primeira recomendação?
- **Estratégia B:** Qual a segunda recomendação?

### 4. Plano de Implementação Sugerido
- **Fase 1 (Planejamento):** O que precisa ser feito para preparar a implementação?
- **Fase 2 (Execução):** Quais são os passos práticos para executar as estratégias?
- **Fase 3 (Otimização):** Como os resultados serão medidos e o processo otimizado?

### 5. Métricas de Sucesso (KPIs)
- **KPI Primário:** Qual é o indicador mais importante de sucesso?
- **KPI Secundário:** Que outros indicadores devem ser monitorados?

---
*Gerado pelo ARQV30 Enhanced v3.0 - Módulo de Fallback Robusto*
'''

    async def _generate_consolidated_report(self, session_id: str, results: Dict[str, Any]) -> None:
        '''Gera um relatório consolidado final com os resumos dos módulos gerados.'''
        try:
            logger.info("📋 Gerando relatório consolidado final...")
            modules_dir = BASE_DATA_DIR / session_id / "modules"
            
            consolidated_content = f'''# RELATÓRIO FINAL CONSOLIDADO - ARQV30 Enhanced v3.0

**Sessão:** {session_id}  
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Módulos Gerados:** {results['successful_modules']}/{results['total_modules']}  
**Taxa de Sucesso:** {(results['successful_modules']/results['total_modules']*100):.1f}%

---

## SUMÁRIO EXECUTIVO

Este relatório consolida os {results['successful_modules']} módulos de análise estratégica gerados para a sessão. Cada seção abaixo apresenta o resumo executivo do módulo correspondente.

---

'''

            for module_name in results['modules_generated']:
                config = self.modules_config.get(module_name, {'title': module_name.replace("_", " ").title()})
                file_extension = "json" if module_name == 'cpl_completo' else "md"
                module_file = modules_dir / f"{module_name}.{file_extension}"

                consolidated_content += f"## MÓDULO: {config['title']}\n\n"

                if module_file.exists():
                    try:
                        with open(module_file, 'r', encoding='utf-8') as f:
                            if file_extension == "json":
                                cpl_data = json.load(f)
                                summary = cpl_data.get('descricao', 'Descrição não disponível.')
                            else:
                                content = f.read()
                                summary = self._extract_summary(content)
                        consolidated_content += f"{summary}\n\n"
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao carregar conteúdo do módulo {module_name} para relatório: {e}")
                        consolidated_content += "*Conteúdo indisponível devido a um erro de leitura.*\n\n"
                else:
                    consolidated_content += "*Arquivo do módulo não encontrado.*\n\n"
                consolidated_content += "---\n\n"

            if results['modules_failed']:
                consolidated_content += "\n## MÓDULOS COM FALHA NA GERAÇÃO\n\n"
                for failed in results['modules_failed']:
                    config = self.modules_config.get(failed['module'], {'title': failed['module'].replace("_", " ").title()})
                    consolidated_content += f"- **{config['title']}**: {failed['error']}\n"

            consolidated_path = BASE_DATA_DIR / session_id / "relatorio_final_consolidado.md"
            with open(consolidated_path, 'w', encoding='utf-8') as f:
                f.write(consolidated_content)

            logger.info(f"✅ Relatório consolidado salvo em: {consolidated_path}")

        except Exception as e:
            logger.error(f"❌ Erro crítico ao gerar o relatório consolidado: {e}", exc_info=True)
            salvar_erro("geracao_relatorio_consolidado", str(e), contexto={"session_id": session_id})

    # ========================================================================
    # MÉTODOS DE EXPERTISE NO SYNTHESIS ENGINE - IMPLEMENTAÇÃO ROBUSTA
    # ========================================================================

    def _update_quality_metrics(self, results: Dict[str, Any], validation: Dict[str, Any]):
        """Atualiza métricas de qualidade dos módulos"""
        try:
            self.module_quality_metrics['total_generated'] = len(results.get('modules', {}))
            
            # Contar módulos de alta qualidade
            high_quality_count = 0
            for module_data in results.get('modules', {}).values():
                if isinstance(module_data, dict) and module_data.get('quality_score', 0) > 0.8:
                    high_quality_count += 1
            
            self.module_quality_metrics['high_quality_modules'] = high_quality_count
            self.module_quality_metrics['coherence_score'] = validation.get('coherence_score', 0.0)
            self.module_quality_metrics['synthesis_alignment'] = validation.get('synthesis_alignment', 0.0)
            
            logger.info(f"📊 Métricas atualizadas: {high_quality_count}/{self.module_quality_metrics['total_generated']} módulos de alta qualidade")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas: {e}")

    async def analyze_synthesis_content_deeply(self, synthesis_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        ANÁLISE PROFUNDA DO CONTEÚDO DO SYNTHESIS ENGINE
        
        Este método torna o Module Processor um EXPERT no conteúdo gerado pelo Synthesis Engine,
        extraindo insights especializados, padrões semânticos e conhecimento específico do domínio.
        
        Args:
            synthesis_data: Dados completos do Synthesis Engine
            session_id: ID da sessão
            
        Returns:
            Dict com análise profunda e expertise extraída
        """
        logger.info("🧠 INICIANDO ANÁLISE PROFUNDA DO SYNTHESIS ENGINE")
        
        try:
            deep_analysis = {
                'session_id': session_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'synthesis_expertise': {},
                'semantic_patterns': {},
                'domain_knowledge': {},
                'content_insights': {},
                'module_generation_strategy': {},
                'quality_indicators': {}
            }
            
            # 1. EXTRAÇÃO DE EXPERTISE SEMÂNTICA
            logger.info("🔍 Extraindo expertise semântica...")
            deep_analysis['synthesis_expertise'] = await self._extract_synthesis_expertise(synthesis_data)
            
            # 2. ANÁLISE DE PADRÕES SEMÂNTICOS
            logger.info("🧩 Analisando padrões semânticos...")
            deep_analysis['semantic_patterns'] = await self._analyze_semantic_patterns(synthesis_data)
            
            # 3. EXTRAÇÃO DE CONHECIMENTO DO DOMÍNIO
            logger.info("📚 Extraindo conhecimento do domínio...")
            deep_analysis['domain_knowledge'] = await self._extract_domain_knowledge(synthesis_data)
            
            # 4. GERAÇÃO DE INSIGHTS DE CONTEÚDO
            logger.info("💡 Gerando insights de conteúdo...")
            deep_analysis['content_insights'] = await self._generate_content_insights(synthesis_data)
            
            # 5. ESTRATÉGIA DE GERAÇÃO DE MÓDULOS
            logger.info("🎯 Definindo estratégia de geração...")
            deep_analysis['module_generation_strategy'] = await self._define_module_strategy(deep_analysis)
            
            # 6. INDICADORES DE QUALIDADE
            logger.info("📊 Calculando indicadores de qualidade...")
            deep_analysis['quality_indicators'] = await self._calculate_quality_indicators(deep_analysis)
            
            logger.info(f"✅ Análise profunda concluída! Expertise extraída: {len(deep_analysis['synthesis_expertise'])} elementos")
            return deep_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise profunda: {e}")
            return {'error': str(e), 'session_id': session_id}

    async def _extract_synthesis_expertise(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai expertise específica do conteúdo do Synthesis Engine"""
        try:
            expertise = {
                'key_concepts': [],
                'specialized_terms': [],
                'market_insights': [],
                'strategic_points': [],
                'audience_characteristics': [],
                'competitive_intelligence': [],
                'opportunity_areas': []
            }
            
            # Extrair de diferentes seções do synthesis
            synthesis_content = str(synthesis_data)
            
            # 1. Conceitos-chave (usando padrões de texto)
            key_concept_patterns = [
                r'conceito[:\s]+([^.]+)',
                r'principal[:\s]+([^.]+)',
                r'fundamental[:\s]+([^.]+)',
                r'essencial[:\s]+([^.]+)'
            ]
            
            for pattern in key_concept_patterns:
                matches = re.findall(pattern, synthesis_content, re.IGNORECASE)
                expertise['key_concepts'].extend([match.strip() for match in matches])
            
            # 2. Termos especializados (palavras técnicas/específicas do domínio)
            specialized_patterns = [
                r'(?:estratégia|tática|abordagem|metodologia|framework)[:\s]+([^.]+)',
                r'(?:segmento|nicho|mercado|público)[:\s]+([^.]+)',
                r'(?:tendência|oportunidade|insight|análise)[:\s]+([^.]+)'
            ]
            
            for pattern in specialized_patterns:
                matches = re.findall(pattern, synthesis_content, re.IGNORECASE)
                expertise['specialized_terms'].extend([match.strip() for match in matches])
            
            # 3. Insights de mercado
            market_patterns = [
                r'mercado[:\s]+([^.]+)',
                r'indústria[:\s]+([^.]+)',
                r'setor[:\s]+([^.]+)',
                r'economia[:\s]+([^.]+)'
            ]
            
            for pattern in market_patterns:
                matches = re.findall(pattern, synthesis_content, re.IGNORECASE)
                expertise['market_insights'].extend([match.strip() for match in matches])
            
            # 4. Pontos estratégicos
            strategic_patterns = [
                r'estratégia[:\s]+([^.]+)',
                r'objetivo[:\s]+([^.]+)',
                r'meta[:\s]+([^.]+)',
                r'plano[:\s]+([^.]+)'
            ]
            
            for pattern in strategic_patterns:
                matches = re.findall(pattern, synthesis_content, re.IGNORECASE)
                expertise['strategic_points'].extend([match.strip() for match in matches])
            
            # 5. Características do público
            audience_patterns = [
                r'público[:\s]+([^.]+)',
                r'audiência[:\s]+([^.]+)',
                r'consumidor[:\s]+([^.]+)',
                r'cliente[:\s]+([^.]+)'
            ]
            
            for pattern in audience_patterns:
                matches = re.findall(pattern, synthesis_content, re.IGNORECASE)
                expertise['audience_characteristics'].extend([match.strip() for match in matches])
            
            # Limpar e deduplificar
            for key in expertise:
                if isinstance(expertise[key], list):
                    expertise[key] = list(set([item for item in expertise[key] if len(item) > 5]))[:10]  # Top 10
            
            return expertise
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de expertise: {e}")
            return {}

    async def _analyze_semantic_patterns(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa padrões semânticos no conteúdo do Synthesis Engine"""
        try:
            patterns = {
                'content_themes': [],
                'recurring_concepts': {},
                'semantic_clusters': [],
                'content_structure': {},
                'narrative_flow': []
            }
            
            synthesis_text = str(synthesis_data)
            
            # 1. Temas de conteúdo (análise de frequência de palavras)
            words = re.findall(r'\b\w{4,}\b', synthesis_text.lower())
            word_freq = {}
            for word in words:
                if word not in ['para', 'com', 'uma', 'dos', 'das', 'que', 'não', 'mais', 'como', 'por']:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top temas por frequência
            patterns['content_themes'] = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # 2. Conceitos recorrentes
            concept_patterns = [
                'marketing', 'estratégia', 'público', 'mercado', 'produto', 'serviço',
                'cliente', 'consumidor', 'análise', 'oportunidade', 'tendência',
                'segmento', 'nicho', 'competição', 'vantagem', 'posicionamento'
            ]
            
            for concept in concept_patterns:
                count = synthesis_text.lower().count(concept)
                if count > 0:
                    patterns['recurring_concepts'][concept] = count
            
            # 3. Estrutura do conteúdo
            sections = synthesis_text.split('\n\n')
            patterns['content_structure'] = {
                'total_sections': len(sections),
                'avg_section_length': sum(len(s) for s in sections) / len(sections) if sections else 0,
                'section_types': self._classify_sections(sections)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erro na análise semântica: {e}")
            return {}

    async def _extract_domain_knowledge(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai conhecimento específico do domínio"""
        try:
            domain_knowledge = {
                'industry_specifics': [],
                'technical_concepts': [],
                'business_models': [],
                'market_dynamics': [],
                'success_factors': [],
                'risk_factors': [],
                'best_practices': []
            }
            
            synthesis_text = str(synthesis_data)
            
            # 1. Especificidades da indústria
            industry_patterns = [
                r'(?:indústria|setor|mercado)\s+(?:de\s+)?([^.]+?)(?:\s+(?:é|tem|possui|apresenta))',
                r'(?:no\s+)?(?:ramo|segmento|área)\s+(?:de\s+)?([^.]+?)(?:\s+(?:é|tem|possui))'
            ]
            
            for pattern in industry_patterns:
                matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
                domain_knowledge['industry_specifics'].extend([match.strip() for match in matches])
            
            # 2. Conceitos técnicos
            technical_patterns = [
                r'(?:tecnologia|ferramenta|plataforma|sistema)\s+([^.]+)',
                r'(?:método|processo|procedimento|técnica)\s+([^.]+)',
                r'(?:algoritmo|modelo|framework|arquitetura)\s+([^.]+)'
            ]
            
            for pattern in technical_patterns:
                matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
                domain_knowledge['technical_concepts'].extend([match.strip() for match in matches])
            
            # 3. Modelos de negócio
            business_patterns = [
                r'(?:modelo|estratégia|abordagem)\s+(?:de\s+)?(?:negócio|comercial|empresarial)\s+([^.]+)',
                r'(?:receita|monetização|faturamento)\s+([^.]+)',
                r'(?:canal|distribuição|vendas)\s+([^.]+)'
            ]
            
            for pattern in business_patterns:
                matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
                domain_knowledge['business_models'].extend([match.strip() for match in matches])
            
            # 4. Dinâmicas de mercado
            market_patterns = [
                r'(?:tendência|movimento|direção)\s+(?:do\s+)?mercado\s+([^.]+)',
                r'(?:crescimento|expansão|desenvolvimento)\s+([^.]+)',
                r'(?:demanda|procura|interesse)\s+([^.]+)'
            ]
            
            for pattern in market_patterns:
                matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
                domain_knowledge['market_dynamics'].extend([match.strip() for match in matches])
            
            # Limpar e deduplificar
            for key in domain_knowledge:
                if isinstance(domain_knowledge[key], list):
                    domain_knowledge[key] = list(set([item for item in domain_knowledge[key] if len(item) > 3]))[:8]
            
            return domain_knowledge
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de conhecimento: {e}")
            return {}

    async def _generate_content_insights(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera insights específicos do conteúdo para orientar a geração de módulos"""
        try:
            insights = {
                'content_quality_score': 0.0,
                'depth_indicators': {},
                'specialization_level': '',
                'content_gaps': [],
                'enhancement_opportunities': [],
                'module_priorities': [],
                'coherence_factors': {}
            }
            
            synthesis_text = str(synthesis_data)
            
            # 1. Score de qualidade do conteúdo
            quality_factors = {
                'length': min(len(synthesis_text) / 10000, 1.0),  # Normalizado para 10k chars
                'complexity': len(set(synthesis_text.split())) / len(synthesis_text.split()) if synthesis_text.split() else 0,
                'structure': synthesis_text.count('\n') / 100,  # Indicador de estruturação
                'specificity': len(re.findall(r'\d+', synthesis_text)) / 100  # Presença de dados específicos
            }
            
            insights['content_quality_score'] = sum(quality_factors.values()) / len(quality_factors)
            
            # 2. Indicadores de profundidade
            insights['depth_indicators'] = {
                'detailed_analysis': synthesis_text.lower().count('análise') + synthesis_text.lower().count('estudo'),
                'data_references': len(re.findall(r'\d+%|\d+\.\d+%|\d+,\d+%', synthesis_text)),
                'expert_terminology': len(re.findall(r'(?:estratégia|metodologia|framework|abordagem)', synthesis_text, re.IGNORECASE)),
                'case_studies': synthesis_text.lower().count('caso') + synthesis_text.lower().count('exemplo')
            }
            
            # 3. Nível de especialização
            specialization_score = sum(insights['depth_indicators'].values())
            if specialization_score > 50:
                insights['specialization_level'] = 'expert'
            elif specialization_score > 20:
                insights['specialization_level'] = 'advanced'
            elif specialization_score > 10:
                insights['specialization_level'] = 'intermediate'
            else:
                insights['specialization_level'] = 'basic'
            
            # 4. Lacunas de conteúdo (áreas que podem precisar de mais desenvolvimento)
            expected_topics = [
                'público-alvo', 'concorrência', 'mercado', 'estratégia', 'produto',
                'preço', 'distribuição', 'comunicação', 'métricas', 'cronograma'
            ]
            
            for topic in expected_topics:
                if topic.lower() not in synthesis_text.lower():
                    insights['content_gaps'].append(topic)
            
            # 5. Oportunidades de aprimoramento
            if insights['content_quality_score'] < 0.7:
                insights['enhancement_opportunities'].append('Expandir análise com mais detalhes específicos')
            if len(insights['content_gaps']) > 3:
                insights['enhancement_opportunities'].append('Abordar tópicos essenciais ausentes')
            if insights['depth_indicators']['data_references'] < 5:
                insights['enhancement_opportunities'].append('Incluir mais dados quantitativos')
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de insights: {e}")
            return {}

    async def _define_module_strategy(self, deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Define estratégia de geração de módulos baseada na análise profunda"""
        try:
            strategy = {
                'generation_approach': '',
                'priority_modules': [],
                'content_adaptation': {},
                'quality_targets': {},
                'coherence_strategy': {},
                'specialization_focus': []
            }
            
            # 1. Abordagem de geração baseada no nível de especialização
            specialization = deep_analysis.get('content_insights', {}).get('specialization_level', 'basic')
            
            if specialization == 'expert':
                strategy['generation_approach'] = 'deep_specialization'
                strategy['quality_targets']['min_quality_score'] = 0.9
            elif specialization == 'advanced':
                strategy['generation_approach'] = 'enhanced_analysis'
                strategy['quality_targets']['min_quality_score'] = 0.8
            else:
                strategy['generation_approach'] = 'comprehensive_coverage'
                strategy['quality_targets']['min_quality_score'] = 0.7
            
            # 2. Módulos prioritários baseados no conteúdo
            expertise = deep_analysis.get('synthesis_expertise', {})
            
            if expertise.get('market_insights'):
                strategy['priority_modules'].append('insights_mercado')
            if expertise.get('audience_characteristics'):
                strategy['priority_modules'].append('avatares')
            if expertise.get('competitive_intelligence'):
                strategy['priority_modules'].append('analise_competitiva')
            if expertise.get('strategic_points'):
                strategy['priority_modules'].append('estrategia_posicionamento')
            
            # 3. Adaptação de conteúdo
            semantic_patterns = deep_analysis.get('semantic_patterns', {})
            recurring_concepts = semantic_patterns.get('recurring_concepts', {})
            
            strategy['content_adaptation'] = {
                'emphasize_concepts': list(recurring_concepts.keys())[:5],
                'content_style': 'data_driven' if recurring_concepts.get('análise', 0) > 5 else 'strategic',
                'detail_level': 'high' if specialization in ['expert', 'advanced'] else 'medium'
            }
            
            # 4. Estratégia de coerência
            strategy['coherence_strategy'] = {
                'cross_reference_modules': True,
                'maintain_terminology': True,
                'align_recommendations': True,
                'consistent_tone': True
            }
            
            # 5. Foco de especialização
            domain_knowledge = deep_analysis.get('domain_knowledge', {})
            if domain_knowledge.get('industry_specifics'):
                strategy['specialization_focus'].append('industry_expertise')
            if domain_knowledge.get('technical_concepts'):
                strategy['specialization_focus'].append('technical_depth')
            if domain_knowledge.get('business_models'):
                strategy['specialization_focus'].append('business_strategy')
            
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Erro na definição de estratégia: {e}")
            return {}

    async def _calculate_quality_indicators(self, deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula indicadores de qualidade para orientar a geração"""
        try:
            indicators = {
                'content_richness': 0.0,
                'semantic_coherence': 0.0,
                'domain_expertise': 0.0,
                'strategic_alignment': 0.0,
                'overall_readiness': 0.0,
                'recommendations': []
            }
            
            # 1. Riqueza de conteúdo
            content_insights = deep_analysis.get('content_insights', {})
            indicators['content_richness'] = content_insights.get('content_quality_score', 0.0)
            
            # 2. Coerência semântica
            semantic_patterns = deep_analysis.get('semantic_patterns', {})
            recurring_concepts = semantic_patterns.get('recurring_concepts', {})
            if recurring_concepts:
                # Mais conceitos recorrentes = maior coerência
                indicators['semantic_coherence'] = min(len(recurring_concepts) / 10, 1.0)
            
            # 3. Expertise do domínio
            domain_knowledge = deep_analysis.get('domain_knowledge', {})
            domain_elements = sum(len(v) if isinstance(v, list) else 0 for v in domain_knowledge.values())
            indicators['domain_expertise'] = min(domain_elements / 20, 1.0)
            
            # 4. Alinhamento estratégico
            synthesis_expertise = deep_analysis.get('synthesis_expertise', {})
            strategic_elements = len(synthesis_expertise.get('strategic_points', []))
            indicators['strategic_alignment'] = min(strategic_elements / 5, 1.0)
            
            # 5. Prontidão geral
            indicators['overall_readiness'] = (
                indicators['content_richness'] * 0.3 +
                indicators['semantic_coherence'] * 0.25 +
                indicators['domain_expertise'] * 0.25 +
                indicators['strategic_alignment'] * 0.2
            )
            
            # 6. Recomendações baseadas nos indicadores
            if indicators['content_richness'] < 0.6:
                indicators['recommendations'].append('Enriquecer conteúdo com mais detalhes específicos')
            if indicators['semantic_coherence'] < 0.5:
                indicators['recommendations'].append('Melhorar consistência terminológica')
            if indicators['domain_expertise'] < 0.6:
                indicators['recommendations'].append('Aprofundar conhecimento específico do domínio')
            if indicators['strategic_alignment'] < 0.7:
                indicators['recommendations'].append('Fortalecer elementos estratégicos')
            
            if indicators['overall_readiness'] > 0.8:
                indicators['recommendations'].append('✅ Conteúdo pronto para geração de módulos de alta qualidade')
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de indicadores: {e}")
            return {}

    def _classify_sections(self, sections: List[str]) -> Dict[str, int]:
        """Classifica seções do conteúdo por tipo"""
        try:
            section_types = {
                'analytical': 0,
                'strategic': 0,
                'descriptive': 0,
                'data_driven': 0,
                'recommendations': 0
            }
            
            for section in sections:
                section_lower = section.lower()
                
                if any(word in section_lower for word in ['análise', 'estudo', 'pesquisa', 'investigação']):
                    section_types['analytical'] += 1
                elif any(word in section_lower for word in ['estratégia', 'plano', 'objetivo', 'meta']):
                    section_types['strategic'] += 1
                elif any(word in section_lower for word in ['recomendação', 'sugestão', 'proposta', 'ação']):
                    section_types['recommendations'] += 1
                elif re.search(r'\d+%|\d+\.\d+|\d+,\d+', section):
                    section_types['data_driven'] += 1
                else:
                    section_types['descriptive'] += 1
            
            return section_types
            
        except Exception as e:
            logger.error(f"❌ Erro na classificação de seções: {e}")
            return {}

    async def generate_expert_modules_from_synthesis(self, session_id: str, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        GERAÇÃO DE MÓDULOS EXPERT BASEADA NA ANÁLISE PROFUNDA DO SYNTHESIS ENGINE
        
        Este é o método PRINCIPAL que utiliza toda a expertise extraída do Synthesis Engine
        para gerar módulos altamente coerentes e especializados.
        """
        logger.info("🎓 INICIANDO GERAÇÃO EXPERT DE MÓDULOS COM BASE NO SYNTHESIS ENGINE")
        
        try:
            # 1. ANÁLISE PROFUNDA DO SYNTHESIS ENGINE
            logger.info("🧠 Executando análise profunda do Synthesis Engine...")
            deep_analysis = await self.analyze_synthesis_content_deeply(synthesis_data, session_id)
            
            if deep_analysis.get('error'):
                return self._create_error_result(session_id, f"Erro na análise profunda: {deep_analysis['error']}")
            
            # 2. PREPARAÇÃO DO CONTEXTO EXPERT
            logger.info("🎯 Preparando contexto expert para geração...")
            expert_context = await self._prepare_expert_context(synthesis_data, deep_analysis)
            
            # 3. GERAÇÃO SEQUENCIAL COM EXPERTISE
            logger.info("⚙️ Gerando módulos com expertise especializada...")
            expert_results = await self._generate_modules_with_expertise(session_id, expert_context, deep_analysis)
            
            # 4. VALIDAÇÃO DE COERÊNCIA EXPERT
            logger.info("🔍 Validando coerência expert entre módulos...")
            expert_validation = await self._validate_expert_coherence(session_id, expert_results, deep_analysis)
            
            # 5. REFINAMENTO BASEADO NA EXPERTISE
            if expert_validation.get('needs_expert_refinement'):
                logger.info("🔧 Refinando módulos com base na expertise...")
                expert_results = await self._refine_modules_with_expertise(session_id, expert_results, expert_validation, deep_analysis)
            
            # 6. MÉTRICAS FINAIS DE EXPERTISE
            final_metrics = await self._calculate_expert_metrics(expert_results, deep_analysis, expert_validation)
            
            logger.info(f"🎉 GERAÇÃO EXPERT CONCLUÍDA! Score de expertise: {final_metrics.get('expertise_score', 0):.2f}")
            
            return {
                **expert_results,
                'synthesis_expertise_applied': True,
                'deep_analysis': deep_analysis,
                'expert_validation': expert_validation,
                'expert_metrics': final_metrics,
                'generation_approach': 'synthesis_expert'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração expert: {e}")
            return self._create_error_result(session_id, str(e))

    async def _prepare_expert_context(self, synthesis_data: Dict[str, Any], deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara contexto expert enriquecido com a análise profunda"""
        try:
            expert_context = {
                'original_synthesis': synthesis_data,
                'extracted_expertise': deep_analysis.get('synthesis_expertise', {}),
                'semantic_intelligence': deep_analysis.get('semantic_patterns', {}),
                'domain_mastery': deep_analysis.get('domain_knowledge', {}),
                'content_insights': deep_analysis.get('content_insights', {}),
                'generation_strategy': deep_analysis.get('module_generation_strategy', {}),
                'quality_benchmarks': deep_analysis.get('quality_indicators', {}),
                'expert_prompts': await self._create_expert_prompts(deep_analysis)
            }
            
            return expert_context
            
        except Exception as e:
            logger.error(f"❌ Erro na preparação do contexto expert: {e}")
            return {}

    async def _create_expert_prompts(self, deep_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Cria prompts especializados baseados na análise profunda"""
        try:
            expertise = deep_analysis.get('synthesis_expertise', {})
            strategy = deep_analysis.get('module_generation_strategy', {})
            
            expert_prompts = {
                'expert_prefix': f"""
# VOCÊ É UM CONSULTOR EXPERT ESPECIALIZADO

Baseado na análise profunda do Synthesis Engine, você domina:

**CONCEITOS-CHAVE IDENTIFICADOS:**
{', '.join(expertise.get('key_concepts', [])[:5])}

**TERMOS ESPECIALIZADOS:**
{', '.join(expertise.get('specialized_terms', [])[:5])}

**INSIGHTS DE MERCADO:**
{', '.join(expertise.get('market_insights', [])[:3])}

**ABORDAGEM DE GERAÇÃO:** {strategy.get('generation_approach', 'comprehensive')}
**NÍVEL DE ESPECIALIZAÇÃO:** {deep_analysis.get('content_insights', {}).get('specialization_level', 'intermediate')}

INSTRUÇÕES CRÍTICAS:
- Use EXATAMENTE os termos e conceitos identificados na análise
- Mantenha COERÊNCIA total com o Synthesis Engine
- Aplique o nível de especialização apropriado
- Gere conteúdo EXPERT baseado no conhecimento extraído
""",
                
                'coherence_instruction': """
MANTER COERÊNCIA ABSOLUTA:
- Referencie conceitos do Synthesis Engine
- Use terminologia consistente
- Alinhe recomendações com insights identificados
- Mantenha tom e estilo consistentes
""",
                
                'quality_standard': f"""
PADRÃO DE QUALIDADE EXPERT:
- Score mínimo: {strategy.get('quality_targets', {}).get('min_quality_score', 0.8)}
- Profundidade: {strategy.get('content_adaptation', {}).get('detail_level', 'high')}
- Estilo: {strategy.get('content_adaptation', {}).get('content_style', 'strategic')}
"""
            }
            
            return expert_prompts
            
        except Exception as e:
            logger.error(f"❌ Erro na criação de prompts expert: {e}")
            return {}

    async def _generate_modules_with_expertise(self, session_id: str, expert_context: Dict[str, Any], deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera módulos aplicando toda a expertise extraída"""
        try:
            results = {
                'session_id': session_id,
                'modules': {},
                'failed_modules': [],
                'expert_applied': True,
                'generation_stats': {
                    'total_attempted': 0,
                    'successful': 0,
                    'expert_quality': 0,
                    'synthesis_alignment': 0.0
                }
            }
            
            # Obter estratégia de geração
            strategy = deep_analysis.get('module_generation_strategy', {})
            priority_modules = strategy.get('priority_modules', [])
            
            # Gerar módulos prioritários primeiro
            all_modules = list(self.modules_config.keys())
            ordered_modules = priority_modules + [m for m in all_modules if m not in priority_modules]
            
            for module_name in ordered_modules:
                try:
                    logger.info(f"🎯 Gerando módulo expert: {module_name}")
                    
                    # Aplicar expertise específica para o módulo
                    module_result = await self._generate_single_expert_module(
                        module_name, expert_context, deep_analysis, session_id
                    )
                    
                    if module_result.get('success'):
                        results['modules'][module_name] = module_result
                        results['generation_stats']['successful'] += 1
                        
                        # Verificar qualidade expert
                        if module_result.get('expert_quality_score', 0) > 0.8:
                            results['generation_stats']['expert_quality'] += 1
                    else:
                        results['failed_modules'].append({
                            'module': module_name,
                            'error': module_result.get('error', 'Unknown error')
                        })
                    
                    results['generation_stats']['total_attempted'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erro no módulo {module_name}: {e}")
                    results['failed_modules'].append({
                        'module': module_name,
                        'error': str(e)
                    })
            
            # Calcular alinhamento com synthesis
            if results['generation_stats']['successful'] > 0:
                results['generation_stats']['synthesis_alignment'] = (
                    results['generation_stats']['expert_quality'] / 
                    results['generation_stats']['successful']
                )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com expertise: {e}")
            return {'error': str(e), 'session_id': session_id}

    async def _generate_single_expert_module(self, module_name: str, expert_context: Dict[str, Any], deep_analysis: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Gera um único módulo com aplicação de expertise"""
        try:
            module_config = self.modules_config.get(module_name, {})
            expert_prompts = expert_context.get('expert_prompts', {})
            
            # Construir prompt expert para o módulo
            expert_prompt = f"""
{expert_prompts.get('expert_prefix', '')}

# MÓDULO: {module_config.get('title', module_name)}

{module_config.get('description', '')}

{expert_prompts.get('coherence_instruction', '')}

{expert_prompts.get('quality_standard', '')}

## CONTEXTO EXPERT ESPECÍFICO:

**EXPERTISE APLICÁVEL:**
{self._get_relevant_expertise_for_module(module_name, expert_context)}

**CONHECIMENTO DO DOMÍNIO:**
{self._get_relevant_domain_knowledge_for_module(module_name, expert_context)}

**INSIGHTS DE CONTEÚDO:**
{self._get_relevant_insights_for_module(module_name, expert_context)}

## DADOS DO SYNTHESIS ENGINE:
{str(expert_context.get('original_synthesis', {}))[:2000]}...

GERE O MÓDULO COM EXPERTISE MÁXIMA E COERÊNCIA TOTAL!
"""
            
            # Gerar conteúdo com IA
            if self.ai_manager:
                content = await self.ai_manager.generate_content(
                    prompt=expert_prompt,
                    max_tokens=3000,
                    temperature=0.7
                )
                
                # Calcular score de qualidade expert
                expert_quality_score = await self._calculate_module_expert_score(
                    content, expert_context, module_name
                )
                
                return {
                    'success': True,
                    'content': content,
                    'expert_quality_score': expert_quality_score,
                    'module_name': module_name,
                    'expertise_applied': True,
                    'generation_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'AI Manager não disponível',
                    'module_name': module_name
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na geração do módulo expert {module_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'module_name': module_name
            }

    def _get_relevant_expertise_for_module(self, module_name: str, expert_context: Dict[str, Any]) -> str:
        """Obtém expertise relevante para um módulo específico"""
        try:
            expertise = expert_context.get('extracted_expertise', {})
            
            # Mapear módulos para tipos de expertise
            module_expertise_map = {
                'avatares': expertise.get('audience_characteristics', []),
                'analise_competitiva': expertise.get('competitive_intelligence', []),
                'insights_mercado': expertise.get('market_insights', []),
                'estrategia_posicionamento': expertise.get('strategic_points', []),
                'sintese_master': expertise.get('key_concepts', [])
            }
            
            relevant_expertise = module_expertise_map.get(module_name, expertise.get('key_concepts', []))
            return ' | '.join(relevant_expertise[:5]) if relevant_expertise else 'Expertise geral aplicável'
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter expertise para {module_name}: {e}")
            return 'Expertise não disponível'

    def _get_relevant_domain_knowledge_for_module(self, module_name: str, expert_context: Dict[str, Any]) -> str:
        """Obtém conhecimento do domínio relevante para um módulo específico"""
        try:
            domain_knowledge = expert_context.get('domain_mastery', {})
            
            # Mapear módulos para conhecimento do domínio
            module_domain_map = {
                'analise_competitiva': domain_knowledge.get('market_dynamics', []),
                'insights_mercado': domain_knowledge.get('industry_specifics', []),
                'estrategia_posicionamento': domain_knowledge.get('business_models', []),
                'plano_marketing': domain_knowledge.get('best_practices', [])
            }
            
            relevant_knowledge = module_domain_map.get(module_name, domain_knowledge.get('industry_specifics', []))
            return ' | '.join(relevant_knowledge[:3]) if relevant_knowledge else 'Conhecimento geral do domínio'
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter conhecimento para {module_name}: {e}")
            return 'Conhecimento não disponível'

    def _get_relevant_insights_for_module(self, module_name: str, expert_context: Dict[str, Any]) -> str:
        """Obtém insights relevantes para um módulo específico"""
        try:
            content_insights = expert_context.get('content_insights', {})
            
            insights_summary = f"""
Nível de especialização: {content_insights.get('specialization_level', 'intermediate')}
Score de qualidade: {content_insights.get('content_quality_score', 0):.2f}
Oportunidades: {', '.join(content_insights.get('enhancement_opportunities', [])[:2])}
"""
            return insights_summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter insights para {module_name}: {e}")
            return 'Insights não disponíveis'

    async def _calculate_module_expert_score(self, content: str, expert_context: Dict[str, Any], module_name: str) -> float:
        """Calcula score de qualidade expert para um módulo"""
        try:
            score = 0.0
            
            # 1. Uso de expertise extraída (30%)
            expertise = expert_context.get('extracted_expertise', {})
            all_expertise_terms = []
            for expertise_list in expertise.values():
                if isinstance(expertise_list, list):
                    all_expertise_terms.extend(expertise_list)
            
            expertise_usage = sum(1 for term in all_expertise_terms if term.lower() in content.lower())
            expertise_score = min(expertise_usage / 5, 1.0) * 0.3
            
            # 2. Coerência semântica (25%)
            semantic_patterns = expert_context.get('semantic_intelligence', {})
            recurring_concepts = semantic_patterns.get('recurring_concepts', {})
            
            concept_usage = sum(1 for concept in recurring_concepts.keys() if concept in content.lower())
            semantic_score = min(concept_usage / 3, 1.0) * 0.25
            
            # 3. Aplicação de conhecimento do domínio (25%)
            domain_knowledge = expert_context.get('domain_mastery', {})
            all_domain_terms = []
            for domain_list in domain_knowledge.values():
                if isinstance(domain_list, list):
                    all_domain_terms.extend(domain_list)
            
            domain_usage = sum(1 for term in all_domain_terms if term.lower() in content.lower())
            domain_score = min(domain_usage / 3, 1.0) * 0.25
            
            # 4. Qualidade geral do conteúdo (20%)
            content_quality = min(len(content) / 2000, 1.0) * 0.2  # Normalizado para 2k chars
            
            score = expertise_score + semantic_score + domain_score + content_quality
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo do score expert: {e}")
            return 0.0

    async def _validate_expert_coherence(self, session_id: str, expert_results: Dict[str, Any], deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida coerência expert entre módulos"""
        try:
            validation = {
                'coherence_score': 0.0,
                'synthesis_alignment': 0.0,
                'expert_consistency': 0.0,
                'needs_expert_refinement': False,
                'refinement_areas': [],
                'quality_distribution': {}
            }
            
            modules = expert_results.get('modules', {})
            if not modules:
                return validation
            
            # 1. Score de coerência entre módulos
            module_contents = [m.get('content', '') for m in modules.values() if m.get('content')]
            
            if len(module_contents) > 1:
                # Verificar consistência terminológica
                expertise = deep_analysis.get('synthesis_expertise', {})
                key_terms = expertise.get('key_concepts', [])[:5]
                
                term_consistency = []
                for term in key_terms:
                    usage_count = sum(1 for content in module_contents if term.lower() in content.lower())
                    consistency = usage_count / len(module_contents)
                    term_consistency.append(consistency)
                
                validation['expert_consistency'] = sum(term_consistency) / len(term_consistency) if term_consistency else 0.0
            
            # 2. Alinhamento com synthesis
            original_synthesis = str(deep_analysis.get('original_synthesis', ''))
            synthesis_terms = set(original_synthesis.lower().split())
            
            alignment_scores = []
            for content in module_contents:
                content_terms = set(content.lower().split())
                common_terms = synthesis_terms.intersection(content_terms)
                alignment = len(common_terms) / len(synthesis_terms) if synthesis_terms else 0
                alignment_scores.append(alignment)
            
            validation['synthesis_alignment'] = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
            
            # 3. Score geral de coerência
            validation['coherence_score'] = (
                validation['expert_consistency'] * 0.6 +
                validation['synthesis_alignment'] * 0.4
            )
            
            # 4. Distribuição de qualidade
            quality_scores = [m.get('expert_quality_score', 0) for m in modules.values()]
            validation['quality_distribution'] = {
                'high_quality': len([s for s in quality_scores if s > 0.8]),
                'medium_quality': len([s for s in quality_scores if 0.6 <= s <= 0.8]),
                'low_quality': len([s for s in quality_scores if s < 0.6]),
                'average_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            }
            
            # 5. Necessidade de refinamento
            if validation['coherence_score'] < 0.7:
                validation['needs_expert_refinement'] = True
                validation['refinement_areas'].append('Melhorar consistência terminológica')
            
            if validation['synthesis_alignment'] < 0.6:
                validation['needs_expert_refinement'] = True
                validation['refinement_areas'].append('Aumentar alinhamento com synthesis')
            
            if validation['quality_distribution']['low_quality'] > len(modules) * 0.3:
                validation['needs_expert_refinement'] = True
                validation['refinement_areas'].append('Elevar qualidade dos módulos de baixo score')
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Erro na validação expert: {e}")
            return {'error': str(e)}

    async def _refine_modules_with_expertise(self, session_id: str, expert_results: Dict[str, Any], validation: Dict[str, Any], deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Refina módulos aplicando expertise adicional"""
        try:
            logger.info("🔧 Iniciando refinamento expert dos módulos...")
            
            refinement_areas = validation.get('refinement_areas', [])
            modules = expert_results.get('modules', {})
            
            for module_name, module_data in modules.items():
                try:
                    current_score = module_data.get('expert_quality_score', 0)
                    
                    # Refinar apenas módulos que precisam
                    if current_score < 0.8:
                        logger.info(f"🔧 Refinando módulo: {module_name}")
                        
                        refined_content = await self._apply_expert_refinement(
                            module_name, module_data.get('content', ''), 
                            refinement_areas, deep_analysis
                        )
                        
                        if refined_content:
                            # Atualizar módulo com conteúdo refinado
                            modules[module_name]['content'] = refined_content
                            modules[module_name]['refined'] = True
                            modules[module_name]['refinement_timestamp'] = datetime.now().isoformat()
                            
                            # Recalcular score
                            expert_context = {
                                'extracted_expertise': deep_analysis.get('synthesis_expertise', {}),
                                'semantic_intelligence': deep_analysis.get('semantic_patterns', {}),
                                'domain_mastery': deep_analysis.get('domain_knowledge', {})
                            }
                            
                            new_score = await self._calculate_module_expert_score(
                                refined_content, expert_context, module_name
                            )
                            modules[module_name]['expert_quality_score'] = new_score
                            
                            logger.info(f"✅ Módulo {module_name} refinado: {current_score:.2f} → {new_score:.2f}")
                
                except Exception as e:
                    logger.error(f"❌ Erro no refinamento do módulo {module_name}: {e}")
            
            expert_results['modules'] = modules
            expert_results['refinement_applied'] = True
            
            return expert_results
            
        except Exception as e:
            logger.error(f"❌ Erro no refinamento expert: {e}")
            return expert_results

    async def _apply_expert_refinement(self, module_name: str, original_content: str, refinement_areas: List[str], deep_analysis: Dict[str, Any]) -> str:
        """Aplica refinamento expert a um módulo específico"""
        try:
            expertise = deep_analysis.get('synthesis_expertise', {})
            
            refinement_prompt = f"""
# REFINAMENTO EXPERT DO MÓDULO: {module_name}

## CONTEÚDO ORIGINAL:
{original_content}

## ÁREAS DE REFINAMENTO NECESSÁRIAS:
{chr(10).join(f'- {area}' for area in refinement_areas)}

## EXPERTISE A SER APLICADA:
**Conceitos-chave:** {', '.join(expertise.get('key_concepts', [])[:5])}
**Termos especializados:** {', '.join(expertise.get('specialized_terms', [])[:5])}
**Insights de mercado:** {', '.join(expertise.get('market_insights', [])[:3])}

## INSTRUÇÕES DE REFINAMENTO:
1. MANTER todo o conteúdo original válido
2. ADICIONAR os conceitos e termos especializados identificados
3. MELHORAR a coerência com o Synthesis Engine
4. ELEVAR o nível de especialização
5. GARANTIR consistência terminológica

REFINE O CONTEÚDO APLICANDO MÁXIMA EXPERTISE:
"""
            
            if self.ai_manager:
                refined_content = await self.ai_manager.generate_content(
                    prompt=refinement_prompt,
                    max_tokens=3500,
                    temperature=0.5
                )
                return refined_content
            else:
                return original_content
                
        except Exception as e:
            logger.error(f"❌ Erro no refinamento do módulo {module_name}: {e}")
            return original_content

    async def _calculate_expert_metrics(self, expert_results: Dict[str, Any], deep_analysis: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas finais de expertise"""
        try:
            metrics = {
                'expertise_score': 0.0,
                'synthesis_integration_score': 0.0,
                'module_quality_average': 0.0,
                'coherence_achievement': 0.0,
                'expert_features_applied': 0,
                'overall_expert_rating': '',
                'recommendations': []
            }
            
            modules = expert_results.get('modules', {})
            
            # 1. Score médio de qualidade dos módulos
            quality_scores = [m.get('expert_quality_score', 0) for m in modules.values()]
            metrics['module_quality_average'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            # 2. Score de integração com synthesis
            metrics['synthesis_integration_score'] = validation.get('synthesis_alignment', 0.0)
            
            # 3. Achievement de coerência
            metrics['coherence_achievement'] = validation.get('coherence_score', 0.0)
            
            # 4. Features expert aplicadas
            expert_features = 0
            if deep_analysis.get('synthesis_expertise'):
                expert_features += 1
            if deep_analysis.get('semantic_patterns'):
                expert_features += 1
            if deep_analysis.get('domain_knowledge'):
                expert_features += 1
            if deep_analysis.get('content_insights'):
                expert_features += 1
            
            metrics['expert_features_applied'] = expert_features
            
            # 5. Score geral de expertise
            metrics['expertise_score'] = (
                metrics['module_quality_average'] * 0.4 +
                metrics['synthesis_integration_score'] * 0.3 +
                metrics['coherence_achievement'] * 0.2 +
                (expert_features / 4) * 0.1
            )
            
            # 6. Rating geral
            if metrics['expertise_score'] > 0.9:
                metrics['overall_expert_rating'] = 'EXPERT_MASTER'
            elif metrics['expertise_score'] > 0.8:
                metrics['overall_expert_rating'] = 'EXPERT_ADVANCED'
            elif metrics['expertise_score'] > 0.7:
                metrics['overall_expert_rating'] = 'EXPERT_INTERMEDIATE'
            else:
                metrics['overall_expert_rating'] = 'EXPERT_BASIC'
            
            # 7. Recomendações
            if metrics['expertise_score'] > 0.85:
                metrics['recommendations'].append('✅ Excelente aplicação de expertise - módulos prontos para uso')
            else:
                metrics['recommendations'].append('🔧 Considerar refinamento adicional para maximizar expertise')
            
            if metrics['synthesis_integration_score'] < 0.7:
                metrics['recommendations'].append('🔗 Melhorar integração com Synthesis Engine')
            
            if metrics['coherence_achievement'] < 0.8:
                metrics['recommendations'].append('🎯 Fortalecer coerência entre módulos')
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de métricas expert: {e}")
            return {}

# Exemplo de como executar o processador (para fins de teste)
async def main():
    print("Executando o EnhancedModuleProcessor em modo de teste.")
    processor = EnhancedModuleProcessor()
    
    # Simular dados base para uma sessão de teste
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_data_dir = BASE_DATA_DIR / session_id
    test_data_dir.mkdir(parents=True, exist_ok=True)

    contexto_estrategico = {
        "tema": "Lançamento de um novo café especial gourmet",
        "segmento": "Consumidores de café de alta qualidade no Brasil",
        "publico_alvo": "Jovens profissionais, apreciadores de café, que buscam uma experiência premium e valorizam a origem e a sustentabilidade do produto.",
        "diferenciais": ["Grãos 100% arábica de origem única", "Torra artesanal", "Embalagem sustentável"],
        "objetivo": "Se tornar a marca de café especial preferida pelo público jovem profissional em 2 anos."
    }

    with open(test_data_dir / "contexto_estrategico.json", 'w', encoding='utf-8') as f:
        json.dump(contexto_estrategico, f, indent=4, ensure_ascii=False)

    # Executar a geração de todos os módulos
    results = await processor.generate_all_modules(session_id)
    print("\nResultados da Geração:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    # Para executar este script diretamente, descomente a linha abaixo
    # asyncio.run(main())
    logger.info("Script enhanced_module_processor.py carregado. Para execução de teste, chame a função main().")




# Instância global do processador para ser importada por outros módulos
enhanced_module_processor = EnhancedModuleProcessor()

