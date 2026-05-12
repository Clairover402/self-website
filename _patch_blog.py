import re

# ===== BLOG.PY =====
path = r"D:\AAAagent\AgentStudyProject\SelfWebsite\backend\routers\blog.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add import
content = content.replace(
    "from typing import Optional",
    "from typing import Optional\nfrom schemas.common import PaginationParams, PaginatedResult"
)

# 2. Change decorator
content = content.replace(
    '@router.get(\"/\", response_model=Result[dict])',
    '@router.get(\"/\", response_model=Result[PaginatedResult[Blog]])'
)

print(content[:500])
