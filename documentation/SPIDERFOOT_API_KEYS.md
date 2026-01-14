# SpiderFoot API Keys Configuration Guide

> **Status**: All API keys are currently **Not Configured** (Blind)
>
> **Last Updated**: 2025-12-18
>
> **Total API Keys**: 116 across 116 modules

## Executive Summary

This document provides a comprehensive list of all API keys required to enable SpiderFoot's reconnaissance and intelligence gathering capabilities. SpiderFoot integrates with 116 different external services and data providers across multiple categories.

| Metric | Value |
|--------|-------|
| **Total Modules** | 278 |
| **Modules Requiring API Keys** | 116 (41.7%) |
| **Categories** | 10 |
| **Configured Keys** | 0 |
| **Not Configured Keys** | 116 |
| **Free Tier Services** | ~45 |
| **Paid Tier Services** | ~60 |
| **Freemium Services** | ~11 |

---

## Quick Configuration Status

| Status | Count | Priority |
|--------|-------|----------|
| ✅ Configured (Blind) | 0 | N/A |
| ❌ Not Configured | 116 | All levels |
| ⚠️ Requires Verification | 0 | N/A |

---

## API Key Categories

### 1. Security & Threat Intelligence (10 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 1 | AbuseIPDB | `sfp_abuseipdb.py` | `api_key` | ❌ | Free | High |
| 2 | AlienVault OTX | `sfp_alienvault.py` | `api_key` | ❌ | Free | High |
| 3 | GreyNoise | `sfp_greynoise.py` | `api_key` | ❌ | Freemium | High |
| 4 | GreyNoise Community | `sfp_greynoise_community.py` | `api_key` | ❌ | Free | High |
| 5 | Hybrid Analysis | `sfp_hybrid_analysis.py` | `api_key` | ❌ | Free | Medium |
| 6 | Mandiant Threat Intel | `sfp_mandiant_ti.py` | `api_key` | ❌ | Paid | Medium |
| 7 | Recorded Future | `sfp_recordedfuture.py` | `api_key` | ❌ | Paid | High |
| 8 | SHODAN | `sfp_shodan.py` | `api_key` | ❌ | Paid | High |
| 9 | VirusTotal | `sfp_virustotal.py` | `api_key` | ❌ | Freemium | High |
| 10 | Pulsedive | `sfp_pulsedive.py` | `api_key` | ❌ | Free | Medium |

### 2. Search & Discovery Services (9 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 11 | BinaryEdge | `sfp_binaryedge.py` | `binaryedge_api_key` | ❌ | Freemium | Medium |
| 12 | Bing Search | `sfp_bingsearch.py` | `api_key` | ❌ | Paid | Medium |
| 13 | Bing Shared IPs | `sfp_bingsharedip.py` | `api_key` | ❌ | Paid | Low |
| 14 | Censys | `sfp_censys.py` | `censys_api_key_uid`, `censys_api_key_secret` | ❌ | Freemium | High |
| 15 | Google Search | `sfp_googlesearch.py` | `api_key` | ❌ | Paid | High |
| 16 | Google Maps | `sfp_googlemaps.py` | `api_key` | ❌ | Paid | Low |
| 17 | Google Safe Browsing | `sfp_googlesafebrowsing.py` | `api_key` | ❌ | Free | Medium |
| 18 | Project Discovery | `sfp_projectdiscovery.py` | `api_key` | ❌ | Freemium | Medium |
| 19 | ZoomEye | `sfp_zoomeye.py` | `api_key` | ❌ | Paid | Medium |

