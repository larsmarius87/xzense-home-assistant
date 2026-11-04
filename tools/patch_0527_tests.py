from pathlib import Path
import zipfile
r=Path("_build_0527")
for p in (r/"tests").glob("test_*.py"):
    s=p.read_text()
    s=s.replace("assert \"vol.In(choices)\" in source", "assert \"multiple=True\" in source")
    s=s.replace("'0.5.26'", "'0.5.27'").replace('"0.5.26"', '"0.5.27"')
    s=s.replace('RS009-41 motor', 'Viftetype RS009-41')
    s=s.replace("0.5.26.2","0.5.27")
    p.write_text(s)
out=Path("xzense-alpha-0.5.27-source.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for f in sorted(r.rglob("*")):
        if f.is_file() and not any(x in f.parts for x in ("__pycache__",".pytest_cache")) and not f.name.endswith(".pyc"):
            z.write(f,f.relative_to(r))
print("Republished",out.stat().st_size)
