from github import Github

g = Github()  # No token needed for public repos
repos = ["RooVetGit/Roo-Code", "Mnehmos/The-Ultimate-Roo-Code-Hack-Building-a-Structured-Transparent-and-Well-Documented-AI-Team"]
with open("github_data.txt", "w") as f:
    for repo_name in repos:
        repo = g.get_repo(repo_name)
        f.write(f"{repo.description}\n")
        readme = repo.get_readme()
        f.write(readme.decoded_content.decode() + "\n")