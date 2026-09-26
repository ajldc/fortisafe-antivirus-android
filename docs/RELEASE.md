# Política de release — FortiSafe Antivírus para Android

Como uma versão é numerada, o que ela contém, como é assinada e o que a AGPL
exige de cada binário distribuído. **Nenhuma versão foi publicada ainda**;
esta política vale a partir da primeira.

## 1. Versão

- **`versionName` semântico** (`MAJOR.MINOR.PATCH`, [SemVer](https://semver.org/lang/pt-BR/)):
  - `MAJOR` — mudança que quebra compatibilidade com bases ou dados locais
    já instalados, ou mudança de escopo do produto.
  - `MINOR` — funcionalidade nova compatível.
  - `PATCH` — correção.
  - Pré-lançamentos usam sufixo: `1.0.0-beta.1`, `1.0.0-rc.1` (o
    `app/build.gradle` já aceita `-DversionNameSuffix=...`).
- **`versionCode` sempre crescente**, derivado da versão:

  ```
  versionCode = MAJOR × 1 000 000 + MINOR × 10 000 + PATCH × 100 + N
  ```

  onde `N` (00–99) é o número do build dentro do mesmo `PATCH` (faixas de
  teste, correções de última hora antes de publicar). Exemplos:
  `1.0.0` build 1 → `1000001`; `1.2.3` build 0 → `1020300`. A Google Play
  rejeita `versionCode` menor ou igual a um já enviado — a fórmula garante a
  ordem sem contagem manual.
- **Primeira versão do FortiSafe: `1.0.0`.** Decisão deste documento:
  o upstream está em `3.18` (`versionCode 318`), mas o FortiSafe é outro
  produto, com outro `applicationId`; continuar de `3.19` sugeriria uma
  continuidade de lançamentos que o FortiSafe não teve. Alternativa
  descartada: herdar a numeração do Hypatia. Não há conflito na loja porque o
  `applicationId` é diferente, e `1000001 > 318` de qualquer forma.
- **Tag git:** `vMAJOR.MINOR.PATCH` (por exemplo, `v1.0.0`; pré-lançamento
  `v1.0.0-beta.1`), **anotada e assinada** (`git tag -s`) por quem faz o
  release. A tag aponta para o commit de `main` que gerou os binários — nunca
  para um commit fora de `main`. É o **único** formato que o
  `.github/workflows/release.yml` aceita: tag fora dele (inclusive as 87
  herdadas do Hypatia, como `v3.18`) não gera release — ver
  `docs/UPSTREAM.md`, "Tags do upstream".

## 2. O que um release contém

Publicado na página de *Releases* do GitHub, na tag correspondente, em duas
etapas.

**Etapa automática (`.github/workflows/release.yml`).** O push de uma tag no
formato da seção 1 cria um **pré-lançamento** com estes anexos, onde `<tag>`
é o nome da tag (por exemplo, `v1.0.0`):

| Artefato | Observação |
|---|---|
| `fortisafe-antivirus-android-<tag>-unsigned.apk` | APK de release **não assinado** (`assembleRelease`). Serve para teste e verificação; não é para usuário final. |
| `fortisafe-antivirus-android-<tag>-unsigned.aab` | Android App Bundle **não assinado** (`bundleRelease`). |
| `fortisafe-antivirus-android-<tag>.cdx.json` | SBOM no formato **CycloneDX 1.5**, gerado na CI por `scripts/sbom_from_verification_metadata.py` a partir de `gradle/verification-metadata.xml`. É a lista de artefatos verificados pelo Gradle, **não** uma análise do APK; cobertura e limites em `scripts/README-sbom.md`. |
| `SHA256SUMS.txt` | Somas SHA-256 dos três arquivos acima, uma por linha, geradas no job de build e conferidas pelo job de publicação antes de criar o release. |
| Notas | Geradas pelo GitHub, precedidas do aviso de que os binários não estão assinados e da indicação do código-fonte correspondente (seção 3). |

⚠️ **Estado transitório (16/09/2026):** enquanto a assinatura pela Google
Play não estiver configurada (o que será feito quando a publicação na Google
Play for preparada), o workflow publica **só esse pré-lançamento, com APK e
AAB não assinados, para teste e verificação**. Nada disso é distribuído a
usuários finais nem enviado à loja.

**Etapa manual (promover a release).** Quando a assinatura existir, quem faz
o release anexa ao pré-lançamento os arquivos abaixo e o promove a release:

| Artefato | Observação |
|---|---|
| `fortisafe-antivirus-android-<tag>.aab` | O AAB assinado com a chave de upload e enviado à Google Play. |
| `fortisafe-antivirus-android-<tag>.apk` | APK universal **gerado pela Google Play a partir do AAB** (App Bundle Explorer), assinado com a chave de assinatura do app — a mesma dos APKs que a loja entrega. Assim, quem instala pelo GitHub recebe atualizações pela loja e vice-versa. |
| `SHA256SUMS.txt` | Regenerado para cobrir todos os anexos (os da CI mais os dois acima), substituindo o da etapa automática. |
| Notas de versão | No corpo do release, em pt-BR, com as seções *Novidades*, *Correções*, *Segurança* e *Bases de assinaturas*. As mesmas notas vão para `fastlane/metadata/android/<idioma>/changelogs/<versionCode>.txt` em pt-BR, en e es. |

Alternativa descartada para o APK: assinar localmente com a chave de upload.
Descartada porque a assinatura seria diferente da que a loja usa; o Android
recusaria atualizar um APK pelo outro, e o usuário teria de desinstalar.

## 3. Código-fonte correspondente (obrigação da AGPL)

A AGPL-3.0 exige que quem recebe o binário possa obter o **código-fonte
correspondente** exato daquele binário. Regras deste projeto:

- **A tag do release é a fonte.** Todo binário distribuído (AAB, APK no
  GitHub, APK entregue pela Google Play) é construído a partir do commit da
  tag, sem alteração local.
- **Toda distribuição de binário aponta para a tag:** a página do release, a
  ficha na loja (campo de site/código-fonte) e a tela "Sobre" do app mostram
  o repositório, a versão e o hash curto do commit. O hash do commit **deve
  ser** gravado no `BuildConfig` na hora do build para aparecer na tela
  "Sobre" (a implementar quando a identidade do app for definida; hoje
  `app/build.gradle` não tem `buildConfigField`).
- O código-fonte correspondente inclui os scripts de build (`gradle/`,
  `build.gradle`, `app/build.gradle`, `gradle/verification-metadata.xml`).
  Chaves de assinatura e segredos **não** fazem parte do código-fonte
  correspondente e nunca são publicados.
- Se alguma vez um binário for construído de um commit que não é uma tag (por
  exemplo, uma faixa de teste interna), esse commit precisa estar em `main`
  e ser referenciado na descrição da faixa de teste. Binário de commit não
  publicado não é distribuído a ninguém fora da equipe.

## 4. Assinatura

- **Google Play App Signing.** A Google guarda a chave de assinatura do app;
  nós guardamos só a **chave de upload**, usada para assinar o AAB enviado.
- **Chave de upload gerada em 26/09/2026** (D-AV28): keystore PKCS12, alias
  `fortisafe-antivirus-upload`, RSA 4096, válida até 11/02/2054,
  `CN=FortiSafe Antivirus, O=Tascom Global Network LLC, L=Orlando, ST=Florida,
  C=US`. Impressão digital do certificado (pública, para conferir no Play
  Console): SHA-256
  `4B:6B:38:BD:EE:CD:51:F6:5E:4D:68:BE:8B:F6:6E:41:02:0C:81:50:41:CB:DC:F9:F8:16:73:55:C9:8B:71:F6`.
  Keystore, senha e certificado no cofre Fortisafe do 1Password.
- A chave de upload **fica fora do repositório**, em cofre de senhas, e é
  injetada no ambiente de build por variável de ambiente ou arquivo
  temporário apagado ao fim do job. Nunca em `gradle.properties` versionado,
  nunca em `local.properties` commitado, nunca como texto num workflow.
- **Nunca versionar keystore.** Nenhum `.jks`, `.keystore`, `.pk8` ou `.pem`
  de chave privada entra no repositório. Os arquivos `debugkey.pk8` e
  `debugkey.x509.pem` herdados do upstream (chave de **depuração** pública do
  Hypatia, sem valor para assinar nada do FortiSafe) **foram removidos em
  16/09/2026**, e o `.gitignore` bloqueia `*.pk8` e `*.pem`. Eles não devem
  voltar em nenhuma sincronização com o upstream (ver `docs/UPSTREAM.md`)
  nem ser usados para nenhum build nosso.
- Se a chave de upload vazar: revogar pelo Play Console (a Google permite
  registrar uma nova chave de upload), rotacionar, e registrar o incidente
  nas notas da versão seguinte. Como a chave de assinatura do app fica com a
  Google, o vazamento da chave de upload **não** compromete os usuários já
  instalados.
- A tag git é assinada com a chave GPG de quem faz o release; o fingerprint
  dessa chave será publicado no `SECURITY.md` quando existir.

## 5. Reprodutibilidade

- **Objetivo:** que qualquer pessoa consiga reconstruir o APK a partir da tag
  e obter o mesmo binário (descontada a assinatura).
- **Hoje: não verificada.** Nenhum build nosso foi comparado com outro. O
  upstream mantém `shrinkResources false` em `app/build.gradle` exatamente
  para preservar a reprodutibilidade no F-Droid; **mantenha assim** até que
  a reprodutibilidade seja verificada com e sem a opção.
- Caminho previsto: fixar versão do JDK e do SDK na CI, gravar as versões
  usadas nas notas do release, e comparar o APK da CI com um build local da
  mesma tag. Quando dois builds independentes coincidirem, esta seção passa a
  "verificada" com a data e o procedimento.

## 6. Checklist antes de marcar a tag

Todos os itens, na ordem. Um item em aberto = release adiado.

1. [ ] `main` com CI verde a partir do commit candidato (build, lint,
       testes, validação do wrapper).
2. [ ] `versionName` e `versionCode` atualizados conforme a seção 1, num
       commit `release(app): vX.Y.Z`.
3. [ ] Notas de versão escritas em pt-BR, en e es (`fastlane/.../changelogs/`)
       e revisadas — ortografia e acentuação incluídas.
4. [ ] `NOTICE` conferido: toda dependência nova ou atualizada está na seção 3
       com a licença conferida na fonte; `gradle/verification-metadata.xml`
       atualizado.
5. [ ] Varredura de segredos no histórico desde a última tag: nenhuma chave,
       token ou keystore.
6. [ ] SBOM gerado e revisado: nenhuma dependência com vulnerabilidade
       conhecida sem correção ou sem justificativa registrada.
7. [ ] `AndroidManifest.xml` revisado: só as permissões declaradas à loja,
       nenhum componente exportado sem necessidade.
8. [ ] App testado com a base de assinaturas atual do FortiSafe: baixa,
       verifica a assinatura, recusa base sem assinatura e recusa base mais
       antiga que a instalada.
9. [ ] Instalação limpa e atualização a partir da versão anterior testadas
       em emulador (e em aparelho real, quando houver).
10. [ ] Tela "Sobre" mostra versão e hash do commit corretos e o link para o
        repositório (exige o hash gravado no `BuildConfig` na hora do build —
        seção 3; a implementar quando a identidade do app for definida).
11. [ ] Tag `vX.Y.Z` anotada e assinada, apontando para o commit de `main`.
12. [ ] Pré-lançamento criado pela CI conferido (APK e AAB `-unsigned`,
        `.cdx.json`, `SHA256SUMS.txt`); depois, promovido a release com AAB
        assinado, APK universal da loja, `SHA256SUMS.txt` regenerado e notas
        (seção 2); ficha da loja atualizada com o link do código-fonte.
