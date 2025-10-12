# SpiderFoot Branch Comparison Analysis

**Generated:** 2025-10-11 21:33:42
**Comparing:** prod-_808_-5.2.9 (current) vs dev-5.3.3

---

## 1. Main File Consolidation Analysis

### sf.py
- **Current branch:** 1179 lines
- **dev-5.3.3 branch:** 360 lines
- **Difference:** +819 lines
- **Current functions/classes:** 12
- **dev-5.3.3 functions/classes:** 9

**Current definitions:**
- `def load_modules_custom(mod_dir, log):`
- `def main():`
- `def start_scan(sfConfig: dict, sfModules: dict, args, loggingQueue) -> None:`
- `def validate_arguments(args, log):`
- `def process_target(args, log):`
- `def prepare_modules(args, sf, sfModules, log, targetType):`
- `def prepare_scan_output(args):`
- `def execute_scan(loggingQueue, target, targetType, modlist, cfg, log):`
- `def start_fastapi_server(sfApiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def start_both_servers(sfWebUiConfig: dict, sfApiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def start_web_server(sfWebUiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def handle_abort(signal, frame) -> None:`

### sfapi.py
- **Current branch:** 1029 lines
- **dev-5.3.3 branch:** 47 lines
- **Difference:** +982 lines
- **Current functions/classes:** 18
- **dev-5.3.3 functions/classes:** 1

**Current definitions:**
- `class Config:`
- `def get_app_config():`
- `class ScanRequest(BaseModel):`
- `class ScanResponse(BaseModel):`
- `class WorkspaceRequest(BaseModel):`
- `class WorkspaceResponse(BaseModel):`
- `class TargetRequest(BaseModel):`
- `class MultiScanRequest(BaseModel):`
- `class CTIReportRequest(BaseModel):`
- `class EventResponse(BaseModel):`
- `class ModuleInfo(BaseModel):`
- `class ApiKeyModel(BaseModel):`
- `class ConfigUpdate(BaseModel):`
- `class WebSocketManager:`
- `def clean_user_input(input_list: list) -> list:`
- `def search_base(config: dict, scan_id: str = None, event_type: str = None, value: str = None) -> list:`
- `def build_excel(data: list, column_names: list, sheet_name_index: int = 0) -> str:`
- `def main():`

### sfcli.py
- **Current branch:** 1490 lines
- **dev-5.3.3 branch:** 899 lines
- **Difference:** +591 lines
- **Current functions/classes:** 2
- **dev-5.3.3 functions/classes:** 1

**Current definitions:**
- `class bcolors:`
- `class SpiderFootCli(cmd.Cmd):`

### sfwebui.py
- **Current branch:** 3021 lines
- **dev-5.3.3 branch:** 883 lines
- **Difference:** +2138 lines
- **Current functions/classes:** 1
- **dev-5.3.3 functions/classes:** 2

**Current definitions:**
- `class SpiderFootWebUi:`

### sflib.py
- **Current branch:** 1780 lines
- **dev-5.3.3 branch:** 0 lines
- **Difference:** +1780 lines
- **Current functions/classes:** 1
- **dev-5.3.3 functions/classes:** 0

## 2. Removed Modular Components

### spiderfoot/api/
**Files that existed in dev-5.3.3:**
- `spiderfoot/api/__init__.py`
- `spiderfoot/api/dependencies.py`
- `spiderfoot/api/main.py`
- `spiderfoot/api/models.py`
- `spiderfoot/api/routers/__init__.py`
- `spiderfoot/api/routers/config.py`
- `spiderfoot/api/routers/correlations.py`
- `spiderfoot/api/routers/data.py`
- `spiderfoot/api/routers/scan.py`
- `spiderfoot/api/routers/visualization.py`
- `spiderfoot/api/routers/websocket.py`
- `spiderfoot/api/routers/workspace.py`
- `spiderfoot/api/search_base.py`
- `spiderfoot/api/utils.py`

