"""
skills_db.py
Curated dictionary and taxonomy of technical skills, soft skills, tools, and domain definitions.
Used for offline NLP extraction, skill gap analysis, and career role matching.
"""

SKILLS_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "ruby", 
        "php", "swift", "kotlin", "go", "golang", "rust", "scala", "r", "dart", 
        "matlab", "perl", "bash", "shell", "powershell", "sql", "html", "html5", 
        "css", "css3", "sass", "scss"
    ],
    "Frontend Frameworks & Libraries": [
        "react", "react.js", "next.js", "vue", "vue.js", "angular", "angular.js", 
        "svelte", "tailwind", "tailwind css", "bootstrap", "material-ui", "mui", 
        "redux", "redux toolkit", "zustand", "jquery", "vite", "webpack"
    ],
    "Backend Frameworks & Technologies": [
        "node.js", "nodejs", "express", "express.js", "django", "fastapi", "flask", 
        "spring", "spring boot", "asp.net", ".net core", "laravel", "rails", 
        "ruby on rails", "nest.js", "nestjs", "graphql", "rest api", "restful api", 
        "microservices", "websockets", "grpc"
    ],
    "Databases & ORMs": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", 
        "cassandra", "oracle", "mariadb", "dynamodb", "elasticsearch", "neo4j", 
        "prisma", "sqlalchemy", "hibernate", "mongoose", "firebase", "supabase"
    ],
    "AI, Machine Learning & Data Science": [
        "machine learning", "deep learning", "nlp", "natural language processing", 
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", 
        "sklearn", "pandas", "numpy", "opencv", "hugging face", "transformers", 
        "large language models", "llm", "generative ai", "genai", "langchain", 
        "llamaindex", "bert", "gpt", "rag", "vector database", "faiss", "pinecone", 
        "chromadb", "data analysis", "data visualization", "matplotlib", "seaborn", 
        "power bi", "tableau", "statistics", "data mining"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", 
        "google cloud platform", "docker", "kubernetes", "k8s", "terraform", 
        "ansible", "jenkins", "github actions", "gitlab ci", "ci/cd", "circleci", 
        "linux", "nginx", "apache", "prometheus", "grafana", "helm", "serverless", 
        "lambda"
    ],
    "Mobile & Cross-Platform": [
        "react native", "flutter", "android", "ios", "swiftui", "xcode", 
        "android studio", "ionic", "expo"
    ],
    "Cybersecurity & Networking": [
        "penetration testing", "ethical hacking", "owasp", "network security", 
        "cryptography", "wireshark", "metasploit", "burp suite", "siem", "soc", 
        "firewall", "vpn", "vulnerability assessment", "iam", "ssl/tls"
    ],
    "Software Tools & Methodologies": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", 
        "agile", "scrum", "kanban", "postman", "swagger", "unit testing", 
        "pytest", "jest", "selenium", "cypress", "ci/cd pipelines", "figma"
    ],
    "Soft Skills & Core Competencies": [
        "communication", "team leadership", "problem solving", "critical thinking", 
        "collaboration", "adaptability", "time management", "project management", 
        "agile mindset", "analytical thinking", "presentation skills", "mentoring", 
        "conflict resolution", "creativity"
    ]
}

# Flatted list of all skills for fast lookup
ALL_SKILLS_FLAT = set()
for category, skills in SKILLS_TAXONOMY.items():
    for skill in skills:
        ALL_SKILLS_FLAT.add(skill.lower())

# Tech roles and their required/recommended core competencies
TECH_ROLES_PROFILES = {
    "Full-Stack Developer": [
        "javascript", "typescript", "react", "node.js", "express", "python", 
        "sql", "postgresql", "mongodb", "rest api", "git", "html", "css", 
        "docker", "tailwind"
    ],
    "Frontend Developer": [
        "javascript", "typescript", "react", "next.js", "vue", "html", "css", 
        "tailwind css", "bootstrap", "redux", "ui/ux", "figma", "git", "webpack", "responsive design"
    ],
    "Backend Developer": [
        "python", "java", "node.js", "django", "fastapi", "spring boot", 
        "postgresql", "mysql", "mongodb", "redis", "docker", "rest api", 
        "microservices", "aws", "git"
    ],
    "AI / Machine Learning Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch", 
        "scikit-learn", "nlp", "computer vision", "pandas", "numpy", "transformers", 
        "llm", "generative ai", "docker", "sql"
    ],
    "Data Scientist / Analyst": [
        "python", "r", "sql", "pandas", "numpy", "scikit-learn", "data analysis", 
        "data visualization", "matplotlib", "seaborn", "power bi", "tableau", 
        "statistics", "machine learning", "excel"
    ],
    "DevOps & Cloud Engineer": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", 
        "jenkins", "github actions", "linux", "bash", "ansible", "nginx", 
        "prometheus", "monitoring"
    ],
    "Mobile Application Developer": [
        "flutter", "dart", "react native", "swift", "kotlin", "ios", "android", 
        "mobile development", "rest api", "firebase", "sqlite", "git"
    ],
    "Cybersecurity Analyst": [
        "network security", "penetration testing", "ethical hacking", "wireshark", 
        "burp suite", "owasp", "linux", "python", "firewall", "siem", 
        "vulnerability assessment", "cryptography"
    ],
    "QA / Automation Test Engineer": [
        "selenium", "cypress", "jest", "pytest", "unit testing", "automation testing", 
        "postman", "jira", "python", "javascript", "ci/cd", "git"
    ],
    "Data Engineer": [
        "python", "sql", "postgresql", "spark", "kafka", "hadoop", "airflow", 
        "aws", "docker", "etl", "data warehousing", "snowflake", "mongodb"
    ]
}

