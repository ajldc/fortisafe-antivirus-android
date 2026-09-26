# FortiSafe Antivírus para Android

🇺🇸 [Read this in English](README.en.md)

> [!WARNING]
> **Em desenvolvimento. Não publicado. Não há versão para uso.**
> Este repositório contém o código-fonte de um produto que ainda está sendo
> construído. Nenhum APK foi distribuído, nenhuma versão está na Google Play e
> o código, hoje, ainda é o do projeto de origem, sem as mudanças descritas
> abaixo.

## O que é

O FortiSafe Antivírus para Android é um verificador de apps e arquivos para
Android, da marca **FortiSafe** (Tascom Global Network LLC). É uma **obra
derivada do [Hypatia](https://github.com/MaintainTeam/Hypatia)**, mantido pelo
MaintainTeam e originalmente criado pela DivestOS
([Divested-Mobile/Hypatia](https://github.com/Divested-Mobile/Hypatia)),
distribuído sob a **GNU Affero General Public License v3** (AGPL-3.0) — a
mesma licença deste repositório.

O histórico git do Hypatia foi preservado. Este repositório não é um módulo
nem um branch do projeto de origem: é um produto separado, com identidade,
bases de assinaturas e distribuição próprias.

### O que muda em relação ao Hypatia

| Aspecto | Hypatia (origem) | FortiSafe Antivírus (planejado) |
|---|---|---|
| Identidade | `org.maintainteam.hypatia`, nome e ícones do Hypatia | `net.fortisafe.antivirus`, marca FortiSafe |
| Bases de assinaturas | Geradas e publicadas pelo MaintainTeam | **Geradas e assinadas pelo FortiSafe**, em servidor próprio |
| Serviço de acessibilidade (`LinkScannerService`) | Presente (verificação de links lendo a tela) | **Removido** |
| `targetSdk` | 34 | **36** |
| Distribuição | IzzyOnDroid (o Hypatia original, da DivestOS, esteve no F-Droid) | **Google Play** (prevista) |

A identidade (primeira linha) foi aplicada na entrega 1.1, em 25/09/2026: nome,
`applicationId`, ícone, cores e textos em pt-BR, en e es. Na entrega 1.3, na
mesma data, saíram o serviço de acessibilidade (terceira linha) e o download
pelo Tor/Orbot; na 1.2, o `targetSdk` passou a 36 (quarta linha), com os
defeitos herdados corrigidos — a regressão em emuladores dessa entrega ainda
está por rodar. As demais mudanças ainda não estão aplicadas; o resto do
código é o do upstream na versão 3.18.

## O que faz — e o que não faz

**Faz:**

- Calcula os hashes (MD5, SHA-1 e SHA-256) de apps instalados e de arquivos e
  compara com bases de assinaturas de malware **conhecido**, armazenadas em
  Bloom filters.
- Verifica, sob demanda, os apps instalados e o armazenamento (interno,
  externo e `/system`); verifica arquivos compartilhados com o app; e, com o
  serviço em tempo real ligado, verifica arquivos gravados ou renomeados no
  armazenamento interno.
- Baixa as bases por HTTPS e confere a assinatura GPG destacada antes de usar.
- Funciona sem enviar arquivos para fora do aparelho: a rede é usada só para
  baixar as bases.

**Não faz:**

- **Não detecta o que não está nas bases.** A detecção é por hash de arquivo
  conhecido. Uma ameaça nova, ou uma variante com um byte diferente, não é
  reconhecida.
- **Pode dar falso positivo.** Bloom filter é uma estrutura probabilística:
  por natureza, pode apontar como conhecido um arquivo que não está na base.
- **Não descompacta arquivos** (ZIP, conteúdo interno de APK etc.): o hash é
  do arquivo como está.
- **Não verifica automaticamente um app no instante em que é instalado.** No
  código atual, o receptor de eventos de instalação existe, mas a chamada de
  verificação está desativada; apps são verificados sob demanda.
- **Não faz análise de comportamento nem heurística.** Não observa o que os
  apps fazem.
- **Não faz proteção web** (filtro de sites, links ou DNS) e não usa
  `VpnService`.
- **Não substitui bom senso.** Instalar apps só de fontes confiáveis, manter
  o Android atualizado e desconfiar de links continuam sendo a proteção
  principal.

O app **não foi avaliado por nenhum laboratório independente**. Não há
resultado de AV-TEST, AV-Comparatives ou similar para este produto.

## Como compilar

Requisitos confirmados pela CI deste repositório em 16/09/2026 (run do
commit `9bafbf2` em `ubuntu-latest`: build de debug, lint e testes em 3 min
41 s — ver a aba *Actions*):

- **JDK 17** (o build declara `sourceCompatibility 17`; JDKs mais antigos não
  compilam o projeto).
- **Android SDK** com a plataforma **36** (`compileSdkVersion 36`).
- O Gradle Wrapper incluído no repositório (`./gradlew`).

```bash
export JAVA_HOME=/caminho/para/jdk-17
export ANDROID_HOME=/caminho/para/android-sdk
./gradlew assembleDebug
```

O APK de depuração sai em `app/build/outputs/apk/debug/`.

O projeto usa **verificação estrita de dependências**
(`org.gradle.dependency.verification=strict`, com as somas em
`gradle/verification-metadata.xml`). Ao sincronizar no Android Studio, o
upstream recomenda marcar temporariamente os artefatos de javadoc e sources
como confiáveis:

```xml
<trusted-artifacts>
   <trust file=".*-javadoc[.]jar" regex="true"/>
   <trust file=".*-sources[.]jar" regex="true"/>
</trusted-artifacts>
```

## Branches e upstream

| Branch / remote | Função |
|---|---|
| `main` | O produto. Recebe mudanças **só por pull request**. |
| `upstream-stable` | Espelho do branch `stable` do `MaintainTeam/Hypatia`. Atualizado só por *fast-forward*; **nunca recebe commit nosso**. |
| remote `upstream` | `https://github.com/MaintainTeam/Hypatia.git`. Só leitura na prática: **nunca fazemos push para lá**. |

O procedimento de sincronização e a política do que **não** trazer do upstream
estão em [`docs/UPSTREAM.md`](docs/UPSTREAM.md).

## Como contribuir e como reportar uma vulnerabilidade

- Contribuições: leia [`CONTRIBUTING.md`](CONTRIBUTING.md) — fluxo por pull
  request, Conventional Commits, DCO e o que é proibido no repositório.
- Vulnerabilidades: **não abra issue pública**. Siga
  [`SECURITY.md`](SECURITY.md).
- Política de versões e de releases: [`docs/RELEASE.md`](docs/RELEASE.md).

## Licença e atribuições

- Código: **GNU Affero General Public License, versão 3 ou posterior**
  (`AGPL-3.0-or-later`). Texto completo em [`LICENSE`](LICENSE).
- Obra derivada do Hypatia — Copyright 2017–2024 Divested Computing Group;
  Copyleft 2025 MaintainTeam Organization (aviso reproduzido como o próprio
  upstream o declara no app). Modificações a partir de 2026: Copyright © 2026
  Tascom Global Network LLC.
- Componentes de terceiros, dependências, fontes de assinaturas e tradutores
  do upstream: [`NOTICE`](NOTICE).
- ClamAV é da Cisco. A Tascom Global Network LLC, a DivestOS e o MaintainTeam
  **não são afiliados** à Cisco nem à ESET, e este produto não é patrocinado
  nem endossado por elas.

---

**Identificadores.** `applicationId`: `net.fortisafe.antivirus` (debug:
`net.fortisafe.antivirus.debug`), aplicado na entrega 1.1. O namespace do
código continua o do upstream, `us.spotco.malwarescanner`, e a versão ainda é
a 3.18 herdada.
