# FortiSafe Antivirus for Android

🇧🇷 [Leia em português (Brasil)](README.md)

> [!WARNING]
> **Under development. Not published. There is no version available for use.**
> This repository holds the source code of a product that is still being
> built. No APK has been distributed, no version is on Google Play, and the
> code, today, is still the upstream project's code, without the changes
> described below.

## What it is

FortiSafe Antivirus for Android is an app and file checker for Android, under
the **FortiSafe** brand (Tascom Global Network LLC). It is a **derivative work
of [Hypatia](https://github.com/MaintainTeam/Hypatia)**, maintained by
MaintainTeam and originally created by DivestOS
([Divested-Mobile/Hypatia](https://github.com/Divested-Mobile/Hypatia)),
distributed under the **GNU Affero General Public License v3** (AGPL-3.0) —
the same license as this repository.

Hypatia's git history has been preserved. This repository is neither a module
nor a branch of the upstream project: it is a separate product, with its own
identity, signature databases and distribution.

### What changes compared to Hypatia

| Aspect | Hypatia (upstream) | FortiSafe Antivirus (planned) |
|---|---|---|
| Identity | `org.maintainteam.hypatia`, Hypatia name and icons | `net.fortisafe.antivirus`, FortiSafe brand |
| Signature databases | Generated and published by MaintainTeam | **Generated and signed by FortiSafe**, on its own server |
| Accessibility service (`LinkScannerService`) | Present (link checking by reading the screen) | **Removed** |
| `targetSdk` | 34 | **36** |
| Distribution | IzzyOnDroid (the original DivestOS Hypatia was on F-Droid) | **Google Play** (planned) |

The identity (first row) was applied in delivery 1.1, on 2026-09-25: name,
`applicationId`, icon, colors and texts in pt-BR, en and es. Delivery 1.3, on
the same date, removed the accessibility service (third row) and the
download over Tor/Orbot; delivery 1.2 raised `targetSdk` to 36 (fourth row)
and fixed the inherited defects — its emulator regression run is still
pending. In deliveries 1.6 and 1.7 (second row, app side) the app started to
accept databases **only** from the FortiSafe server and only when signed by a
FortiSafe key pinned in the build, and to honor the emergency list
(allowlist and revocation). **The production server and key do not exist
yet** (Phase 2): today the app builds and runs, but has nowhere to download
databases from. The other changes are not applied yet; the rest of the code
is upstream version 3.18.

## What it does — and what it does not do

**It does:**

- Compute the hashes (MD5, SHA-1 and SHA-256) of installed apps and files and
  compare them against databases of **known** malware signatures, stored in
  Bloom filters.
- Check, on demand, installed apps and storage (internal, external and
  `/system`); check files shared with the app; and, with the real-time
  service enabled, check files written or renamed in internal storage.
- Download the databases only from the FortiSafe server
  (`https://db.fortisafe.net/v1/`), only over HTTPS, and install them only if
  the manifest is signed (OpenPGP, Ed25519) by a key whose full fingerprint
  is pinned in the app; reject a version older than the installed one, an
  expired database, and any file that does not match the manifest. Each file
  is checked again when loaded.
- Honor FortiSafe's signed emergency list: a known false positive (by the
  file's SHA-256, or by package **and** signing certificate of an installed
  app) does not become an alert, and a revoked database version stops being
  used.
- Work without sending files off the device: the network is used only to
  download the databases.

**It does not:**

- **Detect what is not in the databases.** Detection is by known file hash.
  A new threat, or a variant that differs by a single byte, is not
  recognized.
- **Guarantee no false positives.** A Bloom filter is a probabilistic data
  structure: by its nature, it may flag as known a file that is not in the
  database.
- **Unpack archives** (ZIP, the inner contents of an APK, etc.): the hash is
  of the file as it is.
- **Automatically check an app the moment it is installed.** In the current
  code, the install-event receiver exists, but the scan call is disabled;
  apps are checked on demand.
- **Perform behavioral analysis or heuristics.** It does not observe what
  apps do.
- **Provide web protection** (site, link or DNS filtering), and does not use
  `VpnService`.
- **Replace common sense.** Installing apps only from trusted sources,
  keeping Android up to date and being wary of links remain the main
  protection.

The app **has not been evaluated by any independent laboratory**. There are no
AV-TEST, AV-Comparatives or similar results for this product.

## How to build

Requirements confirmed by this repository's CI on 16/09/2026 (run of commit
`9bafbf2` on `ubuntu-latest`: debug build, lint and tests in 3 min 41 s — see
the *Actions* tab):

- **JDK 17** (the build declares `sourceCompatibility 17`; older JDKs do not
  compile the project).
- **Android SDK** with platform **36** (`compileSdkVersion 36`).
- The Gradle Wrapper included in the repository (`./gradlew`).

```bash
export JAVA_HOME=/path/to/jdk-17
export ANDROID_HOME=/path/to/android-sdk
./gradlew assembleDebug
```

The debug APK is written to `app/build/outputs/apk/debug/`.

The project uses **strict dependency verification**
(`org.gradle.dependency.verification=strict`, with checksums in
`gradle/verification-metadata.xml`). When syncing in Android Studio, the
upstream recommends temporarily trusting javadoc and sources artifacts:

```xml
<trusted-artifacts>
   <trust file=".*-javadoc[.]jar" regex="true"/>
   <trust file=".*-sources[.]jar" regex="true"/>
</trusted-artifacts>
```

### Signature databases: server and keys come from the build

The database server and keys appear in no menu: they come from the build
(databases protocol v1; decision D-AV18).

| Gradle property | Debug | Release |
|---|---|---|
| `fortisafe.bases.url` | optional (e.g. `http://10.0.2.2:8080/v1/` for a local server) | not accepted: always `https://db.fortisafe.net/v1/` |
| `fortisafe.bases.fingerprints` | optional | **required**: full fingerprints (40 uppercase hex), primary and backup, comma-separated |
| `fortisafe.bases.chaves` | optional: path to an `.asc` with **public** test keys | not accepted: the keyring is `app/src/main/res/raw/fortisafe_bases_chaves.asc` (**required**) |

- **Without any of these**, the debug build compiles and runs, but refuses to
  update the databases with a clear message (fail closed) — this is how CI
  builds it.
- **A release build without the fingerprints or without the keyring does not
  compile** (guard in `app/build.gradle`). The production key does not exist
  yet.
- In debug builds, cleartext HTTP is accepted only for `10.0.2.2` and
  `localhost` (local testing against a server on the development machine).

```bash
./gradlew assembleDebug \
  -Pfortisafe.bases.url=http://10.0.2.2:8080/v1/ \
  -Pfortisafe.bases.chaves=/path/test-keys.asc \
  -Pfortisafe.bases.fingerprints=<FINGERPRINT>
```

### Unit tests

`./gradlew testDebugUnitTest` runs the databases protocol tests on the JVM
(`app/src/test/`): accepted and rejected signatures, manifest validation,
anti-downgrade, freshness, size and SHA-256 checks, atomic swap, emergency
list, and a cross-check against fixtures signed by the databases generator.
The Ed25519 keys used by the tests are generated inside the tests.

## Branches and upstream

| Branch / remote | Role |
|---|---|
| `main` | The product. Receives changes **only through pull requests**. |
| `upstream-stable` | Mirror of the `stable` branch of `MaintainTeam/Hypatia`. Updated by *fast-forward* only; **never receives a commit of ours**. |
| remote `upstream` | `https://github.com/MaintainTeam/Hypatia.git`. Read-only in practice: **we never push there**. |

The sync procedure and the policy on what **not** to bring from upstream are
in [`docs/UPSTREAM.md`](docs/UPSTREAM.md) (in Brazilian Portuguese).

## How to contribute and how to report a vulnerability

- Contributions: read [`CONTRIBUTING.md`](CONTRIBUTING.md) (in Brazilian
  Portuguese) — pull request flow, Conventional Commits, DCO and what is
  forbidden in the repository.
- Vulnerabilities: **do not open a public issue**. Follow
  [`SECURITY.md`](SECURITY.md) (Brazilian Portuguese, with an English
  summary).
- Version and release policy: [`docs/RELEASE.md`](docs/RELEASE.md) (in
  Brazilian Portuguese).

## License and attributions

- Code: **GNU Affero General Public License, version 3 or later**
  (`AGPL-3.0-or-later`). Full text in [`LICENSE`](LICENSE).
- Derivative work of Hypatia — Copyright 2017–2024 Divested Computing Group;
  Copyleft 2025 MaintainTeam Organization (notice reproduced as the upstream
  itself declares it in the app). Modifications from 2026 on: Copyright ©
  2026 Tascom Global Network LLC.
- Third-party components, dependencies, signature sources and upstream
  translators: [`NOTICE`](NOTICE).
- ClamAV belongs to Cisco. Tascom Global Network LLC, DivestOS and
  MaintainTeam **are not affiliated** with Cisco or ESET, and this product is
  neither sponsored nor endorsed by them.

---

**Identifiers.** `applicationId`: `net.fortisafe.antivirus` (debug:
`net.fortisafe.antivirus.debug`), applied in delivery 1.1. The code namespace
is still upstream's, `us.spotco.malwarescanner`, and the version is still the
inherited 3.18.
