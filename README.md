# Robotiklubi programmeerimiskursus

Materjalid on Moodle'ist eksporditud HTML-fragmendid, mis asuvad kaustas `Materjalid/`. Staatiline veeb genereeritakse Pythoniga:

```powershell
python build.py
```

Tulemus on kaustas `site/`. Ava kohapeal `site/index.html` või käivita staatiline failiserver. Build proovib materjalides olevad välised pildid lokaalselt kausta `site/assets/images/` laadida. Moodle'i `draftfile.php` lingid vajavad Moodle'ist käsitsi alla laaditud faile, sest need ei ole avalikud.

Koodinäited märgistatakse C/C++-na ja värvitakse build'i ajal otse HTML-i sisse, seega töötab süntaksivärvimine ka lokaalselt ja ilma välise teenuseta.

## Logo lisamine

Google-hostitud logo URL võib otse allalaadimisel anda 403. Ava logo Chrome'is, vali pildil paremklõpsuga **Save image as...** ja salvesta fail nimega `assets/branding/robotiklubi-logo.png` (sobivad ka `.jpg`, `.jpeg`, `.svg` või `.webp`). Järgmine build lisab logo automaatselt saidi päisesse. Ära salvesta HTML-vealehte pildifailina.

Moodle'i privaatpildid saab lisada samal viisil kausta `assets/images/` järgmiste nimedega: `arduino-ide-screenshot-1.png`, `arduino-ide-screenshot-2.png`, `n-idiskood-blokkdiagramm.png` ja `arduino-ide-esp32-url.png`. Build kasutab neid automaatselt ja asendab vastavad Moodle'i URL-id lokaalsete viidetega.

## GitHub Pages

Workflow `.github/workflows/pages.yml` ehitab saidi `main` harusse tehtud muudatuse järel. GitHubi repositooriumi seadetes tuleb Pagesi all valida **GitHub Actions**. Sait ei vaja backendi ega andmebaasi.

## Kujunduse kohandamine

Värvid on CSS-muutujatena failis `assets/styles.css`. Kui Proxima Nova fondi kasutusõigus on olemas, lisa fondifail ja `@font-face` deklaratsioon samasse faili; praegu kasutatakse seda ainult võimaliku süsteemse fondina ning põhifondi fallback on Verdana.
