# This file is to help map every tech stack with its badge details
# Format:-   "Display Name": ("BG_COLOR", "LOGO_NAME", "LOGO_COLOR")
type = dict[str,dict[str,tuple[str,str,str]]]

STACK_BADGE_MAP : type =  {
    "Languages": {
        "Python": ("3776AB", "python", "FFE873"),
        "JavaScript": ("F7DF1E", "javascript", "black"),
        "TypeScript": ("3178C6", "typescript", "white"),
        "Java": ("007396", "openjdk", "white"),       #the slug for java is openjdk
        "C": ("A8B9CC", "c", "white"),
        "C++": ("00599C", "cplusplus", "white"),
        "C#": ("239120", "csharp", "white"),
        "Go": ("00ADD8", "go", "black"),
        "Rust": ("000000", "rust", "white"),
        "Ruby": ("CC342D", "ruby", "white"),
        "Swift": ("FA7343", "swift", "white"),
        "Kotlin": ("7F52FF", "kotlin", "white"),
        "PHP": ("777BB4", "php", "white"),
        "Scala": ("DC322F", "scala", "white"),
        "R": ("276DC3", "r", "white"),
        "Dart": ("0175C2", "dart", "white"),
        "Lua": ("2C2D72", "lua", "white"),
        "Perl": ("39457E", "perl", "white"),
        "Haskell": ("5D4F85", "haskell", "white"),
        "Elixir": ("4B275F", "elixir", "white"),
        "Clojure": ("5881D8", "clojure", "white"),
        "Julia": ("9558B2", "julia", "white"),
        "Shell": ("121011", "gnubash", "white"),
        "PowerShell": ("5391FE", "powershell", "white"),
        "HTML": ("E34F26", "html5", "white"),
        "CSS": ("1572B6", "css3", "white"),
        "SQL": ("4479A1", "mysql", "white"),
        "MATLAB": ("0076A8", "mathworks", "white"),
        "Assembly": ("6E4C13", "assemblyscript", "white")
    },

    "Frontend Frameworks": {
        "React": ("20232A", "react", "61DAFB"),
        "Vue": ("4FC08D", "vuedotjs", "white"),
        "Angular": ("DD0031", "angular", "white"),
        "Next.js": ("000000", "nextdotjs", "white"),
        "Nuxt.js": ("00DC82", "nuxtdotjs", "white"),
        "Svelte": ("FF3E00", "svelte", "white"),
        "Astro": ("FF5D01", "astro", "white"),
        "Remix": ("000000", "remix", "white")
    },

    "Backend Frameworks": {
        "FastAPI": ("009688", "fastapi", "white"),
        "Django": ("092E20", "django", "white"),
        "Flask": ("000000", "flask", "white"),
        "Express": ("000000", "express", "white"),
        "NestJS": ("E0234E", "nestjs", "white"),
        "Spring": ("6DB33F", "spring", "white"),
        "Laravel": ("FF2D20", "laravel", "white"),
        "Rails": ("CC0000", "rubyonrails", "white"),
        "Gin": ("00ADD8", "go", "white"),
        "Fiber": ("00ADD8", "go", "white"),
        "Actix": ("000000", "rust", "white"),
        "Hono": ("E36002", "hono", "white")
    },

    "Mobile Development": {
        "React Native": ("20232A", "react", "61DAFB"),
        "Flutter": ("02569B", "flutter", "white"),
        "Expo": ("000020", "expo", "white")
    },

    "Databases": {
        "PostgreSQL": ("4169E1", "postgresql", "white"),
        "MySQL": ("4479A1", "mysql", "F29111"),
        "MongoDB": ("47A248", "mongodb", "white"),
        "SQLite": ("003B57", "sqlite", "white"),
        "Redis": ("DC382D", "redis", "white"),
        "Supabase": ("3ECF8E", "supabase", "white"),
        "Firebase": ("FFCA28", "firebase", "039BE5"),
        "Cassandra": ("1287B1", "apachecassandra", "white"),
        "Elasticsearch": ("005571", "elasticsearch", "white"),
        "DynamoDB": ("4053D6", "amazondynamodb", "white")
    },

    "Cloud & DevOps": {
        "Docker": ("2496ED", "docker", "white"),
        "Kubernetes": ("326CE5", "kubernetes", "white"),
        "AWS": ("232F3E", "amazonaws", "FF9900"),
        "GCP": ("4285F4", "googlecloud", "white"),
        "Azure": ("0078D4", "microsoftazure", "white"),
        "Vercel": ("000000", "vercel", "white"),
        "Netlify": ("00C7B7", "netlify", "white"),
        "Render": ("46E3B7", "render", "white"),
        "Heroku": ("430098", "heroku", "white"),
        "GitHub Actions": ("2088FF", "githubactions", "white"),
        "Terraform": ("7B42BC", "terraform", "white"),
        "Ansible": ("EE0000", "ansible", "white"),
        "Nginx": ("009639", "nginx", "white"),
        "Linux": ("FCC624", "linux", "black")
    },

    "AI / ML": {
        "TensorFlow": ("FF6F00", "tensorflow", "white"),
        "PyTorch": ("EE4C2C", "pytorch", "white"),
        "scikit-learn": ("F7931E", "scikitlearn", "white"),
        "Keras": ("D00000", "keras", "white"),
        "Hugging Face": ("FFD21E", "huggingface", "black"),
        "OpenCV": ("5C3EE8", "opencv", "white"),
        "NumPy": ("013243", "numpy", "white"),
        "Pandas": ("150458", "pandas", "white"),
        "Matplotlib": ("11557C", "matplotlib", "white"),
        "Jupyter": ("F37626", "jupyter", "white"),
        "LangChain": ("1C3C3C", "langchain", "white"),
        "Ollama": ("000000", "ollama", "white")
    },

    "Tools & Others": {
        "Git": ("F05032", "git", "white"),
        "GitHub": ("181717", "github", "white"),
        "VS Code": ("007ACC", "visualstudiocode", "white"),
        "Postman": ("FF6C37", "postman", "white"),
        "Figma": ("F24E1E", "figma", "black"),
        "GraphQL": ("E10098", "graphql", "white"),
        "REST API": ("009688", "fastapi", "white"),
        "WebSocket": ("010101", "socket.io", "white"),
        "Prisma": ("2D3748", "prisma", "white"),
        "tRPC": ("2596BE", "trpc", "white"),
        "Celery": ("37814A", "celery", "white"),
        "RabbitMQ": ("FF6600", "rabbitmq", "white"),
        "Kafka": ("231F20", "apachekafka", "white"),
        "Stripe": ("635BFF", "stripe", "white"),
        "Twilio": ("F22F46", "twilio", "white")
    }
}