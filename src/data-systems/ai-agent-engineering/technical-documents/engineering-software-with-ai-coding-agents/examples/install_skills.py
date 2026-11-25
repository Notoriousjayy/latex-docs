from pathlib import Path
import shutil
root = Path(__file__).resolve().parent
for destination in (root/'.agents/skills', root/'.claude/skills'):
    destination.mkdir(parents=True, exist_ok=True)
    for skill in sorted((root/'skills').iterdir()):
        if skill.is_dir():
            shutil.copytree(skill, destination/skill.name, dirs_exist_ok=True)
