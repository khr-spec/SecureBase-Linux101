# Evidence — historik og ny v1.2-verifikation

[Til repoets overblik](../README.md)

Her ligger **87 oprindelige figurer** udtrukket fra [den afsluttede Word-rapport](../reports/SecureBase_Modul_1_2_3_4_5_6_DOKUMENTATION.docx). Billedfilerne er bevaret byte-for-byte som rapportens indlejrede billeder; beskæringer er de udsnit, der allerede fandtes i rapporten. Ingen nye VM-kørsler er fremstillet som gamle beviser.

| Modul | Indeks |
|---|---|
| 1 | [VM og netværk](01-vm-netvaerk/README.md) |
| 2 | [Filsystem](02-filsystem/README.md) |
| 3 | [Brugere og grupper](03-brugere-grupper/README.md) |
| 4 | [Firewall](04-firewall/README.md) |
| 5 | [Monitorering](05-monitorering/README.md) |
| 6 | [Scripting og deployment](06-scripting/README.md) |

[index.json](index.json) angiver original billedrelation i Word, modul, figur, billedtekst, dimensioner og SHA-256. `SHA256SUMS` i repo-roden beskytter de versionerede filers indhold mod utilsigtede ændringer; det er ikke en digital signatur fra serveren.

## Nyt tillæg: v1.2 på Ubuntu den 18. september 2026

[16 nye screenshots](06-scripting/v1.2-2026-09-18/README.md) dokumenterer den nye repos `scripts/`-struktur: fresh-install, preflight, første apply, statisk netværk, SSH/sudo og anden apply med 0 ændrede administrerede filer. Det giver **103 billeder i alt**, uden at nogen af de oprindelige 87 billeder ændres.

Det oprindelige [index.json](index.json) er fortsat kun indekset over Word-figurerne. De nye screenshots har et [særskilt kilde-/hashindeks](06-scripting/v1.2-2026-09-18/index.json). De 16 billeder er et separat tillæg til rapportens oprindelige billedserie.

## Hvad materialet ikke er

Screenshots og kodeudsnit er dokumentation af de viste handlinger. Der er ikke konstrueret komplette rå serverlogs eller nye `ufw`-eksporter af billederne. Hvor en kort tekstlig opsummering bruges i modulbeskrivelserne, henviser den til den tilsvarende figur. Beviserne dokumenterer ikke alle tænkelige bruger-/netværkskombinationer.

Tidsstempler i VM-outputtet tilhører det konkrete forløb: de oprindelige beviser og det særskilte v1.2-tillæg holdes adskilt. Kildeadressen `10.0.2.2` er den observerede VirtualBox NAT-adgangsvej, ikke en unik personidentitet.
