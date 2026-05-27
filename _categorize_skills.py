#!/usr/bin/env python3
"""Categorize and rank all opencode skills by usefulness within each area."""

import json, sys

sys.stdout.reconfigure(encoding="utf-8")

with open(
    r"C:\Users\LENOVO\.opencode\interactive-skills\skills.json", encoding="utf-8"
) as f:
    data = json.load(f)

skills = data["skills"]

# ---- Manual overrides for skills that keyword matching gets wrong ----
MANUAL_CAT = {
    "react-expert": "Desarrollo Web - Frontend",
    "typescript-pro": "Desarrollo Web - Frontend",
    "spring-boot-engineer": "Desarrollo Web - Backend",
    "python-pro": "Desarrollo Web - Backend",
    "golang-pro": "Desarrollo Web - Backend",
    "rust-engineer": "Desarrollo Web - Backend",
    "ml-pipeline": "IA & Machine Learning",
    "cli-developer": "DevOps & Infraestructura",
    "flutter-expert": "Móvil & Desktop",
    "react-native-expert": "Móvil & Desktop",
    "swift-expert": "Móvil & Desktop",
    "kotlin-specialist": "Móvil & Desktop",
    "embedded-systems": "DevOps & Infraestructura",
    "cpp-pro": "Desarrollo Web - Backend",
    "fastapi-expert": "Desarrollo Web - Backend",
    "csharp-developer": "Desarrollo Web - Backend",
    "java-architect": "Desarrollo Web - Backend",
    "nestjs-expert": "Desarrollo Web - Backend",
    "spring-boot-engineer": "Desarrollo Web - Backend",
    "pandas-pro": "Bases de Datos & Datos",
    "postgres-pro": "Bases de Datos & Datos",
    "database-optimizer": "Bases de Datos & Datos",
    "database-designer": "Bases de Datos & Datos",
    "database-schema-designer": "Bases de Datos & Datos",
    "debugging-wizard": "Testing & Calidad",
    "architecture-designer": "Desarrollo Web - Backend",
    "the-fool": "Testing & Calidad",
    "spec-miner": "Testing & Calidad",
    "google-workspace-cli": "DevOps & Infraestructura",
    "terraform-engineer": "DevOps & Infraestructura",
    "kubernetes-specialist": "DevOps & Infraestructura",
    "secure-code-guardian": "Seguridad",
    "fine-tuning-expert": "IA & Machine Learning",
    "rag-architect": "IA & Machine Learning",
    "scrum-master": "Gestión de Producto & Proyectos",
    "paywalls": "Marketing & Crecimiento",
    "threat-detection": "Seguridad",
    "cannibalization-check": "Marketing & Crecimiento",
    "dockerfile-and-jvm-tuning": "DevOps & Infraestructura",
    "backend-architecture": "Desarrollo Web - Backend",
    "business-growth-skills": "Liderazgo & Estrategia",
    "business-operations-skills": "Liderazgo & Estrategia",
    "business-investment-advisor": "Liderazgo & Estrategia",
    "legacy-modernizer": "Desarrollo Web - Backend",
    "vpe-advisor": "Liderazgo & Estrategia",
    "aws-dr-and-multi-region-readiness": "DevOps & Infraestructura",
    "aws-observability-and-cost-readiness": "DevOps & Infraestructura",
    "aws-workload-runtime-and-deployment": "DevOps & Infraestructura",
    "aws-account-and-organization-topology": "DevOps & Infraestructura",
    "aws-network-and-identity-foundation": "DevOps & Infraestructura",
    "intl-expansion": "Liderazgo & Estrategia",
    "general-counsel-advisor": "Legal & Compliance",
    "commercial-forecaster": "Marketing & Crecimiento",
    "commercial-policy": "Liderazgo & Estrategia",
    "iso42001-specialist": "Legal & Compliance",
    "monitoring-expert": "DevOps & Infraestructura",
    "security-reviewer": "Seguridad",
    "prompt-engineer": "IA & Machine Learning",
    "sql-pro": "Bases de Datos & Datos",
    "spark-engineer": "Bases de Datos & Datos",
    "vue-expert": "Desarrollo Web - Frontend",
    "vue-expert-js": "Desarrollo Web - Frontend",
    "commercial-skills": "Liderazgo & Estrategia",
    "ads-creative": "Marketing & Crecimiento",
    "developing-genkit-go": "IA & Machine Learning",
    "developing-genkit-python": "IA & Machine Learning",
    "developing-genkit-dart": "IA & Machine Learning",
    "developing-genkit-js": "IA & Machine Learning",
}