# Strong action verbs for ATS and resume bullet point analysis
STRONG_ACTION_VERBS = [
    # Leadership & Management
    "spearheaded", "orchestrated", "engineered", "championed", "directed", 
    "founded", "governed", "guided", "led", "managed", "mentored", "supervised",
    # Development & Execution
    "architected", "built", "created", "coded", "deployed", "designed", 
    "developed", "devised", "implemented", "programmed", "formulated", "constructed",
    # Optimization & Results
    "accelerated", "boosted", "maximized", "optimized", "streamlined", 
    "reduced", "eliminated", "automated", "enhanced", "upgraded", "revamped", 
    "scaled", "transformed", "generated", "achieved", "delivered", "cut",
    # Collaboration & Problem Solving
    "collaborated", "partnered", "negotiated", "resolved", "troubleshot", 
    "debugged", "integrated", "facilitated", "standardized", "conducted"
]

WEAK_ACTION_VERBS = [
    "worked on", "helped with", "responsible for", "handled", "assisted in", 
    "did", "made", "looked at", "tried to", "participated in", "duties included",
    "was part of", "tasked with"
]

# Skill learning roadmaps for Gap Analysis
SKILL_LEARNING_ROADMAPS = {
    "docker": {
        "title": "Containerization with Docker",
        "description": "Learn container packaging, Dockerfiles, docker-compose, and multi-stage builds.",
        "link": "https://docker-curriculum.com/"
    },
    "kubernetes": {
        "title": "Kubernetes (K8s) Fundamentals",
        "description": "Master Pods, Services, Deployments, and orchestration for distributed microservices.",
        "link": "https://kubernetes.io/docs/tutorials/"
    },
    "aws": {
        "title": "AWS Cloud Practitioner & Solutions Architect",
        "description": "Understand EC2, S3, Lambda, IAM, VPC, and modern serverless architectures.",
        "link": "https://aws.amazon.com/training/"
    },
    "fastapi": {
        "title": "High-Performance APIs with FastAPI",
        "description": "Build asynchronous Python REST APIs with automatic OpenAPI/Swagger documentation.",
        "link": "https://fastapi.tiangolo.com/tutorial/"
    },
    "react": {
        "title": "Modern React & Next.js Ecosystem",
        "description": "Learn React hooks, state management (Zustand/Redux), SSR, and modern component patterns.",
        "link": "https://react.dev/learn"
    },
    "pytorch": {
        "title": "Deep Learning with PyTorch",
        "description": "Learn neural networks, autograd, CNNs, RNNs, and Transformer fine-tuning.",
        "link": "https://pytorch.org/tutorials/"
    },
    "machine learning": {
        "title": "Machine Learning Specialization",
        "description": "Supervised/Unsupervised learning, feature engineering, evaluation metrics, and Scikit-Learn.",
        "link": "https://www.coursera.org/specializations/machine-learning-introduction"
    },
    "generative ai": {
        "title": "Generative AI & LLM Engineering",
        "description": "Prompt engineering, RAG (Retrieval Augmented Generation), LangChain, and fine-tuning.",
        "link": "https://learn.deeplearning.ai/"
    },
    "sql": {
        "title": "Mastering SQL & Relational Databases",
        "description": "Complex JOINs, window functions, indexing, optimization, and stored procedures.",
        "link": "https://sqlbolt.com/"
    },
    "ci/cd": {
        "title": "CI/CD with GitHub Actions",
        "description": "Automate linting, unit tests, building, and deployment pipelines.",
        "link": "https://docs.github.com/en/actions"
    },
    "typescript": {
        "title": "TypeScript Fundamentals for Modern Web",
        "description": "Static typing, generics, interfaces, and building type-safe JavaScript applications.",
        "link": "https://www.typescriptlang.org/docs/"
    },
    "graphql": {
        "title": "GraphQL API Architecture",
        "description": "Queries, mutations, subscriptions, Apollo Server/Client, and schema design.",
        "link": "https://graphql.org/learn/"
    }
}
