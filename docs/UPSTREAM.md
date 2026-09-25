# Sincronização com o upstream (MaintainTeam/Hypatia)

Este repositório foi criado em 16/09/2026 a partir do histórico completo do
[`MaintainTeam/Hypatia`](https://github.com/MaintainTeam/Hypatia) (branch
`stable`, commit `c0f9897`, "logger: Clean up comments" — autoria em 22/04/2026,
commit em 17/05/2026). Este
documento diz como trazer mudanças novas de lá, como devolver melhorias e o
que **não** trazer.

## Estrutura

| Nome | O que é | Regra |
|---|---|---|
| remote `origin` | `https://github.com/ajldc/fortisafe-antivirus-android.git` | Nosso repositório. |
| remote `upstream` | `https://github.com/MaintainTeam/Hypatia.git` | **Só leitura.** Nunca fazemos push para lá. |
| branch `main` | O produto FortiSafe. | Recebe mudanças só por pull request revisado. |
| branch `upstream-stable` | Espelho do `upstream/stable`. | Avança **só por fast-forward**. **Nunca recebe commit nosso**, nem merge, nem cherry-pick, nem "só um ajuste". |

Por que um espelho local em vez de mesclar direto de `upstream/stable`: o
espelho deixa registrado, no nosso repositório, **exatamente** qual estado do
upstream foi revisado em cada sincronização (a tag ou o commit fica visível
em `git log upstream-stable`), e o PR de `upstream-stable` para `main` mostra
o diff inteiro do que está entrando. Se `upstream-stable` receber um commit
nosso, o fast-forward deixa de funcionar e essa rastreabilidade se perde — é
por isso que a regra é absoluta.

### Blindagem local contra push acidental

Uma vez por clone, desligue o push para o upstream. É configuração local,
não muda nada no GitHub:

```bash
git remote set-url --push upstream DISABLED
```

Depois disso, `git push upstream ...` falha com "DISABLED" em vez de tentar
enviar. (Não temos permissão de escrita lá de qualquer forma, mas a regra não
depende de a permissão continuar não existindo.)

Também uma vez por clone, **fixe o repositório padrão do `gh`**. O GitHub CLI
trata um remote chamado `upstream` como repositório-base preferido: sem esta
configuração, `gh run`, `gh workflow run`, `gh pr` e `gh api` sem `--repo`
apontam para `MaintainTeam/Hypatia`, não para o nosso. Armadilha paga em
16/09/2026: um `gh workflow run` cujo `--repo` ficou vazio tentou disparar o
workflow no repositório do MaintainTeam — só não rodou porque não temos
permissão lá.

```bash
gh repo set-default ajldc/fortisafe-antivirus-android
```

Também uma vez por clone, desligue o acompanhamento automático de tags do
upstream (por padrão, `git fetch` traz toda tag que aponte para um commit
buscado):

```bash
git config remote.upstream.tagOpt --no-tags
```

### ⚠️ Tags do upstream — nunca empurrar para o `origin`

Fato medido em 16/09/2026: como o repositório nasceu do histórico completo do
Hypatia, o `origin` **já carrega as 87 tags `v*` do upstream**
(`git ls-remote --tags origin`: 131 refs, contando as `^{}` das tags
anotadas; de `v2.9-39` até `v3.18`). Uma tag dessas
disparada no `release.yml` compilaria o código do Hypatia e publicaria um
pré-lançamento com nome FortiSafe neste repositório. O workflow tem duas
travas (filtro de formato no gatilho e guarda no primeiro passo do build —
ver o cabeçalho de `.github/workflows/release.yml`), mas a regra aqui é não
alimentar o problema:

- **Nunca** `git push origin --tags`, `git push origin --follow-tags` nem
  `git push origin --mirror`. O push de sincronização é só do branch
  (`git push origin upstream-stable`).
- Tag nova do upstream que aparecer localmente (`v3.19`, por exemplo) fica
  local ou é apagada (`git tag -d v3.19`); não sobe.
- As únicas tags que sobem para o `origin` são as de release do FortiSafe,
  no formato `vMAJOR.MINOR.PATCH` (`docs/RELEASE.md`, seção 1).

## Procedimento de sincronização

