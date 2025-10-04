import os
import logging
import requests
import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from collections import Counter
import re
from services.mcp_supadata_manager import MCPSupadataManager
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CompetitorContentCollector:
    def __init__(self, storage_path: str = "data/competitors"):
        self.mcp_supadata_manager = MCPSupadataManager()
        self.storage_path = storage_path
        self._ensure_storage_directory()
        # Carrega configurações e dados existentes
        self.competitors_config = self._load_config()
        self.competitor_content_db = self._load_content_db()
        self.discovered_competitors = self._load_discovered_competitors()

        # Carrega chaves de API do ambiente
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        self.exa_api_key = os.getenv('EXA_API_KEY')

        # Headers para requisições HTTP mais realistas
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        }

    def _ensure_storage_directory(self):
        """Garante que o diretório de armazenamento existe."""
        os.makedirs(self.storage_path, exist_ok=True)
        logger.info(f"Diretório de armazenamento verificado: {self.storage_path}")

    def _load_config(self) -> Dict:
        """Carrega configurações de concorrentes do arquivo."""
        config_file = os.path.join(self.storage_path, "competitors_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar configurações: {e}")
        return {}

    def _save_config(self):
        """Salva configurações de concorrentes no arquivo."""
        config_file = os.path.join(self.storage_path, "competitors_config.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.competitors_config, f, indent=2, ensure_ascii=False)
            logger.info("Configurações salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def _load_content_db(self) -> List[Dict]:
        """Carrega banco de dados de conteúdo coletado."""
        db_file = os.path.join(self.storage_path, "content_database.json")
        if os.path.exists(db_file):
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar banco de dados de conteúdo: {e}")
        return []

    def _save_content_db(self):
        """Salva banco de dados de conteúdo."""
        db_file = os.path.join(self.storage_path, "content_database.json")
        try:
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(self.competitor_content_db, f, indent=2, ensure_ascii=False)
            logger.info(f"Banco de dados de conteúdo salvo: {len(self.competitor_content_db)} itens")
        except Exception as e:
            logger.error(f"Erro ao salvar banco de dados de conteúdo: {e}")

    def _load_discovered_competitors(self) -> List[Dict]:
        """Carrega lista de concorrentes descobertos automaticamente."""
        discovered_file = os.path.join(self.storage_path, "discovered_competitors.json")
        if os.path.exists(discovered_file):
            try:
                with open(discovered_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar concorrentes descobertos: {e}")
        return []

    def _save_discovered_competitors(self):
        """Salva lista de concorrentes descobertos."""
        discovered_file = os.path.join(self.storage_path, "discovered_competitors.json")
        try:
            with open(discovered_file, 'w', encoding='utf-8') as f:
                json.dump(self.discovered_competitors, f, indent=2, ensure_ascii=False)
            logger.info(f"Concorrentes descobertos salvos: {len(self.discovered_competitors)}")
        except Exception as e:
            logger.error(f"Erro ao salvar concorrentes descobertos: {e}")

    def add_competitor(self, name: str, base_urls: List[str], industry: str = "", keywords: List[str] = None):
        """
        Adiciona ou atualiza a configuração de um concorrente.
        Args:
            name: Nome do concorrente
            base_urls: Lista de URLs base para monitorar
            industry: Indústria/setor do concorrente
            keywords: Palavras-chave relacionadas ao concorrente
        """
        self.competitors_config[name] = {
            "base_urls": base_urls,
            "industry": industry,
            "keywords": keywords or [],
            "last_crawled": None,
            "added_date": datetime.now().isoformat(),
            "status": "active",
            "relevance_score": 0.0
        }
        self._save_config()
        logger.info(f"Concorrente {name} adicionado/atualizado com URLs: {base_urls}")

    def discover_competitors_from_search(self, your_business_description: str,
                                         your_keywords: List[str],
                                         location: str = "",
                                         max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Descobre concorrentes através de busca inteligente baseada em sua descrição de negócio.
        Args:
            your_business_description: Descrição do seu negócio
            your_keywords: Palavras-chave do seu negócio
            location: Localização geográfica (opcional)
            max_results: Número máximo de resultados
        Returns:
            Lista de concorrentes descobertos com scores de relevância
        """
        logger.info(f"Iniciando descoberta de concorrentes para: {your_business_description}")
        discovered = []
        # Constrói queries de busca inteligentes
        search_queries = self._build_search_queries(your_business_description, your_keywords, location)

        for query in search_queries[:3]:  # Limita a 3 queries principais
            logger.info(f"Buscando com query: {query}")
            # Tenta buscar resultados reais com APIs
            results = self._fetch_search_results(query, your_keywords)
            for result in results[:max_results]:
                competitor_data = self._analyze_potential_competitor(
                    result,
                    your_keywords,
                    your_business_description
                )
                if competitor_data and competitor_data["relevance_score"] >= 0.6:
                    discovered.append(competitor_data)

        # Remove duplicatas e ordena por relevância
        discovered = self._deduplicate_and_rank(discovered)
        # Salva descobertos
        for competitor in discovered:
            if not any(d["domain"] == competitor["domain"] for d in self.discovered_competitors):
                self.discovered_competitors.append({
                    **competitor,
                    "discovered_date": datetime.now().isoformat(),
                    "status": "pending_review"
                })
        self._save_discovered_competitors()
        logger.info(f"Descoberta concluída: {len(discovered)} concorrentes relevantes encontrados")
        return discovered

    def _build_search_queries(self, business_description: str, keywords: List[str], location: str) -> List[str]:
        """Constrói queries de busca otimizadas."""
        queries = []
        # Query principal com palavras-chave
        main_keywords = " ".join(keywords[:3])
        queries.append(f"{main_keywords} {location}".strip())
        # Query com descrição
        if business_description:
            queries.append(f"{business_description} empresas {location}".strip())
        # Query para encontrar líderes do setor
        queries.append(f"melhores {main_keywords} empresas {location}".strip())
        # Query para encontrar alternativas
        queries.append(f"alternativas {main_keywords} {location}".strip())
        return queries

    def _fetch_search_results(self, query: str, your_keywords: List[str]) -> List[Dict]:
        """
        Tenta obter resultados reais de APIs de busca.
        Retorna uma lista de dicionários no formato esperado ou uma lista vazia.
        """
        logger.info(f"Tentando buscar resultados reais para: {query}")

        # Definir ordem de tentativas com base nas chaves disponíveis
        providers = []
        if self.serper_api_key:
            providers.append(('serper', self._search_with_serper))
        if self.serp_api_key:
            providers.append(('serp', self._search_with_serp))
        if self.tavily_api_key:
            providers.append(('tavily', self._search_with_tavily))
        if self.firecrawl_api_key:
            providers.append(('firecrawl', self._search_with_firecrawl)) # Geralmente não é busca direta
        if self.exa_api_key:
            providers.append(('exa', self._search_with_exa))

        # Tentar cada provedor disponível
        for provider_name, search_func in providers:
            try:
                logger.info(f"Tentando {provider_name}...")
                results = search_func(query)
                if results:
                    logger.info(f"Resultados obtidos com {provider_name}.")
                    return results
                else:
                    logger.warning(f"{provider_name} retornou resultados vazios.")
            except Exception as e:
                logger.error(f"Erro ao usar {provider_name}: {e}")

        # Se todos falharem ou não houver chaves, usar o simulado
        logger.warning("Todas as APIs de busca falharam ou não estão configuradas. Usando resultados simulados.")
        return self._simulate_search_results(query, your_keywords)


    def _search_with_serper(self, query: str) -> List[Dict]:
        """Busca usando a API Serper."""
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "gl": "br",  # País
            "hl": "pt-br" # Idioma
        })
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('organic', []):
            results.append({
                "title": item.get('title', ''),
                "url": item.get('link', ''),
                "snippet": item.get('snippet', ''),
                "domain": urlparse(item.get('link', '')).netloc
            })
        return results

    def _search_with_serp(self, query: str) -> List[Dict]:
        """Busca usando a API SerpAPI."""
        params = {
            "engine": "google",
            "q": query,
            "gl": "br",
            "hl": "pt-br",
            "api_key": self.serp_api_key
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('organic_results', []):
            results.append({
                "title": item.get('title', ''),
                "url": item.get('link', ''),
                "snippet": item.get('snippet', ''),
                "domain": urlparse(item.get('link', '')).netloc
            })
        return results

    def _search_with_tavily(self, query: str) -> List[Dict]:
        """Busca usando a API Tavily."""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
            "max_results": 10,
            "country": "br"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('results', []):
            results.append({
                "title": item.get('title', ''),
                "url": item.get('url', ''),
                "snippet": item.get('content', ''),
                "domain": urlparse(item.get('url', '')).netloc
            })
        return results

    def _search_with_firecrawl(self, query: str) -> List[Dict]:
        """Busca usando a API Firecrawl (exemplo de uso de 'crawl' ou 'search')."""
        # Firecrawl é mais focado em crawling e scraping, mas tem uma funcionalidade de busca.
        # A API de busca direta pode ter limitações.
        url = "https://api.firecrawl.dev/v0/search"
        payload = {
            "query": query,
            "limit": 10
        }
        headers = {
            'Authorization': f'Bearer {self.firecrawl_api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('data', []): # Estrutura de resposta pode variar
            # Ajuste conforme a estrutura real da resposta
            if 'url' in item:
                results.append({
                    "title": item.get('metadata', {}).get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('metadata', {}).get('description', ''),
                    "domain": urlparse(item.get('url', '')).netloc
                })
        return results

    def _search_with_exa(self, query: str) -> List[Dict]:
        """Busca usando a API Exa AI."""
        url = "https://api.exa.ai/search"
        payload = {
            "query": query,
            "type": "keyword",
            "size": 10,
            "category": "company",
            "contents": {
                "text": {
                    "maxCharacters": 200,
                    "includeHtml": False
                },
                "highlights": {
                    "numSentences": 1,
                    "highlightsPerUrl": 1
                }
            }
        }
        headers = {
            'x-api-key': self.exa_api_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('results', []):
            results.append({
                "title": item.get('title', ''),
                "url": item.get('url', ''),
                "snippet": item.get('text', ''), # Pode vir de 'highlights' ou 'text'
                "domain": urlparse(item.get('url', '')).netloc
            })
        return results


    def _simulate_search_results(self, query: str, your_keywords: List[str]) -> List[Dict]:
        """
        Simula resultados de busca (em produção, usar API real de busca).
        Em um ambiente real, você integraria com:
        - Google Custom Search API
        - Bing Search API
        - DuckDuckGo API
        - Serper.dev API
        """
        logger.info(f"Simulando busca para: {query}")
        # Dados simulados para demonstração
        simulated_results = [
            {
                "title": "Empresa Concorrente A - Soluções Inovadoras",
                "url": "https://www.concorrente-a.com",
                "snippet": f"Líder em {your_keywords[0] if your_keywords else 'mercado'}. Oferecemos soluções completas para empresas.",
                "domain": "concorrente-a.com"
            },
            {
                "title": "Expert Solutions B | Consultoria Especializada",
                "url": "https://www.expert-b.com.br",
                "snippet": f"Especialistas em {your_keywords[1] if len(your_keywords) > 1 else 'tecnologia'}. 15 anos de experiência no mercado.",
                "domain": "expert-b.com.br"
            },
            {
                "title": "TechPro Solutions - Seu Parceiro de Negócios",
                "url": "https://www.techpro.com",
                "snippet": "Transformação digital e inovação para empresas de todos os portes.",
                "domain": "techpro.com"
            },
            {
                "title": "Innovate Corp - Tecnologia e Estratégia",
                "url": "https://www.innovatecorp.io",
                "snippet": f"Plataforma completa de {your_keywords[0] if your_keywords else 'gestão'}. Cases de sucesso e ROI comprovado.",
                "domain": "innovatecorp.io"
            },
            {
                "title": "Mega Solutions - Liderança em Inovação",
                "url": "https://www.megasolutions.net",
                "snippet": "Soluções enterprise para grandes empresas. Tecnologia de ponta.",
                "domain": "megasolutions.net"
            }
        ]
        return simulated_results


    def _analyze_potential_competitor(self, search_result: Dict,
                                     your_keywords: List[str],
                                     your_description: str) -> Optional[Dict[str, Any]]:
        """
        Analisa um resultado de busca para determinar se é um concorrente relevante.
        Args:
            search_result: Resultado da busca
            your_keywords: Suas palavras-chave
            your_description: Descrição do seu negócio
        Returns:
            Dados do concorrente com score de relevância ou None
        """
        try:
            url = search_result["url"]
            domain = search_result.get("domain", urlparse(url).netloc)
            logger.info(f"Analisando potencial concorrente: {domain}")
            # Extrai conteúdo da página principal
            page_data = self.mcp_supadata_manager.extract_from_url(url)
            if "error" in page_data:
                logger.warning(f"Erro ao extrair dados de {url}: {page_data['error']}")
                # Usa apenas snippet da busca
                content = search_result.get("snippet", "")
                title = search_result.get("title", "")
            else:
                content = page_data.get("extracted_text", "")
                title = page_data.get("title", search_result.get("title", ""))

            # Calcula score de relevância
            relevance_score = self._calculate_relevance_score(
                content,
                title,
                your_keywords,
                your_description
            )
            # Identifica indústria/setor
            industry = self._identify_industry(content, title)
            # Extrai palavras-chave do concorrente
            competitor_keywords = self._extract_keywords(content)
            # Detecta presença de redes sociais e contatos
            social_media = self._extract_social_media(content)

            competitor_data = {
                "name": self._extract_company_name(title, domain),
                "domain": domain,
                "url": url,
                "title": title,
                "industry": industry,
                "relevance_score": relevance_score,
                "keywords": competitor_keywords[:10],
                "social_media": social_media,
                "snippet": search_result.get("snippet", "")[:200],
                "analyzed_date": datetime.now().isoformat()
            }
            return competitor_data
        except Exception as e:
            logger.error(f"Erro ao analisar potencial concorrente {search_result.get('url')}: {e}")
            return None

    def _calculate_relevance_score(self, content: str, title: str,
                                   your_keywords: List[str],
                                   your_description: str) -> float:
        """
        Calcula score de relevância de 0 a 1 baseado em múltiplos fatores.
        """
        score = 0.0
        content_lower = content.lower()
        title_lower = title.lower()

        # Peso 1: Match de palavras-chave (40%)
        keyword_matches = sum(1 for kw in your_keywords if kw.lower() in content_lower)
        keyword_score = min(keyword_matches / len(your_keywords) if your_keywords else 0, 1.0)
        score += keyword_score * 0.4

        # Peso 2: Match no título (25%)
        title_matches = sum(1 for kw in your_keywords if kw.lower() in title_lower)
        title_score = min(title_matches / len(your_keywords) if your_keywords else 0, 1.0)
        score += title_score * 0.25

        # Peso 3: Palavras-chave de negócio (20%)
        business_indicators = ['empresa', 'solução', 'serviço', 'produto', 'cliente',
                               'consultoria', 'plataforma', 'software', 'sistema']
        business_count = sum(1 for word in business_indicators if word in content_lower)
        business_score = min(business_count / len(business_indicators), 1.0)
        score += business_score * 0.2

        # Peso 4: Comprimento e qualidade do conteúdo (15%)
        content_quality = min(len(content) / 5000, 1.0)  # Normaliza até 5000 caracteres
        score += content_quality * 0.15

        return round(score, 2)

    def _identify_industry(self, content: str, title: str) -> str:
        """Identifica a indústria/setor com base no conteúdo."""
        content_lower = (content + " " + title).lower()
        industries = {
            "Tecnologia": ['software', 'tecnologia', 'tech', 'digital', 'sistema', 'plataforma', 'app'],
            "Consultoria": ['consultoria', 'consultores', 'estratégia', 'advisory'],
            "Marketing": ['marketing', 'publicidade', 'mídia', 'comunicação', 'branding'],
            "E-commerce": ['e-commerce', 'loja virtual', 'marketplace', 'vendas online'],
            "Educação": ['educação', 'ensino', 'curso', 'treinamento', 'capacitação'],
            "Saúde": ['saúde', 'médico', 'clínica', 'hospital', 'telemedicina'],
            "Financeiro": ['financeiro', 'finanças', 'investimento', 'banco', 'fintech'],
            "RH": ['recursos humanos', 'recrutamento', 'rh', 'gestão de pessoas']
        }
        industry_scores = {}
        for industry, keywords in industries.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                industry_scores[industry] = score

        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return "Geral"

    def _extract_keywords(self, content: str, top_n: int = 15) -> List[str]:
        """Extrai palavras-chave relevantes do conteúdo."""
        # Remove stopwords comuns
        stopwords = {'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para',
                     'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por',
                     'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele',
                     'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'the',
                     'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        # Limpa e tokeniza
        words = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{4,}\b', content.lower())
        # Filtra stopwords e conta frequências
        word_freq = Counter(w for w in words if w not in stopwords)
        # Retorna top N palavras
        return [word for word, _ in word_freq.most_common(top_n)]

    def _extract_social_media(self, content: str) -> Dict[str, str]:
        """Extrai links de redes sociais do conteúdo."""
        social_patterns = {
            'linkedin': r'linkedin\.com/(?:company|in)/([a-zA-Z0-9-]+)',
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
            'instagram': r'instagram\.com/([a-zA-Z0-9_.]+)',
            'youtube': r'youtube\.com/(?:c|channel|user)/([a-zA-Z0-9_-]+)'
        }
        social_media = {}
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, content)
            if match:
                social_media[platform] = match.group(0)
        return social_media

    def _extract_company_name(self, title: str, domain: str) -> str:
        """Extrai o nome da empresa do título ou domínio."""
        # Remove palavras comuns do final do título
        common_suffixes = [' - ', ' | ', ' :: ', 'Início', 'Home', 'Site Oficial']
        clean_title = title
        for suffix in common_suffixes:
            if suffix in title:
                clean_title = title.split(suffix)[0]
                break

        if len(clean_title) < 50 and clean_title:
            return clean_title.strip()
        # Fallback para domínio
        return domain.replace('www.', '').split('.')[0].title()

    def _deduplicate_and_rank(self, competitors: List[Dict]) -> List[Dict]:
        """Remove duplicatas e ordena por relevância."""
        seen_domains = {}
        for comp in competitors:
            domain = comp["domain"]
            if domain not in seen_domains or comp["relevance_score"] > seen_domains[domain]["relevance_score"]:
                seen_domains[domain] = comp

        unique_competitors = list(seen_domains.values())
        unique_competitors.sort(key=lambda x: x["relevance_score"], reverse=True)
        return unique_competitors

    def _crawl_for_new_urls(self, base_url: str, max_urls: int = 10) -> List[str]:
        """
        Rastrea uma URL base para encontrar novas URLs de conteúdo relevante.
        Args:
            base_url: URL base para rastrear
            max_urls: Número máximo de URLs para retornar
        Returns:
            Lista de URLs encontradas
        """
        logger.info(f"Rastreando novas URLs em: {base_url}")
        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Encontra todos os links
            links = soup.find_all('a', href=True)
            urls = set()
            for link in links:
                href = link['href']
                # Converte URLs relativas em absolutas
                full_url = urljoin(base_url, href)
                # Filtra URLs relevantes
                if self._is_relevant_url(full_url, base_url):
                    urls.add(full_url)
                if len(urls) >= max_urls:
                    break

            logger.info(f"Encontradas {len(urls)} URLs relevantes em {base_url}")
            return list(urls)
        except Exception as e:
            logger.error(f"Erro ao rastrear {base_url}: {e}")
            return []

    def _is_relevant_url(self, url: str, base_url: str) -> bool:
        """Verifica se uma URL é relevante para coleta."""
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)

        # Deve ser do mesmo domínio
        if parsed_url.netloc != parsed_base.netloc:
            return False

        # Filtra extensões não relevantes
        excluded_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar', '.doc', '.docx'}
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False

        # Prefere URLs com conteúdo
        relevant_paths = ['blog', 'artigo', 'post', 'noticia', 'produto', 'servico',
                         'solucao', 'case', 'sobre', 'about', 'news', 'article']
        path_lower = parsed_url.path.lower()
        return any(keyword in path_lower for keyword in relevant_paths)

    def collect_and_analyze_content(self, competitor_name: str,
                                    deep_crawl: bool = False,
                                    max_pages: int = 20) -> List[Dict[str, Any]]:
        """
        Coleta e analisa o conteúdo de um concorrente específico.
        Args:
            competitor_name: Nome do concorrente
            deep_crawl: Se True, faz rastreamento profundo
            max_pages: Número máximo de páginas para analisar
        Returns:
            Lista de itens de conteúdo coletados
        """
        config = self.competitors_config.get(competitor_name)
        if not config:
            logger.warning(f"Concorrente {competitor_name} não configurado.")
            return []

        new_content_items = []
        analyzed_urls = set()

        for base_url in config["base_urls"]:
            if deep_crawl:
                urls_to_analyze = self._crawl_for_new_urls(base_url, max_urls=max_pages)
            else:
                # Análise simples - apenas URLs mockadas
                urls_to_analyze = [
                    f"{base_url}/blog/post-recente",
                    f"{base_url}/produtos/lancamento",
                    f"{base_url}/noticias/ultimas"
                ]

            for url in urls_to_analyze:
                if url in analyzed_urls:
                    continue
                analyzed_urls.add(url)
                logger.info(f"Extraindo conteúdo de: {url}")

                extracted_data = self.mcp_supadata_manager.extract_from_url(url)
                if "error" not in extracted_
                    content = extracted_data.get("extracted_text", "")
                    title = extracted_data.get("title", "Sem Título")

                    # Análise avançada de palavras-chave
                    keywords = self._extract_keywords(content, top_n=10)
                    # Extrai tópicos principais
                    topics = self._extract_topics(content)
                    # Análise de sentimento (simplificada)
                    sentiment = self._analyze_sentiment(content)

                    content_item = {
                        "competitor": competitor_name,
                        "url": url,
                        "title": title,
                        "content_preview": content[:300] + "..." if len(content) > 300 else content,
                        "content_length": len(content),
                        "keywords": keywords,
                        "topics": topics,
                        "sentiment": sentiment,
                        "timestamp": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat()
                    }

                    # Verifica se já existe (atualiza se sim)
                    existing_idx = next((i for i, item in enumerate(self.competitor_content_db)
                                       if item["url"] == url), None)
                    if existing_idx is not None:
                        self.competitor_content_db[existing_idx] = content_item
                        logger.info(f"Conteúdo atualizado: {url}")
                    else:
                        self.competitor_content_db.append(content_item)
                        new_content_items.append(content_item)
                        logger.info(f"Novo conteúdo adicionado: {url}")
                else:
                    logger.warning(f"Falha ao extrair conteúdo de {url}: {extracted_data.get('error')}")

        config["last_crawled"] = datetime.now().isoformat()
        self._save_config()
        self._save_content_db()
        logger.info(f"Coleta para {competitor_name} concluída. Novos itens: {len(new_content_items)}")
        return new_content_items

    def _extract_topics(self, content: str, top_n: int = 5) -> List[str]:
        """Extrai tópicos principais do conteúdo."""
        # Palavras-chave de tópicos comuns em negócios
        topic_keywords = {
            "Inovação": ['inovação', 'inovador', 'tecnologia', 'futuro', 'transformação'],
            "Estratégia": ['estratégia', 'planejamento', 'objetivo', 'meta', 'visão'],
            "Produto": ['produto', 'solução', 'feature', 'funcionalidade', 'lançamento'],
            "Cliente": ['cliente', 'usuário', 'experiência', 'satisfação', 'atendimento'],
            "Crescimento": ['crescimento', 'expansão', 'mercado', 'vendas', 'receita'],
            "Equipe": ['equipe', 'time', 'colaborador', 'cultura', 'liderança'],
            "Sustentabilidade": ['sustentabilidade', 'esg', 'ambiental', 'social', 'responsabilidade']
        }
        content_lower = content.lower()
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(content_lower.count(kw) for kw in keywords)
            if score > 0:
                topic_scores[topic] = score

        # Retorna top N tópicos
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, _ in sorted_topics[:top_n]]

    def _analyze_sentiment(self, content: str) -> str:
        """Análise de sentimento simplificada do conteúdo."""
        content_lower = content.lower()
        positive_words = ['sucesso', 'excelente', 'melhor', 'ótimo', 'inovador', 'líder',
                         'crescimento', 'oportunidade', 'vantagem', 'qualidade']
        negative_words = ['problema', 'desafio', 'dificuldade', 'crise', 'falha',
                         'risco', 'prejuízo', 'queda']

        positive_count = sum(content_lower.count(word) for word in positive_words)
        negative_count = sum(content_lower.count(word) for word in negative_words)

        if positive_count > negative_count * 1.5:
            return "positivo"
        elif negative_count > positive_count * 1.5:
            return "negativo"
        else:
            return "neutro"

    def get_competitor_content_summary(self, competitor_name: str = None,
                                      days: int = 30) -> Dict[str, Any]:
        """
        Retorna um resumo detalhado do conteúdo coletado.
        Args:
            competitor_name: Nome do concorrente (None para todos)
            days: Número de dias para considerar no resumo
        Returns:
            Dicionário com análise completa do conteúdo
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_content = [
            c for c in self.competitor_content_db
            if datetime.fromisoformat(c["timestamp"]) >= cutoff_date
        ]

        if competitor_name:
            filtered_content = [c for c in filtered_content if c["competitor"] == competitor_name]

        total_items = len(filtered_content)

        # Agrega palavras-chave
        all_keywords = []
        for item in filtered_content:
            all_keywords.extend(item.get("keywords", []))
        keyword_freq = Counter(all_keywords)

        # Agrega tópicos
        all_topics = []
        for item in filtered_content:
            all_topics.extend(item.get("topics", []))
        topic_freq = Counter(all_topics)

        # Análise de sentimento
        sentiment_counts = Counter(item.get("sentiment", "neutro") for item in filtered_content)

        # Atividade por concorrente
        activity_by_competitor = Counter(item["competitor"] for item in filtered_content)

        # URLs mais recentes
        recent_content = sorted(
            filtered_content,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:10]

        return {
            "period_days": days,
            "total_content_items": total_items,
            "competitors_tracked": len(activity_by_competitor),
            "top_keywords": [{"keyword": k, "count": v} for k, v in keyword_freq.most_common(15)],
            "top_topics": [{"topic": t, "count": v} for t, v in topic_freq.most_common(10)],
            "sentiment_distribution": dict(sentiment_counts),
            "activity_by_competitor": dict(activity_by_competitor),
            "recent_content": recent_content,
            "content_list": filtered_content
        }

    def get_discovered_competitors_report(self, min_score: float = 0.6) -> Dict[str, Any]:
        """
        Retorna relatório detalhado dos concorrentes descobertos.
        Args:
            min_score: Score mínimo de relevância para incluir
        Returns:
            Relatório completo com análise de concorrentes descobertos
        """
        filtered = [
            c for c in self.discovered_competitors
            if c.get("relevance_score", 0) >= min_score
        ]

        # Agrupa por indústria
        by_industry = {}
        for comp in filtered:
            industry = comp.get("industry", "Outros")
            if industry not in by_industry:
                by_industry[industry] = []
            by_industry[industry].append(comp)

        # Top concorrentes por relevância
        top_competitors = sorted(
            filtered,
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )[:20]

        # Estatísticas de redes sociais
        social_stats = {
            "linkedin": sum(1 for c in filtered if "linkedin" in c.get("social_media", {})),
            "twitter": sum(1 for c in filtered if "twitter" in c.get("social_media", {})),
            "facebook": sum(1 for c in filtered if "facebook" in c.get("social_media", {})),
            "instagram": sum(1 for c in filtered if "instagram" in c.get("social_media", {})),
        }

        return {
            "total_discovered": len(filtered),
            "industries": {k: len(v) for k, v in by_industry.items()},
            "top_competitors": top_competitors,
            "by_industry": by_industry,
            "social_media_presence": social_stats,
            "average_relevance_score": round(
                sum(c.get("relevance_score", 0) for c in filtered) / len(filtered) if filtered else 0,
                2
            )
        }

    def promote_discovered_to_tracked(self, domain: str, custom_name: str = None) -> bool:
        """
        Promove um concorrente descoberto para monitoramento ativo.
        Args:
            domain: Domínio do concorrente descoberto
            custom_name: Nome customizado (opcional)
        Returns:
            True se bem-sucedido, False caso contrário
        """
        competitor = next((c for c in self.discovered_competitors if c["domain"] == domain), None)
        if not competitor:
            logger.warning(f"Concorrente com domínio {domain} não encontrado nos descobertos")
            return False

        name = custom_name or competitor.get("name", domain)
        base_url = competitor.get("url", f"https://{domain}")

        self.add_competitor(
            name=name,
            base_urls=[base_url],
            industry=competitor.get("industry", ""),
            keywords=competitor.get("keywords", [])
        )

        # Atualiza status
        competitor["status"] = "promoted"
        competitor["promoted_date"] = datetime.now().isoformat()
        self._save_discovered_competitors()

        logger.info(f"Concorrente {name} ({domain}) promovido para monitoramento ativo")
        return True

    def get_competitive_intelligence_report(self, your_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Gera relatório completo de inteligência competitiva.
        Args:
            your_keywords: Suas palavras-chave para comparação
        Returns:
            Relatório completo com insights acionáveis
        """
        content_summary = self.get_competitor_content_summary()
        discovered_report = self.get_discovered_competitors_report()

        # Análise de gaps de conteúdo
        competitor_topics = set()
        for item in self.competitor_content_db:
            competitor_topics.update(item.get("topics", []))

        # Tendências de palavras-chave
        recent_keywords = []
        cutoff = datetime.now() - timedelta(days=7)
        for item in self.competitor_content_db:
            if datetime.fromisoformat(item["timestamp"]) >= cutoff:
                recent_keywords.extend(item.get("keywords", []))
        trending_keywords = Counter(recent_keywords).most_common(10)

        # Concorrentes mais ativos
        activity_last_30_days = {}
        cutoff_30 = datetime.now() - timedelta(days=30)
        for item in self.competitor_content_db:
            if datetime.fromisoformat(item["timestamp"]) >= cutoff_30:
                comp = item["competitor"]
                activity_last_30_days[comp] = activity_last_30_days.get(comp, 0) + 1

        most_active = sorted(activity_last_30_days.items(), key=lambda x: x[1], reverse=True)[:5]

        # Análise de overlap de keywords
        keyword_overlap = {}
        if your_keywords:
            competitor_keywords = set()
            for item in self.competitor_content_db:
                competitor_keywords.update(item.get("keywords", []))

            overlap = set(kw.lower() for kw in your_keywords) & competitor_keywords
            unique_to_competitors = competitor_keywords - set(kw.lower() for kw in your_keywords)

            keyword_overlap = {
                "overlap": list(overlap),
                "unique_to_competitors": list(unique_to_competitors)[:20],
                "overlap_percentage": round(len(overlap) / len(your_keywords) * 100 if your_keywords else 0, 1)
            }

        return {
            "generated_at": datetime.now().isoformat(),
            "overview": {
                "total_competitors_tracked": len(self.competitors_config),
                "total_competitors_discovered": len(self.discovered_competitors),
                "total_content_analyzed": len(self.competitor_content_db),
            },
            "content_summary": content_summary,
            "discovered_competitors": discovered_report,
            "trending_keywords": [{"keyword": k, "mentions": v} for k, v in trending_keywords],
            "most_active_competitors": [{"name": name, "content_count": count} for name, count in most_active],
            "content_topics_identified": list(competitor_topics),
            "keyword_analysis": keyword_overlap,
            "recommendations": self._generate_recommendations(
                content_summary,
                trending_keywords,
                most_active,
                keyword_overlap
            )
        }

    def _generate_recommendations(self, content_summary: Dict, trending: List,
                                 active_competitors: List, keyword_analysis: Dict) -> List[str]:
        """Gera recomendações acionáveis baseadas na análise."""
        recommendations = []

        # Recomendação 1: Tópicos em alta
        if trending:
            top_trend = trending[0][0]
            recommendations.append(
                f"Criar conteúdo sobre '{top_trend}' - palavra-chave mais trending entre concorrentes"
            )

        # Recomendação 2: Concorrentes ativos
        if active_competitors:
            most_active_name = active_competitors[0][0]
            recommendations.append(
                f"Analisar estratégia de conteúdo de '{most_active_name}' - concorrente mais ativo"
            )

        # Recomendação 3: Gaps de keywords
        if keyword_analysis and keyword_analysis.get("unique_to_competitors"):
            unique_kw = keyword_analysis["unique_to_competitors"][:3]
            recommendations.append(
                f"Explorar keywords que concorrentes usam mas você não: {', '.join(unique_kw)}"
            )

        # Recomendação 4: Tópicos populares
        top_topics = content_summary.get("top_topics", [])
        if top_topics:
            topic = top_topics[0]["topic"]
            recommendations.append(
                f"Desenvolver estratégia focada em '{topic}' - tópico mais frequente no mercado"
            )

        # Recomendação 5: Sentimento
        sentiment = content_summary.get("sentiment_distribution", {})
        if sentiment.get("positivo", 0) > sentiment.get("negativo", 0):
            recommendations.append(
                "Concorrentes mantêm tom positivo - reforçar mensagens otimistas e cases de sucesso"
            )

        return recommendations

    def export_to_json(self, filepath: str = None) -> str:
        """
        Exporta todos os dados para arquivo JSON.
        Args:
            filepath: Caminho do arquivo (opcional)
        Returns:
            Caminho do arquivo criado
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.storage_path, f"export_{timestamp}.json")

        export_data = {
            "export_date": datetime.now().isoformat(),
            "competitors_config": self.competitors_config,
            "discovered_competitors": self.discovered_competitors,
            "content_database": self.competitor_content_db,
            "statistics": {
                "total_competitors": len(self.competitors_config),
                "total_discovered": len(self.discovered_competitors),
                "total_content_items": len(self.competitor_content_db)
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Dados exportados com sucesso para: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            raise

    def cleanup_old_content(self, days: int = 90):
        """
        Remove conteúdo antigo do banco de dados.
        Args:
            days: Conteúdo mais antigo que este número de dias será removido
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.competitor_content_db)

        self.competitor_content_db = [
            item for item in self.competitor_content_db
            if datetime.fromisoformat(item["timestamp"]) >= cutoff_date
        ]

        removed_count = original_count - len(self.competitor_content_db)

        if removed_count > 0:
            self._save_content_db()
            logger.info(f"Limpeza concluída: {removed_count} itens antigos removidos")
        else:
            logger.info("Nenhum item antigo para remover")

        return removed_count

# Exemplo de uso completo
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env.example'))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

    print("="*80)
    print("SISTEMA AVANÇADO DE INTELIGÊNCIA COMPETITIVA")
    print("="*80)

    collector = CompetitorContentCollector()

    # 1. DESCOBERTA AUTOMÁTICA DE CONCORRENTES
    print("\n📊 FASE 1: Descoberta Automática de Concorrentes")
    print("-"*80)

    your_business = "Plataforma SaaS de automação de marketing e vendas"
    your_keywords = ["automação de marketing", "crm", "vendas B2B", "email marketing", "lead nurturing"]

    discovered = collector.discover_competitors_from_search(
        your_business_description=your_business,
        your_keywords=your_keywords,
        location="Brasil",
        max_results=15
    )

    print(f"\n✅ Descobertos {len(discovered)} concorrentes relevantes:")
    for i, comp in enumerate(discovered[:5], 1):
        print(f"\n{i}. {comp['name']} ({comp['domain']})")
        print(f"   Relevância: {comp['relevance_score']*100:.1f}%")
        print(f"   Indústria: {comp['industry']}")
        print(f"   Keywords: {', '.join(comp['keywords'][:5])}")

    # 2. PROMOVER CONCORRENTES PARA MONITORAMENTO
    print("\n📌 FASE 2: Promovendo Concorrentes para Monitoramento Ativo")
    print("-"*80)

    if len(discovered) > 0:
        # Promove os 2 mais relevantes
        for comp in discovered[:2]:
            success = collector.promote_discovered_to_tracked(comp['domain'])
            if success:
                print(f"✅ {comp['name']} adicionado ao monitoramento ativo")

    # 3. ADICIONAR CONCORRENTES MANUALMENTE
    print("\n➕ FASE 3: Adicionando Concorrentes Manualmente")
    print("-"*80)

    collector.add_competitor(
        name="HubSpot Brasil",
        base_urls=["https://www.hubspot.com.br"],
        industry="Marketing & Sales Tech",
        keywords=["inbound marketing", "crm", "automação"]
    )
    print("✅ HubSpot Brasil adicionado")

    collector.add_competitor(
        name="RD Station",
        base_urls=["https://www.rdstation.com"],
        industry="Marketing Automation",
        keywords=["marketing digital", "automação", "leads"]
    )
    print("✅ RD Station adicionado")

    # 4. COLETA E ANÁLISE DE CONTEÚDO
    print("\n🔍 FASE 4: Coletando e Analisando Conteúdo")
    print("-"*80)

    for competitor in ["HubSpot Brasil", "RD Station"]:
        print(f"\nAnalisando: {competitor}")
        new_content = collector.collect_and_analyze_content(
            competitor_name=competitor,
            deep_crawl=False  # True para rastreamento profundo real
        )
        print(f"✅ {len(new_content)} novos itens coletados")

    # 5. RELATÓRIO DE INTELIGÊNCIA COMPETITIVA
    print("\n📈 FASE 5: Relatório de Inteligência Competitiva")
    print("="*80)

    report = collector.get_competitive_intelligence_report(your_keywords=your_keywords)

    print(f"\n🎯 OVERVIEW:")
    print(f"  • Concorrentes Monitorados: {report['overview']['total_competitors_tracked']}")
    print(f"  • Concorrentes Descobertos: {report['overview']['total_competitors_discovered']}")
    print(f"  • Conteúdos Analisados: {report['overview']['total_content_analyzed']}")

    print(f"\n🔥 KEYWORDS TRENDING (últimos 7 dias):")
    for kw in report['trending_keywords'][:5]:
        print(f"  • {kw['keyword']}: {kw['mentions']} menções")

    print(f"\n⚡ CONCORRENTES MAIS ATIVOS:")
    for comp in report['most_active_competitors']:
        print(f"  • {comp['name']}: {comp['content_count']} conteúdos publicados")

    print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")

    # 6. RESUMO DE CONTEÚDO
    print("\n📑 FASE 6: Resumo de Conteúdo Coletado")
    print("-"*80)

    summary = collector.get_competitor_content_summary(days=30)
    print(f"\n📊 Últimos 30 dias:")
    print(f"  • Total de itens: {summary['total_content_items']}")
    print(f"  • Concorrentes ativos: {summary['competitors_tracked']}")

    print(f"\n🏷️  Top Palavras-chave:")
    for kw in summary['top_keywords'][:8]:
        print(f"  • {kw['keyword']}: {kw['count']} ocorrências")

    print(f"\n📚 Top Tópicos:")
    for topic in summary['top_topics'][:5]:
        print(f"  • {topic['topic']}: {topic['count']} ocorrências")

    print(f"\n😊 Sentimento do Conteúdo:")
    for sentiment, count in summary['sentiment_distribution'].items():
        print(f"  • {sentiment.capitalize()}: {count} itens")

    # 7. RELATÓRIO DE DESCOBERTOS
    print("\n🔎 FASE 7: Análise de Concorrentes Descobertos")
    print("-"*80)

    discovered_report = collector.get_discovered_competitors_report(min_score=0.6)
    print(f"\n📍 Total descobertos (score ≥ 60%): {discovered_report['total_discovered']}")
    print(f"📊 Score médio de relevância: {discovered_report['average_relevance_score']*100:.1f}%")

    print(f"\n🏢 Por Indústria:")
    for industry, count in discovered_report['industries'].items():
        print(f"  • {industry}: {count} empresas")

    print(f"\n📱 Presença em Redes Sociais:")
    for platform, count in discovered_report['social_media_presence'].items():
        print(f"  • {platform.capitalize()}: {count} empresas")

    # 8. EXPORTAR DADOS
    print("\n💾 FASE 8: Exportando Dados")
    print("-"*80)

    export_path = collector.export_to_json()
    print(f"✅ Dados exportados para: {export_path}")

    # 9. LIMPEZA (OPCIONAL)
    print("\n🧹 FASE 9: Limpeza de Dados Antigos")
    print("-"*80)

    removed = collector.cleanup_old_content(days=90)
    print(f"✅ {removed} itens antigos removidos (>90 dias)")

    print("\n" + "="*80)
    print("✨ ANÁLISE COMPLETA FINALIZADA!")
    print("="*80)