# ---- Category definitions ----
CATEGORIES = {
    "Desarrollo Web - Frontend": {
        "icon": "🎨",
        "keywords": [
            "react",
            "next.js",
            "vue",
            "angular",
            "svelte",
            "nuxt",
            "astro",
            "tailwind",
            "css",
            "html",
            "frontend",
            "ui",
            "ux",
            "typescript",
            "javascript",
            "jsx",
            "tsx",
            "web component",
            "storybook",
            "front",
        ],
    },
    "Desarrollo Web - Backend": {
        "icon": "⚙️",
        "keywords": [
            "django",
            "fastapi",
            "flask",
            "spring-boot",
            "spring boot",
            "node.js",
            "express",
            "nestjs",
            "dotnet",
            "csharp",
            "go",
            "golang",
            "rust",
            "python",
            "java",
            "backend",
            "rest api",
            "graphql",
            "laravel",
            "php",
            "ruby",
            "rails",
            "microservice",
            "api design",
        ],
    },
    "Bases de Datos & Datos": {
        "icon": "🗄️",
        "keywords": [
            "postgresql",
            "postgres",
            "mysql",
            "sql",
            "sqlite",
            "mongodb",
            "dynamodb",
            "redis",
            "cassandra",
            "database",
            "orm",
            "prisma",
            "data-architecture",
            "data-quality",
            "data",
            "pandas",
            "etl",
            "warehouse",
        ],
    },
    "IA & Machine Learning": {
        "icon": "🤖",
        "keywords": [
            "machine-learning",
            "deep-learning",
            "llm",
            "rag",
            "anthropic",
            "claude",
            "openai",
            "genai",
            "genkit",
            "fine-tuning",
            "embedding",
            "ai-agent",
            "ai-native",
            "ai-regression",
            "prompt",
            "vector",
            "autogen",
            "crewai",
            "claude-api",
            "data-science",
            "jupyter",
        ],
    },
    "Herramientas para AI Agents": {
        "icon": "🛠️",
        "keywords": [
            "agent-",
            "caveman",
            "continuous-learning",
            "opencode",
            "claude-code",
            "mcp",
            "hookify",
            "ecc",
            "agenthub",
            "autoresearch",
            "dispatching-parallel",
            "subagent",
            "eval-harness",
            "extract",
            "skill-",
            "command-guide",
        ],
    },
    "Móvil & Desktop": {
        "icon": "📱",
        "keywords": [
            "android",
            "kotlin",
            "swift",
            "ios",
            "ipados",
            "compose",
            "flutter",
            "react native",
            "wpf",
            "winforms",
            "win32",
            "qt",
            "desktop",
            "mobile",
            "react-native",
            "expo",
            "android-room",
            "android-clean",
        ],
    },
    "DevOps & Infraestructura": {
        "icon": "☁️",
        "keywords": [
            "docker",
            "kubernetes",
            "k8s",
            "terraform",
            "pulumi",
            "aws",
            "azure",
            "gcp",
            "cloud-",
            "ci/cd",
            "cicd",
            "jenkins",
            "github actions",
            "devops",
            "linux",
            "nginx",
            "deploy",
            "cli-",
            "env-secret",
            "dockerfile",
        ],
    },
    "Testing & Calidad": {
        "icon": "🧪",
        "keywords": [
            "test",
            "testing",
            "tdd",
            "e2e",
            "playwright",
            "cypress",
            "pytest",
            "jest",
            "vitest",
            "coverage",
            "qa",
            "regression",
            "debug",
            "chaos-engineer",
            "chaos-engineering",
            "code-reviewer",
            "adversarial-review",
            "spec-miner",
            "the-fool",
        ],
    },
    "Seguridad": {
        "icon": "🔒",
        "keywords": [
            "security",
            "cyber",
            "owasp",
            "auth",
            "cloud-security",
            "ai-security",
            "vulnerability",
            "audit",
            "compliance",
            "ciso",
            "iso",
            "soc2",
            "secret",
            "threat-detection",
        ],
    },
    "Diseño & UX/UI": {
        "icon": "✨",
        "keywords": [
            "design",
            "figma",
            "apple-hig",
            "canvas-design",
            "algorithmic-art",
            "epic-design",
            "gsap",
            "animejs",
            "lottie",
            "three.js",
            "css-animation",
            "waapi",
            "typegpu",
            "brand-guidelines",
        ],
    },
    "Video & Multimedia": {
        "icon": "🎬",
        "keywords": [
            "hyperframes",
            "video",
            "demo-video",
            "remotion",
            "website-to-hyperframes",
            "voiceover",
            "tts",
            "caption",
        ],
    },
    "Marketing & Crecimiento": {
        "icon": "📈",
        "keywords": [
            "ads-",
            "ad-",
            "advertising",
            "aeo",
            "seo",
            "marketing",
            "copywriting",
            "copy-editing",
            "email",
            "campaign",
            "cmo",
            "analytics",
            "ga4",
            "gtm",
            "aso",
            "app-store",
            "cro",
            "ab-test",
            "ab test",
            "competitor",
            "competitive",
            "content-strategy",
            "content-",
            "cold-email",
            "co-marketing",
            "brand-",
            "demand-generation",
            "cro-",
            "paywall",
            "cannibalization",
            "directory-submission",
        ],
    },
    "Content & Documentación": {
        "icon": "📝",
        "keywords": [
            "content",
            "writing",
            "doc",
            "documentation",
            "code-documenter",
            "doc-coauthoring",
            "changelog",
            "readme",
            "docx",
            "pdf",
            "code-tour",
            "codebase-onboarding",
            "humanizer",
            "behuman",
            "capture",
            "brief",
        ],
    },
    "Gestión de Producto & Proyectos": {
        "icon": "📋",
        "keywords": [
            "product",
            "project",
            "agile",
            "scrum",
            "sprint",
            "jira",
            "confluence",
            "atlassian",
            "backlog",
            "roadmap",
            "pmf",
            "cpo",
            "product-owner",
            "code-to-prd",
            "experiment-designer",
        ],
    },
    "Legal & Compliance": {
        "icon": "⚖️",
        "keywords": [
            "legal",
            "compliance",
            "regulatory",
            "fda",
            "capa",
            "eu-ai-act",
            "iso",
            "qms",
            "contract",
            "proposal",
            "nda",
            "compliance-os",
            "compliance-readiness",
            "fda-",
            "aims-audit",
        ],
    },
    "Liderazgo & Estrategia": {
        "icon": "👔",
        "keywords": [
            "ceo",
            "cto",
            "cfo",
            "cro",
            "coo",
            "chro",
            "ciso",
            "c-level",
            "board",
            "executive",
            "council",
            "founder",
            "strategy",
            "leadership",
            "management",
            "chief-",
            "advisor",
            "boardroom",
            "board-",
            "company-os",
            "culture",
            "change-management",
            "commercial-",
            "deal-desk",
            "revenue",
            "capacity-planner",
            "operations",
            "channel-economics",
            "andreessen",
            "challenge",
            "decide",
        ],
    },
    "Otros": {"icon": "📦", "keywords": []},
}