### spiderfoot/cli/
**Files that existed in dev-5.3.3:**
- `spiderfoot/cli/__init__.py`
- `spiderfoot/cli/banner.py`
- `spiderfoot/cli/commands/__init__.py`
- `spiderfoot/cli/commands/api.py`
- `spiderfoot/cli/commands/batch.py`
- `spiderfoot/cli/commands/commands.py`
- `spiderfoot/cli/commands/correlationrules.py`
- `spiderfoot/cli/commands/correlations.py`
- `spiderfoot/cli/commands/data.py`
- `spiderfoot/cli/commands/delete.py`
- `spiderfoot/cli/commands/export.py`
- `spiderfoot/cli/commands/find.py`
- `spiderfoot/cli/commands/help.py`
- `spiderfoot/cli/commands/interactive.py`
- `spiderfoot/cli/commands/logs.py`
- `spiderfoot/cli/commands/modules.py`
- `spiderfoot/cli/commands/monitor.py`
- `spiderfoot/cli/commands/ping.py`
- `spiderfoot/cli/commands/query.py`
- `spiderfoot/cli/commands/scaninfo.py`

### spiderfoot/core/
**Files that existed in dev-5.3.3:**
- `spiderfoot/core/__init__.py`
- `spiderfoot/core/api_security.py`
- `spiderfoot/core/config.py`
- `spiderfoot/core/error_handling.py`
- `spiderfoot/core/modules.py`
- `spiderfoot/core/performance.py`
- `spiderfoot/core/scan.py`
- `spiderfoot/core/security.py`
- `spiderfoot/core/server.py`
- `spiderfoot/core/validation.py`

### spiderfoot/webui/
**Files that existed in dev-5.3.3:**
- `spiderfoot/webui/__init__.py`
- `spiderfoot/webui/export.py`
- `spiderfoot/webui/helpers.py`
- `spiderfoot/webui/info.py`
- `spiderfoot/webui/main.py`
- `spiderfoot/webui/performance.py`
- `spiderfoot/webui/routes.py`
- `spiderfoot/webui/scan.py`
- `spiderfoot/webui/security.py`
- `spiderfoot/webui/settings.py`
- `spiderfoot/webui/templates.py`
- `spiderfoot/webui/workspace.py`

### spiderfoot/db/
**Files that existed in dev-5.3.3:**
- `spiderfoot/db/__init__.py`
- `spiderfoot/db/db_config.py`
- `spiderfoot/db/db_core.py`
- `spiderfoot/db/db_correlation.py`
- `spiderfoot/db/db_event.py`
- `spiderfoot/db/db_scan.py`
- `spiderfoot/db/db_utils.py`

### spiderfoot/sflib/
**Files that existed in dev-5.3.3:**
- `spiderfoot/sflib/__init__.py`
- `spiderfoot/sflib/config.py`
- `spiderfoot/sflib/core.py`
- `spiderfoot/sflib/helpers.py`
- `spiderfoot/sflib/logging.py`
- `spiderfoot/sflib/network.py`

### scripts/ directory
**Removed scripts:**
- `scripts/THREADREAPER_ORGANIZATION.md`

## 3. Database Architecture Changes

### spiderfoot/db.py
- **Current:** 2210 lines
- **dev-5.3.3:** 206 lines

### spiderfoot_db.py (NEW)
- **Lines:** 2258
- This appears to be a new consolidated database file

## 4. Module Changes Analysis
### Modified Modules

**modules/sfp__ai_threat_intel.py**
- +2 -19 lines

**modules/sfp__security_hardening.py**
- +5 -9 lines

**modules/sfp__stor_db_advanced.py**
- +70 -143 lines

**modules/sfp__stor_stdout.py**
- +13 -15 lines

**modules/sfp_abstractapi.py**
- modules/sfp_abstractapi.py | 2 --
 1 file changed, 2 deletions(-)

**modules/sfp_abusech.py**
- +1 -1 lines

**modules/sfp_abuseipdb.py**
- +1 -1 lines

**modules/sfp_accounts.py**
- +1 -1 lines

**modules/sfp_adblock.py**
- +1 -2 lines

