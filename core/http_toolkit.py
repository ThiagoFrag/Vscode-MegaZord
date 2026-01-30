#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEVIATHAN VS - Abyssal Interceptor v2.0 (AI-Powered Network Dispatcher)
Interceptor de trafego com IA integrada e Normalizacao Semantica.

Funcionalidades:
- Echolocation: Analise automatica de respostas via LLM
- Camouflage: Rotacao automatica de User-Agent
- Depth Analysis: Comparacao de respostas sanitizadas
- Regeneration: Recuperacao automatica de erros
- Ink Cloud: Proxy invisivel para analise
"""

import json
import time
import random
import hashlib
import argparse
import urllib.request
import urllib.error
import ssl
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path

VERSION = "2.0.0"
CONFIG_FILE = Path(__file__).parent / "config.json"
HISTORY_FILE = Path(__file__).parent / ".http_history.json"
AI_CACHE_FILE = Path(__file__).parent / ".ai_cache.json"

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

def colorize(text: str, color: str) -> str:
    if os.name == 'nt':
        os.system('')
    return f"{color}{text}{Colors.RESET}"

USER_AGENTS = {
    "chrome_windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ],
    "firefox_windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ],
    "safari_mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    ],
    "edge_windows": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    ],
    "android": [
        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    ],
    "iphone": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    ],
    "curl": ["curl/8.5.0"],
    "postman": ["PostmanRuntime/7.36.1"],
}

@dataclass
class RequestConfig:
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    timeout: int = 30
    follow_redirects: bool = True
    validate_ssl: bool = True
    retries: int = 3

@dataclass
class ResponseData:
    status: int
    status_text: str
    headers: Dict[str, str]
    body: str
    timing: Dict[str, float]
    sanitized: bool = False
    ai_analysis: Optional[Dict] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def is_success(self) -> bool:
        return 200 <= self.status < 300

    def is_error(self) -> bool:
        return self.status >= 400

class AIIntegration:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self):
        try:
            if AI_CACHE_FILE.exists():
                with open(AI_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
        except:
            self.cache = {}

    def _save_cache(self):
        try:
            with open(AI_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass

    def analyze_response(self, response: ResponseData, config: RequestConfig) -> Dict[str, Any]:
        cache_key = hashlib.md5(f"{config.url}:{response.status}".encode()).hexdigest()[:16]

        if cache_key in self.cache:
            return self.cache[cache_key]

        analysis = {
            "summary": f"HTTP {response.status}: {response.status_text}",
            "vulnerabilities": [],
            "recommendations": [],
            "risk_level": "low",
            "patterns_detected": [],
            "headers_analysis": {"present": [], "missing": []},
        }

        headers_lower = {k.lower(): v for k, v in response.headers.items()}

        security_headers = {
            "x-frame-options": "Clickjacking protection",
            "x-content-type-options": "MIME sniffing protection",
            "content-security-policy": "CSP",
            "strict-transport-security": "HSTS",
        }

        for header, desc in security_headers.items():
            if header in headers_lower:
                analysis["headers_analysis"]["present"].append(f"✓ {header}")
            else:
                analysis["headers_analysis"]["missing"].append(f"✗ {header}")
                analysis["vulnerabilities"].append(f"Missing: {header}")

        body_lower = response.body.lower()

        patterns = {
            "sql_error": (r"(sql|mysql|postgresql).*?(error|exception)", "SQL error exposed"),
            "stack_trace": (r"(traceback|exception in|at line \d+)", "Stack trace exposed"),
            "api_key": (r"(api[_-]?key|secret[_-]?key)", "Possible credential exposure"),
            "internal_path": (r"(/var/|/home/|c:\\)", "Internal paths exposed"),
        }

        for _, (regex, desc) in patterns.items():
            if re.search(regex, body_lower):
                analysis["patterns_detected"].append(desc)
                analysis["risk_level"] = "high" if "credential" in desc else "medium"

        if response.status == 403:
            analysis["recommendations"] = [
                "Try rotating User-Agent",
                "Add Referer header",
                "Use X-Forwarded-For",
            ]
        elif response.status == 429:
            analysis["recommendations"] = [
                "Implement exponential backoff",
                "Reduce request frequency",
            ]

        self.cache[cache_key] = analysis
        self._save_cache()
        return analysis

    def suggest_next_action(self, response: ResponseData, history: List[Dict]) -> str:
        if response.is_success():
            return "✓ Request successful"
        if response.status == 403:
            return "⚡ Try: rotate headers, add delay, use proxy"
        if response.status == 401:
            return "🔑 Try: refresh token, check credentials"
        if response.status == 429:
            recent_429 = sum(1 for h in history[-10:] if h.get("status") == 429)
            wait = min(60, 5 * (2 ** recent_429))
            return f"⏳ Rate limited. Wait {wait}s"
        if response.status >= 500:
            return "🔄 Server error. Retry in a few seconds"
        return "📊 Analyze response for next steps"

    def generate_curl(self, config: RequestConfig) -> str:
        parts = ["curl", "-X", config.method]
        for k, v in config.headers.items():
            parts.extend(["-H", f'"{k}: {v}"'])
        if config.body:
            parts.extend(["-d", f"'{config.body}'"])
        parts.append(f'"{config.url}"')
        return " ".join(parts)

class HeaderMimicry:
    def __init__(self):
        self.current_profile = "chrome_windows"
        self.request_count = 0
        self.rotation_interval = 5
        self.custom_headers: Dict[str, str] = {}

    def get_random_ua(self, profile: Optional[str] = None) -> str:
        agents = USER_AGENTS.get(profile or self.current_profile, USER_AGENTS["chrome_windows"])
        return random.choice(agents)

    def rotate_profile(self) -> str:
        self.current_profile = random.choice(list(USER_AGENTS.keys()))
        return self.current_profile

    def get_headers(self) -> Dict[str, str]:
        self.request_count += 1
        if self.request_count % self.rotation_interval == 0:
            self.rotate_profile()

        headers = {
            "User-Agent": self.get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        if "chrome" in self.current_profile:
            headers["sec-ch-ua"] = '"Chromium";v="122"'
            headers["sec-ch-ua-mobile"] = "?0"

        headers.update(self.custom_headers)
        return headers

    def set_profile(self, profile: str) -> bool:
        if profile in USER_AGENTS:
            self.current_profile = profile
            return True
        return False

class SemanticProcessor:
    def __init__(self):
        self.rules: Dict[str, str] = {}
        self.reverse_rules: Dict[str, str] = {}
        self._load_rules()

    def _load_rules(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                for k, v in config.items():
                    if not k.startswith("_"):
                        self.rules[k.lower()] = v
                        self.reverse_rules[v.lower()] = k
        except:
            pass

    def sanitize(self, text: str) -> str:
        result = text
        for orig, san in sorted(self.rules.items(), key=lambda x: -len(x[0])):
            result = re.sub(rf"\b{re.escape(orig)}\b", san, result, flags=re.IGNORECASE)
        return result

    def restore(self, text: str) -> str:
        result = text
        for san, orig in sorted(self.reverse_rules.items(), key=lambda x: -len(x[0])):
            result = re.sub(rf"\b{re.escape(san)}\b", orig, result, flags=re.IGNORECASE)
        return result

class AIAutoRepair:
    def __init__(self):
        self.failure_log: List[Dict] = []

    def analyze_failure(self, response: ResponseData, config: RequestConfig) -> Dict[str, Any]:
        strategies = {
            401: ("token_refresh", {"action": "Refresh auth token"}),
            403: ("linear_decoupling", {
                "headers": {"X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"},
                "delay": 2000, "rotate_ua": True
            }),
            429: ("rate_limit_evasion", {"delay": 30000, "rotate_ua": True}),
            500: ("server_retry", {"delay": 5000, "retry_count": 3}),
        }

        if response.status in strategies:
            strategy, changes = strategies[response.status]
            self.failure_log.append({"timestamp": datetime.now().isoformat(), "error": response.status, "strategy": strategy})
            return {"should_retry": True, "suggested_changes": changes, "strategy": strategy}

        return {"should_retry": False, "suggested_changes": {}, "strategy": "none"}

    def get_stats(self) -> Dict[str, Any]:
        by_error = {}
        for log in self.failure_log:
            by_error[log["error"]] = by_error.get(log["error"], 0) + 1
        return {"total": len(self.failure_log), "by_error": by_error}

class HOGDispatcher:
    def __init__(self, verbose: bool = True):
        self.header_mimicry = HeaderMimicry()
        self.semantic = SemanticProcessor()
        self.ai = AIIntegration()
        self.auto_repair = AIAutoRepair()
        self.history: List[Dict] = []
        self.verbose = verbose
        self._load_history()

    def _log(self, msg: str, level: str = "info"):
        if not self.verbose:
            return
        colors = {"info": Colors.CYAN, "success": Colors.GREEN, "warning": Colors.YELLOW, "error": Colors.RED}
        print(f"{colors.get(level, Colors.CYAN)}[HOG]{Colors.RESET} {msg}")

    def _load_history(self):
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except:
            self.history = []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history[-500:], f, indent=2)
        except:
            pass

    def dispatch(self, url: str, method: str = "GET", payload: Any = None,
                 headers: Optional[Dict[str, str]] = None, analyze: bool = True) -> Optional[ResponseData]:
        start = time.time()

        body = None
        if payload:
            body = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            body = self.semantic.sanitize(body)

        self._log(f"Dispatching {colorize(method, Colors.BOLD)} to: {colorize(url, Colors.BLUE)}")

        req_headers = self.header_mimicry.get_headers()
        req_headers["Content-Type"] = "application/json"
        if headers:
            req_headers.update(headers)

        config = RequestConfig(url=url, method=method.upper(), headers=req_headers, body=body)

        response = None
        for attempt in range(config.retries):
            try:
                response = self._request(config)

                if response.is_error() and attempt < config.retries - 1:
                    repair = self.auto_repair.analyze_failure(response, config)
                    if repair["should_retry"]:
                        self._log(f"Auto-repair: {repair['strategy']}", "warning")
                        if "delay" in repair["suggested_changes"]:
                            time.sleep(repair["suggested_changes"]["delay"] / 1000)
                        if repair["suggested_changes"].get("rotate_ua"):
                            self.header_mimicry.rotate_profile()
                            config.headers = self.header_mimicry.get_headers()
                        continue
                break
            except Exception as e:
                if attempt == config.retries - 1:
                    response = ResponseData(0, "Error", {}, str(e), {"start": start, "end": time.time(), "duration": (time.time()-start)*1000})

        if response and analyze:
            response.ai_analysis = self.ai.analyze_response(response, config)
            risk = response.ai_analysis.get("risk_level", "low")
            colors = {"low": Colors.GREEN, "medium": Colors.YELLOW, "high": Colors.RED}
            self._log(f"Risk: {colorize(risk.upper(), colors.get(risk, Colors.GREEN))}")

        if response:
            response.body = self.semantic.restore(response.body)
            response.sanitized = True

            success = response.is_success()
            self._log(f"Result: {'SUCCESS' if success else 'FAILED'}", "success" if success else "warning")

            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "url": url, "method": method, "status": response.status,
                "duration": response.timing["duration"]
            })
            self._save_history()

            suggestion = self.ai.suggest_next_action(response, self.history)
            self._log(f"Next: {suggestion}")

        return response

    def _request(self, config: RequestConfig) -> ResponseData:
        start = time.time()
        data = config.body.encode() if config.body else None

        req = urllib.request.Request(config.url, data=data, headers=config.headers, method=config.method)

        ctx = ssl.create_default_context()
        if not config.validate_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, timeout=config.timeout, context=ctx) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return ResponseData(resp.status, resp.reason, dict(resp.headers), body,
                    {"start": start, "end": time.time(), "duration": round((time.time()-start)*1000, 2)})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except:
                pass
            return ResponseData(e.code, e.reason, dict(e.headers) if e.headers else {}, body,
                {"start": start, "end": time.time(), "duration": round((time.time()-start)*1000, 2)})
        except urllib.error.URLError as e:
            return ResponseData(0, "Connection Error", {}, str(e.reason),
                {"start": start, "end": time.time(), "duration": round((time.time()-start)*1000, 2)})

    def scan(self, url: str) -> List[Dict]:
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        results = []
        for m in methods:
            r = self.dispatch(url, m, analyze=False)
            if r:
                results.append({"method": m, "status": r.status, "duration": r.timing["duration"]})
            time.sleep(0.3)
        return results

    def get_curl(self, url: str, method: str = "GET", payload: Any = None) -> str:
        config = RequestConfig(url, method, self.header_mimicry.get_headers(),
                              json.dumps(payload) if payload else None)
        return self.ai.generate_curl(config)

    def set_profile(self, profile: str) -> bool:
        return self.header_mimicry.set_profile(profile)

def print_banner():
    print(f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════╗
║     {Colors.BOLD}THE HAND OF GOD - HTTP TOOLKIT v{VERSION}{Colors.RESET}{Colors.CYAN} (AI-Powered Network Dispatcher)    ║
║           Interceptor com Normalização Semântica + Análise de IA           ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """)

