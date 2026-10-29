# Robotiklubi programmeerimiskursus

Materjalid on Moodle'ist eksporditud HTML-fragmendid, mis asuvad kaustas `Materjalid/`. Staatiline veeb genereeritakse Pythoniga:

```powershell
python build.py
```

Tulemus on kaustas `site/`. Ava kohapeal `site/index.html` või käivita staatiline failiserver. Build proovib materjalides olevad välised pildid lokaalselt kausta `site/assets/images/` laadida. Moodle'i `draftfile.php` lingid vajavad Moodle'ist käsitsi alla laaditud faile, sest need ei ole avalikud.

## GitHub Pages

Workflow `.github/workflows/pages.yml` ehitab saidi `main` harusse tehtud muudatuse järel. GitHubi repositooriumi seadetes tuleb Pagesi all valida **GitHub Actions**. Sait ei vaja backendi ega andmebaasi.

## Kujunduse kohandamine

Värvid on CSS-muutujatena failis `assets/styles.css`. Kui Proxima Nova fondi kasutusõigus on olemas, lisa fondifail ja `@font-face` deklaratsioon samasse faili; praegu kasutatakse seda ainult võimaliku süsteemse fondina ning põhifondi fallback on Verdana.
