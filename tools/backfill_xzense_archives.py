"""Backfill Xzense release ZIPs using lossless deltas and validated file digests."""
import base64, hashlib, json, pathlib, zipfile
import brotli

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'arkiv' / 'versjoner'
SUPPLEMENT_ARCHIVE = ROOT / 'arkiv' / 'tillegg'
BUNDLE = pathlib.Path(__file__).with_name("xzense_brotli_patch.b64")
NAMES = {
"19":"xzense-alpha-0.5.19-hybrid-source.zip",
"19.1":"xzense-alpha-0.5.19.1-afterrun-source.zip",
"19.2":"xzense-alpha-0.5.19.2-dual-interval-source.zip",
"19.3":"xzense-alpha-0.5.19.3-slider-seconds-source.zip",
"20":"xzense-alpha-0.5.20-adaptive-ble-source.zip",
"20.1":"xzense-alpha-0.5.20.1-norsk-sprakpakke-source.zip",
"20.1r":"xzense-alpha-0.5.20.1-norsk-sprakpakke-revidert-source.zip",
"20.2":"xzense-alpha-0.5.20.2-norske-driftstilstander-source.zip",
"21":"xzense-alpha-0.5.21-burnout-notifications-source.zip",
"22":"xzense-alpha-0.5.22-stue-only-test-source.zip",
"23":"xzense-alpha-0.5.23-stue-only-relaxed-source.zip",
"24":"xzense-alpha-0.5.24-multi-proxy-relaxed-source.zip"
}
EXPECTED = {
"19":"dd125557bf2a519a6f3d8abfdf4cc8bf22f8733941f585414fd6576b9c9e0324",
"19.1":"6ea763dcfeb5e4bc7fb6041033120855ebbb873e3700d4cb2a7e4506c6971816",
"19.2":"b0ae3debdbc61d72e6a06e792086af99b2b1cfd97f8e50725a3decb379b7c943",
"20.1":"d1bae15a24ecc26e89570016fd2aff4d24d5398d1e7549d6a9a6e6e5944586c2",
"20.1r":"d85949eabc6120953883d43e2720fcc98a416354041ca6c4a0043612c82fe3a9",
"21":"a26afd04774813c9d808a20453bf9dcf66fbe6c122a215334640548517309c4d",
"22":"b4eb4bc22fb1721c19f3bcb663625752d1971bd504168f2a9db88c5d068ace0c",
"23":"d9740cb88451879cac25d803481ab18c2a55cde94ba8aec438584407a9cba5fb",
"24":"20b3ee27e985326700a06892d0426bed392a21fb202de66c51183a62aa4880d0"}
SUPPLEMENT = {
"20.1":"xzense-alpha-0.5.20.1-norsk-sprakpakke-tillegg.zip",
"20.1r":"xzense-alpha-0.5.20.1-norsk-sprakpakke-revidert-tillegg.zip",
"21":"xzense-alpha-0.5.21-burnout-notifications-tillegg.zip"}
SUPPLEMENT_PATHS = {
"20.1":["custom_components/xzense_full_preview/binary_sensor.py","custom_components/xzense_full_preview/const.py","custom_components/xzense_full_preview/entity.py","custom_components/xzense_full_preview/manifest.json","custom_components/xzense_full_preview/number.py","custom_components/xzense_full_preview/sensor.py","custom_components/xzense_full_preview/strings.json","custom_components/xzense_full_preview/translations/en.json","custom_components/xzense_full_preview/translations/nb.json","NORSK_SPRAKPAKKE_0.5.20.1.md"],
"21":["INSTALLASJON_0.5.21.md","custom_components/xzense_full_preview/__init__.py","custom_components/xzense_full_preview/burnout_notifications.py","custom_components/xzense_full_preview/client.py","custom_components/xzense_full_preview/config_flow.py","custom_components/xzense_full_preview/const.py","custom_components/xzense_full_preview/manifest.json","custom_components/xzense_full_preview/strings.json","custom_components/xzense_full_preview/translations/en.json","custom_components/xzense_full_preview/translations/nb.json"]}
def digest(files):
    d=hashlib.sha256()
    for name,body in sorted(files.items()):
        d.update(name.encode()+b"\0")
        d.update(len(body).to_bytes(8,"big"))
        d.update(body)
    return d.hexdigest()
def archive_path(version):
    """Keep the current installable release at the repository root."""
    return ROOT / NAMES[version] if version == '24' else ARCHIVE / NAMES[version]

def load(version):
    with zipfile.ZipFile(archive_path(version)) as z:
        return {x.filename:z.read(x) for x in z.infolist() if not x.is_dir()}
def patch_files(files, diff):
    files=dict(files)
    for name in diff["remove"]:
        del files[name]
    for name,(kind,value) in diff["set"].items():
        if kind=="b":
            files[name]=base64.b64decode(value,validate=True)
        elif kind=="t":
            files[name]=value.encode()
        elif kind=="s":
            lines=files[name].decode().splitlines(keepends=True)
            for start,stop,add in reversed(value):
                lines[start:stop]=add.splitlines(keepends=True)
            files[name]="".join(lines).encode()
        else:
            raise ValueError("Unknown patch type: "+kind)
    return files
def save(path,files,ordered=None):
    if path.exists():
        print("Existing, kept:",path.name)
        return
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for key in (ordered or sorted(files)):
            z.writestr(key,files[key])
    print("Created:",path.name)
def main():
    ARCHIVE.mkdir(parents=True,exist_ok=True)
    SUPPLEMENT_ARCHIVE.mkdir(parents=True,exist_ok=True)
    changes=json.loads(brotli.decompress(base64.b64decode(BUNDLE.read_text())).decode())
    states={}
    for version,diff in changes.items():
        base=diff["base"]
        if base not in states:
            states[base]=load(base)
        files=patch_files(states[base],diff)
        actual=digest(files)
        if actual!=EXPECTED[version]:
            raise RuntimeError(f"Integrity check failed on {version}: {actual}")
        states[version]=files
        save(archive_path(version),files)
        if version in SUPPLEMENT:
            contents=SUPPLEMENT_PATHS["20.1" if version=="20.1r" else version]
            save(SUPPLEMENT_ARCHIVE/SUPPLEMENT[version],files,contents)
if __name__=="__main__":
    main()
