#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIRAL POSTS REPORT INTEGRATION - V400
Integra posts virais baixados no relatório final HTML
Máximo 8 posts, 4 por página, com descrições detalhadas das imagens
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class ViralPostsReportIntegration:
    """Integrador de posts virais no relatório final"""
    
    def __init__(self):
        self.max_posts = 8
        self.posts_per_page = 4
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        logger.info("📊 Viral Posts Report Integration inicializado")
    
    def integrate_viral_posts_to_report(self, session_dir: Path, viral_data: List[Dict[str, Any]]) -> str:
        """
        Integra posts virais ao relatório HTML
        
        Args:
            session_dir: Diretório da sessão
            viral_data: Dados dos posts virais
            
        Returns:
            HTML formatado com posts virais
        """
        try:
            # Seleciona os melhores posts
            selected_posts = self._select_best_posts(viral_data)
            
            # Gera HTML dos posts
            html_content = self._generate_viral_posts_html(selected_posts, session_dir)
            
            logger.info(f"✅ {len(selected_posts)} posts virais integrados ao relatório")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro integrando posts virais: {e}")
            return self._generate_fallback_html()
    
    def _select_best_posts(self, viral_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Seleciona os melhores posts virais baseado em métricas"""
        
        if not viral_data:
            return []
        
        # Filtra posts com imagens válidas
        posts_with_images = []
        for post in viral_data:
            if self._has_valid_images(post):
                posts_with_images.append(post)
        
        # Calcula score de relevância para cada post
        for post in posts_with_images:
            score = self._calculate_post_score(post)
            post['relevance_score'] = score
        
        # Ordena por score e pega os melhores
        sorted_posts = sorted(posts_with_images, key=lambda x: x.get('relevance_score', 0), reverse=True)
        selected = sorted_posts[:self.max_posts]
        
        logger.info(f"🎯 Selecionados {len(selected)} posts de {len(viral_data)} disponíveis")
        return selected
    
    def _has_valid_images(self, post: Dict[str, Any]) -> bool:
        """Verifica se o post tem imagens válidas"""
        
        # Verifica imagens baixadas
        images = post.get('images', [])
        if images:
            for img in images:
                if img.get('local_path') and Path(img['local_path']).exists():
                    return True
        
        # Verifica screenshots
        screenshots = post.get('screenshots', [])
        if screenshots:
            for screenshot in screenshots:
                if isinstance(screenshot, str) and Path(screenshot).exists():
                    return True
                elif isinstance(screenshot, dict) and screenshot.get('path'):
                    if Path(screenshot['path']).exists():
                        return True
        
        # Verifica visual_content
        visual_content = post.get('visual_content', {})
        if visual_content.get('screenshots'):
            for screenshot in visual_content['screenshots']:
                if Path(screenshot).exists():
                    return True
        
        return False
    
    def _calculate_post_score(self, post: Dict[str, Any]) -> float:
        """Calcula score de relevância do post"""
        
        score = 0.0
        
        # Score por engajamento
        engagement = post.get('engagement', {})
        likes = engagement.get('likes', 0)
        comments = engagement.get('comments', 0)
        shares = engagement.get('shares', 0)
        
        # Normaliza métricas (assumindo valores típicos)
        if likes > 0:
            score += min(likes / 10000, 0.3)  # Máximo 0.3 por likes
        if comments > 0:
            score += min(comments / 1000, 0.2)  # Máximo 0.2 por comments
        if shares > 0:
            score += min(shares / 500, 0.2)  # Máximo 0.2 por shares
        
        # Score por qualidade do conteúdo
        content = post.get('content', {})
        text = content.get('text', '') or post.get('text', '')
        
        if text:
            # Bonus por tamanho do texto (conteúdo substancial)
            if len(text) > 100:
                score += 0.1
            
            # Bonus por palavras-chave virais
            viral_keywords = ['viral', 'trending', 'popular', 'amazing', 'incredible', 'must-see']
            text_lower = text.lower()
            for keyword in viral_keywords:
                if keyword in text_lower:
                    score += 0.05
        
        # Score por qualidade das imagens
        images = post.get('images', [])
        if images:
            score += min(len(images) * 0.1, 0.2)  # Bonus por múltiplas imagens
        
        # Score por fonte confiável
        source = post.get('source', {})
        platform = source.get('platform', '').lower()
        if platform in ['instagram', 'facebook', 'twitter', 'linkedin']:
            score += 0.1
        
        # Score por data recente
        timestamp = post.get('timestamp') or post.get('created_at')
        if timestamp:
            try:
                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.now() - post_date.replace(tzinfo=None)).days
                if days_old <= 7:
                    score += 0.15  # Bonus por conteúdo recente
                elif days_old <= 30:
                    score += 0.1
            except:
                pass
        
        return min(score, 1.0)  # Máximo 1.0
    
    def _generate_viral_posts_html(self, posts: List[Dict[str, Any]], session_dir: Path) -> str:
        """Gera HTML formatado dos posts virais"""
        
        if not posts:
            return self._generate_fallback_html()
        
        html_parts = []
        
        # Cabeçalho da seção
        html_parts.append("""
<hr />
<h2 id="conteúdo-viral-analisado">🔥 CONTEÚDO VIRAL ANALISADO</h2>
<p><strong>Posts Selecionados:</strong> {total_posts} | <strong>Critério:</strong> Alto engajamento e relevância</p>
<p><em>Análise baseada em métricas reais de engajamento, qualidade visual e relevância temática.</em></p>
""".format(total_posts=len(posts)))
        
        # Divide posts em páginas (4 por página)
        pages = [posts[i:i + self.posts_per_page] for i in range(0, len(posts), self.posts_per_page)]
        
        for page_num, page_posts in enumerate(pages, 1):
            html_parts.append(f"""
<h3 id="página-{page_num}-posts-virais">📄 Página {page_num} - Posts Virais</h3>
""")
            
            for post_num, post in enumerate(page_posts, 1):
                post_html = self._generate_single_post_html(post, session_dir, page_num, post_num)
                html_parts.append(post_html)
        
        # Resumo estatístico
        stats_html = self._generate_viral_stats_html(posts)
        html_parts.append(stats_html)
        
        return '\n'.join(html_parts)
    
    def _generate_single_post_html(self, post: Dict[str, Any], session_dir: Path, page_num: int, post_num: int) -> str:
        """Gera HTML de um post individual"""
        
        # Extrai dados do post
        content = post.get('content', {})
        text = content.get('text', '') or post.get('text', '') or post.get('description', '')
        
        engagement = post.get('engagement', {})
        likes = engagement.get('likes', 0)
        comments = engagement.get('comments', 0)
        shares = engagement.get('shares', 0)
        
        source = post.get('source', {})
        platform = source.get('platform', 'Desconhecido')
        url = source.get('url', '') or post.get('url', '')
        
        score = post.get('relevance_score', 0.0)
        
        # Trunca texto se muito longo
        if len(text) > 300:
            text = text[:297] + "..."
        
        # Gera HTML das imagens
        images_html = self._generate_post_images_html(post, session_dir)
        
        # HTML do post
        post_html = f"""
<div style="border: 2px solid #e1e5e9; border-radius: 8px; padding: 20px; margin: 20px 0; background: #f8f9fa;">
    <h4 id="post-viral-{page_num}-{post_num}">🔥 Post Viral #{page_num}.{post_num}</h4>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
        <div>
            <p><strong>📱 Plataforma:</strong> {platform}</p>
            <p><strong>⭐ Score de Relevância:</strong> {score:.2f}/1.00</p>
            <p><strong>🔗 URL:</strong> <a href="{url}" target="_blank">Ver Post Original</a></p>
        </div>
        <div>
            <p><strong>👍 Likes:</strong> {likes:,}</p>
            <p><strong>💬 Comentários:</strong> {comments:,}</p>
            <p><strong>🔄 Compartilhamentos:</strong> {shares:,}</p>
        </div>
    </div>
    
    <div style="margin: 15px 0;">
        <p><strong>📝 Conteúdo:</strong></p>
        <blockquote style="background: #fff; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0; font-style: italic;">
            {text or "Conteúdo visual sem texto descritivo"}
        </blockquote>
    </div>
    
    {images_html}
</div>
"""
        
        return post_html
    
    def _generate_post_images_html(self, post: Dict[str, Any], session_dir: Path) -> str:
        """Gera HTML das imagens do post"""
        
        images_html_parts = []
        image_count = 0
        
        # Processa imagens baixadas
        images = post.get('images', [])
        for img in images:
            if image_count >= 3:  # Máximo 3 imagens por post
                break
                
            local_path = img.get('local_path')
            if local_path and Path(local_path).exists():
                # Caminho relativo para o HTML
                rel_path = Path(local_path).relative_to(session_dir.parent)
                
                title = img.get('title', f'Imagem {image_count + 1}')
                description = self._generate_image_description(img, post)
                
                img_html = f"""
<div style="margin: 10px 0;">
    <figure style="text-align: center;">
        <img src="{rel_path}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
        <figcaption style="margin-top: 8px; font-size: 0.9em; color: #666;">
            <strong>{title}</strong><br />
            {description}
        </figcaption>
    </figure>
</div>
"""
                images_html_parts.append(img_html)
                image_count += 1
        
        # Processa screenshots se não há imagens suficientes
        if image_count < 2:
            screenshots = post.get('screenshots', [])
            for screenshot in screenshots:
                if image_count >= 3:
                    break
                
                screenshot_path = None
                if isinstance(screenshot, str):
                    screenshot_path = screenshot
                elif isinstance(screenshot, dict):
                    screenshot_path = screenshot.get('path')
                
                if screenshot_path and Path(screenshot_path).exists():
                    rel_path = Path(screenshot_path).relative_to(session_dir.parent)
                    
                    img_html = f"""
<div style="margin: 10px 0;">
    <figure style="text-align: center;">
        <img src="{rel_path}" alt="Screenshot do Post" style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
        <figcaption style="margin-top: 8px; font-size: 0.9em; color: #666;">
            <strong>Screenshot do Post Viral</strong><br />
            Captura da tela do conteúdo original na plataforma
        </figcaption>
    </figure>
</div>
"""
                    images_html_parts.append(img_html)
                    image_count += 1
        
        if images_html_parts:
            return f"""
<div style="margin: 15px 0;">
    <p><strong>🖼️ Conteúdo Visual ({image_count} imagem{'ns' if image_count != 1 else ''}):</strong></p>
    {''.join(images_html_parts)}
</div>
"""
        else:
            return """
<div style="margin: 15px 0;">
    <p><strong>🖼️ Conteúdo Visual:</strong> <em>Imagens não disponíveis localmente</em></p>
</div>
"""
    
    def _generate_image_description(self, img: Dict[str, Any], post: Dict[str, Any]) -> str:
        """Gera descrição inteligente da imagem"""
        
        descriptions = []
        
        # Informações técnicas
        width = img.get('actual_width') or img.get('width', 0)
        height = img.get('actual_height') or img.get('height', 0)
        if width and height:
            descriptions.append(f"Resolução: {width}x{height}px")
        
        # Fonte da imagem
        source = img.get('source', '')
        if source:
            domain = re.findall(r'https?://([^/]+)', source)
            if domain:
                descriptions.append(f"Fonte: {domain[0]}")
        
        # Score de relevância
        score = img.get('relevance_score', 0)
        if score > 0:
            descriptions.append(f"Relevância: {score:.1f}/1.0")
        
        # Contexto do post
        platform = post.get('source', {}).get('platform', '')
        if platform:
            descriptions.append(f"Plataforma: {platform}")
        
        return " | ".join(descriptions) if descriptions else "Imagem viral de alta qualidade"
    
    def _generate_viral_stats_html(self, posts: List[Dict[str, Any]]) -> str:
        """Gera estatísticas dos posts virais"""
        
        if not posts:
            return ""
        
        # Calcula estatísticas
        total_likes = sum(post.get('engagement', {}).get('likes', 0) for post in posts)
        total_comments = sum(post.get('engagement', {}).get('comments', 0) for post in posts)
        total_shares = sum(post.get('engagement', {}).get('shares', 0) for post in posts)
        
        avg_score = sum(post.get('relevance_score', 0) for post in posts) / len(posts)
        
        platforms = {}
        for post in posts:
            platform = post.get('source', {}).get('platform', 'Desconhecido')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        platforms_list = [f"{platform}: {count}" for platform, count in platforms.items()]
        
        return f"""
<hr />
<h3 id="estatísticas-do-conteúdo-viral">📊 Estatísticas do Conteúdo Viral</h3>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">
    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
        <h4>💫 Engajamento Total</h4>
        <p><strong>👍 Likes:</strong> {total_likes:,}</p>
        <p><strong>💬 Comentários:</strong> {total_comments:,}</p>
        <p><strong>🔄 Shares:</strong> {total_shares:,}</p>
    </div>
    <div style="background: #f3e5f5; padding: 15px; border-radius: 8px;">
        <h4>⭐ Qualidade Média</h4>
        <p><strong>Score de Relevância:</strong> {avg_score:.2f}/1.00</p>
        <p><strong>Posts Analisados:</strong> {len(posts)}</p>
        <p><strong>Critério:</strong> Alto engajamento</p>
    </div>
    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px;">
        <h4>📱 Distribuição por Plataforma</h4>
        {'<br />'.join(f'<p><strong>{item}</strong></p>' for item in platforms_list)}
    </div>
</div>

<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <h4>🎯 Insights Estratégicos</h4>
    <ul>
        <li><strong>Padrões de Sucesso:</strong> Posts com maior engajamento tendem a ter conteúdo visual impactante</li>
        <li><strong>Timing Ideal:</strong> Conteúdo recente (últimos 30 dias) apresenta melhor performance</li>
        <li><strong>Formato Vencedor:</strong> Combinação de imagem + texto descritivo gera mais interação</li>
        <li><strong>Plataformas Eficazes:</strong> {', '.join(platforms.keys()) if platforms else 'Múltiplas plataformas analisadas'}</li>
    </ul>
</div>
"""
    
    def _generate_fallback_html(self) -> str:
        """Gera HTML de fallback quando não há posts"""
        
        return """
<hr />
<h2 id="conteúdo-viral-analisado">🔥 CONTEÚDO VIRAL ANALISADO</h2>
<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <h4>⚠️ Posts Virais Não Disponíveis</h4>
    <p>Nenhum post viral foi encontrado ou baixado durante esta análise.</p>
    <p><strong>Possíveis causas:</strong></p>
    <ul>
        <li>APIs de busca temporariamente indisponíveis</li>
        <li>Critérios de relevância muito restritivos</li>
        <li>Problemas de conectividade durante a coleta</li>
    </ul>
    <p><em>Recomendação: Execute uma nova análise com termos de busca mais amplos.</em></p>
</div>
"""

    def extract_viral_data_from_session(self, session_dir: Path) -> List[Dict[str, Any]]:
        """Extrai dados de posts virais dos arquivos da sessão"""
        
        viral_data = []
        
        try:
            # Procura por arquivos de dados virais
            viral_files = list(session_dir.glob("*viral*.json"))
            viral_files.extend(list(session_dir.glob("*posts*.json")))
            viral_files.extend(list(session_dir.glob("*social*.json")))
            
            for file_path in viral_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        if isinstance(data, list):
                            viral_data.extend(data)
                        elif isinstance(data, dict):
                            # Se é um dict, pode ser um post único ou container
                            if 'posts' in data:
                                viral_data.extend(data['posts'])
                            elif 'results' in data:
                                viral_data.extend(data['results'])
                            else:
                                viral_data.append(data)
                                
                except Exception as e:
                    logger.warning(f"⚠️ Erro lendo arquivo viral {file_path}: {e}")
                    continue
            
            logger.info(f"📊 Extraídos {len(viral_data)} posts virais da sessão")
            return viral_data
            
        except Exception as e:
            logger.error(f"❌ Erro extraindo dados virais: {e}")
            return []