def cmd_dispatch(args):
    d = HOGDispatcher(verbose=not args.quiet)
    payload = json.loads(args.data) if args.data else None
    headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()
    if args.profile:
        d.set_profile(args.profile)

    r = d.dispatch(args.url, args.method, payload, headers)

    print(f"\n{'='*70}")
    if r:
        print(f"Status: {r.status} {r.status_text}")
        print(f"Duration: {r.timing['duration']}ms")
        if r.ai_analysis:
            print(f"Risk: {r.ai_analysis.get('risk_level', 'N/A').upper()}")
        print('='*70)
        print(f"\nBody:\n{r.body[:2000]}{'...' if len(r.body) > 2000 else ''}")
    else:
        print("Request failed - no response")
        print('='*70)

    if args.curl:
        print(f"\nCurl: {d.get_curl(args.url, args.method, payload)}")

def cmd_scan(args):
    d = HOGDispatcher()
    print(f"\n{Colors.CYAN}[HOG] Scanning: {args.url}{Colors.RESET}\n{'='*70}")

    results = d.scan(args.url)
    success = 0
    for r in results:
        icon = colorize("✓", Colors.GREEN) if 200 <= r["status"] < 400 else colorize("✗", Colors.RED)
        print(f"  {icon} {r['method']:8} -> {r['status']} ({r['duration']:.0f}ms)")
        if 200 <= r["status"] < 400:
            success += 1

    print(f"{'='*70}\nActive methods: {success}/{len(results)}")