**modules/sfp_adguard_dns.py**
- +1 -1 lines

**modules/sfp_advanced_correlation.py**

**modules/sfp_ahmia.py**
- +4 -4 lines

**modules/sfp_ai_summary.py**
- modules/sfp_ai_summary.py | 1 -
 1 file changed, 1 deletion(-)

**modules/sfp_alienvault.py**
- +1 -1 lines

**modules/sfp_alienvaultiprep.py**
- +1 -1 lines

**modules/sfp_aparat.py**
- modules/sfp_aparat.py | 1 -
 1 file changed, 1 deletion(-)

**modules/sfp_apileak.py**
- modules/sfp_apileak.py | 1 -
 1 file changed, 1 deletion(-)

**modules/sfp_apple_itunes.py**
- +1 -1 lines

**modules/sfp_arbitrum.py**
- modules/sfp_arbitrum.py | 1 -
 1 file changed, 1 deletion(-)

**modules/sfp_arin.py**
- modules/sfp_arin.py | 1 -
 1 file changed, 1 deletion(-)

### Removed Modules
- `modules/sfp_advanced_correlation.py`
- `modules/sfp_blockchain_analytics.py`
- `modules/sfp_performance_optimizer.py`
- `modules/sfp_tiktok_osint.py`

## 5. Test Structure Changes
- **ThreadReaper backup files removed:** 247
- **Overall test changes:** 788 files changed, 2365 insertions(+), 32964 deletions(-)

## 6. New Files Added
- `.claude/settings.json`
- `BUILD-PROCESS.md`
- `Dockerfile.tor`
- `ENTERPRISE_DEPLOYMENT_GUIDE.md`
- `ENTERPRISE_REGISTRY_OPTIONS.md`
- `FUTURE_WORK.md`
- `build-deploy.sh`
- `claudes_decoys/db.py.backup`
- `claudes_decoys/db_optimal.py`
- `claudes_decoys/spiderfoot_db.py.backup`
- `code_structure.json`
- `init-postgres-db.sh.donotuse`
- `migration_add_cascade.sql`
- `sflib.py`
- `spiderfoot/code_structure.json`
- `spiderfoot/db.db.py.backup`
- `spiderfoot/logger.py.backup.20251010_142432`
- `spiderfoot/security/__init__.py`
- `spiderfoot/security/csrf_middleware.py`
- `spiderfoot/spider.gv`

## 7. Overall Architecture Summary
- **Total changes:** 1135 files changed, 31617 insertions(+), 74937 deletions(-)

### Key Architectural Changes:
1. **Massive Consolidation:** Modular structure collapsed into main files
2. **Removed Enterprise Features:** Many advanced/enterprise components removed
3. **Simplified Architecture:** Move from distributed to monolithic structure
4. **Database Restructuring:** New consolidated database files
5. **Test Simplification:** Removal of complex testing infrastructure

### Impact Assessment:
- **Maintainability:** Potentially easier to maintain with fewer files
- **Modularity:** Significant loss of modular architecture
- **Features:** Likely reduction in advanced features
- **Testing:** Simplified but potentially less comprehensive testing

---
# DETAILED METHOD ANALYSIS
**Generated:** 2025-10-11 21:34:21


---
# Detailed Method Analysis

## Method-by-Method Analysis: sf.py

### Summary
- **Current version:** 13 functions/methods/classes
- **dev-5.3.3 version:** 0 functions/methods/classes
- **New:** 13
- **Removed:** 0
- **Common:** 0

### ✅ New Functions/Methods (13)
- `def execute_scan(loggingQueue, target, targetType, modlist, cfg, log):`
- `def handle_abort(signal, frame) -> None:`
- `def load_modules_custom(mod_dir, log):`
- `def main():`
- `def prepare_modules(args, sf, sfModules, log, targetType):`
- `def prepare_scan_output(args):`
- `def process_target(args, log):`
- `def run_fastapi():`
- `def start_both_servers(sfWebUiConfig: dict, sfApiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def start_fastapi_server(sfApiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def start_scan(sfConfig: dict, sfModules: dict, args, loggingQueue) -> None:`
- `def start_web_server(sfWebUiConfig: dict, sfConfig: dict, loggingQueue=None) -> None:`
- `def validate_arguments(args, log):`

