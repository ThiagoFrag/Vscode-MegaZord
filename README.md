# MEGAZORD CODE

## THE HAND OF GOD - Semantic Translation Engine v5.0

Uma ferramenta de alto desempenho para normalizacao semantica de codigo. Traduz termos sensiveis para termos neutros antes de enviar para IAs e restaura os termos originais depois.

![Version](https://img.shields.io/badge/version-5.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![MCP](https://img.shields.io/badge/MCP-enabled-purple)

---

## Novidades v5.0

- **MCP Server** - Servidor Model Context Protocol para integracao com GitHub Copilot
- **Traducao em Tempo Real** - Ferramentas disponiveis diretamente no chat do Copilot
- **104 Regras** - Paradigma de Teoria de Grafos e Compiladores
- **SAFE DEPLOY** - Bloqueia push com termos sensiveis

---

## Inicio Rapido

### Windows (Recomendado)
```batch
START_HOG.bat
```

### Linha de Comando
```bash
python translator.py encode      # Sanitizar codigo
python translator.py restore     # Restaurar originais
python translator.py stats       # Estatisticas
python translator.py interactive # Modo interativo
```

### VSCode (Ctrl+Shift+B)
Acesse o menu de tasks e selecione a operacao desejada.

### MCP Server (GitHub Copilot)
O servidor MCP integra automaticamente com o chat do Copilot.
Use os comandos: `encode`, `decode`, `check`, `find_terms`, `get_rules`

---

## Requisitos

- Python 3.8+
- Windows/Linux/macOS
- VSCode com GitHub Copilot (para MCP)

---

## Instalacao

```bash
git clone git@github.com:ThiagoFrag/Megazord-Code.git
cd Megazord-Code
python translator.py
```

---

## Comandos Disponiveis

| Comando | Alias | Descricao |
|---------|-------|-----------|
| `encode` | `e`, `sanitize`, `clean` | Sanitiza o conteudo |
| `decode` | `d`, `r`, `restore`, `revert` | Restaura os termos originais |
| `stats` | `s` | Mostra estatisticas |
| `history` | `h` | Mostra historico de operacoes |
| `undo` | `u` | Desfaz a ultima operacao |
| `validate` | `v` | Valida o arquivo de configuracao |
| `preview` | `p` | Preview das alteracoes |
| `interactive` | `i` | Modo interativo |
| `help` | `-h`, `--help` | Mostra ajuda |

---

## Fluxo de Trabalho

```
1. Cole seu codigo em work.txt
2. Execute ENCODE (Ctrl+Shift+B > ENCODE)
   - "exploit" -> "performance_case"
   - "bypass" -> "bridge_compatibility"
3. Envie o codigo sanitizado para a IA
4. Cole a resposta da IA em work.txt
5. Execute RESTORE (Ctrl+Shift+B > RESTORE)
   - "performance_case" -> "exploit"
   - "bridge_compatibility" -> "bypass"
6. Pronto! Codigo original restaurado
```

---

## Estrutura de Arquivos

```
Megazord-Code/
    .vscode/
        extensions.json    # Extensoes recomendadas
        keybindings.json   # Atalhos de teclado
        launch.json        # Configuracoes de debug
        settings.json      # Configuracoes do VSCode
        tasks.json         # Tasks automatizadas (16 tasks)
    config.json            # Regras de traducao (104 regras)
    LICENSE                # Licenca MIT
    README.md              # Documentacao
    semantic-engine.ts     # Versao TypeScript (em desenvolvimento)
    START_HOG.bat          # Interface grafica Windows
    translator.py          # Motor principal Python
    work.txt               # Arquivo de trabalho
```

---

## Configuracao

Edite o arquivo `config.json` para adicionar ou modificar regras:

```json
{
    "termo_original": "termo_sanitizado",
    "exploit": "performance_case",
    "bypass": "bridge_compatibility"
}
```

### Regras Incluidas (104 regras)

| Categoria | Exemplos |
|-----------|----------|
| Seguranca | bypass, exploit, vulnerability, injection |
| Malware | virus, trojan, backdoor, rootkit, keylogger |
| Ataques | xss, csrf, ddos, sql_injection, bruteforce |
| Ferramentas | scanner, fuzzer, debugger, decompiler |
| Acesso | privilege, root, admin, shell, terminal |

---

## Recursos

- Backup Automatico - Cada operacao cria um backup
- Historico - Registra as ultimas 50 operacoes
- Undo - Desfaz a ultima operacao
- Preview - Ve as alteracoes antes de aplicar
- Validacao - Verifica conflitos na configuracao
- Case Preserving - Mantem maiusculas/minusculas
- Word Boundaries - So substitui palavras completas
- Estatisticas - Contagem detalhada de alteracoes
- Hash Tracking - Rastreia alteracoes por hash MD5
- Cores no Terminal - Feedback visual colorido

---

## VSCode Tasks (Ctrl+Shift+B)

| Task | Descricao |
|------|-----------|
| [HOG] ENCODE | Converte termos sensiveis para neutros |
| [HOG] RESTORE | Restaura termos originais |
| [HOG] STATS | Mostra estatisticas |
| [HOG] PREVIEW | Pre-visualiza alteracoes |
| [HOG] HISTORY | Exibe historico |
| [HOG] UNDO | Desfaz ultima operacao |
| [HOG] VALIDATE | Valida config.json |
| [HOG] INTERACTIVE | Modo console |
| [HOG] CLEAN | Remove backups |
| [HOG] LIST BACKUPS | Lista backups |
| [HOG] CONFIG COUNT | Conta regras |
| [HOG] GIT STATUS | Status do git |
| [HOG] GIT PUSH | Push para GitHub |
| [HOG] GIT COMMIT ALL | Commit todas alteracoes |
| [HOG] FULL CYCLE | Encode + Copia para clipboard |

---

## Configuracoes do VSCode

O projeto inclui configuracoes otimizadas:

- Tema escuro customizado (verde neon)
- Fonte Cascadia Code com ligatures
- Python analysis com type checking
- Auto-save habilitado
- Git auto-fetch
- Extensoes recomendadas pre-configuradas

---

## Debug (F5)

Configuracoes de debug incluidas:

- HOG: Modo Interativo
- HOG: ENCODE
- HOG: RESTORE
- HOG: STATS
- HOG: VALIDATE
- HOG: PREVIEW
- HOG: Debug com Args Customizados
- Python: Arquivo Atual

---

## Contribuicao

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/NovaRegra`)
3. Commit suas mudancas (`git commit -m 'Add: nova regra de traducao'`)
4. Push para a Branch (`git push origin feature/NovaRegra`)
5. Abra um Pull Request

---

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo LICENSE para mais detalhes.

---

## Autor

**ThiagoFrag**

GitHub: [@ThiagoFrag](https://github.com/ThiagoFrag)

---

MEGAZORD CODE - THE HAND OF GOD v3.0
Semantic Translation Engine
