# Evidence — Modul 3

[Til dokumentationen](../../docs/03-brugere-grupper.md) · [Samlet evidensoversigt](../README.md)

Billederne er udtrukket fra den samlede Word-rapport. De viser de oprindelige terminalresultater; de er ikke nye kørsler af den omstrukturerede kode. Eventuelle udsnit fremgår af billedteksterne.

| Figur | Indhold |
|---|---|
| [3.1](figur-3-01.png) | Udgangspunkt før Modul 3. id, gruppeoplysninger, projektmappens ACL og den brede sudo-tilladelse er samlet i samme terminaludsnit. |
| [3.2](figur-3-02.png) | Rollegrupperne admins, developers og guests er oprettet med GID 1004, 1005 og 1006. Udsnit af det uploadede terminalbillede. |
| [3.3](figur-3-03.png) | De tre konti, deres UID/GID og /etc/group efter rolletildelingen. secureadmin har endnu både sudo og admins. Developer og guest er ikke medlemmer af sudo eller securebase. |
| [3.4](figur-3-04.png) | Før-bevis: de nye brugere kan ikke liste /srv/securebase. Ejer, gruppe, SGID og den daværende ACL vises. |
| [3.5](figur-3-05.png) | Efter-bevis: developers har rwx på mappen, guests har r-x, og other har ingen adgang. Ejerskabet root:securebase og SGID er bevaret. |
| [3.6](figur-3-06.png) | test.txt før og efter setfacl. Udsnittet viser både de oprindelige rettigheder, ændringskommandoen og de nye filregler. |
| [3.7](figur-3-07.png) | Projektmappens adgangs-ACL og default ACL. Begge rollegrupper er med i standardreglerne, mens default:other::--- udelukker generel adgang for øvrige brugere. |
| [3.8](figur-3-08.png) | Ny fil ejet af secureadmin, vellykket tilføjelse og læsning som developer1 samt de nedarvede ACL-regler. Udsnit af det samlede terminalbillede. |
| [3.9](figur-3-09.png) | Gæsten læser begge linjer. Skrivning til rolletest.txt og oprettelse af guest-test.txt afvises. Den afsluttende læsning viser uændret indhold. Udsnit af det uploadede billede. |
| [3.10](figur-3-10.png) | Afprøvet opsætnings-/gendannelseskonto. Udsnittet viser den lokale konto og dens fulde sudo-adgang. |
| [3.11](figur-3-11.png) | Reglerne, filens root:root-ejerskab og -r--r----- samt sudo visudo -c med parsed OK. Den faktiske indlæsning blev efterfølgende kontrolleret med sudo -l. |
| [3.12](figur-3-12.png) | Før: secureadmin er medlem af både sudo og admins. Den generelle (ALL : ALL) ALL-regel gælder stadig ved siden af de tre konkrete regler. |
| [3.13](figur-3-13.png) | Efter: sudo-gruppen og den brede tilladelse er væk. secureadmin har stadig admins og securebase, og kun de tre afgrænsede kommandoer vises i sudo -l. |
| [3.14](figur-3-14.png) | Den tilladte SSH-kontrol afsluttes med returkode 0. sudo /usr/bin/id afvises og afsluttes med returkode 1. |
| [3.15](figur-3-15.png) | Udsnit af SSH-logtesten med Accepted publickey og returkode 0. Ældre linjer og højre del af de lange nøglefingeraftryk er beskåret; den udførte kommando er gengivet ovenfor. |
| [3.16](figur-3-16.png) | Konfigurationskontrol og reload lykkes med returkode 0. Den efterfølgende statuskontrol uden sudo viser active. |
| [3.17](figur-3-17.png) | vboxuser foretager politikopslaget. Sudo angiver, at hverken developer1 eller guest1 må køre sudo på securebase-server. |