## Method-by-Method Analysis: sfapi.py

### Summary
- **Current version:** 25 functions/methods/classes
- **dev-5.3.3 version:** 1 functions/methods/classes
- **New:** 23
- **Removed:** 0
- **Common:** 1

### ✅ New Functions/Methods (23)
- `class ApiKeyModel(BaseModel):`
- `class CTIReportRequest(BaseModel):`
- `class Config:`
- `class ConfigUpdate(BaseModel):`
- `class EventResponse(BaseModel):`
- `class ModuleInfo(BaseModel):`
- `class MultiScanRequest(BaseModel):`
- `class ScanRequest(BaseModel):`
- `class ScanResponse(BaseModel):`
- `class TargetRequest(BaseModel):`
- `class WebSocketManager:`
- `class WorkspaceRequest(BaseModel):`
- `class WorkspaceResponse(BaseModel):`
- `def __init__(self):`
- `def build_excel(data: list, column_names: list, sheet_name_index: int = 0) -> str:`
- `def clean_user_input(input_list: list) -> list:`
- `def disconnect(self, websocket: WebSocket):`
- `def get_app_config():`
- `def get_config(self):`
- `def name_must_not_be_empty(cls, v):`
- `def search_base(config: dict, scan_id: str = None, event_type: str = None, value: str = None) -> list:`
- `def target_must_not_be_empty(cls, v):`
- `def update_config(self, updates: dict):`

### 🔄 Modified Functions/Methods (showing line count changes)
- `def main` (line 1005 vs 30)

## Method-by-Method Analysis: sfcli.py

### Summary
- **Current version:** 44 functions/methods/classes
- **dev-5.3.3 version:** 49 functions/methods/classes
- **New:** 4
- **Removed:** 9
- **Common:** 40

### ✅ New Functions/Methods (4)
- `class bcolors:`
- `def do_load(self, line):`
- `def do_search(self, line):`
- `def print_topics(self, header, cmds, cmdlen, maxcol):`

### ❌ Removed Functions/Methods (9)
- `def __init__(self, *args, **kwargs):`
- `def _fetch_api_list(self, endpoint):`
- `def _init_dynamic_completions(self):`
- `def _init_inline_help(self):`
- `def cmdloop(self, intro=None):`
- `def do_help(self, line):`
- `def postcmd(self, stop, line):`
- `def preloop(self):`
- `def spinner():`

### 🔄 Modified Functions/Methods (showing line count changes)
- `def completedefault` (line 414 vs 420)
- `def do_clear` (line 1356 vs 726)
- `def do_exit` (line 1361 vs 731)
- `def do_modules` (line 587 vs 608)
- `def do_ping` (line 567 vs 594)
- `def do_types` (line 622 vs 615)
- `def dprint` (line 127 vs 137)
- `def precmd` (line 215 vs 224)
- `def pretty` (line 240 vs 264)
- `def send_output` (line 461 vs 483)

## Method-by-Method Analysis: sfwebui.py

### Summary
- **Current version:** 74 functions/methods/classes
- **dev-5.3.3 version:** 0 functions/methods/classes
- **New:** 74
- **Removed:** 0
- **Common:** 0