### 3. Blockchain & Cryptocurrency Services (7 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 20 | Advanced Blockchain Analytics | `sfp_blockchain_analytics.py` | `blockcypher_api_key`, `etherscan_api_key`, `blockchair_api_key` | ❌ | Mixed | Low |
| 21 | Arbitrum | `sfp_arbitrum.py` | `api_key` | ❌ | Free | Low |
| 22 | Bitcoin Who | `sfp_bitcoinwhoswho.py` | `api_key` | ❌ | Freemium | Low |
| 23 | BNB Chain | `sfp_bnb.py` | `api_key` | ❌ | Free | Low |
| 24 | Ethereum | `sfp_ethereum.py` | `api_key` | ❌ | Free | Low |
| 25 | Etherscan | `sfp_etherscan.py` | `api_key` | ❌ | Free | Medium |
| 26 | Tron | `sfp_tron.py` | `api_key` | ❌ | Free | Low |

### 4. Email & Identity Services (9 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 27 | Dehashed | `sfp_dehashed.py` | `api_key_username`, `api_key` | ❌ | Paid | High |
| 28 | EmailCrawlr | `sfp_emailcrawlr.py` | `api_key` | ❌ | Paid | Medium |
| 29 | EmailRep | `sfp_emailrep.py` | `api_key` | ❌ | Free | Medium |
| 30 | FullContact | `sfp_fullcontact.py` | `api_key` | ❌ | Paid | Medium |
| 31 | HaveIBeenPwned | `sfp_haveibeenpwned.py` | `api_key` | ❌ | Free | High |
| 32 | Hunter.io | `sfp_hunter.py` | `api_key` | ❌ | Freemium | High |
| 33 | LeakCheck | `sfp_leakcheck.py` | `api_key` | ❌ | Paid | High |
| 34 | LeakIX | `sfp_leakix.py` | `api_key` | ❌ | Free | Medium |
| 35 | Snov.io | `sfp_snov.py` | `api_key_client_id`, `api_key_client_secret` | ❌ | Freemium | Medium |

### 5. Domain & DNS Services (14 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 36 | CertSpotter | `sfp_certspotter.py` | `api_key` | ❌ | Free | High |
| 37 | CIRCL.LU | `sfp_circllu.py` | `api_key_login`, `api_key_password` | ❌ | Free | Medium |
| 38 | Cisco Umbrella | `sfp_cisco_umbrella.py` | `api_key` | ❌ | Paid | High |
| 39 | DNSGrep | `sfp_dnsgrep.py` | (Auto-managed CSRF tokens) | ❌ | Free | Low |
| 40 | HostIO | `sfp_hostio.py` | `api_key` | ❌ | Freemium | Medium |
| 41 | JsonWHOIS.com | `sfp_jsonwhoiscom.py` | `api_key` | ❌ | Freemium | Low |
| 42 | SecurityTrails | `sfp_securitytrails.py` | `api_key` | ❌ | Paid | High |
| 43 | ViewDNS.info | `sfp_viewdns.py` | `api_key` | ❌ | Freemium | Medium |
| 44 | WhoisFreaks | `sfp_whoisfreaks.py` | `api_key` | ❌ | Freemium | Medium |
| 45 | Whoisology | `sfp_whoisology.py` | `api_key` | ❌ | Paid | Medium |
| 46 | Whoxy | `sfp_whoxy.py` | `api_key` | ❌ | Freemium | Low |
| 47 | ZoneFile.io | `sfp_zonefiles.py` | `api_key` | ❌ | Paid | Low |
| 48 | Zetalytics | `sfp_zetalytics.py` | `api_key` | ❌ | Paid | Low |

