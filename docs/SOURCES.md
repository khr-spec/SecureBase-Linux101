# Primære tekniske referencer

Design og kildekode er skrevet til dette SecureBase-forløb. Kravgrundlag: den i samtalen udleverede Linux 101-opgave, Modul 6, side 7–8. De følgende offentlige manualer blev konsulteret ved implementeringen; de dokumenterer værktøjernes mekanismer. Den aktuelle v1.2-teststatus fra 18. september 2026 dokumenteres i [VM_TEST_REPORT.md](VM_TEST_REPORT.md) med [nye screenshots](../evidence/06-scripting/v1.2-2026-09-18/README.md). Word-rapportens Modul 6 og [den historiske testrapport](VM_TEST_REPORT_2026-09-17.md) dokumenterer det oprindelige forløb fra 17. september.

- OpenSSH sshd: konfigurationstest, effektiv konfiguration og hostnøgler. https://man.openbsd.org/sshd
- OpenSSH sshd_config: public key, UsePAM, direktivernes prioritet og Includes. https://man.openbsd.org/sshd_config
- Ubuntu sudoers-rs: præcise kommandoregler, NOPASSWD og Includes. https://manpages.ubuntu.com/manpages/resolute/man5/sudoers-rs.5.html
- Netplan YAML: netværksmodel, adresser, DNS, routes og interface-match. https://netplan.readthedocs.io/en/stable/netplan-yaml/
- Netplan try: interaktiv bekræftelse og begrænsninger ved rollback. https://netplan.readthedocs.io/en/stable/netplan-try/
- Ubuntu UFW: kildebaserede regler, indbyggede regler, IPv6 og firewallrapporter. https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html
- Linux-kernens /proc: CPU-tællere og MemAvailable. https://www.kernel.org/doc/html/latest/filesystems/proc.html
- Ubuntu logrotate: su, create, daily, rotate, compress, delaycompress og debug. https://manpages.ubuntu.com/manpages/noble/man8/logrotate.8.html
- Ubuntu crontab: system-cron, tidsfelter og miljø. https://manpages.ubuntu.com/manpages/noble/man5/crontab.5.html
- Ubuntu apt-get: update, upgrade og installation. https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html

Pakke- og kommandoversioner kan variere mellem Ubuntu-udgivelser. Deploymentet stopper derfor uden for 26.04 og validerer den installerede servers konfiguration med dens egne værktøjer. Et korrekt svar fra en valideringskommando er ikke i sig selv et end-to-end-loginbevis.


## GitHub-omstrukturering (18. september 2026)

De følgende referencer vedrører kun de nye Git-/Markdown-valg, ikke historiske VM-beviser:

- [GitHub: README, relative links og billedstier](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Git: .gitattributes og linjeskift](https://git-scm.com/docs/gitattributes)
- [Git: update-index og --chmod](https://git-scm.com/docs/git-update-index)

Kilde-/versionsafgrænsning og billedproveniens findes i [GRUNDLAG.md](GRUNDLAG.md).