### ✅ New Functions/Methods (74)
- `class SpiderFootWebUi:`
- `def __init__(self: 'SpiderFootWebUi', web_config: dict, config: dict, loggingQueue: 'logging.handlers.QueueListener' = None) -> None:`
- `def active_maintenance_status(self: 'SpiderFootWebUi') -> str:`
- `def buildExcel(self: 'SpiderFootWebUi', data: list, columnNames: list, sheetNameIndex: int = 0) -> str:`
- `def cleanUserInput(self: 'SpiderFootWebUi', inputList: list) -> list:`
- `def clonescan(self: 'SpiderFootWebUi', id: str) -> str:`
- `def correlationrules(self: 'SpiderFootWebUi') -> list:`
- `def documentation(self: 'SpiderFootWebUi', doc: str = None, q: str = None) -> str:`
- `def error_page(self: 'SpiderFootWebUi') -> None:`
- `def error_page(self: 'SpiderFootWebUi') -> None:`
- `def error_page_401(self: 'SpiderFootWebUi', status: str, message: str, traceback: str, version: str) -> str:`
- `def error_page_404(self: 'SpiderFootWebUi', status: str, message: str, traceback: str, version: str) -> str:`
- `def eventtypes(self: 'SpiderFootWebUi') -> list:`
- `def footer(self: 'SpiderFootWebUi') -> str:`
- `def highlight(text, query):`
- `def index(self: 'SpiderFootWebUi') -> str:`
- `def jsonify_error(self: 'SpiderFootWebUi', status: str, message: str) -> dict:`
- `def md_link_rewrite(match):`
- `def modules(self: 'SpiderFootWebUi') -> list:`
- `def newscan(self: 'SpiderFootWebUi') -> str:`
- `def opts(self: 'SpiderFootWebUi', updated: str = None) -> str:`
- `def optsexport(self: 'SpiderFootWebUi', pattern: str = None) -> str:`
- `def optsraw(self: 'SpiderFootWebUi') -> str:`
- `def ping(self: 'SpiderFootWebUi') -> list:`
- `def query(self: 'SpiderFootWebUi', query: str) -> str:`
- `def rerunscan(self: 'SpiderFootWebUi', id: str) -> None:`
- `def rerunscanmulti(self: 'SpiderFootWebUi', ids: str) -> str:`
- `def reset_settings(self: 'SpiderFootWebUi') -> bool:`
- `def resultsetfp(self: 'SpiderFootWebUi', id: str, resultids: str, fp: str) -> str:`
- `def savesettings(self: 'SpiderFootWebUi', allopts: str, token: str, configFile: 'cherrypy._cpreqbody.Part' = None) -> None:`
- `def savesettingsraw(self: 'SpiderFootWebUi', allopts: str, token: str) -> str:`
- `def scancorrelationsexport(self: 'SpiderFootWebUi', id: str, filetype: str = "csv", dialect: str = "excel") -> str:`
- `def scancorrelationsexport(self: 'SpiderFootWebUi', id: str, filetype: str = "csv", dialect: str = "excel") -> str:`
- `def scandelete(self: 'SpiderFootWebUi', id: str) -> str:`
- `def scanelementtypediscovery(self: 'SpiderFootWebUi', id: str, eventType: str) -> dict:`
- `def scanerrors(self: 'SpiderFootWebUi', id: str, limit: str = None) -> list:`
- `def scaneventresultexport(self: 'SpiderFootWebUi', id: str, type: str, filetype: str = "csv", dialect: str = "excel") -> str:`
- `def scaneventresultexportmulti(self: 'SpiderFootWebUi', ids: str, filetype: str = "csv", dialect: str = "excel") -> str:`
- `def scaneventresults(self: 'SpiderFootWebUi', id: str, eventType: str = None, filterfp: bool = False, correlationId: str = None) -> list:`
- `def scaneventresultsunique(self: 'SpiderFootWebUi', id: str, eventType: str, filterfp: bool = False) -> list:`
- `def scanexportjsonmulti(self: 'SpiderFootWebUi', ids: str) -> str:`
- `def scanexportlogs(self: 'SpiderFootWebUi', id: str, dialect: str = "excel") -> bytes:`
- `def scanhistory(self: 'SpiderFootWebUi', id: str) -> list:`
- `def scaninfo(self: 'SpiderFootWebUi', id: str) -> str:`
- `def scanlist(self: 'SpiderFootWebUi') -> list:`
- `def scanlog(self: 'SpiderFootWebUi', id: str, limit: str = None, rowId: str = None, reverse: str = None) -> list:`
- `def scanopts(self: 'SpiderFootWebUi', id: str) -> dict:`
- `def scansearchresultexport(self: 'SpiderFootWebUi', id: str, eventType: str = None, value: str = None, filetype: str = "csv", dialect: str = "excel") -> str:`
- `def scanstatus(self: 'SpiderFootWebUi', id: str) -> list:`
- `def scansummary(self: 'SpiderFootWebUi', id: str, by: str) -> list:`
- `def scanviz(self: 'SpiderFootWebUi', id: str, gexf: str = "0") -> str:`
- `def scanvizmulti(self: 'SpiderFootWebUi', ids: str, gexf: str = "1") -> str:`
- `def searchBase(self: 'SpiderFootWebUi', id: str = None, eventType: str = None, value: str = None) -> list:`
- `def searchBase(self: 'SpiderFootWebUi', id: str = None, eventType: str = None, value: str = None) -> list:`
- `def startscan(self: 'SpiderFootWebUi', scanname: str, scantarget: str, modulelist: str, typelist: str, usecase: str) -> str:`
- `def stopscan(self: 'SpiderFootWebUi', id: str) -> str:`
- `def vacuum(self):`
- `def workspaceaddtarget(self: 'SpiderFootWebUi', workspace_id: str, target: str, target_type: str = None) -> dict:`
- `def workspacecreate(self: 'SpiderFootWebUi', name: str, description: str = '') -> dict:`
- `def workspacedelete(self: 'SpiderFootWebUi', workspace_id: str) -> dict:`
- `def workspacedetails(self: 'SpiderFootWebUi', workspace_id: str) -> str:`
- `def workspaceget(self: 'SpiderFootWebUi', workspace_id: str) -> dict:`
- `def workspaceimportscans(self: 'SpiderFootWebUi', workspace_id: str, scan_ids: str) -> dict:`
- `def workspacelist(self: 'SpiderFootWebUi') -> list:`
- `def workspacemcpreport(self: 'SpiderFootWebUi', workspace_id: str, report_type: str, format: str = 'json', include_correlations: str = 'true', include_threat_intel: str = 'true',`
- `def workspacemultiscan(self: 'SpiderFootWebUi', workspace_id: str, targets: str, modules: str, scan_name_prefix: str, enable_correlation: str = 'false') -> dict:`
- `def workspaceremovetarget(self: 'SpiderFootWebUi', workspace_id: str, target_id: str) -> dict:`
- `def workspacereportdownload(self: 'SpiderFootWebUi', report_id: str, workspace_id: str, format: str = 'json'):`
- `def workspaces(self: 'SpiderFootWebUi') -> str:`
- `def workspacescancorrelations(self: 'SpiderFootWebUi', workspace_id: str) -> dict:`
- `def workspacescanresults(self: 'SpiderFootWebUi', workspace_id: str, scan_id: str = None, event_type: str = None, limit: int = 100) -> dict:`
- `def workspacesummary(self: 'SpiderFootWebUi', workspace_id: str) -> dict:`
- `def workspacetiming(self: 'SpiderFootWebUi', workspace_id: str, timezone: str = None, default_start_time: str = None, retention_period: str = None, auto_scheduling: str = None, business_hours_only: str = None, enable_throttling: str = None, business_start: str = None,`
- `def workspaceupdate(self: 'SpiderFootWebUi', workspace_id: str, name: str = None, description: str = None) -> dict:`