### 6. IP & Geolocation Services (13 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 49 | AbstractAPI | `sfp_abstractapi.py` | `companyenrichment_api_key`, `phonevalidation_api_key`, `ipgeolocation_api_key` | ❌ | Freemium | Medium |
| 50 | CriminalIP | `sfp_criminalip.py` | `api_key` | ❌ | Freemium | High |
| 51 | Fraudguard | `sfp_fraudguard.py` | `fraudguard_api_key_account`, `fraudguard_api_key_password` | ❌ | Paid | Medium |
| 52 | IPInfo.io | `sfp_ipinfo.py` | `api_key` | ❌ | Freemium | High |
| 53 | IPQualityScore | `sfp_ipqualityscore.py` | `api_key` | ❌ | Freemium | Medium |
| 54 | IP Registry | `sfp_ipregistry.py` | `api_key` | ❌ | Freemium | Medium |
| 55 | IPStack | `sfp_ipstack.py` | `api_key` | ❌ | Freemium | Medium |
| 56 | ipapi.com | `sfp_ipapicom.py` | `api_key` | ❌ | Freemium | Medium |
| 57 | iknowwhatyoudownload.com | `sfp_iknowwhatyoudownload.py` | `api_key` | ❌ | Paid | Low |
| 58 | Netlas | `sfp_netlas.py` | `api_key` | ❌ | Freemium | Medium |
| 59 | NetworksDB | `sfp_networksdb.py` | `api_key` | ❌ | Paid | Low |
| 60 | spur.us | `sfp_spur.py` | `api_key` | ❌ | Paid | Low |
| 61 | UnwiredLabs | `sfp_unwiredlabs.py` | `api_key` | ❌ | Free | Low |

### 7. Social Media & Communication Platforms (13 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 62 | Bluesky | `sfp_bluesky.py` | `access_token` | ❌ | Free | Low |
| 63 | Discord | `sfp_discord.py` | `bot_token` | ❌ | Free | Low |
| 64 | Instagram | `sfp_instagram.py` | `access_token` | ❌ | Paid | Low |
| 65 | Mastodon | `sfp_mastodon.py` | `access_token` | ❌ | Free | Low |
| 66 | Matrix | `sfp_matrix.py` | `access_token` | ❌ | Free | Low |
| 67 | Mattermost | `sfp_mattermost.py` | `access_token` | ❌ | Free | Low |
| 68 | Reddit | `sfp_reddit.py` | `client_secret`, `client_id` | ❌ | Free | Medium |
| 69 | Rocket.Chat | `sfp_rocketchat.py` | `access_token` | ❌ | Free | Low |
| 70 | Social Links | `sfp_sociallinks.py` | `api_key` | ❌ | Paid | Low |
| 71 | Social Profiles | `sfp_socialprofiles.py` | `bing_api_key`, `google_api_key` | ❌ | Paid | Medium |
| 72 | TikTok OSINT | `sfp_tiktok_osint.py` | `api_key`, `api_secret` | ❌ | Free | Low |
| 73 | WeChat | `sfp_wechat.py` | `api_key` | ❌ | Paid | Low |
| 74 | WhatsApp | `sfp_whatsapp.py` | `api_key` | ❌ | Paid | Low |

### 8. Business Intelligence & Data Enrichment (17 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 75 | BuiltWith | `sfp_builtwith.py` | `api_key` | ❌ | Paid | Medium |
| 76 | c99 | `sfp_c99.py` | `api_key` | ❌ | Paid | Low |
| 77 | Deepinfo | `sfp_deepinfo.py` | `api_key` | ❌ | Paid | Low |
| 78 | Focsec | `sfp_focsec.py` | `api_key` | ❌ | Paid | Low |
| 79 | Fofa | `sfp_fofa.py` | `api_key` | ❌ | Freemium | Medium |
| 80 | FullHunt | `sfp_fullhunt.py` | `api_key` | ❌ | Paid | Medium |
| 81 | Leak-Lookup (Citadel) | `sfp_citadel.py` | `api_key` | ❌ | Paid | High |
| 82 | Luminar | `sfp_luminar.py` | `api_key` | ❌ | Paid | Low |
| 83 | NameAPI | `sfp_nameapi.py` | `api_key` | ❌ | Paid | Low |
| 84 | numverify | `sfp_numverify.py` | `api_key` | ❌ | Freemium | Low |
| 85 | NeutrinoAPI | `sfp_neutrinoapi.py` | `api_key` | ❌ | Freemium | Low |
| 86 | OpenCorporates | `sfp_opencorporates.py` | `api_key` | ❌ | Freemium | Low |
| 87 | Onyphe | `sfp_onyphe.py` | `api_key` | ❌ | Freemium | Medium |
| 88 | RocketReach | `sfp_rocketreach.py` | `api_key` | ❌ | Paid | Medium |
| 89 | Seon | `sfp_seon.py` | `api_key` | ❌ | Paid | Low |
| 90 | StackOverflow | `sfp_stackoverflow.py` | `api_key` | ❌ | Free | Low |
| 91 | WhatCMS | `sfp_whatcms.py` | `api_key` | ❌ | Freemium | Low |

