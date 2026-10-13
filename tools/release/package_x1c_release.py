#!/usr/bin/env python3
"""Package the existing de2 installer without rebuilding or changing its bytes."""
import hashlib
import json
import re
import subprocess
import tarfile
import urllib.parse
import zipfile
from pathlib import Path

SOURCE_SHA = '306d5e6dfec7834ec7fbebd16531b6156d8be657'
RUN_ID = 37981590537
INSTALLER_ID = 11649267493
INSTALLER_ZIP_SHA = '7416b638951783dae28d1962c652e8576d58b6bb5570fd29f1650662fb947c50'
ROOTFS_ZIP_SHA = '313a570f6d426aeba09b53d7cae04e97b9a582e331a004d7d563ff021bfc40fa'
TAG = 'v02.08.01.55-x1c-de2-rc1'
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'release-output'
INPUT = ROOT / 'release-input'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    OUT.mkdir(exist_ok=True)
    installer_zip = INPUT / 'installer.zip'
    rootfs_zip = INPUT / 'rootfs.zip'
    for path, digest in [(installer_zip, INSTALLER_ZIP_SHA), (rootfs_zip, ROOTFS_ZIP_SHA)]:
        if sha256(path) != digest:
            raise RuntimeError(f'Artifact digest mismatch: {path.name}')
    expected_exe = 'OrcaStudio_Windows_Installer_V02.08.01.55-x1c-controls-de2.exe'
    with zipfile.ZipFile(installer_zip) as archive:
        names = [n for n in archive.namelist() if not n.endswith('/')]
        if names != [expected_exe]:
            raise RuntimeError(f'Unexpected installer artifact content: {names}')
        with archive.open(names[0]) as src, (OUT / expected_exe).open('wb') as dst:
            import shutil
            shutil.copyfileobj(src, dst)
    # List NSIS contents without executing any installer code.
    listing = subprocess.check_output(['7z', 'l', str(OUT / expected_exe)], text=True)
    if re.search(r'(?im)^.*(?:libbambu_networking\.so|bambu_networking\.dll).*$', listing):
        raise RuntimeError('Proprietary networking plugin found in installer')
    with zipfile.ZipFile(rootfs_zip) as archive:
        names = [n for n in archive.namelist() if n.endswith('.tar.gz')]
        if len(names) != 1:
            raise RuntimeError('Expected exactly one rootfs tar.gz')
        with archive.open(names[0]) as packed:
            with tarfile.open(fileobj=packed, mode='r|gz') as outer:
                found = False
                for member in outer:
                    if member.isfile() and Path(member.name).name == 'windows-wsl2-rootfs.tar':
                        with outer.extractfile(member) as src, (INPUT / 'rootfs.tar').open('wb') as dst:
                            import shutil
                            shutil.copyfileobj(src, dst)
                        found = True
                if not found:
                    raise RuntimeError('WSL rootfs missing')
    status = None
    with zipfile.ZipFile(OUT / 'OrcaStudio_Licenses.zip', 'w', zipfile.ZIP_DEFLATED) as notices:
        paths = git('ls-tree', '-r', '--name-only', SOURCE_SHA).decode().splitlines()
        for path in paths:
            name = Path(path).name.lower()
            if name.startswith(('license', 'copying', 'copyright', 'notice')):
                notices.writestr('application/' + path, git('show', SOURCE_SHA + ':' + path))
        notices.write(ROOT / 'THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md')
        with tarfile.open(INPUT / 'rootfs.tar', 'r:') as rootfs:
            for member in rootfs:
                name = member.name.removeprefix('./').lstrip('/')
                if Path(name).name in ('libbambu_networking.so', 'bambu_networking.dll'):
                    raise RuntimeError('Proprietary networking plugin found in rootfs')
                if not member.isfile():
                    continue
                if name == 'var/lib/dpkg/status':
                    status = rootfs.extractfile(member).read().decode()
                elif (name.startswith('usr/share/doc/') and name.endswith('/copyright')) or name.startswith('usr/share/common-licenses/'):
                    notices.writestr('runtime/' + name, rootfs.extractfile(member).read())
    if not status:
        raise RuntimeError('Runtime package database missing')
    rows = []
    sources = set()
    for paragraph in status.split('\n\n'):
        fields = dict(line.split(': ', 1) for line in paragraph.splitlines() if ': ' in line and not line.startswith(' '))
        if fields.get('Status') != 'install ok installed':
            continue
        binary, version = fields['Package'], fields['Version']
        match = re.fullmatch(r'([^ ]+)(?: \((.+)\))?', fields.get('Source', binary))
        if not match:
            raise RuntimeError('Invalid source package field')
        source = match[1]
        source_version = match[2] or version
        rows.append((binary, version, source, source_version))
        sources.add((source, source_version))
    (OUT / 'runtime-packages.tsv').write_text('binary\tversion\tsource\tsource_version\n' + ''.join('\t'.join(row) + '\n' for row in sorted(rows)))
    (OUT / 'runtime-source-links.tsv').write_text('source\tversion\turl\n' + ''.join(f'{name}\t{version}\thttps://launchpad.net/ubuntu/+source/{urllib.parse.quote(name, safe="")}/{urllib.parse.quote(version, safe="")}\n' for name, version in sorted(sources)))
    recipes = []
    for path in paths:
        if path.startswith('deps/') and path.endswith('.cmake'):
            content = git('show', SOURCE_SHA + ':' + path).decode(errors='replace')
            recipes.append(f'\n===== {path} =====\n{content}')
    (OUT / 'dependency-recipes.txt').write_text('Dependency build recipes at ' + SOURCE_SHA + '\n' + ''.join(recipes))
    subprocess.run(['git', 'archive', '--format=tar.gz', '--prefix=OrcaStudio/', '-o', str(OUT / 'OrcaStudio_Source_306d5e6d.tar.gz'), SOURCE_SHA], cwd=ROOT, check=True)
    with zipfile.ZipFile(OUT / 'OrcaStudio_Dokumentation.zip', 'w', zipfile.ZIP_DEFLATED) as docs:
        for path in ['README.md', 'CHANGELOG.md', 'AUTHORS.md', 'THIRD_PARTY_NOTICES.md', 'CONTRIBUTING.md', 'LICENSE.txt']:
            docs.write(ROOT / path, path)
        for path in (ROOT / 'docs').rglob('*.md'):
            docs.write(path, path.relative_to(ROOT))
        for path in (ROOT / 'tools/release').glob('*.py'):
            docs.write(path, path.relative_to(ROOT))
    manifest = {
        'release': TAG, 'application_commit': SOURCE_SHA,
        'publication_commit': git('rev-parse', 'HEAD').decode().strip(),
        'original_build_run': RUN_ID, 'installer_artifact_id': INSTALLER_ID,
        'installer_artifact_zip_sha256': INSTALLER_ZIP_SHA,
        'application_rebuilt': False, 'release_kind': 'prerelease',
        'runtime_packages': len(rows), 'runtime_source_packages': len(sources),
        'files': [{'name': p.name, 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('release-manifest.json', 'SHA256SUMS.txt')]
    }
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (OUT / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'SHA256SUMS.txt'))
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