## Method-by-Method Analysis: sflib.py

### Summary
- **Current version:** 52 functions/methods/classes
- **dev-5.3.3 version:** 0 functions/methods/classes
- **New:** 49
- **Removed:** 0
- **Common:** 0

### ✅ New Functions/Methods (49)
- `class SpiderFoot:`
- `def __init__(self, options: dict) -> None:`
- `def bingIterate(self, searchString: str, opts: dict = None) -> dict:`
- `def cacheGet(self, label: str, timeoutHrs: int) -> str:`
- `def cachePut(self, label: str, data: str) -> None:`
- `def checkDnsWildcard(self, target: str) -> bool:`
- `def configSerialize(self, opts: dict, filterSystem: bool = True):`
- `def configUnserialize(self, opts: dict, referencePoint: dict, filterSystem: bool = True):`
- `def cveInfo(self, cveId: str, sources: str = "circl,nist") -> (str, str):`
- `def cveRating(score: int) -> str:`
- `def dbh(self):`
- `def debug(self, message: str) -> None:`
- `def domainKeyword(self, domain: str, tldList: list) -> str:`
- `def domainKeywords(self, domainList: list, tldList: list) -> set:`
- `def error(self, message: str) -> None:`
- `def eventsFromModules(self, modules: list) -> list:`
- `def eventsToModules(self, modules: list) -> list:`
- `def fatal(self, error: str) -> None:`
- `def fetchUrl( self, url: str, cookies: str = None, timeout: int = 30, useragent: str = "SpiderFoot", headers: dict = None, noLog: bool = False, postData: str = None, disableContentEncoding: bool = False, sizeLimit: int = None, headOnly: bool = False,`
- `def getSession(self) -> 'requests.sessions.Session':`
- `def googleIterate(self, searchString: str, opts: dict = None) -> dict:`
- `def hashstring(self, string: str) -> str:`
- `def hostDomain(self, hostname: str, tldList: list) -> str:`
- `def info(self, message: str) -> None:`
- `def isDomain(self, hostname: str, tldList: list) -> bool:`
- `def isPublicIpAddress(self, ip: str) -> bool:`
- `def isValidLocalOrLoopbackIp(self, ip: str) -> bool:`
- `def loadModules(self):`
- `def modulesConsuming(self, events: list) -> list:`
- `def modulesProducing(self, events: list) -> list:`
- `def normalizeDNS(self, res: list) -> list:`
- `def optValueToData(self, val: str) -> str:`
- `def parseCert(self, rawcert: str, fqdn: str = None, expiringdays: int = 30) -> dict:`
- `def removeUrlCreds(self, url: str) -> str:`
- `def resolveHost(self, host: str) -> list:`
- `def resolveHost6(self, hostname: str) -> list:`
- `def resolveIP(self, ipaddr: str) -> list:`
- `def safeSSLSocket(self, host: str, port: int, timeout: int) -> 'ssl.SSLSocket':`
- `def safeSocket(self, host: str, port: int, timeout: int) -> 'ssl.SSLSocket':`
- `def scanId(self) -> str:`
- `def socksProxy(self) -> str:`
- `def status(self, message: str) -> None:`
- `def urlFQDN(self, url: str) -> str:`
- `def useProxyForUrl(self, url: str) -> bool:`
- `def validHost(self, hostname: str, tldList: str) -> bool:`
- `def validIP(self, address: str) -> bool:`
- `def validIP6(self, address: str) -> bool:`
- `def validIpNetwork(self, cidr: str) -> bool:`
- `def validateIP(self, host: str, ip: str) -> bool:`