### 9. Malware & Security Analysis (5 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 92 | Grayhat Warfare | `sfp_grayhatwarfare.py` | `api_key` | ❌ | Paid | Low |
| 93 | Koodous | `sfp_koodous.py` | `api_key` | ❌ | Free | Low |
| 94 | MalwarePatrol | `sfp_malwarepatrol.py` | `api_key` | ❌ | Freemium | Low |
| 95 | MetaDefender | `sfp_metadefender.py` | `api_key` | ❌ | Freemium | Low |
| 96 | Project Honey Pot | `sfp_honeypot.py` | `api_key` | ❌ | Free | Low |

### 10. Communication & Specialized Services (19 Services)

| # | Service | Module | Config Key | Status | Tier | Priority |
|---|---------|--------|-----------|--------|------|----------|
| 97 | Twilio | `sfp_twilio.py` | `api_key_account_sid`, `api_key_auth_token` | ❌ | Paid | Low |
| 98 | TextMagic | `sfp_textmagic.py` | `api_key_username`, `api_key` | ❌ | Paid | Low |
| 99 | Onion.link | `sfp_onioncity.py` | `api_key` | ❌ | Paid | Low |
| 100 | WiGLE | `sfp_wigle.py` | `api_key_encoded` | ❌ | Free | Low |
| 101 | API Key Leak Detector | `sfp_apileak.py` | `github_token` | ❌ | Free | Low |
| 102 | Template Module | `sfp_template.py` | `api_key` | ❌ | N/A | N/A |
| 103 | AI Summary | `sfp_ai_summary.py` | `api_key` (OpenAI) | ❌ | Paid | Low |
| 104 | BotScout | `sfp_botscout.py` | `api_key` | ❌ | Free | Low |
| 105 | F-Secure Riddler.io | `sfp_fsecure_riddler.py` | `password` | ❌ | Paid | Low |
| 106 | IntelligenceX | `sfp_intelx.py` | `api_key` | ❌ | Paid | High |
| 107 | PasteBin | `sfp_pastebin.py` | `api_key` | ❌ | Freemium | Medium |
| 108 | XForce Exchange | `sfp_xforce.py` | `xforce_api_key`, `xforce_api_key_password` | ❌ | Paid | Medium |
| 109 | Tool - Nmap | `sfp_tool_nmap.py` | `remote_password` | ❌ | N/A | Medium |
| 110 | Tool - Nuclei | `sfp_tool_nuclei.py` | `remote_password` | ❌ | N/A | Medium |
| 111 | Tool - Gobuster | `sfp_tool_gobuster.py` | `remote_password` | ❌ | N/A | Low |
| 112 | Tool - PhoneInfoga | `sfp_tool_phoneinfoga.py` | `api_key`, `remote_password` | ❌ | Free | Low |
| 113 | Tool - Wappalyzer | `sfp_tool_wappalyzer.py` | `wappalyzer_api_key` | ❌ | Paid | Low |
| 114 | Database Storage | `sfp__stor_db.py` | `postgresql_password` | ❌ | N/A | N/A |
| 115 | ElasticSearch Storage | `sfp__stor_elasticsearch.py` | `api_key`, `password` | ❌ | N/A | N/A |

---

## Top Priority API Keys (Recommended First Setup)

Configure these keys first for maximum reconnaissance capability:

1. **VirusTotal** - Malware detection & file reputation
2. **Shodan** - Internet search & device enumeration
3. **HaveIBeenPwned** - Breach database searches
4. **SecurityTrails** - WHOIS & DNS history
5. **Hunter.io** - Email discovery
6. **Censys** - Internet scanning & certificate data
7. **AlienVault OTX** - Threat intelligence feeds
8. **CertSpotter** - SSL certificate monitoring
9. **Cisco Umbrella** - Malware & phishing detection
10. **IPInfo.io** - IP geolocation & metadata

