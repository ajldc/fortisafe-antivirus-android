# Como contribuir — FortiSafe Antivírus para Android

Obrigado pelo interesse. Este documento diz como uma mudança entra no
repositório e o que **nunca** pode entrar. Leia também o
[`README.md`](README.md) (o que o app é e não é) e o
[`SECURITY.md`](SECURITY.md) (falhas de segurança **não** são discutidas em
issue pública).

## Fluxo de trabalho

1. **Toda mudança entra em `main` por pull request.** Não há push direto em
   `main`, nem para o mantenedor. Exceção registrada: a configuração inicial
   do repositório (16/09/2026 — workflows, chaves, governança) entrou por
   commits diretos do mantenedor, antes de a regra existir; a partir do
   primeiro código do produto, a regra é imposta pela proteção do branch.
2. Crie um branch a partir de `main` com o prefixo `feature/`
   (por exemplo, `feature/onboarding-permissoes`). Para correções, o mesmo
   prefixo serve; o tipo do commit é que distingue.
3. **Nunca faça commit em `upstream-stable`.** Esse branch é espelho do
   `MaintainTeam/Hypatia` e só avança por *fast-forward*. Mudança nossa que
   for parar lá quebra a sincronização com o upstream
   (ver [`docs/UPSTREAM.md`](docs/UPSTREAM.md)).
4. **Revisão é obrigatória.** O PR precisa de aprovação de quem consta em
   [`.github/CODEOWNERS`](.github/CODEOWNERS). Mantenedor também abre PR e
   espera revisão; quando não houver segundo revisor disponível, o PR fica
   aberto pelo menos 24 horas antes do merge, com a justificativa escrita.
5. A CI precisa passar (ver "Lint e testes" abaixo). PR com CI vermelha não é
   revisado.
6. Um PR resolve **um** assunto. Refatoração e correção de bug vão em PRs
   separados.

## Commits