## Method-by-Method Analysis: spiderfoot/db.py

### Summary
- **Current version:** 38 functions/methods/classes
- **dev-5.3.3 version:** 8 functions/methods/classes
- **New:** 37
- **Removed:** 7
- **Common:** 1

### ✅ New Functions/Methods (37)
- `class SpiderFootDb:`
- `def __dbregex__(qry: str, data: str) -> bool:`
- `def _placeholder(self, count=1):`
- `def close(self) -> None:`
- `def configClear(self) -> None:`
- `def configGet(self) -> dict:`
- `def configSet(self, optMap: dict = {}) -> bool:`
- `def correlationResultCreate(self, instanceId: str, event_hash: str, ruleId: str, ruleName: str, ruleDescr: str, ruleRisk: str, ruleYaml: str,`
- `def create(self) -> None:`
- `def eventTypes(self) -> list:`
- `def get_entities(self, scan_id: str, event_hash: str) -> list:`
- `def get_sources(self, scan_id: str, event_hash: str) -> list:`
- `def scanConfigGet(self, instanceId: str) -> dict:`
- `def scanConfigSet(self, scan_id, optMap=dict()) -> None:`
- `def scanCorrelationList(self, instanceId: str) -> list:`
- `def scanCorrelationSummary(self, instanceId: str, by: str = "rule") -> list:`
- `def scanElementChildrenAll(self, instanceId: str, parentIds: list) -> list:`
- `def scanElementChildrenDirect(self, instanceId: str, elementIdList: list) -> list:`
- `def scanElementSourcesAll(self, instanceId: str, childData: list) -> list:`
- `def scanElementSourcesDirect(self, instanceId: str, elementIdList: list) -> list:`
- `def scanErrors(self, instanceId: str, limit: int = 0) -> list:`
- `def scanEventStore(self, instanceId: str, sfEvent, truncateSize: int = 0) -> None:`
- `def scanInstanceCreate(self, instanceId: str, scanName: str, scanTarget: str) -> None:`
- `def scanInstanceDelete(self, instanceId: str) -> bool:`
- `def scanInstanceGet(self, instanceId: str) -> list: """Return info about a scan instance (name, target, created, started,`
- `def scanInstanceList(self) -> list:`
- `def scanInstanceSet(self, instanceId: str, started: str = None, ended: str = None, status: str = None) -> None:`
- `def scanLogEvents(self, batch: list) -> bool:`
- `def scanLogEvents(self, batch: list) -> bool:`
- `def scanLogs(self, instanceId: str, limit: int = None, fromRowId: int = 0, reverse: bool = False) -> list:`
- `def scanResultEvent( self, instanceId: str, eventType: str = 'ALL', srcModule: str = None, data: list = None, sourceId: list = None, correlationId: str = None,`
- `def scanResultEventUnique(self, instanceId: str, eventType: str = 'ALL', filterFp: bool = False) -> list:`
- `def scanResultHistory(self, instanceId: str) -> list:`
- `def scanResultSummary(self, instanceId: str, by: str = "type") -> list:`
- `def scanResultsUpdateFP(self, instanceId: str, resultHashes: list, fpFlag: int) -> bool:`
- `def search(self, criteria: dict, filterFp: bool = False) -> list:`
- `def vacuumDB(self) -> None:`