---

## Configuration Methods

### Method 1: Web UI (Recommended)

1. Navigate to `Settings` → `Module Settings`
2. Find the module you want to configure
3. Enter the API key in the configuration field
4. Save the settings
5. The key is encrypted and stored in the database

**Advantages:**
- Easiest to use
- Keys are automatically encrypted
- Per-module configuration

### Method 2: Environment Variables

Set environment variables before starting SpiderFoot:

```bash
export VIRUSTOTAL_API_KEY="your_key_here"
export SHODAN_API_KEY="your_key_here"
export HUNTER_API_KEY="your_key_here"
export SECURITYTRAILS_API_KEY="your_key_here"
export HIBP_API_KEY="your_key_here"
```

Then start SpiderFoot:

```bash
./sfcli.py
```

**Advantages:**
- Keys never stored on disk
- Suitable for containerized deployments
- Supports CI/CD pipelines

### Method 3: .env File

Create or edit `/stuff/spiderfoot/.env`:

```bash
# Security & Threat Intelligence
VIRUSTOTAL_API_KEY=your_virustotal_key
SHODAN_API_KEY=your_shodan_key
ABUSEIPDB_API_KEY=your_abuseipdb_key

# Search & Discovery
CENSYS_API_KEY_UID=your_censys_uid
CENSYS_API_KEY_SECRET=your_censys_secret

# Email & Identity
HUNTER_API_KEY=your_hunter_key
HAVEIBEENPWNED_API_KEY=your_hibp_key

# Domain & DNS
SECURITYTRAILS_API_KEY=your_securitytrails_key
```

Load the environment:

```bash
source .env
./sfcli.py
```

---

## Security Best Practices

### 1. Key Storage & Encryption

- SpiderFoot automatically encrypts API keys in the database
- Sensitive keys are prefixed with `enc:` when stored
- Use the Web UI or environment variables; avoid plaintext configuration files

### 2. Key Rotation

Periodically rotate your API keys:

```python
# Via Web UI: Settings → Module Settings → Edit → Save
# Via Environment Variables: Update exports and restart
```

### 3. Rate Limiting & Monitoring

- Monitor API usage to avoid hitting rate limits
- Many free tiers have daily/monthly quotas
- Use paid tier keys for production deployments

### 4. Access Control

- Store keys securely (use environment variables in production)
- Restrict database access
- Enable database encryption at rest
- Use unique keys for each environment (dev/staging/prod)

### 5. Compliance

SpiderFoot configuration includes validation for:
- OWASP compliance
- NIST guidelines
- ISO 27001 standards

---

## API Key Acquisition Guide

### Free Tier Services (No Credit Card Required)

These services offer free API keys without requiring a credit card:

| Service | Link | Tier | Notes |
|---------|------|------|-------|
| AlienVault OTX | https://otx.alienvault.com/api | Free | Open-source threat intelligence |
| Etherscan | https://etherscan.io/apis | Free | Ethereum blockchain explorer |
| GreyNoise Community | https://www.greynoise.io/community | Free | Basic IP threat data |
| HaveIBeenPwned | https://haveibeenpwned.com/API/v3 | Free | Breach database (requires verification) |
| Hunter.io | https://hunter.io/ | Freemium | Email discovery (free tier limited) |
| Pulsedive | https://pulsedive.com/api/ | Free | OSINT API |
| VirusTotal | https://www.virustotal.com/gui/home/upload | Freemium | Malware detection |

### Freemium Services (Credit Card May Be Required)

| Service | Link | Free Quota | Priority |
|---------|------|-----------|----------|
| Censys | https://censys.io/ | 50 queries/month | High |
| HostIO | https://hostio.com/api | 50 requests/day | Medium |
| IPInfo.io | https://ipinfo.io/ | 50k requests/month | High |
| Shodan | https://www.shodan.io/api | Limited | High |
| Whoxy | https://www.whoxy.com/api/ | 500 queries/month | Low |

