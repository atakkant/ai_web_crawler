from pydantic import BaseModel

class Repo(BaseModel):
    name: str
    url: str
    description: str
    tags: str
    topics: str
    owner: str
    license : str
    architecure: str
    programming_language: str
    frameworks: str
    project_type:str
    database: str
    stars: int
    forks: int
    watchers: int
    contributors: int
    active_issues: int
    closed_issues: int
    prs: int
    discussions: int
    last_commit_date: str
    readme_quality:str
    instruction_quality:str
    demo_link:str
    documentation_link:str
    test_coverage:str
    ci_cd:str
    auto_deploy_support:str
    security_checklist:str
    security_vulnarabilities:str
    dependency_management:str
    archived_or_active:str

class Tag(BaseModel):
    tag: str
    url: str