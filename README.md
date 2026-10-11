
# Autonomous AI Video Production Studio - Ubuntu Beginner Guide

## Concept
Note Box = তোমার মূল নিয়ন্ত্রণ। তুমি শুধু Idea Prompt বদলাবে। Python worker প্রতিদিন Asia/Dhaka time অনুযায়ী Camoufox দিয়ে AI site এ prompt পাঠাবে, result parse করে random idea বেছে production pipeline চালাবে।

## Install (Ubuntu)
```bash
cd AI-Video-Studio
chmod +x install.sh start.sh
./install.sh
```

## Run
```bash
./start.sh
# Dashboard: http://127.0.0.1:8000
# API docs: http://127.0.0.1:8000/docs
```

## First 5 tests (তোমার চাওয়া)
1. Dashboard > Idea Prompt Note Box এ prompt লিখে Save
2. Run Now চাপো
3. Camoufox connectivity test: /api/camoufox/test
4. Result থেকে random idea select হবে -> /api/ideas/history দেখো
5. Browser বন্ধ করে আবার খুললেও prompt, job, idea অক্ষত থাকবে (SQLite)

## Structure
- backend/ FastAPI + SQLite + Scheduler (APScheduler) + Queue
- frontend/ Single-page studio UI (vanilla JS, works local + Cloudflare Pages)
- adapters/ Camoufox + provider adapters
- data/ database.sqlite, settings.json
- projects/ PROJ001 ...

## Camoufox config
`data/settings.json` এ:
```json
{
  "camoufox": {
    "executable_path": "/home/YOU/.cache/camoufox/camoufox",
    "headless": false,
    "profile_dir": "/home/YOU/.mozilla/camoufox-profile",
    "connect_url": null
  }
}
```
যদি তোমার customized Camoufox already চলছে এবং remote debugging port থাকে, connect_url ব্যবহার করো।

## Cloudflare Pages deploy
frontend/ folder টা upload করো। local controller এর public URL থাকলে dashboard থেকে API_BASE সেট করো।

## Troubleshooting
- laptop off ছিল -> missed_run_policy: skip / run_on_startup (settings.json)
- selector fail -> adapters/sites/*.json এ selector আপডেট করো, screenshot logs/ এ দেখো
- DB backup -> data/backups/