Formato **[Conventional Commits](https://www.conventionalcommits.org/pt-br/)
com escopo**, em uma linha de até 72 caracteres:

```
tipo(escopo): descrição no imperativo
```

- Tipos: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`,
  `chore`, `revert`.
- Escopos usados aqui: `app` (código Android), `db` (bases de assinaturas e
  scripts), `build` (Gradle, dependências), `ci` (workflows), `docs`, `i18n`
  (traduções), `release`, `upstream` (sincronização).
- Exemplos: `feat(app): explicar cada permissão antes de pedi-la`,
  `build(deps): atualizar guava para 33.5.0`,
  `docs(security): publicar fingerprint da chave PGP`.

Commits pequenos e coesos. `git rebase` para limpar o histórico do branch é
bem-vindo **antes** da revisão começar; depois, só commits novos.

## Licença e DCO

- O código deste repositório é **AGPL-3.0-or-later**. **Toda contribuição é
  aceita sob essa mesma licença.** Não aceitamos código sob outra licença sem
  discussão prévia e registro em [`NOTICE`](NOTICE).
- Cada commit precisa do **sign-off do
  [Developer Certificate of Origin](https://developercertificate.org/)**:

  ```
  Signed-off-by: Seu Nome <seu@email>
  ```

  O `git commit -s` adiciona a linha. O sign-off declara que você tem o
  direito de contribuir aquele código sob a licença do projeto. PR sem
  sign-off em todos os commits não é mesclado.
- Código copiado de outro projeto livre precisa vir com o cabeçalho de
  copyright e licença originais e com uma entrada em `NOTICE`.

## Idioma

- **Código, identificadores, nomes de arquivos, mensagens de log e
  comentários no código: inglês.**
- **Textos mostrados ao usuário** (strings de recursos, notificações, telas):
  obrigatoriamente em **português do Brasil** (`values-pt-rBR`), **inglês**
  (`values`, padrão) e **espanhol** (`values-es`), com ortografia e
  acentuação corretas. PR que adiciona uma string sem as três não é mesclado.
  Os demais idiomas herdados do upstream não são exigidos no PR.
- **Documentação** (`docs/`, `CONTRIBUTING.md`, `SECURITY.md`, issues e PRs):
  **português do Brasil**. O `README.en.md` é a exceção e precisa continuar
  fiel ao `README.md`; quem altera um, altera o outro no mesmo PR.
- Mensagens de commit: pt-BR ou inglês, desde que sigam o formato acima.

## Proibições — o que nunca entra no repositório

- **Nenhum segredo:** senha, token, chave de API, keystore, chave de
  assinatura (de APK, de bases ou de qualquer coisa), arquivo `.jks`,
  `.keystore`, `.pk8`, `.pem` de chave privada, `local.properties` com
  caminhos pessoais. Se um segredo vazar num commit, avise pelo canal do
  `SECURITY.md` **imediatamente**: o segredo é revogado, não basta apagar o
  arquivo.
- **Nenhuma amostra de malware**, nem no código, nem em testes, nem em
  issues ou PRs. Para testar detecção use **arquivos inofensivos** (por
  exemplo, o arquivo de teste EICAR ou arquivos sintéticos criados no
  próprio teste) e **hashes** injetados numa base de teste. Se precisar
  discutir um arquivo real, cite o hash SHA-256 e a descrição.
- **Nenhuma dependência nova, nem mudança de versão, sem atualizar
  `gradle/verification-metadata.xml`.** O projeto roda com
  `org.gradle.dependency.verification=strict`; sem a soma de verificação o
  build falha, e é assim que deve ser. Dependência nova também exige entrada
  na seção 3 do `NOTICE` com a licença conferida na fonte oficial.
- **Nenhuma mudança de `applicationId`, `namespace`, assinatura, workflows
  de release ou fonte das bases** sem o mantenedor ter aberto a discussão
  antes. São decisões de produto, não de PR.
- **Nenhum dado pessoal** em issues, logs ou capturas de tela (caminhos com
  nome de usuário, IMEI, conta Google, lista de apps de um aparelho de
  terceiro).
- **Nenhum commit em `upstream-stable`** e **nenhum push para o remote
  `upstream`**.

## Lint e testes — o que a CI roda

O workflow de CI (`.github/workflows/ci.yml`) executa, com **JDK 17**:

```bash
./gradlew assembleDebug lintDebug testDebugUnitTest --stacktrace
```

Rode o mesmo comando antes de abrir o PR. Observações honestas sobre o estado
atual:

- Desde a entrega 1.6 (25/09/2026) há testes de unidade em `app/src/test`
  (JUnit 4, na JVM), para o protocolo das bases de assinaturas: verificação
  de assinatura, validação do manifesto e da lista de emergência,
  anti-rebaixamento, frescor, conferência de arquivos, troca atômica e a
  prova cruzada com fixturas assinadas pelo gerador. A lógica que decide
  fica em classes sem Android (`us.spotco.malwarescanner.bases`) justamente
  para poder ser testada assim. Chave de teste é gerada **dentro** do teste;
  nenhuma chave privada, nem de teste, entra no repositório.
- O `lintDebug` roda com `abortOnError false` (herdado do upstream); o
  relatório sai em `app/build/reports/`. Não introduza avisos novos.
- A opção `-DskipFormatKtlint`, que o CI do upstream passava, foi removida
  do nosso CI em 16/09/2026: não há plugin ktlint nem leitura dessa
  propriedade em nenhum arquivo de build do projeto, então ela não tinha
  efeito. Não a reintroduza pela sincronização com o upstream.
- Um segundo workflow (`validate-gradle-wrapper.yml`) confere o Gradle
  Wrapper. Localmente, compare a soma SHA-256 de
  `gradle/wrapper/gradle-wrapper.jar` com a publicada em
  https://gradle.org/release-checksums/ sempre que o wrapper mudar.
- As GitHub Actions foram **religadas em 16/09/2026**, depois de os
  workflows herdados serem reescritos (privilégio mínimo, actions fixadas por
  SHA, só actions do GitHub e `gradle/actions/*` permitidas). Primeiro run
  verde a partir de um commit nosso: `9bafbf2`.

## Issues

Antes de abrir, procure se já existe. Para bug, informe: versão do app ou
commit, modelo do aparelho, versão do Android, versão da base de assinaturas
(quando aplicável), o que esperava e o que aconteceu, e log sem dados
pessoais. Para falso positivo ou falso negativo: **hash SHA-256 do arquivo**,
nome do app (se for app) e a fonte de onde veio — nunca o arquivo.

Falha de segurança: **não abra issue**; siga o [`SECURITY.md`](SECURITY.md).
