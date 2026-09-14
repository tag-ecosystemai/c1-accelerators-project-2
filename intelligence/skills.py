SKILL_ALIASES: dict[str, str] = {
    # Programming languages
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "c++": "c++",
    "c#": "c#",
    "go": "go",
    "golang": "go",
    "rust": "rust",

    # Backend
    "fastapi": "fastapi",
    "fast api": "fastapi",
    "flask": "flask",
    "django": "django",
    "express": "express",
    "express.js": "express",

    # APIs
    "rest": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "graphql": "graphql",

    # Databases
    "sql": "sql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "postgres db": "postgresql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "sqlite": "sqlite",
    "redis": "redis",

    # Frontend
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "vue": "vue",
    "vue.js": "vue",
    "angular": "angular",
    "html": "html",
    "css": "css",

    # AI / ML
    "machine learning": "machine learning",
    "ml": "machine learning",
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
    "deep learning": "deep learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "computer vision": "computer vision",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    # Cloud
    "aws": "aws",
    "amazon web services": "aws",
    "azure": "azure",
    "gcp": "gcp",
    "google cloud": "gcp",

    # DevOps / infrastructure
    "docker": "docker",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "git": "git",
    "github": "github",
    "gitlab": "gitlab",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",

    # Data
    "pandas": "pandas",
    "numpy": "numpy",
    "excel": "excel",
    "power bi": "power bi",
    "tableau": "tableau",
}


SKILL_CATEGORIES: dict[str, set[str]] = {
    "programming": {
        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "c#",
        "go",
        "rust",
    },
    "backend": {
        "fastapi",
        "flask",
        "django",
        "express",
    },
    "apis": {
        "rest api",
        "graphql",
    },
    "databases": {
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "sqlite",
        "redis",
    },
    "frontend": {
        "react",
        "vue",
        "angular",
        "html",
        "css",
    },
    "ai_ml": {
        "machine learning",
        "artificial intelligence",
        "deep learning",
        "natural language processing",
        "computer vision",
        "pytorch",
        "tensorflow",
        "scikit-learn",
    },
    "cloud": {
        "aws",
        "azure",
        "gcp",
    },
    "devops": {
        "docker",
        "kubernetes",
        "git",
        "github",
        "gitlab",
        "ci/cd",
    },
    "data": {
        "pandas",
        "numpy",
        "excel",
        "power bi",
        "tableau",
    },
}

AMBIGUOUS_SKILL_ALIASES: set[str] = {
    "ai",
    "go",
    "rest",
}