---

## Database Configuration Storage

### Storage Location

API keys are stored in the SpiderFoot database:

```
Database: spiderfoot.db (SQLite)
Tables:
  - tbl_config (global settings)
  - tbl_scan_config (scan-specific overrides)
```

### Viewing Stored Configuration

Query the database:

```sql
SELECT config_name, config_value FROM tbl_config
WHERE config_name LIKE '%api%' OR config_name LIKE '%key%';
```

Note: Values are encrypted with Fernet encryption when stored via the Web UI.

---

## Testing API Keys

### Manual Testing

Test a key's validity before running scans:

```bash
# Via Python
from spiderfoot.spiderfoot import SpiderFoot
sf = SpiderFoot()
sf.setModuleOption('VirusTotal', 'api_key', 'your_key_here')
# Run test scan with single target
```

### Verification Checklist

Before running full scans:

- [ ] API key is correctly formatted
- [ ] API key is still active (not revoked)
- [ ] Rate limits are appropriate for your use case
- [ ] Test endpoint returns valid response
- [ ] Key has required permissions/scopes

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Invalid API Key" | Typo or expired key | Verify key format and regenerate if needed |
| Rate limit errors | Quota exhausted | Wait for reset or upgrade to paid tier |
| "Authentication failed" | Wrong credentials | Check API key and secret both required |
| Missing results | Module disabled | Enable module in Settings → Module Settings |
| Connection timeout | API service down | Check service status page |

### Debug Logging

Enable debug mode to troubleshoot API issues:

```bash
./sfcli.py --debug
```

Check logs at: `spiderfoot/logs/spiderfoot.log`

---

## Module Configuration Reference

### How to Find Module Configuration Options

1. Open module file: `/stuff/spiderfoot/modules/sfp_<modulename>.py`
2. Look for `self.opts` dictionary
3. Configuration keys are defined there
4. Example:

```python
self.opts = {
    'api_key': {
        'value': '',
        'flags': self.FLAG_CREDENTIAL,
        'description': 'API Key for Service'
    }
}
```

---

## Support & Documentation

### Official Documentation

- **SpiderFoot Docs**: https://docs.spiderfoot.net
- **API Module Guide**: Check individual module docstrings
- **Configuration Guide**: https://docs.spiderfoot.net/configuration/

### Community Resources

- **GitHub Issues**: Report configuration issues
- **OSINT Community Forums**: Share API experiences
- **Reddit r/OSINT**: Get recommendations for alternatives

---

## Configuration Backup

### Export Current Configuration

```python
# Backup API keys (encrypted)
sqlite3 spiderfoot.db ".dump tbl_config" > config_backup.sql

# Backup as JSON
sqlite3 spiderfoot.db \
  "SELECT config_name, config_value FROM tbl_config" \
  --json > config_backup.json
```

### Restore Configuration

```bash
sqlite3 spiderfoot.db < config_backup.sql
```

---

## Version Information

| Component | Version |
|-----------|---------|
| SpiderFoot | Latest (check `spiderfoot/__init__.py`) |
| Database Schema | Current (auto-migrated) |
| API Key Encryption | Fernet (symmetric) |
| Documentation Generated | 2025-12-18 |

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-18 | Initial comprehensive API key documentation |
| - | All 116 API keys cataloged |
| - | Configuration methods documented |
| - | Security best practices added |
| - | Troubleshooting guide included |

---

## Next Steps

1. **Priority 1**: Configure top 10 recommended API keys
2. **Priority 2**: Set up environment variables or .env file
3. **Priority 3**: Test each API key with a small scan
4. **Priority 4**: Enable additional services as needed
5. **Priority 5**: Implement key rotation schedule

---

**Document Owner**: SpiderFoot Development Team
**Last Reviewed**: 2025-12-18
**Confluence Ready**: Yes ✅