def classify_skill(name, desc):
    text = (name + " " + desc).lower()

    best_cat = None
    best_score = 0

    for cat_name, cat_info in CATEGORIES.items():
        if cat_name == "Otros":
            continue
        score = 0
        for kw in cat_info["keywords"]:
            if kw.lower() in text:
                score += 1
        if score > best_score:
            best_score = score
            best_cat = cat_name

    if best_score == 0:
        return "Otros"
    return best_cat


def usefulness_score(skill):
    score = 60
    name = skill["name"].lower()
    desc = (skill.get("description", "") or "").lower()
    triggers = skill.get("triggers", [])
    domain = (skill.get("domain", "") or "").lower()
    role = (skill.get("role", "") or "").lower()

    desc_len = len(desc)
    if desc_len > 200:
        score += 15
    elif desc_len > 100:
        score += 10
    elif desc_len > 50:
        score += 5

    if triggers:
        score += 8
    if domain:
        score += 5
    if role:
        score += 3
    if "expert" in role or "specialist" in role:
        score += 5
    if "architect" in role:
        score += 4

    if desc_len < 20:
        score -= 20
    if not desc or desc.strip() == "":
        score -= 30

    core_keywords = [
        "django",
        "react",
        "python",
        "typescript",
        "rust",
        "go",
        "kubernetes",
        "docker",
        "aws",
        "postgresql",
        "fastapi",
        "next.js",
        "android",
        "kotlin",
        "spring",
        "angular",
        "vue",
        "svelte",
        "tailwind",
    ]
    for kw in core_keywords:
        if kw in name:
            score += 5
            break

    return max(0, min(100, score))


