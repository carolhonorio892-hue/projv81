#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENHANCED VIRAL IMAGE OPTIMIZER - V400
Otimizador para melhorar taxa de sucesso de imagens relevantes
Implementa múltiplas estratégias de busca e validação de imagens
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import re

try:
    import aiohttp
    import aiofiles
    from PIL import Image
    import requests
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

logger = logging.getLogger(__name__)

class EnhancedViralImageOptimizer:
    """Otimizador avançado para captura de imagens virais relevantes"""
    
    def __init__(self):
        self.session = None
        self.image_quality_threshold = 0.7
        self.relevance_threshold = 0.8
        self.max_images_per_search = 20
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
        
        # APIs para busca de imagens
        self.search_apis = {
            'serper': self._load_serper_keys(),
            'google_custom': self._load_google_keys(),
            'bing': self._load_bing_keys()
        }
        
        logger.info("🎯 Enhanced Viral Image Optimizer inicializado")
    
    def _load_serper_keys(self) -> List[str]:
        """Carrega chaves Serper API"""
        keys = []
        for i in range(1, 6):
            key = os.getenv(f'SERPER_API_KEY_{i}', os.getenv('SERPER_API_KEY'))
            if key:
                keys.append(key)
        return keys
    
    def _load_google_keys(self) -> List[Dict[str, str]]:
        """Carrega chaves Google Custom Search"""
        keys = []
        for i in range(1, 4):
            api_key = os.getenv(f'GOOGLE_SEARCH_KEY_{i}', os.getenv('GOOGLE_SEARCH_KEY'))
            cse_id = os.getenv(f'GOOGLE_CSE_ID_{i}', os.getenv('GOOGLE_CSE_ID'))
            if api_key and cse_id:
                keys.append({'api_key': api_key, 'cse_id': cse_id})
        return keys
    
    def _load_bing_keys(self) -> List[str]:
        """Carrega chaves Bing Search API"""
        keys = []
        for i in range(1, 4):
            key = os.getenv(f'BING_SEARCH_KEY_{i}')
            if key:
                keys.append(key)
        return keys
    
    async def optimize_image_search(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """
        Busca otimizada de imagens com múltiplas estratégias
        
        Args:
            query: Termo de busca
            context: Contexto adicional para relevância
            
        Returns:
            Lista de imagens otimizadas com metadados
        """
        try:
            # Estratégia 1: Busca com múltiplas APIs
            all_images = []
            
            # Serper API
            if self.search_apis['serper']:
                serper_images = await self._search_with_serper(query, context)
                all_images.extend(serper_images)
            
            # Google Custom Search
            if self.search_apis['google_custom']:
                google_images = await self._search_with_google(query, context)
                all_images.extend(google_images)
            
            # Bing Search
            if self.search_apis['bing']:
                bing_images = await self._search_with_bing(query, context)
                all_images.extend(bing_images)
            
            # Estratégia 2: Filtrar e validar imagens
            validated_images = await self._validate_images(all_images, query, context)
            
            # Estratégia 3: Ranking por relevância
            ranked_images = await self._rank_by_relevance(validated_images, query, context)
            
            # Estratégia 4: Otimização final
            optimized_images = await self._optimize_final_selection(ranked_images)
            
            logger.info(f"🎯 Otimização concluída: {len(optimized_images)} imagens de alta qualidade")
            return optimized_images[:8]  # Máximo 8 imagens
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização de imagens: {e}")
            return []
    
    async def _search_with_serper(self, query: str, context: str) -> List[Dict[str, Any]]:
        """Busca com Serper API"""
        images = []
        
        for api_key in self.search_apis['serper']:
            try:
                # Múltiplas variações da query
                queries = [
                    f"{query} viral post instagram",
                    f"{query} trending social media",
                    f"{query} popular content {context}",
                    f"{query} high engagement post"
                ]
                
                for search_query in queries:
                    async with aiohttp.ClientSession() as session:
                        headers = {
                            'X-API-KEY': api_key,
                            'Content-Type': 'application/json'
                        }
                        
                        payload = {
                            'q': search_query,
                            'type': 'images',
                            'num': 10,
                            'safe': 'off'
                        }
                        
                        async with session.post(
                            'https://google.serper.dev/images',
                            headers=headers,
                            json=payload
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                for img in data.get('images', []):
                                    images.append({
                                        'url': img.get('imageUrl'),
                                        'title': img.get('title', ''),
                                        'source': img.get('link', ''),
                                        'width': img.get('imageWidth', 0),
                                        'height': img.get('imageHeight', 0),
                                        'api_source': 'serper',
                                        'search_query': search_query,
                                        'relevance_score': 0.0
                                    })
                
                break  # Se sucesso, não tenta próxima chave
                
            except Exception as e:
                logger.warning(f"⚠️ Erro com Serper API: {e}")
                continue
        
        return images
    
    async def _search_with_google(self, query: str, context: str) -> List[Dict[str, Any]]:
        """Busca com Google Custom Search"""
        images = []
        
        for config in self.search_apis['google_custom']:
            try:
                queries = [
                    f"{query} viral instagram post",
                    f"{query} social media trending",
                    f"{query} popular {context}"
                ]
                
                for search_query in queries:
                    url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        'key': config['api_key'],
                        'cx': config['cse_id'],
                        'q': search_query,
                        'searchType': 'image',
                        'num': 10,
                        'safe': 'off',
                        'imgSize': 'large'
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                for item in data.get('items', []):
                                    images.append({
                                        'url': item.get('link'),
                                        'title': item.get('title', ''),
                                        'source': item.get('image', {}).get('contextLink', ''),
                                        'width': item.get('image', {}).get('width', 0),
                                        'height': item.get('image', {}).get('height', 0),
                                        'api_source': 'google_custom',
                                        'search_query': search_query,
                                        'relevance_score': 0.0
                                    })
                
                break
                
            except Exception as e:
                logger.warning(f"⚠️ Erro com Google Custom Search: {e}")
                continue
        
        return images
    
    async def _search_with_bing(self, query: str, context: str) -> List[Dict[str, Any]]:
        """Busca com Bing Search API"""
        images = []
        
        for api_key in self.search_apis['bing']:
            try:
                queries = [
                    f"{query} viral social media post",
                    f"{query} trending content {context}",
                    f"{query} popular instagram"
                ]
                
                for search_query in queries:
                    headers = {'Ocp-Apim-Subscription-Key': api_key}
                    params = {
                        'q': search_query,
                        'count': 10,
                        'safeSearch': 'Off',
                        'size': 'Large'
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            'https://api.bing.microsoft.com/v7.0/images/search',
                            headers=headers,
                            params=params
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                for img in data.get('value', []):
                                    images.append({
                                        'url': img.get('contentUrl'),
                                        'title': img.get('name', ''),
                                        'source': img.get('hostPageUrl', ''),
                                        'width': img.get('width', 0),
                                        'height': img.get('height', 0),
                                        'api_source': 'bing',
                                        'search_query': search_query,
                                        'relevance_score': 0.0
                                    })
                
                break
                
            except Exception as e:
                logger.warning(f"⚠️ Erro com Bing Search: {e}")
                continue
        
        return images
    
    async def _validate_images(self, images: List[Dict[str, Any]], query: str, context: str) -> List[Dict[str, Any]]:
        """Valida qualidade e relevância das imagens"""
        validated = []
        
        for img in images:
            try:
                # Validação 1: URL válida
                if not img.get('url') or not img['url'].startswith(('http://', 'https://')):
                    continue
                
                # Validação 2: Formato suportado
                url_lower = img['url'].lower()
                if not any(fmt in url_lower for fmt in self.supported_formats):
                    continue
                
                # Validação 3: Dimensões mínimas
                width = img.get('width', 0)
                height = img.get('height', 0)
                if width < 200 or height < 200:
                    continue
                
                # Validação 4: Relevância do título
                title = img.get('title', '').lower()
                query_words = query.lower().split()
                context_words = context.lower().split() if context else []
                
                relevance_score = 0.0
                for word in query_words:
                    if word in title:
                        relevance_score += 0.3
                
                for word in context_words:
                    if word in title:
                        relevance_score += 0.2
                
                # Bonus para palavras-chave virais
                viral_keywords = ['viral', 'trending', 'popular', 'engagement', 'likes', 'shares']
                for keyword in viral_keywords:
                    if keyword in title:
                        relevance_score += 0.1
                
                img['relevance_score'] = min(relevance_score, 1.0)
                
                # Só aceita se relevância >= threshold
                if img['relevance_score'] >= self.relevance_threshold * 0.5:  # Threshold mais flexível
                    validated.append(img)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro validando imagem: {e}")
                continue
        
        logger.info(f"✅ Validação: {len(validated)}/{len(images)} imagens aprovadas")
        return validated
    
    async def _rank_by_relevance(self, images: List[Dict[str, Any]], query: str, context: str) -> List[Dict[str, Any]]:
        """Ranking por relevância e qualidade"""
        
        for img in images:
            score = img.get('relevance_score', 0.0)
            
            # Bonus por dimensões
            width = img.get('width', 0)
            height = img.get('height', 0)
            if width >= 800 and height >= 600:
                score += 0.2
            elif width >= 400 and height >= 300:
                score += 0.1
            
            # Bonus por fonte confiável
            source = img.get('source', '').lower()
            trusted_sources = ['instagram.com', 'facebook.com', 'twitter.com', 'linkedin.com']
            if any(trusted in source for trusted in trusted_sources):
                score += 0.15
            
            # Bonus por API source
            api_source = img.get('api_source', '')
            if api_source == 'google_custom':
                score += 0.1
            elif api_source == 'serper':
                score += 0.05
            
            img['final_score'] = min(score, 1.0)
        
        # Ordena por score final
        ranked = sorted(images, key=lambda x: x.get('final_score', 0.0), reverse=True)
        
        logger.info(f"🏆 Ranking concluído: melhor score = {ranked[0].get('final_score', 0.0) if ranked else 0.0}")
        return ranked
    
    async def _optimize_final_selection(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Seleção final otimizada"""
        
        if not images:
            return []
        
        # Remove duplicatas por URL
        seen_urls = set()
        unique_images = []
        
        for img in images:
            url = img.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_images.append(img)
        
        # Diversifica por fonte
        final_selection = []
        sources_used = set()
        
        # Primeiro, pega as melhores de cada fonte
        for img in unique_images:
            source = img.get('api_source', 'unknown')
            if source not in sources_used and len(final_selection) < 8:
                final_selection.append(img)
                sources_used.add(source)
        
        # Depois, completa com as melhores restantes
        for img in unique_images:
            if img not in final_selection and len(final_selection) < 8:
                final_selection.append(img)
        
        # Adiciona metadados finais
        for i, img in enumerate(final_selection):
            img['selection_rank'] = i + 1
            img['optimization_timestamp'] = datetime.now().isoformat()
            img['quality_rating'] = 'high' if img.get('final_score', 0) > 0.7 else 'medium'
        
        logger.info(f"🎯 Seleção final: {len(final_selection)} imagens otimizadas")
        return final_selection

    async def download_and_validate_image(self, image_data: Dict[str, Any], save_path: Path) -> Optional[Dict[str, Any]]:
        """Download e validação de imagem individual"""
        try:
            url = image_data.get('url')
            if not url:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Salva arquivo
                        filename = f"viral_image_{hashlib.md5(url.encode()).hexdigest()[:8]}.jpg"
                        file_path = save_path / filename
                        
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(content)
                        
                        # Valida imagem com PIL
                        try:
                            with Image.open(file_path) as img:
                                width, height = img.size
                                format_type = img.format
                                
                                # Atualiza metadados
                                image_data.update({
                                    'local_path': str(file_path),
                                    'filename': filename,
                                    'actual_width': width,
                                    'actual_height': height,
                                    'format': format_type,
                                    'file_size': len(content),
                                    'download_success': True,
                                    'download_timestamp': datetime.now().isoformat()
                                })
                                
                                logger.info(f"✅ Imagem baixada: {filename} ({width}x{height})")
                                return image_data
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Erro validando imagem {filename}: {e}")
                            # Remove arquivo inválido
                            if file_path.exists():
                                file_path.unlink()
                            return None
            
        except Exception as e:
            logger.error(f"❌ Erro baixando imagem: {e}")
            return None
        
        return None