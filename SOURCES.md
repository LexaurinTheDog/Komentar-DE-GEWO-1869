# Quellen, Version und Nachweise

Überprüft am **19. Oktober 2026**. Maßgeblicher Rechtsstand und Beginn der Bearbeitung: derselbe Tag. Abrufzeitpunkte sind in UTC angegeben; sie belegen den Abruf, nicht allein die rechtliche Wirksamkeit.

| Quelle | Tatsächlicher Nachweis | Verwendung |
| --- | --- | --- |
| [Gesetze im Internet: GewO](https://www.gesetze-im-internet.de/gewo/) | [Index](sources/gewo-index.html), [HTTP-Antwort](sources/gewo-index-response.json), HTTP 200 | aktuelle amtliche Bereitstellung |
| [Gesamtausgabe](https://www.gesetze-im-internet.de/gewo/BJNR002450869.html) | [HTML](sources/gewo-full.html), HTTP 200 | unabhängiges Einheiteninventar und Standangabe |
| [XML-Paket](https://www.gesetze-im-internet.de/gewo/xml.zip) | [ZIP](sources/gewo.zip), [XML](sources/BJNR002450869.xml), HTTP 200 | mechanische Wortlautextraktion; jurabk GewO |
| [BGBl. 2026 I Nr. 215](https://www.recht.bund.de/bgbl/1/2026/215/regelungstext.pdf?__blob=publicationFile) | [PDF](sources/amendment-215.pdf), [Text](sources/amendment-215.txt), HTTP 200 | Art. 1 und 11: wirksame und zukünftige Änderungen |
| [BGBl. 2026 I Nr. 139](https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf?__blob=publicationFile) | [PDF](sources/amendment-139.pdf), [Text](sources/amendment-139.txt), HTTP 200 | Art. 7 und 16: § 34l gegenüber späterem § 34k |
| [BGBl. 2026 I Nr. 183](https://www.recht.bund.de/bgbl/1/2026/183/regelungstext.pdf?__blob=publicationFile) | [PDF](sources/amendment-183.pdf), [Text](sources/amendment-183.txt), HTTP 200 | Art. 5 und 7: Register- und Zeugenschutzänderungen |

Alle Binärantworten wurden nach Format validiert. Die ZIP-Datei enthält die identifizierte GewO-XML; die gespeicherte XML stimmt mit dem Paketmitglied überein. Die PDF-Dateien haben die PDF-Signatur und wurden erfolgreich in Text umgewandelt. Die HTML-Datei trägt den GewO-Titel und die amtlichen Einzelnormkennungen. Damit wurde nicht allein ein erfolgreicher HTTP-Status als Beweis verwertbaren Inhalts behandelt. Vollständige Hashes, Größen und tatsächliche HTTP-Ergebnisse: [verification.json](sources/verification.json), [manifest.json](sources/manifest.json).

## Auswahl des wirksamen Texts

Die Standangabe nennt die Neufassung vom 22. Februar 1999 und zuletzt Art. 1 des Gesetzes vom 20. Juli 2026. Art. 11 Abs. 1 des Änderungsgesetzes Nr. 215 setzt die Änderungen an §§ 6a und 34c am Tag nach der Verkündung vom 23. Juli 2026 in Kraft. Dagegen gelten die neuen Empfänger des § 14 Abs. 8 nach Art. 11 Abs. 2 erst am 1. Mai 2027. Die im XML noch auf Nummer 14 endende Empfängerliste passt zum Stichtag.

Das Änderungsgesetz Nr. 139 wurde am 18. Mai 2026 verkündet. Nach Art. 16 Abs. 2 Nr. 2 tritt innerhalb von Art. 7 Nr. 6 bereits § 34l am nächsten Tag in Kraft; der übrige hier relevante Änderungsteil folgt nach Art. 16 Abs. 1 erst am 20. November 2026. Deshalb enthält der Band § 34l, aber keinen aus der Zukunft vorgezogenen § 34k oder § 162. Der vorauseilende Verweis ist dokumentiert, nicht „vervollständigt“.

Art. 5 des Gesetzes Nr. 183 trat nach Art. 7 Abs. 2 am Tag nach der Verkündung vom 24. Juni 2026 in Kraft. Die dort ebenfalls genannte Wirksamkeit am 1. Oktober 2026 betrifft nach Art. 7 Abs. 4 einen anderen Änderungsteil, nicht die GewO. Das ist insbesondere für die aktuelle Überschrift des § 150a und den Inhalt des § 155a relevant.

Die bereitgestellte Intake-Fassung vom 1. Oktober 2026 bleibt unverändert als [Snapshot](sources/intake-20261001.md) erhalten. Originalhash: `635d97b6c4cb30b7cae7145c45b6a67e22532ab45c6d3b40bbba434292f6101c`. Der neue kanonische Text wurde aus der frisch abgerufenen XML abgeleitet. Der [vollständige Änderungsabgleich](sources/change-map.json) findet bei allen 171 Einheiten identischen operativen Text unter Ausblendung der Layoutformatierung. Redaktionshinweise wurden lediglich gesondert angeordnet. Die Beibehaltung beider Quellen erlaubt eine spätere Nachprüfung.

## Vollständigkeit und redaktionelle Hinweise

Die XML enthält 194 Normdatensätze: 171 kommentierte Einheiten, 21 Gliederungsdatensätze, eine Rahmen-/Metadateneinheit und die Inhaltsübersicht. Die Einheitenzahl des alten Intake-Metadatensatzes wird nicht mit dieser eigenständigen Zählung gleichgesetzt. Alle amtlichen Kennungen und ihre Behandlung stehen im [Vollständigkeitsbericht](completeness-report.json). Das separate [Audit](audit-report.json) vergleicht 171 Einzelnormen aus dem amtlichen HTML mit den extrahierten Kennungen und prüft den Textinhalt gegen die XML ohne Layoutleerraum.

Die operative Anlage zu § 36 Abs. 4a ist vollständig enthalten, einschließlich beider Abschnitte und der verschachtelten Kriterien. Die Rahmenhinweise erwähnen einen Anhang EV, erklären die betreffenden Maßgaben aber seit 2010 beziehungsweise 2013 für nicht mehr anwendbar. Die Stichtags-XML enthält hierzu keine operative Einzelnorm. Er wird deshalb nicht als heutiger Regelungsbestand rekonstruiert. Quellenfußnoten und im Textfeld eingebettete Zuständigkeitsanmerkungen stehen getrennt von den operativen Sätzen.

Erkennbare Verweisprobleme, etwa § 60d auf § 56 Abs. 3 Satz 2 und § 146 Abs. 2 Nr. 12 auf § 133 Abs. 2 Satz 1, werden offengelegt. Der amtliche Wortlaut bleibt unverändert. Der Kommentar ergänzt daraus keine Eingriffsnorm und keine Sanktion durch Analogie.

## Rechtsprechung und Recherchegrenzen

Die [beiden Fallkarten](cases/README.md) beruhen auf gelesenen amtlichen Volltexten von BVerwG und BAG. Die amtlichen Internetantworten und die entsprechenden Texte des lokalen nationalen Korpus sind gesichert. Das [Rechercheprotokoll](sources/search-log.json) enthält die tatsächlichen Suchanfragen und Ergebnisse; die [Einheitenzuordnung](sources/case-coverage.json) kennzeichnet die selektive Abdeckung. Die weitere im Urteil selbst genannte Literatur oder Rechtsprechung gilt nicht als eigenständig verifiziert.

Die Suchkontrolle nach neueren Änderungen ergänzt das aktuelle amtliche Konsolidat und die gelesenen Verkündungsfassungen. Sie ist kein lückenloser Durchgang durch sämtliche Bundesgesetzblatt-Ausgaben. Bei den Bekanntmachungen nach § 161 hat die gezielte Suche keinen hinreichenden Primärnachweis des Eintritts erbracht. Das beweist weder Eintritt noch Nichteintritt. Die Kommentierung bezeichnet die Bedingungen und setzt keinen tatsächlichen Vollzugsstand voraus. Historische Fassungen externer Gesetze, sämtliche Durchführungsverordnungen und das unterschiedliche Landesrecht sind nicht vollständig Gegenstand dieses Bandes.

Die kanonische Fassung ist mit [_parse.py](_parse.py) reproduzierbar; [_audit.py](_audit.py) prüft Inventar, Textinhalt, Intake-Vergleich und Prosadiagnostik. [_verify_sources.py](_verify_sources.py) dokumentiert die Abruf- und Formatprüfung. Die zentralen Bau- und Validierungsprogramme wurden nicht verändert. Zum tatsächlichen Prüfstand siehe [REVIEW](REVIEW.md).
