#!/usr/bin/env python3
"""Gera um SBOM CycloneDX 1.5 (JSON) a partir de gradle/verification-metadata.xml.

Por que assim, e não com o plugin CycloneDX do Gradle (decisão de 16/09/2026):
  Este repositório usa `org.gradle.dependency.verification=strict`. Adicionar o
  plugin `org.cyclonedx.bom` (ou a action gradle/actions/dependency-submission,
  que injeta um init-script) obrigaria a registrar em
  gradle/verification-metadata.xml os checksums do próprio plugin e de tudo o
  que ele puxa — e isso só se faz com o SDK Android instalado, resolvendo tudo
  de verdade. O arquivo de verificação já lista TODO artefato que o Gradle
  resolveu, com SHA-256; este script só o traduz para CycloneDX. Zero
  dependência além da biblioteca padrão do Python 3 (>= 3.8).

O que o SBOM cobre e o que NÃO cobre: scripts/README-sbom.md — leia antes de
citar este SBOM para qualquer fim. Resumo: é a lista de artefatos Maven
verificados pelo Gradle em todas as configurações (runtime, compilação, testes,
lint e plugins de build), sem distinção de escopo e sem grafo de dependências.
NÃO é uma análise do APK.

Uso:
  python3 scripts/sbom_from_verification_metadata.py > sbom.cdx.json
  python3 scripts/sbom_from_verification_metadata.py --output dist/app.cdx.json

Códigos de saída: 0 = ok; 2 = erro de entrada (arquivo ausente, XML inválido,
versionName não encontrado, componente duplicado).

Reprodutibilidade: `serialNumber` é um UUID v4 novo a cada execução (é o que o
formato pede para identificar cada documento); o `timestamp` respeita
SOURCE_DATE_EPOCH quando definido; os componentes saem ordenados por
(group, name, version) e os artefatos por nome.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_NAME = "sbom_from_verification_metadata.py"
SCRIPT_VERSION = "1.0.0"

# Namespace do XML do Gradle (dependency-verification-1.3.xsd).
NS = {"v": "https://schema.gradle.org/dependency-verification"}

# Tag do Gradle -> nome do algoritmo no CycloneDX (enum `hash-alg` do schema 1.5).
# Hoje o arquivo só tem <sha256>; os outros ficam mapeados para o caso de o
# Gradle passar a gravar outro algoritmo. <pgp> não é hash e é ignorado.
GRADLE_HASH_TO_CDX = {"md5": "MD5", "sha1": "SHA-1", "sha256": "SHA-256", "sha512": "SHA-512"}

# Extensões consideradas "artefato binário principal" de um componente. Só quando
# um componente tem exatamente UM artefato assim é que o hash dele vira o
# `hashes` do componente. Todos os artefatos (.aar, .jar, .pom, .module...)
# ficam sempre registrados em `properties`, sem perda de informação.
BINARY_EXTENSIONS = (".aar", ".jar")

PROPERTY_PREFIX = "gradle:verification-metadata"

# Licença do código deste repositório. Conferido em 16/09/2026: LICENSE é o
# texto da AGPL v3 e os cabeçalhos em app/src dizem "either version 3 of the
# License, or (at your option) any later version".
APP_LICENSE_SPDX = "AGPL-3.0-or-later"

DEFAULT_APP_NAME = "fortisafe-antivirus-android"
DEFAULT_VCS_URL = "https://github.com/ajldc/fortisafe-antivirus-android"


class InputError(Exception):
    """Erro de entrada: o chamador recebe exit 2 e a mensagem no stderr."""


def parse_args(argv: List[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Gera um SBOM CycloneDX 1.5 (JSON) a partir de gradle/verification-metadata.xml.",
    )
    p.add_argument("--repo-root", type=Path, default=default_root,
                   help="raiz do repositório (padrão: pasta acima de scripts/)")
    p.add_argument("--metadata", type=Path, default=None,
                   help="caminho do verification-metadata.xml (padrão: <repo-root>/gradle/verification-metadata.xml)")
    p.add_argument("--build-gradle", type=Path, default=None,
                   help="caminho do app/build.gradle (padrão: <repo-root>/app/build.gradle)")
    p.add_argument("--name", default=DEFAULT_APP_NAME,
                   help=f"nome do componente raiz (padrão: {DEFAULT_APP_NAME})")
    p.add_argument("--vcs-url", default=DEFAULT_VCS_URL,
                   help="URL do repositório para externalReferences (padrão: %(default)s)")
    p.add_argument("--output", type=Path, default=None,
                   help="arquivo de saída (padrão: stdout)")
    return p.parse_args(argv)


def read_app_info(build_gradle: Path) -> Dict[str, Optional[str]]:
    """Lê versionName (obrigatório), versionCode e applicationId de app/build.gradle.

    Só leitura por expressão regular, linha a linha. Não avalia Groovy: se o
    build.gradle passar a montar a versão dinamicamente, este leitor falha de
    forma explícita (exit 2) em vez de inventar um valor.
    """
    if not build_gradle.is_file():
        raise InputError(f"app/build.gradle não encontrado: {build_gradle}")
    text = build_gradle.read_text(encoding="utf-8")
    version_name = re.search(r'^\s*versionName\s+["\']([^"\']+)["\']', text, re.M)
    if not version_name:
        raise InputError(f"versionName não encontrado em {build_gradle} (esperado: versionName \"x.y\")")
    version_code = re.search(r"^\s*versionCode\s+(\d+)\s*$", text, re.M)
    application_id = re.search(r'^\s*applicationId\s+["\']([^"\']+)["\']', text, re.M)
    return {
        "versionName": version_name.group(1),
        "versionCode": version_code.group(1) if version_code else None,
        "applicationId": application_id.group(1) if application_id else None,
    }


Artifact = Tuple[str, Dict[str, str]]  # (nome do arquivo, {alg CycloneDX: hex})
Component = Tuple[str, str, str, List[Artifact]]  # (group, name, version, artefatos)


def read_metadata(metadata: Path) -> Tuple[Dict[str, str], List[Component]]:
    """Lê <configuration> e todos os <component> do verification-metadata.xml."""
    if not metadata.is_file():
        raise InputError(f"verification-metadata.xml não encontrado: {metadata}")
    try:
        root = ET.parse(metadata).getroot()
    except ET.ParseError as exc:
        raise InputError(f"XML inválido em {metadata}: {exc}") from exc

    config: Dict[str, str] = {}
    cfg = root.find("v:configuration", NS)
    if cfg is not None:
        for child in cfg:
            tag = child.tag.split("}")[-1]
            if child.text is not None and not list(child):
                config[tag] = child.text.strip()

    components: List[Component] = []
    for comp in root.findall("./v:components/v:component", NS):
        group, name, version = comp.get("group"), comp.get("name"), comp.get("version")
        if not (group and name and version):
            raise InputError(f"<component> sem group/name/version: {comp.attrib}")
        artifacts: List[Artifact] = []
        for art in comp.findall("v:artifact", NS):
            filename = art.get("name")
            if not filename:
                raise InputError(f"<artifact> sem name em {group}:{name}:{version}")
            hashes: Dict[str, str] = {}
            for h in art:
                tag = h.tag.split("}")[-1]
                if tag in GRADLE_HASH_TO_CDX and h.get("value"):
                    hashes[GRADLE_HASH_TO_CDX[tag]] = h.get("value").lower()
            artifacts.append((filename, hashes))
        artifacts.sort(key=lambda a: a[0])
        components.append((group, name, version, artifacts))
    components.sort(key=lambda c: (c[0], c[1], c[2]))
    return config, components


def purl_maven(group: str, name: str, version: str) -> str:
    """pkg:maven/<group>/<name>@<version>, com percent-encoding conforme a spec purl."""
    q = lambda s: urllib.parse.quote(s, safe="")  # noqa: E731
    return f"pkg:maven/{q(group)}/{q(name)}@{q(version)}"


def build_component(group: str, name: str, version: str, artifacts: List[Artifact]) -> dict:
    purl = purl_maven(group, name, version)
    comp: dict = {
        "type": "library",
        "bom-ref": purl,
        "group": group,
        "name": name,
        "version": version,
        "purl": purl,
    }
    binaries = [a for a in artifacts if a[0].endswith(BINARY_EXTENSIONS)]
    if len(binaries) == 1 and binaries[0][1]:
        comp["hashes"] = [{"alg": alg, "content": hexv} for alg, hexv in sorted(binaries[0][1].items())]
    properties = []
    for filename, hashes in artifacts:
        if hashes:
            for alg, hexv in sorted(hashes.items()):
                properties.append({"name": f"{PROPERTY_PREFIX}:artifact:{filename}", "value": f"{alg}:{hexv}"})
        else:
            properties.append({"name": f"{PROPERTY_PREFIX}:artifact:{filename}", "value": "sem-checksum"})
    if properties:
        comp["properties"] = properties
    return comp


def timestamp_utc() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        now = dt.datetime.fromtimestamp(int(epoch), dt.timezone.utc)
    else:
        now = dt.datetime.now(dt.timezone.utc)
    return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_bom(app_name: str, vcs_url: str, app: Dict[str, Optional[str]],
              config: Dict[str, str], components: List[Component]) -> dict:
    cdx_components = []
    seen = set()
    for group, name, version, artifacts in components:
        c = build_component(group, name, version, artifacts)
        if c["bom-ref"] in seen:
            raise InputError(f"componente duplicado no verification-metadata: {group}:{name}:{version}")
        seen.add(c["bom-ref"])
        cdx_components.append(c)

    artifact_count = sum(len(a) for _, _, _, a in components)
    version_name = app["versionName"] or ""

    root_properties = [{"name": "android:versionName", "value": version_name}]
    if app.get("versionCode"):
        root_properties.append({"name": "android:versionCode", "value": app["versionCode"]})
    if app.get("applicationId"):
        root_properties.append({"name": "android:applicationId", "value": app["applicationId"]})

    metadata_properties = [
        {"name": f"{PROPERTY_PREFIX}:source", "value": "gradle/verification-metadata.xml"},
        {"name": f"{PROPERTY_PREFIX}:component-count", "value": str(len(cdx_components))},
        {"name": f"{PROPERTY_PREFIX}:artifact-count", "value": str(artifact_count)},
        {"name": "fortisafe:sbom:coverage", "value": (
            "Artefatos Maven verificados pelo Gradle em todas as configurações resolvidas "
            "(runtime, compilação, testes, lint, plugins de build); sem distinção de escopo; "
            "sem grafo de dependências; NÃO é análise do APK. Ver scripts/README-sbom.md."
        )},
    ]
    for key in sorted(config):
        metadata_properties.insert(1, {"name": f"{PROPERTY_PREFIX}:{key}", "value": config[key]})

    return {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": timestamp_utc(),
            "tools": {
                "components": [{
                    "type": "application",
                    "name": SCRIPT_NAME,
                    "version": SCRIPT_VERSION,
                    "description": "Tradutor de gradle/verification-metadata.xml para CycloneDX (biblioteca padrão do Python).",
                }]
            },
            "component": {
                "type": "application",
                "bom-ref": f"{app_name}@{version_name}",
                "name": app_name,
                "version": version_name,
                "description": "FortiSafe Antivírus para Android — aplicativo derivado do Hypatia.",
                "licenses": [{"license": {"id": APP_LICENSE_SPDX}}],
                "externalReferences": [{"type": "vcs", "url": vcs_url}],
                "properties": root_properties,
            },
            "properties": metadata_properties,
        },
        "components": cdx_components,
    }


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    metadata = args.metadata or (args.repo_root / "gradle" / "verification-metadata.xml")
    build_gradle = args.build_gradle or (args.repo_root / "app" / "build.gradle")
    try:
        app = read_app_info(build_gradle)
        config, components = read_metadata(metadata)
        bom = build_bom(args.name, args.vcs_url, app, config, components)
    except InputError as exc:
        print(f"{SCRIPT_NAME}: erro: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(bom, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

    with_hashes = sum(1 for c in bom["components"] if "hashes" in c)
    artifact_count = sum(len(a) for _, _, _, a in components)
    if not components:
        print(f"{SCRIPT_NAME}: aviso: nenhum <component> encontrado em {metadata}", file=sys.stderr)
    print(
        f"{SCRIPT_NAME}: {len(bom['components'])} componentes, {artifact_count} artefatos, "
        f"{with_hashes} componentes com hash principal; app {args.name} {app['versionName']}"
        + (f" -> {args.output}" if args.output else ""),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
