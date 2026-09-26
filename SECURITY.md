# Política de segurança — FortiSafe Antivírus para Android

*English summary at the end of this file.*

## Versões com suporte

| Versão | Suporte |
|---|---|
| — | **Nenhuma versão foi publicada ainda.** Não há APK distribuído nem versão na Google Play. |

Quando houver versões publicadas, esta tabela dirá quais recebem correção de
segurança. Até lá, relatos sobre o código deste repositório são bem-vindos e
tratados como descrito abaixo.

## Como reportar uma vulnerabilidade

**Não abra issue pública** para falha de segurança.

1. **Relato privado de vulnerabilidade do GitHub (canal preferencial):**
   está **ativado** neste repositório. Na aba *Security* → *Advisories*,
   use "Report a vulnerability"
   (<https://github.com/ajldc/fortisafe-antivirus-android/security/advisories/new>).
   O relato fica visível só para quem reportou e para o mantenedor, e a
   conversa sobre a correção acontece ali mesmo.
2. **E-mail:** `costaandre@gmail.com`, com o assunto
   **`[FortiSafe Antivírus] segurança`**. Sem esse assunto o relato pode se
   perder entre outras mensagens.

Ainda não há chave PGP publicada para relatos. Quando houver, o fingerprint
ficará aqui. Se o relato exigir sigilo maior do que e-mail comum oferece,
escreva primeiro sem detalhes e combinaremos um canal.

### O que incluir

- Descrição do problema e do impacto (o que um atacante consegue fazer).
- Versão ou commit afetado, modelo do aparelho e versão do Android, quando
  fizer diferença.
- Passos para reproduzir, ou prova de conceito.
- Se envolver um arquivo malicioso: **o hash SHA-256 e a descrição**, nunca o
  arquivo (ver regra abaixo).

### ⚠️ Nunca envie amostras de malware por e-mail

Não anexe, não compacte com senha, não coloque em link "só para vocês". Envie
o **hash SHA-256** (e MD5/SHA-1, se tiver), o nome da família ou da detecção
e a descrição do comportamento. Se uma amostra for indispensável para
reproduzir, combinaremos um canal apropriado depois do primeiro contato.

## O que esperar

Compromisso do mantenedor deste repositório:

| Etapa | Prazo |
|---|---|
| Confirmação de recebimento | até **5 dias úteis** |
| Avaliação inicial (é vulnerabilidade? gravidade? escopo?) | até 15 dias corridos após a confirmação |
| Correção publicada | conforme a gravidade; o status é informado a quem reportou |
| Divulgação pública coordenada | ver abaixo |

Quem reporta é mantido a par do andamento e, se quiser, é creditado nas notas
da correção.

## Escopo

**Dentro do escopo:**

- O código do app neste repositório (`app/`).
- O pipeline de geração e assinatura das bases de assinaturas do FortiSafe,
  quando for publicado, e o formato consumido pelo app (por exemplo: aceitar
  base sem assinatura válida, base antiga no lugar de uma nova, base
  adulterada).
- Os workflows de CI/CD deste repositório (`.github/workflows/`).
- A cadeia de dependências declarada em `gradle/` (dependência comprometida,
  soma de verificação errada).

**Fora do escopo — encaminhe para quem mantém:**

- Vulnerabilidades nos **feeds de terceiros** que alimentam as bases (hoje,
  ESET e Echap): reporte ao respectivo projeto. Se o problema
  afetar o modo como **este app** usa o feed, aí é conosco também.
- Problemas no **Hypatia upstream** que não existam neste repositório:
  reporte ao [MaintainTeam](https://github.com/MaintainTeam/Hypatia). Se o
  problema existir também aqui, avise os dois lados; nós coordenamos com o
  upstream quando fizer sentido.
- Falhas da plataforma Android ou da Google Play em si.
- **Falso positivo ou falso negativo** de detecção não é vulnerabilidade;
  abra uma issue normal (sem anexar a amostra — hash e descrição).

## Divulgação coordenada

Política de **90 dias**: a partir da confirmação de recebimento, pedimos até 90
dias antes da divulgação pública, para corrigir e distribuir. Se a correção
sair antes, a divulgação pode ser antecipada de comum acordo. Se precisarmos
de mais tempo (por exemplo, dependência de terceiro ou de revisão da loja),
pediremos com justificativa, e a decisão final é de quem reportou.

Correções de segurança são identificadas nas notas de versão. Detalhes
técnicos são publicados depois que a versão corrigida estiver disponível.

## Boas práticas para quem pesquisa

- Teste em aparelho ou emulador próprio, com dados próprios.
- Não acesse, altere nem apague dados de terceiros.
- Não use o achado para nada além de demonstrar o problema.

Quem seguir estas regras não será alvo de nenhuma medida da nossa parte por
causa da pesquisa.

---

## English summary

- **Supported versions:** none published yet. No APK has been distributed and
  there is no version on Google Play.
- **How to report:** preferably through GitHub private vulnerability
  reporting, which is **enabled** for this repository (*Security* →
  *Advisories* → "Report a vulnerability", or
  <https://github.com/ajldc/fortisafe-antivirus-android/security/advisories/new>);
  or by e-mail to `costaandre@gmail.com` with the subject
  **`[FortiSafe Antivírus] segurança`**. No PGP key is published yet.
- **Never send malware samples by e-mail.** Send the SHA-256 hash and a
  description instead; if a sample is truly needed, a channel will be agreed
  after first contact.
- **What to expect:** acknowledgement within **5 business days** (maintainer
  commitment), initial assessment within 15 calendar days after that, and
  status updates until the fix ships.
- **In scope:** the app code in this repository, the FortiSafe signature
  database pipeline and format (once published), the CI/CD workflows and the
  declared dependency chain.
- **Out of scope:** third-party feeds (report to their maintainers), issues
  that exist only in the Hypatia upstream (report to MaintainTeam), the
  Android platform and Google Play themselves. Detection false positives or
  negatives are not vulnerabilities — open a regular issue with hash and
  description, not the sample.
- **Coordinated disclosure:** 90 days from acknowledgement, adjustable by
  mutual agreement; the final call is the reporter's.