# Classify all skills
categorized = {}
for s in skills:
    name = s["name"]
    desc = s.get("description", "") or ""

    if name in MANUAL_CAT:
        cat = MANUAL_CAT[name]
    else:
        cat = classify_skill(name, desc)

    if cat not in categorized:
        categorized[cat] = []
    s["_score"] = usefulness_score(s)
    s["_category"] = cat
    categorized[cat].append(s)

# Sort within each category by score desc, then name
for cat in categorized:
    categorized[cat].sort(key=lambda s: (-s["_score"], s["name"]))

CAT_ORDER = [
    "Desarrollo Web - Frontend",
    "Desarrollo Web - Backend",
    "Bases de Datos & Datos",
    "IA & Machine Learning",
    "Herramientas para AI Agents",
    "Móvil & Desktop",
    "DevOps & Infraestructura",
    "Testing & Calidad",
    "Seguridad",
    "Diseño & UX/UI",
    "Video & Multimedia",
    "Marketing & Crecimiento",
    "Content & Documentación",
    "Gestión de Producto & Proyectos",
    "Legal & Compliance",
    "Liderazgo & Estrategia",
    "Otros",
]

output_categories = []
for cat_name in CAT_ORDER:
    if cat_name in categorized:
        icon = CATEGORIES.get(cat_name, {}).get("icon", "📦")
        output_categories.append(
            {
                "name": cat_name,
                "icon": icon,
                "count": len(categorized[cat_name]),
                "skills": [
                    {
                        "name": s["name"],
                        "description": s.get("description", ""),
                        "domain": s.get("domain", ""),
                        "role": s.get("role", ""),
                        "triggers": s.get("triggers", []),
                        "score": s["_score"],
                    }
                    for s in categorized[cat_name]
                ],
            }
        )

# Clean up temp fields
for s in skills:
    s.pop("_score", None)
    s.pop("_category", None)

output = {"categories": output_categories, "total": len(skills)}

out_path = r"C:\Users\LENOVO\.opencode\interactive-skills\skills-categorized.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Categorized {len(skills)} skills into {len(output_categories)} categories")
for cat in output_categories:
    top3 = [s["name"] for s in cat["skills"][:5]]
    print(f"\n{cat['icon']} {cat['name']} ({cat['count']})")
    print(f"   Top 5: {', '.join(top3)}")
print(f"\nOutput: {out_path}")
