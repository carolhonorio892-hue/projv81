#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Application Logger
Sistema de log único e persistente para toda a aplicação
NUNCA limpa o log - mantém todo o histórico
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

class ApplicationLogger:
    """
    Logger único da aplicação com persistência total
    Mantém histórico completo em arquivo único
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ApplicationLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa logger único (apenas uma vez)"""
        if not ApplicationLogger._initialized:
            self.setup_logger()
            ApplicationLogger._initialized = True

    def setup_logger(self):
        """Configura logger único e persistente"""
        # Criar diretório de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Arquivo de log único
        self.log_file = log_dir / "application.log"

        # Configurar logger root
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Remove handlers existentes para evitar duplicação
        self.logger.handlers.clear()

        # Formato detalhado
        log_format = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para arquivo (com rotação para evitar arquivo gigante)
        # Max 50MB por arquivo, mantém 10 backups = 500MB total
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10,          # 10 backups
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

        # Log inicial
        self.log_separator("APLICAÇÃO INICIADA")
        self.info(f"Sistema de log único inicializado")
        self.info(f"Arquivo de log: {self.log_file.absolute()}")
        self.info(f"Nível de log: {logging.getLevelName(self.logger.level)}")

    def log_separator(self, title: str = ""):
        """Adiciona separador visual no log"""
        separator = "=" * 80
        self.logger.info(separator)
        if title:
            self.logger.info(f"  {title}")
            self.logger.info(separator)

    def info(self, message: str, module: Optional[str] = None):
        """Log nível INFO"""
        if module:
            self.logger.info(f"[{module}] {message}")
        else:
            self.logger.info(message)

    def success(self, message: str, module: Optional[str] = None):
        """Log de sucesso (INFO com marcador visual)"""
        if module:
            self.logger.info(f"✅ [{module}] {message}")
        else:
            self.logger.info(f"✅ {message}")

    def warning(self, message: str, module: Optional[str] = None):
        """Log nível WARNING"""
        if module:
            self.logger.warning(f"⚠️  [{module}] {message}")
        else:
            self.logger.warning(f"⚠️  {message}")

    def error(self, message: str, module: Optional[str] = None, exc_info: bool = False):
        """Log nível ERROR"""
        if module:
            self.logger.error(f"❌ [{module}] {message}", exc_info=exc_info)
        else:
            self.logger.error(f"❌ {message}", exc_info=exc_info)

    def critical(self, message: str, module: Optional[str] = None, exc_info: bool = True):
        """Log nível CRITICAL"""
        if module:
            self.logger.critical(f"🔥 [{module}] {message}", exc_info=exc_info)
        else:
            self.logger.critical(f"🔥 {message}", exc_info=exc_info)

    def debug(self, message: str, module: Optional[str] = None):
        """Log nível DEBUG"""
        if module:
            self.logger.debug(f"🔍 [{module}] {message}")
        else:
            self.logger.debug(f"🔍 {message}")

    def module_start(self, module_name: str, action: str = ""):
        """Log de início de módulo"""
        self.log_separator(f"MÓDULO: {module_name}")
        if action:
            self.info(f"Ação: {action}", module_name)

    def module_end(self, module_name: str, success: bool = True, duration: Optional[float] = None):
        """Log de fim de módulo"""
        status = "✅ SUCESSO" if success else "❌ FALHA"
        msg = f"Módulo {module_name} finalizado - {status}"
        if duration:
            msg += f" (duração: {duration:.2f}s)"
        self.info(msg, module_name)
        self.log_separator()

    def api_request(self, api_name: str, endpoint: str, method: str = "GET"):
        """Log de requisição API"""
        self.info(f"API Request: {method} {endpoint}", api_name)

    def api_response(self, api_name: str, status_code: int, success: bool):
        """Log de resposta API"""
        if success:
            self.success(f"API Response: {status_code}", api_name)
        else:
            self.error(f"API Response: {status_code}", api_name)

    def workflow_step(self, step_name: str, step_number: int, total_steps: int):
        """Log de etapa do workflow"""
        self.info(f"⚙️  Etapa {step_number}/{total_steps}: {step_name}")

    def user_action(self, action: str, session_id: Optional[str] = None):
        """Log de ação do usuário"""
        if session_id:
            self.info(f"👤 Ação do usuário [{session_id}]: {action}")
        else:
            self.info(f"👤 Ação do usuário: {action}")

    def system_status(self, component: str, status: str, details: str = ""):
        """Log de status do sistema"""
        msg = f"🖥️  {component}: {status}"
        if details:
            msg += f" - {details}"
        self.info(msg)

    def data_operation(self, operation: str, entity: str, count: Optional[int] = None):
        """Log de operação com dados"""
        msg = f"💾 {operation} {entity}"
        if count is not None:
            msg += f" (quantidade: {count})"
        self.info(msg)

# Instância global do logger
app_logger = ApplicationLogger()

# Funções de conveniência para uso direto
def log_info(message: str, module: Optional[str] = None):
    """Atalho para log INFO"""
    app_logger.info(message, module)

def log_success(message: str, module: Optional[str] = None):
    """Atalho para log de sucesso"""
    app_logger.success(message, module)

def log_warning(message: str, module: Optional[str] = None):
    """Atalho para log WARNING"""
    app_logger.warning(message, module)

def log_error(message: str, module: Optional[str] = None, exc_info: bool = False):
    """Atalho para log ERROR"""
    app_logger.error(message, module, exc_info)

def log_critical(message: str, module: Optional[str] = None, exc_info: bool = True):
    """Atalho para log CRITICAL"""
    app_logger.critical(message, module, exc_info)

def log_debug(message: str, module: Optional[str] = None):
    """Atalho para log DEBUG"""
    app_logger.debug(message, module)

def log_separator(title: str = ""):
    """Atalho para separador"""
    app_logger.log_separator(title)

def log_module_start(module_name: str, action: str = ""):
    """Atalho para início de módulo"""
    app_logger.module_start(module_name, action)

def log_module_end(module_name: str, success: bool = True, duration: Optional[float] = None):
    """Atalho para fim de módulo"""
    app_logger.module_end(module_name, success, duration)

def log_api_request(api_name: str, endpoint: str, method: str = "GET"):
    """Atalho para requisição API"""
    app_logger.api_request(api_name, endpoint, method)

def log_api_response(api_name: str, status_code: int, success: bool):
    """Atalho para resposta API"""
    app_logger.api_response(api_name, status_code, success)

def log_workflow_step(step_name: str, step_number: int, total_steps: int):
    """Atalho para etapa do workflow"""
    app_logger.workflow_step(step_name, step_number, total_steps)

def log_user_action(action: str, session_id: Optional[str] = None):
    """Atalho para ação do usuário"""
    app_logger.user_action(action, session_id)

def log_system_status(component: str, status: str, details: str = ""):
    """Atalho para status do sistema"""
    app_logger.system_status(component, status, details)

def log_data_operation(operation: str, entity: str, count: Optional[int] = None):
    """Atalho para operação com dados"""
    app_logger.data_operation(operation, entity, count)
