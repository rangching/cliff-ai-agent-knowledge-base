"""驗證治理檔案結構與安全不變量。"""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
router = yaml.safe_load((root / '.agents/router.yaml').read_text())
assert router['governance']['max_writers_per_repository'] == 1
assert router['governance']['allow_direct_main_push'] is False
for path in list((root / '.github').rglob('*.yml')) + [root / '.agents/router.yaml']:
    yaml.safe_load(path.read_text())
for name in ['planning', 'implementation', 'code-review', 'testing', 'security-review']:
    text = (root / '.agents/skills' / name / 'SKILL.md').read_text()
    meta = yaml.safe_load(text.split('---', 2)[1])
    assert meta['name'] == name and meta['description']
for name in ['ARCHITECTURE', 'DEVELOPMENT', 'MULTI_AGENT_WORKFLOW']:
    assert (root / 'docs' / (name + '.md')).is_file()
print('治理檔案與 YAML 格式檢查通過')