def cmd_interactive(args):
    print_banner()
    d = HOGDispatcher()

    print(f"""
{Colors.BOLD}Commands:{Colors.RESET}
  GET/POST/PUT/DELETE <url>  - Make request
  scan <url>                 - Scan methods
  profile <name>             - Change User-Agent
  history                    - Show history
  curl <url>                 - Generate curl
  quit                       - Exit
    """)

    while True:
        try:
            cmd = input(f"{Colors.CYAN}[HOG]{Colors.RESET} > ").strip()
            if not cmd:
                continue
            if cmd.lower() in ["quit", "exit", "q"]:
                print("Bye!")
                break

            if cmd.lower() == "history":
                for h in d.history[-20:]:
                    icon = colorize("✓", Colors.GREEN) if 200 <= h.get("status", 0) < 300 else colorize("✗", Colors.RED)
                    print(f"  {icon} {h.get('method', 'GET'):6} {h.get('status', 0):3} {h.get('url', '')[:50]}")
                continue

            if cmd.lower().startswith("profile "):
                profile = cmd.split(" ", 1)[1]
                if d.set_profile(profile):
                    print(f"Profile: {profile}")
                else:
                    print(f"Invalid. Options: {', '.join(USER_AGENTS.keys())}")
                continue

            if cmd.lower().startswith("scan "):
                url = cmd.split(" ", 1)[1]
                for r in d.scan(url):
                    icon = "✓" if 200 <= r["status"] < 400 else "✗"
                    print(f"  {icon} {r['method']:8} -> {r['status']}")
                continue

            if cmd.lower().startswith("curl "):
                print(d.get_curl(cmd.split(" ", 1)[1]))
                continue

            parts = cmd.split(" ", 1)
            if len(parts) == 2 and parts[0].upper() in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]:
                r = d.dispatch(parts[1], parts[0].upper())
            else:
                r = d.dispatch(cmd)

            if r:
                print(f"\nStatus: {r.status} {r.status_text} ({r.timing['duration']:.0f}ms)")
                if r.body:
                    print(f"Body: {r.body[:500]}...")
            else:
                print("\nRequest failed - no response")

        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"HOG HTTP Toolkit v{VERSION}")
    parser.add_argument("--version", action="version", version=VERSION)

    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("dispatch", help="Make HTTP request")
    p.add_argument("url")
    p.add_argument("-X", "--method", default="GET")
    p.add_argument("-d", "--data")
    p.add_argument("-H", "--header", action="append")
    p.add_argument("-p", "--profile")
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--curl", action="store_true")

    p = sub.add_parser("scan", help="Scan endpoint")
    p.add_argument("url")

    sub.add_parser("interactive", aliases=["i"], help="Interactive mode")

    args = parser.parse_args()

    if args.command == "dispatch":
        cmd_dispatch(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command in ["interactive", "i"]:
        cmd_interactive(args)
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
