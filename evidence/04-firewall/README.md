# Evidence — Modul 4

[Til dokumentationen](../../docs/04-firewall.md) · [Samlet evidensoversigt](../README.md)

Billederne er udtrukket fra den samlede Word-rapport. De viser de oprindelige terminalresultater; de er ikke nye kørsler af den omstrukturerede kode. Eventuelle udsnit fremgår af billedteksterne.

| Figur | Indhold |
|---|---|
| [4.1](figur-4-01.png) | Før-bevis: UFW er inaktiv, og socket-tabellen viser blandt andet SSH på IPv4 og IPv6. Udsnit med status og adresser; procesnavnenes højre kolonne er udeladt. |
| [4.2](figur-4-02.png) | Den etablerede forbindelse har lokal adresse 10.0.2.15:22 og peer 10.0.2.2:61044. Udsnit; proceslisten er beskåret. |
| [4.3](figur-4-03.png) | Standardpolitikkerne er sat, og show added viser den præcise SSH-undtagelse, inden UFW aktiveres. |
| [4.4](figur-4-04.png) | UFW er aktiv og aktiveret ved systemstart. Standardpolitikken og SSH-reglen fremgår; Logging er on (low). |
| [4.5](figur-4-05.png) | Den nye SSH-forbindelse lykkes. whoami viser secureadmin, og hostname viser securebase-server. |
| [4.6](figur-4-06.png) | Python-serveren startes i forgrunden og melder, at den lytter på port 8080. |
| [4.7](figur-4-07.png) | Socket-tabellen bekræfter en lyttende TCP-socket på 0.0.0.0:8080. |
| [4.8](figur-4-08.png) | PowerShell-testen giver TcpTestSucceeded: True, selv om HTTP-testen i næste trin endnu ikke får noget svar. |
| [4.9](figur-4-09.png) | Før-bevis: TCP-forbindelsen oprettes, og GET sendes, men testen afsluttes med timeout og 0 bytes modtaget. |
| [4.10](figur-4-10.png) | Den midlertidige TCP/8080-regel er tilføjet. Både SSH og HTTP er begrænset til 10.0.2.2, og deny incoming er bevaret. |
| [4.11](figur-4-11.png) | Efter-bevis: HTTP 200 OK og directory-listing fra Python-serveren. Den viste listing afslører samtidig, at hjemmemappen var valgt som webrod. |
| [4.12](figur-4-12.png) | Det faktiske rettelsesforløb: første server stoppes, testside oprettes, og serveren startes med --directory ~/webtest. Serverloggen viser efterfølgende GET og status 200. |
| [4.13](figur-4-13.png) | Windows får nu kun den oprettede HTML-testside i stedet for den tidligere listing af hjemmemappen. |
| [4.14](figur-4-14.png) | Socket-tabellen viser python3 på TCP/8080 og sshd på TCP/22. Alle tre linjer er med. |
| [4.15](figur-4-15.png) | Testtilstand: regel 1 er TCP/22, og regel 2 er TCP/8080. Begge er ALLOW IN fra 10.0.2.2. |
| [4.16](figur-4-16.png) | cat bekræfter den gemte eksport med begge testperiodens regler. Denne fil blev senere overskrevet med sluttilstanden. |
| [4.17](figur-4-17.png) | UFW viser, at regel 2 gælder TCP/8080 fra 10.0.2.2. Sletningen bekræftes, og den efterfølgende liste indeholder kun SSH. |
| [4.18](figur-4-18.png) | Efter oprydningen viser det filtrerede socket-output kun SSH på IPv4 og IPv6. Der er ingen lyttende TCP/8080-socket i resultatet. |
| [4.19](figur-4-19.png) | Endelig eksport: Status: active; deny incoming; allow outgoing; kun TCP/22 tilladt fra 10.0.2.2. cat viser samme indhold fra den gemte fil. |