1. **Buscar o upstream.**

   ```bash
   git fetch upstream
   git log --oneline upstream-stable..upstream/stable
   ```

   Leia a lista de commits novos **antes** de qualquer merge. Se algum cair
   na seção "O que não trazer", anote para tratar no passo 4. Se o `fetch`
   trouxer tags (`[new tag]` na saída), elas ficam locais — ver "Tags do
   upstream" acima.

2. **Avançar o espelho, só por fast-forward.**

   ```bash
   git checkout upstream-stable
   git merge --ff-only upstream/stable
   git push origin upstream-stable
   ```

   Só o branch: **sem `--tags`, `--follow-tags` ou `--mirror`** (ver "Tags do
   upstream" acima).

   Se o `--ff-only` falhar, **pare**: ou alguém commitou em `upstream-stable`
   (erro nosso — investigar com `git log origin/upstream-stable
   --not upstream/stable` e corrigir com o mantenedor), ou o upstream
   reescreveu o histórico (raro; nesse caso o espelho é recriado a partir do
   novo `upstream/stable` e o fato fica registrado na tabela do fim deste
   documento).

3. **Abrir o pull request de `upstream-stable` para `main`.**

   Título: `upstream: sincronizar com MaintainTeam/Hypatia até <hash curto>`.
   No corpo, cole a lista do passo 1 e diga o que foi descartado e por quê.

   ⚠️ Esse PR é mesclado **somente** com "Create a merge commit" — nunca
   "Squash and merge" nem "Rebase and merge". Só o merge commit preserva a
   linhagem do upstream em `main`; squash ou rebase criariam commits novos com
   o mesmo conteúdo, e a sincronização seguinte reapresentaria tudo como
   conflito artificial.

   Se o GitHub acusar **conflito**, não resolva em `upstream-stable`. Crie um
   branch a partir de `main`, mescle o espelho nele e abra o PR desse branch
   (prefixo `feature/`, coerente com `CONTRIBUTING.md` e com o gatilho
   `feature/**` do CI, e fora do namespace do remote `upstream`):

   ```bash
   git checkout -b feature/upstream-sync-AAAA-MM-DD main
   git merge upstream-stable
   # resolver conflitos, revisar, commitar
   git push origin feature/upstream-sync-AAAA-MM-DD
   ```

   O merge preserva a linhagem (o `git log` continua mostrando de onde cada
   commit veio). Rebase de `main` sobre o upstream é proibido: reescreveria
   os nossos commits e quebraria referências em PRs e releases.

4. **Revisar os conflitos e as mudanças em `app/` com atenção.** As áreas em
   que o upstream e o FortiSafe divergem de propósito, e que por isso
   conflitam com frequência:

   - `app/build.gradle` — `applicationId`, `app_name`, `targetSdkVersion`,
     `versionCode`/`versionName`. A versão do upstream **nunca** substitui a
     nossa (ver `docs/RELEASE.md`).
   - `app/src/main/AndroidManifest.xml` — permissões, serviços e receivers.
     Nada que foi removido de propósito volta pelo merge.
   - Fontes das bases de assinaturas (`DatabaseSource.kt` e afins) — o
     FortiSafe consome as próprias bases; URLs e chaves do upstream não
     entram.
   - `LinkScannerService` e recursos ligados à acessibilidade — removidos do
     produto; mudanças do upstream nesses arquivos são descartadas.
   - `gradle/verification-metadata.xml` e `gradle/libs.versions.toml` —
     dependência nova do upstream entra só com a soma verificada e com a
     entrada correspondente no `NOTICE`.
   - `.github/workflows/` — **nunca** trazer de volta o `release.yml` do
     upstream (ele clona e publica no repositório do MaintainTeam) nem
     `permissions: write-all`; os workflows são nossos.
   - `fastlane/metadata/` e `README*.md` — descrevem o Hypatia; o texto do
     FortiSafe prevalece.
   - Traduções (`app/src/main/res/values-*/`) — bem-vindas, desde que não
     reintroduzam strings de funções removidas.

5. **CI verde e revisão** como em qualquer PR (`CONTRIBUTING.md`). Na hora de
   mesclar, use **só "Create a merge commit"** (ver passo 3): "Squash and
   merge" e "Rebase and merge" descartam a linhagem do upstream. Depois do
   merge, registre a sincronização na tabela do fim deste documento.

## Como devolver melhorias ao upstream

Correções e melhorias **gerais** (bug no scanner, tratamento de erro,
desempenho, tradução) devem ser oferecidas ao upstream — é o espírito da
licença e reduz o nosso custo de sincronização.

- **A decisão de enviar é do mantenedor (André)**, caso a caso. Não abra PR
  no `MaintainTeam/Hypatia` em nome do projeto sem esse aval.
- O PR é aberto **lá**, a partir de um fork pessoal ou do fork `ajldc/Hypatia`,
  com a mudança isolada (sem identidade, URLs ou textos do FortiSafe) e
  seguindo as convenções e a licença do upstream.
- Enquanto o PR não for aceito lá, a mudança vive em `main` normalmente. Quando
  for aceito, a sincronização seguinte a traz de volta pelo espelho e o merge
  reconhece o conteúdo idêntico (ou o conflito trivial é resolvido a favor do
  upstream, para reduzir a divergência).
- Mudanças que **não** se devolvem: identidade FortiSafe, integração com as
  nossas bases, textos de loja, workflows nossos — nada disso serve ao
  upstream.

## O que NÃO trazer do upstream

Lista viva. Cada item tem o motivo, para que a próxima pessoa não "corrija"
a divergência achando que foi esquecimento:

| Mudança do upstream | Por que não entra |
|---|---|
| Reativar o serviço de acessibilidade (`LinkScannerService`) ou qualquer uso de `AccessibilityService` | Removido na entrega 1.3 (25/09/2026) por custo e risco, não por proibição: a Google Play não veta a API a antivírus, mas exige divulgação destacada, declaração e vídeo (correção de 17/09/2026); e a função de proteção web não é deste app (D-AV3). |
| Qualquer uso de `VpnService` | O antivírus não faz proteção web (filtro de sites, links ou DNS) e não usa `VpnService`. |
| Voltar as fontes de bases para os servidores do MaintainTeam ou de terceiros | O FortiSafe distribui só bases geradas e assinadas por ele. |
| `release.yml` do upstream ou qualquer workflow que publique fora deste repositório | Publicaria no repositório do MaintainTeam com as nossas credenciais. |
| `permissions: write-all` em workflows | Privilégio mínimo é regra dos nossos workflows. |
| `debugkey.pk8` / `debugkey.x509.pem` e qualquer chave versionada | Nenhuma chave no repositório (`docs/RELEASE.md`). |
| Tags `v*` do upstream (`v3.19` em diante) | Tag no `origin` é candidata a release; as do Hypatia não descrevem versão nossa (ver "Tags do upstream" acima). |
| Mudança de `applicationId`, `namespace`, `versionName`/`versionCode` | São do produto; o upstream tem os dele. |
| `<queries>` para pacotes que o FortiSafe não integra (por exemplo, Orbot) | Só consultamos o que usamos; consulta de pacote sem uso é pergunta a mais na revisão da loja. |
| Download das bases pelo Tor (Orbot) | Removido na entrega 1.3 (25/09/2026) com a opção de menu, o `<queries>` e o proxy SOCKS: as bases vêm só do servidor do FortiSafe (D-AV18), e o caminho dependia de um app de terceiro. |
| `requestLegacyExternalStorage`, `allowBackup="true"` e outras opções legadas do manifesto | Revisadas para a política atual do Android/Play; não voltam pelo merge. |
| Metadados de loja e READMEs do Hypatia | Descrevem outro produto. |
| `.github/changelog.md` | Notas de release do Hypatia; só eram lidas pelo `release.yml` antigo. Removido do FortiSafe em 16/09/2026. |

Se um item da lista deixar de fazer sentido, ele é removido **com um commit
explicando por quê**, não silenciosamente.

## Registro de sincronizações

| Data | Commit do upstream | PR | Observações |
|---|---|---|---|
| 16/09/2026 | `c0f9897` (stable; autoria 22/04/2026, commit 17/05/2026) | — | Base inicial criada em 16/09/2026 a partir do histórico completo do upstream; `upstream-stable` = `c0f9897` (idêntico ao upstream); `main` recebeu no mesmo dia o commit `3f2f6b8` (aapt2 para macOS em `gradle/verification-metadata.xml`) e segue à frente. |
