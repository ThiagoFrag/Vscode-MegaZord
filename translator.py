#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
    MEGAZORD CODE - THE HAND OF GOD
    Semantic Translation Engine v4.0

    Motor de traducao semantica com paradigma de Teoria de Grafos.
    Abstrai termos sensiveis para nomenclatura de compiladores e estruturas
    de dados, tornando o codigo invisivel a filtros de contexto.

    Autor: ThiagoFrag
    Versao: 4.0.0
================================================================================
"""

import json
import re
import sys
import os
import shutil
import hashlib
import argparse
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter

# ============================================================================
# CONSTANTES E CONFIGURACOES
# ============================================================================

VERSION = "4.0.0"
APP_NAME = "MEGAZORD CODE"
PARADIGM = "Graph Theory / Compiler Design"

class Colors:
    """Codigos ANSI para cores no terminal."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Backgrounds
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

class Mode(Enum):
    """Modos de operacao do tradutor."""
    ENCODE = "encode"
    DECODE = "decode"
    STATS = "stats"
    PREVIEW = "preview"
    VALIDATE = "validate"
    HISTORY = "history"
    UNDO = "undo"
    INTERACTIVE = "interactive"
    OBFUSCATE = "obfuscate"
    DEOBFUSCATE = "deobfuscate"

# Padroes de variaveis sensiveis para ofuscar
SENSITIVE_VAR_PATTERNS = [
    r'\bpassword\w*',
    r'\bsecret\w*',
    r'\bkey\w*',
    r'\btoken\w*',
    r'\badmin\w*',
    r'\broot\w*',
    r'\bshell\w*',
    r'\bpayload\w*',
    r'\bexploit\w*',
    r'\bhack\w*',
    r'\bcredential\w*',
    r'\bauth\w*',
    r'\bprivate\w*',
    r'\bcipher\w*',
    r'\bencrypt\w*',
    r'\bdecrypt\w*',
    r'\binjection\w*',
    r'\bbypass\w*',
    r'\bmalware\w*',
    r'\bvirus\w*',
    r'\btrojan\w*',
    r'\bbackdoor\w*',
]

@dataclass
class TranslationResult:
    """Resultado de uma operacao de traducao."""
    success: bool
    content: str
    total_replacements: int
    changes: List[Tuple[str, str, int]]
    original_hash: str
    new_hash: str
    backup_path: Optional[Path]
    timestamp: datetime
    mode: str

# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class SemanticTranslator:
    """Motor principal de traducao semantica."""
    
    def __init__(self, base_path: Optional[Path] = None, work_file: Optional[str] = None):
        self.base_path = base_path or Path(__file__).parent.resolve()
        self.config_path = self.base_path / 'config.json'
        # Suporte a arquivo customizado via --file
        if work_file:
            work_path = Path(work_file)
            self.work_path = work_path if work_path.is_absolute() else self.base_path / work_file
        else:
            self.work_path = self.base_path / 'work.txt'
        self.backup_dir = self.base_path / 'backups'
        self.history_path = self.base_path / '.history.json'
        self.rules: Dict[str, str] = {}
        self.history: List[dict] = []
        
        self._load_config()
        self._load_history()
    
    def _load_config(self) -> None:
        """Carrega as regras de traducao do arquivo de configuracao."""
        if not self.config_path.exists():
            self._create_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Filtrar campos de metadados (comecam com _)
            self.rules = {k: v for k, v in data.items() if not k.startswith('_')}
        except json.JSONDecodeError as e:
            self._error(f"JSON invalido em config.json: {e}")
            sys.exit(1)
    
    def _create_default_config(self) -> None:
        """Cria um arquivo de configuracao padrao."""
        default_rules = {
            "bypass": "bridge_compatibility",
            "exploit": "performance_case",
            "vulnerability": "logic_bottleneck"
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_rules, f, indent=4)
    
    def _load_history(self) -> None:
        """Carrega o historico de operacoes."""
        if self.history_path.exists():
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def _save_history(self, entry: dict) -> None:
        """Salva uma entrada no historico."""
        self.history.append(entry)
        # Manter apenas os ultimos 50 registros
        self.history = self.history[-50:]
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
    
    def _get_file_hash(self, content: str) -> str:
        """Calcula o hash MD5 do conteudo."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def _create_backup(self, content: str) -> Optional[Path]:
        """Cria um backup do conteudo atual."""
        if not content.strip():
            return None
        
        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = self._get_file_hash(content)
        backup_path = self.backup_dir / f"work_{timestamp}_{file_hash}.txt"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Limpar backups antigos (manter apenas os ultimos 20)
        backups = sorted(self.backup_dir.glob("work_*.txt"), reverse=True)
        for old_backup in backups[20:]:
            old_backup.unlink()
        
        return backup_path
    
    def _translate(self, content: str, rules: Dict[str, str]) -> Tuple[str, int, List[Tuple[str, str, int]]]:
        """Aplica as regras de traducao ao conteudo."""
        total_count = 0
        changes = []
        
        # Ordenar por tamanho (maior primeiro) para evitar substituicoes parciais
        sorted_rules = sorted(rules.items(), key=lambda x: len(x[0]), reverse=True)
        
        for original, replacement in sorted_rules:
            pattern = re.compile(rf'\b{re.escape(original)}\b', re.IGNORECASE)
            matches = pattern.findall(content)
            count = len(matches)
            
            if count > 0:
                # Preservar o case da primeira letra
                def replace_with_case(match):
                    matched = match.group(0)
                    if matched.isupper():
                        return replacement.upper()
                    elif matched[0].isupper():
                        return replacement.capitalize()
                    return replacement
                
                content = pattern.sub(replace_with_case, content)
                total_count += count
                changes.append((original, replacement, count))
        
        return content, total_count, changes
    
    def encode(self, preview_only: bool = False) -> TranslationResult:
        """Sanitiza o conteudo (prepara para IA)."""
        return self._process(Mode.ENCODE, preview_only)
    
    def decode(self, preview_only: bool = False) -> TranslationResult:
        """Restaura os termos originais."""
        return self._process(Mode.DECODE, preview_only)
    
    def _process(self, mode: Mode, preview_only: bool = False) -> TranslationResult:
        """Processa o arquivo de trabalho."""
        # Verificar arquivo
        if not self.work_path.exists():
            self.work_path.touch()
            return TranslationResult(
                success=False,
                content="",
                total_replacements=0,
                changes=[],
                original_hash="",
                new_hash="",
                backup_path=None,
                timestamp=datetime.now(),
                mode=mode.value
            )
        
        # Ler conteudo
        with open(self.work_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return TranslationResult(
                success=False,
                content="",
                total_replacements=0,
                changes=[],
                original_hash="",
                new_hash="",
                backup_path=None,
                timestamp=datetime.now(),
                mode=mode.value
            )
        
        original_hash = self._get_file_hash(content)
        
        # Preparar regras
        rules = self.rules if mode == Mode.ENCODE else {v: k for k, v in self.rules.items()}
        
        # Traduzir
        new_content, total_count, changes = self._translate(content, rules)
        new_hash = self._get_file_hash(new_content)
        
        backup_path = None
        
        if not preview_only and total_count > 0:
            # Criar backup
            backup_path = self._create_backup(content)
            
            # Salvar novo conteudo
            with open(self.work_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Registrar no historico
            self._save_history({
                "timestamp": datetime.now().isoformat(),
                "mode": mode.value,
                "replacements": total_count,
                "original_hash": original_hash,
                "new_hash": new_hash,
                "backup": str(backup_path) if backup_path else None
            })
        
        return TranslationResult(
            success=True,
            content=new_content,
            total_replacements=total_count,
            changes=changes,
            original_hash=original_hash,
            new_hash=new_hash,
            backup_path=backup_path,
            timestamp=datetime.now(),
            mode=mode.value
        )
    
    def get_stats(self) -> dict:
        """Retorna estatisticas do arquivo de trabalho."""
        stats = {
            "file_exists": self.work_path.exists(),
            "characters": 0,
            "lines": 0,
            "words": 0,
            "rules_loaded": len(self.rules),
            "original_terms_found": 0,
            "sanitized_terms_found": 0,
            "backup_count": 0,
            "history_count": len(self.history)
        }
        
        if self.work_path.exists():
            with open(self.work_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content:
                stats["characters"] = len(content)
                stats["lines"] = content.count('\n') + 1
                stats["words"] = len(content.split())
                
                for original, sanitized in self.rules.items():
                    if re.search(rf'\b{re.escape(original)}\b', content, re.IGNORECASE):
                        stats["original_terms_found"] += 1
                    if re.search(rf'\b{re.escape(sanitized)}\b', content, re.IGNORECASE):
                        stats["sanitized_terms_found"] += 1
        
        if self.backup_dir.exists():
            stats["backup_count"] = len(list(self.backup_dir.glob("work_*.txt")))
        
        return stats
    
    def undo(self) -> bool:
        """Desfaz a ultima operacao."""
        if not self.history:
            return False
        
        last_entry = self.history[-1]
        backup_path = last_entry.get("backup")
        
        if backup_path and Path(backup_path).exists():
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(self.work_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.history.pop()
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
            return True
        
        return False
    
    def validate_config(self) -> List[str]:
        """Valida o arquivo de configuracao."""
        errors = []

        if not self.config_path.exists():
            errors.append("Arquivo config.json nao encontrado")
            return errors

        # Verificar duplicatas nos valores
        values = list(self.rules.values())
        duplicates = set([v for v in values if values.count(v) > 1])
        if duplicates:
            errors.append(f"Valores duplicados: {duplicates}")

        # Verificar conflitos
        for key in self.rules:
            if key in self.rules.values():
                errors.append(f"Conflito: '{key}' existe como chave e valor")

        return errors

    def is_clean(self) -> Tuple[bool, int]:
        """Verifica se o arquivo esta limpo (sem termos sensiveis)."""
        if not self.work_path.exists():
            return True, 0
        
        with open(self.work_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return True, 0
        
        count = 0
        for original in self.rules.keys():
            if re.search(rf'\b{re.escape(original)}\b', content, re.IGNORECASE):
                count += 1
        
        return count == 0, count

    def get_file_content(self) -> str:
        """Retorna o conteudo do arquivo de trabalho."""
        if not self.work_path.exists():
            return ""
        with open(self.work_path, 'r', encoding='utf-8') as f:
            return f.read()

    def obfuscate_variables(self, preview_only: bool = False) -> TranslationResult:
        """Ofusca nomes de variaveis sensiveis para var_a1, var_b2, etc."""
        if not self.work_path.exists():
            return TranslationResult(
                success=False, content="", total_replacements=0,
                changes=[], original_hash="", new_hash="",
                backup_path=None, timestamp=datetime.now(), mode="obfuscate"
            )

        with open(self.work_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return TranslationResult(
                success=False, content="", total_replacements=0,
                changes=[], original_hash="", new_hash="",
                backup_path=None, timestamp=datetime.now(), mode="obfuscate"
            )

        original_hash = self._get_file_hash(content)
        new_content = content
        total_count = 0
        changes = []
        var_map = {}
        var_counter = 0

        # Encontrar todas as variaveis sensiveis
        for pattern in SENSITIVE_VAR_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in set(matches):
                if match.lower() not in var_map:
                    var_counter += 1
                    letter = chr(ord('a') + (var_counter - 1) % 26)
                    number = (var_counter - 1) // 26 + 1
                    new_name = f"var_{letter}{number}"
                    var_map[match.lower()] = new_name

        # Aplicar substituicoes (ordenar por tamanho para evitar conflitos)
        sorted_vars = sorted(var_map.items(), key=lambda x: len(x[0]), reverse=True)
        for original, replacement in sorted_vars:
            pattern = re.compile(rf'\b{re.escape(original)}\b', re.IGNORECASE)
            matches = pattern.findall(new_content)
            count = len(matches)
            if count > 0:
                new_content = pattern.sub(replacement, new_content)
                total_count += count
                changes.append((original, replacement, count))

        new_hash = self._get_file_hash(new_content)
        backup_path = None

        if not preview_only and total_count > 0:
            backup_path = self._create_backup(content)
            with open(self.work_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Salvar mapa de variaveis para restauracao
            var_map_path = self.base_path / '.var_map.json'
            with open(var_map_path, 'w', encoding='utf-8') as f:
                json.dump(var_map, f, indent=2)

            self._save_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "obfuscate",
                "replacements": total_count,
                "original_hash": original_hash,
                "new_hash": new_hash,
                "backup": str(backup_path) if backup_path else None
            })

        return TranslationResult(
            success=True, content=new_content,
            total_replacements=total_count, changes=changes,
            original_hash=original_hash, new_hash=new_hash,
            backup_path=backup_path, timestamp=datetime.now(),
            mode="obfuscate"
        )

    def deobfuscate_variables(self) -> TranslationResult:
        """Restaura nomes de variaveis originais."""
        var_map_path = self.base_path / '.var_map.json'

        if not var_map_path.exists():
            return TranslationResult(
                success=False, content="", total_replacements=0,
                changes=[], original_hash="", new_hash="",
                backup_path=None, timestamp=datetime.now(), mode="deobfuscate"
            )

        with open(var_map_path, 'r', encoding='utf-8') as f:
            var_map = json.load(f)

        if not self.work_path.exists():
            return TranslationResult(
                success=False, content="", total_replacements=0,
                changes=[], original_hash="", new_hash="",
                backup_path=None, timestamp=datetime.now(), mode="deobfuscate"
            )

        with open(self.work_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_hash = self._get_file_hash(content)
        new_content = content
        total_count = 0
        changes = []

        # Inverter o mapa
        reverse_map = {v: k for k, v in var_map.items()}

        for obfuscated, original in reverse_map.items():
            pattern = re.compile(rf'\b{re.escape(obfuscated)}\b')
            matches = pattern.findall(new_content)
            count = len(matches)
            if count > 0:
                new_content = pattern.sub(original, new_content)
                total_count += count
                changes.append((obfuscated, original, count))

        new_hash = self._get_file_hash(new_content)
        backup_path = self._create_backup(content)

        with open(self.work_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        var_map_path.unlink()  # Remover mapa apos restaurar

        self._save_history({
            "timestamp": datetime.now().isoformat(),
            "mode": "deobfuscate",
            "replacements": total_count,
            "original_hash": original_hash,
            "new_hash": new_hash,
            "backup": str(backup_path) if backup_path else None
        })

        return TranslationResult(
            success=True, content=new_content,
            total_replacements=total_count, changes=changes,
            original_hash=original_hash, new_hash=new_hash,
            backup_path=backup_path, timestamp=datetime.now(),
            mode="deobfuscate"
        )
    
    # ========================================================================
    # METODOS DE SAIDA
    # ========================================================================
    
    @staticmethod
    def _print(msg: str, end: str = '\n') -> None:
        print(msg, end=end)
    
    @staticmethod
    def _success(msg: str) -> None:
        print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")
    
    @staticmethod
    def _warning(msg: str) -> None:
        print(f"{Colors.YELLOW}[!] {msg}{Colors.RESET}")
    
    @staticmethod
    def _error(msg: str) -> None:
        print(f"{Colors.RED}[ERRO] {msg}{Colors.RESET}")
    
    @staticmethod
    def _info(msg: str) -> None:
        print(f"{Colors.CYAN}[i] {msg}{Colors.RESET}")

# ============================================================================
# INTERFACE DE LINHA DE COMANDO
# ============================================================================

class CLI:
    """Interface de linha de comando."""
    
    def __init__(self, work_file: Optional[str] = None):
        self.translator = SemanticTranslator(work_file=work_file)
        self.work_file = work_file
    
    def print_banner(self) -> None:
        """Exibe o banner do aplicativo."""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
    
                                                                  
                       
                       
                            
                             
                         
                             
                                                                  
                  Semantic Translation Engine v{VERSION}              
                                                                  
    
{Colors.RESET}"""
        print(banner)
    
    def print_result(self, result: TranslationResult) -> None:
        """Exibe o resultado de uma traducao."""
        if not result.success:
            if not result.content:
                print(f"\n{Colors.YELLOW}[!] Arquivo work.txt esta vazio!{Colors.RESET}")
                print(f"{Colors.CYAN}    Cole o conteudo no arquivo e execute novamente.{Colors.RESET}\n")
            return
        
        mode_name = "ENCODE" if result.mode == "encode" else "RESTORE"
        mode_icon = "" if result.mode == "encode" else ""
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  {mode_icon} {mode_name} CONCLUIDO COM SUCESSO{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'' * 60}{Colors.RESET}")
        
        if result.total_replacements > 0:
            print(f"\n{Colors.CYAN}   Estatisticas:{Colors.RESET}")
            print(f"     Total de substituicoes: {Colors.BOLD}{result.total_replacements}{Colors.RESET}")
            print(f"     Hash original: {Colors.DIM}{result.original_hash}{Colors.RESET}")
            print(f"     Hash novo: {Colors.DIM}{result.new_hash}{Colors.RESET}")
            
            if result.changes:
                print(f"\n{Colors.HEADER}   Detalhes das alteracoes:{Colors.RESET}")
                for original, replacement, count in result.changes[:10]:
                    print(f"     {Colors.RED}{original}{Colors.RESET}  {Colors.GREEN}{replacement}{Colors.RESET} ({count}x)")
                if len(result.changes) > 10:
                    print(f"     {Colors.DIM}... e mais {len(result.changes) - 10} alteracoes{Colors.RESET}")
            
            if result.backup_path:
                print(f"\n{Colors.CYAN}   Backup salvo em:{Colors.RESET}")
                print(f"     {Colors.DIM}{result.backup_path.name}{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}   Nenhuma substituicao necessaria.{Colors.RESET}")
        
        print()
    
    def print_stats(self, stats: dict) -> None:
        """Exibe as estatisticas."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}   ESTATISTICAS DO WORKSPACE{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'' * 60}{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}   Arquivo work.txt:{Colors.RESET}")
        print(f"     Caracteres: {Colors.BOLD}{stats['characters']:,}{Colors.RESET}")
        print(f"     Linhas: {Colors.BOLD}{stats['lines']:,}{Colors.RESET}")
        print(f"     Palavras: {Colors.BOLD}{stats['words']:,}{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}   Configuracao:{Colors.RESET}")
        print(f"     Regras carregadas: {Colors.BOLD}{stats['rules_loaded']}{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}   Analise de termos:{Colors.RESET}")
        print(f"     Termos originais detectados: {Colors.RED}{stats['original_terms_found']}{Colors.RESET}")
        print(f"     Termos sanitizados detectados: {Colors.GREEN}{stats['sanitized_terms_found']}{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}   Armazenamento:{Colors.RESET}")
        print(f"     Backups salvos: {Colors.BOLD}{stats['backup_count']}{Colors.RESET}")
        print(f"     Historico: {Colors.BOLD}{stats['history_count']}{Colors.RESET} operacoes")
        
        print()
    
    def print_history(self) -> None:
        """Exibe o historico de operacoes."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}   HISTORICO DE OPERACOES{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'' * 60}{Colors.RESET}\n")
        
        if not self.translator.history:
            print(f"  {Colors.YELLOW}Nenhuma operacao registrada.{Colors.RESET}\n")
            return
        
        for i, entry in enumerate(reversed(self.translator.history[-10:]), 1):
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            mode = entry.get("mode", "?")
            reps = entry.get("replacements", 0)
            icon = "" if mode == "encode" else ""
            
            print(f"  {i}. {icon} [{ts}] {mode.upper()} - {reps} substituicoes")
        
        print()
    
    def run_interactive(self) -> None:
        """Executa o modo interativo."""
        self.print_banner()
        
        while True:
            print(f"{Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [1] ENCODE    - Preparar para IA   {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [2] RESTORE   - Restaurar original {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [3] PREVIEW   - Ver preview        {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [4] STATS     - Estatisticas       {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [5] HISTORY   - Historico          {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [6] UNDO      - Desfazer            {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [7] VALIDATE  - Validar config     {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [8] OBFUSCATE - Ofuscar variaveis  {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [9] DEOBFUSC  - Restaurar vars     {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}  [0] EXIT      - Sair               {Colors.CYAN}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.RESET}")
            
            try:
                opt = input(f"\n{Colors.BOLD}  Opcao: {Colors.RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                break
            
            if opt == '1':
                result = self.translator.encode()
                self.print_result(result)
            elif opt == '2':
                result = self.translator.decode()
                self.print_result(result)
            elif opt == '3':
                result = self.translator.encode(preview_only=True)
                if result.success and result.changes:
                    print(f"\n{Colors.HEADER}  Preview das alteracoes:{Colors.RESET}")
                    for o, r, c in result.changes:
                        print(f"    {Colors.RED}{o}{Colors.RESET}  {Colors.GREEN}{r}{Colors.RESET} ({c}x)")
                    print()
            elif opt == '4':
                stats = self.translator.get_stats()
                self.print_stats(stats)
            elif opt == '5':
                self.print_history()
            elif opt == '6':
                if self.translator.undo():
                    print(f"\n{Colors.GREEN}[OK] Operacao desfeita com sucesso!{Colors.RESET}\n")
                else:
                    print(f"\n{Colors.YELLOW}[!] Nada para desfazer.{Colors.RESET}\n")
            elif opt == '7':
                errors = self.translator.validate_config()
                if errors:
                    print(f"\n{Colors.RED}[!] Problemas encontrados:{Colors.RESET}")
                    for e in errors:
                        print(f"    - {e}")
                else:
                    print(f"\n{Colors.GREEN}[OK] Configuracao valida! ({len(self.translator.rules)} regras){Colors.RESET}")
                print()
            elif opt == '8':
                result = self.translator.obfuscate_variables()
                self.print_result(result)
            elif opt == '9':
                result = self.translator.deobfuscate_variables()
                self.print_result(result)
            elif opt == '0':
                break
            
            input(f"{Colors.DIM}  Pressione ENTER para continuar...{Colors.RESET}")
            print("\033[2J\033[H", end="")  # Limpar tela
            self.print_banner()
        
        print(f"\n{Colors.CYAN}  Ate logo! {Colors.RESET}\n")
    
    def run(self, args: List[str]) -> None:
        """Executa o CLI com os argumentos fornecidos."""
        if len(args) < 1:
            self.run_interactive()
            return
        
        command = args[0].lower()
        
        if command in ('encode', 'sanitize', 'clean', 'e'):
            result = self.translator.encode()
            self.print_result(result)
        
        elif command in ('decode', 'restore', 'revert', 'd', 'r'):
            result = self.translator.decode()
            self.print_result(result)
        
        elif command in ('stats', 's'):
            stats = self.translator.get_stats()
            self.print_stats(stats)
        
        elif command in ('history', 'h'):
            self.print_history()
        
        elif command in ('undo', 'u'):
            if self.translator.undo():
                print(f"{Colors.GREEN}[OK] Operacao desfeita!{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}[!] Nada para desfazer.{Colors.RESET}")
        
        elif command in ('validate', 'v'):
            errors = self.translator.validate_config()
            if errors:
                for e in errors:
                    print(f"{Colors.RED}[!] {e}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}[OK] Configuracao valida!{Colors.RESET}")
        
        elif command in ('check', 'c'):
            # Verifica se o arquivo esta limpo para deploy
            is_clean, count = self.translator.is_clean()
            if is_clean:
                print(f"{Colors.GREEN}[OK] Arquivo limpo - 0 termos sensiveis{Colors.RESET}")
                sys.exit(0)
            else:
                print(f"{Colors.RED}[BLOCKED] {count} termos sensiveis detectados{Colors.RESET}")
                sys.exit(1)
        
        elif command in ('preview', 'p'):
            result = self.translator.encode(preview_only=True)
            if result.success and result.changes:
                for o, r, c in result.changes:
                    print(f"{Colors.RED}{o}{Colors.RESET}  {Colors.GREEN}{r}{Colors.RESET} ({c}x)")

        elif command in ('obfuscate', 'obf', 'o'):
            result = self.translator.obfuscate_variables()
            self.print_result(result)

        elif command in ('deobfuscate', 'deobf', 'do'):
            result = self.translator.deobfuscate_variables()
            self.print_result(result)

        elif command in ('full', 'f'):
            # Ciclo completo: encode + obfuscate
            print(f"{Colors.CYAN}[1/2] Aplicando encode...{Colors.RESET}")
            result1 = self.translator.encode()
            self.print_result(result1)
            print(f"{Colors.CYAN}[2/2] Aplicando ofuscacao de variaveis...{Colors.RESET}")
            result2 = self.translator.obfuscate_variables()
            self.print_result(result2)

        elif command in ('interactive', 'i'):
            self.run_interactive()
        
        elif command in ('help', '--help', '-h'):
            self.print_banner()
            print(f"""
{Colors.CYAN}Uso:{Colors.RESET}
  python translator.py [comando]

{Colors.CYAN}Comandos de Traducao:{Colors.RESET}
  encode, e      Sanitiza o conteudo (prepara para IA)
  decode, d, r   Restaura os termos originais
  preview, p     Preview das alteracoes (sem aplicar)

{Colors.CYAN}Comandos de Ofuscacao:{Colors.RESET}
  obfuscate, o   Ofusca nomes de variaveis sensiveis
  deobfuscate    Restaura nomes de variaveis originais
  full, f        Ciclo completo: encode + obfuscate

{Colors.CYAN}Comandos de Gerenciamento:{Colors.RESET}
  stats, s       Mostra estatisticas
  history, h     Mostra historico de operacoes
  undo, u        Desfaz a ultima operacao
  validate, v    Valida o arquivo de configuracao
  interactive, i Modo interativo

{Colors.CYAN}Exemplos:{Colors.RESET}
  python translator.py encode      # Aplica traducao semantica
  python translator.py obfuscate   # Ofusca variaveis
  python translator.py full        # Encode + Obfuscate juntos
  python translator.py restore     # Restaura termos originais
""")
        
        else:
            print(f"{Colors.RED}[ERRO] Comando desconhecido: {command}{Colors.RESET}")
            print(f"       Use 'python translator.py help' para ver os comandos.")
            sys.exit(1)

# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

def main():
    """Funcao principal."""
    import argparse
    
    # Parser para argumentos
    parser = argparse.ArgumentParser(
        description='MEGAZORD CODE - Semantic Translation Engine',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default='interactive',
                        help='Comando a executar')
    parser.add_argument('--file', '-f', type=str, default=None,
                        help='Arquivo para processar (padrao: work.txt)')
    parser.add_argument('--help', '-h', action='store_true',
                        help='Mostra ajuda')
    
    args = parser.parse_args()
    
    # Se --help ou comando help
    if args.help or args.command in ('help', '--help', '-h'):
        args.command = 'help'
    
    cli = CLI(work_file=args.file)
    cli.run([args.command])

if __name__ == "__main__":
    main()