### ❌ Removed Functions/Methods (7)
- `class DatabaseSecurity:`
- `def _ensure_audit_table(self) -> None:`
- `def audit_log(self, operation: str, table: str, user_id: str = None,`
- `def clean_audit_logs(self, retention_days: int = 90) -> None:`
- `def hash_sensitive_data(self, data: str, salt: str = None) -> str:`
- `def secure_connection_params(self, params: Dict[str, Any]) -> Dict[str, Any]:`
- `def validate_sql_query(self, query: str) -> bool:`

### 🔄 Modified Functions/Methods (showing line count changes)
- `def __init__` (line 404 vs 10)

---
# Significant Module Changes

## modules/sfp__ai_threat_intel.py
**Change summary:** modules/sfp__ai_threat_intel.py      |  21 +-
**Current functions (first 5):**
- `38:def mean(values):`
- `42:def std_dev(values):`

## modules/sfp__security_hardening.py
**Change summary:** modules/sfp__security_hardening.py   |  14 +-

## modules/sfp__stor_db_advanced.py
**Change summary:** modules/sfp__stor_db_advanced.py     | 213 +++++--------

## modules/sfp__stor_stdout.py
**Change summary:** modules/sfp__stor_stdout.py          |  28 +-

## modules/sfp_advanced_correlation.py
**Change summary:** modules/sfp_advanced_correlation.py  | 499 -------------------------------

## modules/sfp_base64.py
**Change summary:** modules/sfp_base64.py                |   1 -

## modules/sfp_blockchain_analytics.py
**Change summary:** modules/sfp_blockchain_analytics.py  | 561 -----------------------------------

## modules/sfp_c99.py
**Change summary:** modules/sfp_c99.py                   |  17 +-

## modules/sfp_cisco_umbrella.py
**Change summary:** modules/sfp_cisco_umbrella.py        | 116 +++++---

## modules/sfp_luminar.py
**Change summary:** modules/sfp_luminar.py               |  29 +-
