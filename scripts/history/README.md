# Historisk script fra Modul 5

`monitor-modul5.sh` er en tekstlig udtrækning af den afsluttende kode i Word-rapportens Modul 5 (side 51). Det er den manuelle, `top`/`free`-baserede version, som hører til screenshots i Modul 5.

Den installeres **ikke** af setup. Den aktive deployment-version er [../monitor.sh](../monitor.sh), der bruger `/proc` og separat konfiguration. Bevar begge for at kunne følge den reelle udvikling uden at beskrive de gamle målinger som resultater af ny kode.

Koden kan syntakskontrolleres uden at køre den:

```bash
bash -n scripts/history/monitor-modul5.sh
```

Normal kørsel af den historiske fil skriver til `/var/log/securebase-monitor.log`; den skal ikke bruges til at erstatte den aktive monitor på en færdig server.
