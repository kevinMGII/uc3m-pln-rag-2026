# Comprobaciones automáticas de las consultas

Fichero generado por `scripts/revisar_consultas.py`. No editar a mano.

Modelo que escribió las consultas (ollama): `llama3.1:8b`.

## Consultas aceptadas (35)

* **Sim. otro doc.**: similitud coseno TF-IDF máxima del fragmento de origen con fragmentos de otros documentos (a partir de 0.75 se considera texto repetido).
* **Términos en el fragmento**: porcentaje de términos de la consulta preprocesada que aparecen en el fragmento de origen.
* **Palabras seguidas**: secuencia más larga de palabras que la consulta comparte literalmente con el fragmento.

| qid | Candidato | Documento | Fuente | Consulta | Origen | Palabras | Sim. otro doc. | Términos en el fragmento | Palabras seguidas |
|---|---|---|---|---|---|---|---|---|---|
| q01 | c01 | Gemini 4 (`doc_1838`) | Wikipedia 1957–1999 | US astronaut's 20-minute spacewalk and subsequent reentry preparations in a small cabin with limited radio communications. | LLM | 16 | 0.24 | 67 % | 3 |
| q02 | c02 | Skylab (`doc_2258`) | Wikipedia 1957–1999 | US space agency planned to extend the life of a space station with a remote-controlled booster system and shuttle flights | LLM | 20 | 0.48 | 73 % | 3 |
| q03 | c05 | Sich-1 (`doc_2939`) | Wikipedia 1957–1999 | Ukrainian remote sensing spacecraft sent up in August 1995 whose Chilean companion payload never separated from it | corregida a mano | 17 | 0.55 | 40 % | 3 |
| q04 | c06 | Kosmos 36 (`doc_1805`) | Wikipedia 1957–1999 | Soviet Union launched first satellite used as radar calibration target in low earth orbit for anti-ballistic missile tests in 1964 | LLM | 20 | 0.56 | 80 % | 3 |
| q05 | c07 | Zond 4 (`doc_2056`) | Wikipedia 1957–1999 | first uncrewed test of a Soyuz spacecraft in an elliptical orbit around Earth in March 1968 | LLM | 16 | 0.55 | 88 % | 2 |
| q06 | c08 | IRS-1E (`doc_2841`) | Wikipedia 1957–1999 | Indian Earth imaging satellite built from an engineering model, lost in September 1993 when its rocket's first flight failed | corregida a mano | 19 | 0.42 | 62 % | 3 |
| q07 | c12 | European Retrievable Carrier (`doc_2783`) | Wikipedia 1957–1999 | spacecraft with X-ray detectors exposed to space for 11 months and later scanned on Earth in Switzerland | LLM | 17 | 0.22 | 60 % | 2 |
| q08 | c14 | Shenzhou 15 (`doc_1429`) | Wikipedia 2000–2025 | Chinese orbital station crew changeover with a record number of astronauts aboard and four spacewalks in their half-year stay | corregida a mano | 19 | 0.54 | 50 % | 2 |
| q09 | c16 | Progress M-01M (`doc_0442`) | Wikipedia 2000–2025 | Spacecraft carrying dry cargo including Japanese food for astronaut arriving in March 2009 docked at ISS module | LLM | 17 | 0.36 | 83 % | 3 |
| q10 | c17 | Interface Region Imaging Spectrograph (`doc_0833`) | Wikipedia 2000–2025 | spacecraft launched by NASA in 2013 that revealed complex features at the Sun's interface region | LLM | 15 | 0.26 | 90 % | 2 |
| q11 | c18 | Sirius FM-5 (`doc_0530`) | Wikipedia 2000–2025 | American communications satellite launched by Proton-M rocket from Baikonur Cosmodrome in June 2009 | LLM | 13 | 0.36 | 89 % | 3 |
| q12 | c19 | Eutelsat 21B (`doc_0731`) | Wikipedia 2000–2025 | television satellite sent up from French Guiana in November 2012 to take over an older one's slot serving Europe | corregida a mano | 19 | 0.49 | 40 % | 2 |
| q13 | c20 | LARES (satellite) (`doc_0749`) | Wikipedia 2000–2025 | Italian laser-ranged satellite and its July 2022 successor for testing general relativity and geodynamics | corregida a mano | 14 | 0.17 | 78 % | 2 |
| q14 | c21 | USA-239 (`doc_0789`) | Wikipedia 2000–2025 | American navigation satellite launched on October 4 2012 with a launch mass of 1630 kilograms | LLM | 15 | 0.53 | 67 % | 3 |
| q15 | c22 | PRSC-EO1 satellite (`doc_1572`) | Wikipedia 2000–2025 | Pakistan's first domestic Earth observation satellite launched from China in January 2025 with Chinese rocket support | LLM | 16 | 0.47 | 83 % | 3 |
| q16 | c23 | Star One D1 (`doc_1076`) | Wikipedia 2000–2025 | Brazilian communications satellite sent up from French Guiana in December 2016 on a European heavy rocket | corregida a mano | 16 | 0.34 | 40 % | 2 |
| q17 | c24 | Inmarsat-6 F1 (`doc_1342`) | Wikipedia 2000–2025 | communications satellite with dual L-band and Ka-band capabilities launched on December 22 2021 from Tanegashima | LLM | 15 | 0.50 | 82 % | 3 |
| q18 | c25 | Selecting Pixels for Kepler Downlink (`doc_3286`) | NTRS pilot | designing masks for stellar and custom targets with specific pixel selection workflow steps | LLM | 13 | 0.39 | 78 % | 3 |
| q19 | c27 | Kepler Mission's Focal Plane Characterization Models Implementation (`doc_3283`) | NTRS pilot | importer classes for different types of models and their implementation in Java and MATLAB programming languages | LLM | 16 | 0.19 | 33 % | 2 |
| q20 | c29 | ICESat-2 Meltwater Depth Estimates: Application to Surface Melt on Amery Ice Shelf, East Antarctica (`doc_3302`) | NTRS pilot | satellite laser altimetry data from January 2019 used to estimate water depths in Antarctic lakes and ice shelf | corregida a mano | 18 | 0.19 | 60 % | 2 |
| q21 | c31 | Aura (1.9Mb) (`doc_3191`) | JPL PDFs | spacecraft launched from Vandenberg Air Force Base in June 2004 with a specific vehicle configuration | LLM | 15 | 0.15 | 22 % | 2 |
| q22 | c32 | Wide-field Infrared Survey Explorer Launch Press Kit (1.7Mb) (`doc_3174`) | JPL PDFs | earlier infrared astronomy missions compared with the sensitivity of NASA's 2009 all-sky survey telescope | corregida a mano | 14 | 0.67 | 57 % | 2 |
| q23 | c33 | 1998 Mars missions (1.2M) (`doc_3212`) | JPL PDFs | orbiter mission with specific instruments to monitor Martian atmosphere and surface for nearly two Earth years starting in 2000 | LLM | 19 | 0.44 | 50 % | 3 |
| q24 | c37 | Apollo 7 Press Kit (`doc_3221`) | Apollo press kits | service structure and umbilical tower at the launch complex used for the first crewed Apollo flight | corregida a mano | 16 | 0.34 | 75 % | 2 |
| q25 | c39 | Apollo 13 Press Kit (`doc_3226`) | Apollo press kits | timeline for discarding the lunar module, its crash on the Moon and the homeward burn of the third landing attempt | corregida a mano | 20 | 0.43 | 0 % | 1 |
| q26 | c43 | Vostok 3 and 4 (`doc_1757`) | Wikipedia 1957–1999 | twin Soviet flights in 1962 where one cosmonaut spotted the other ship and came back early after a codeword mix-up | corregida a mano | 20 | 0.38 | 44 % | 3 |
| q27 | c45 | IRS-P3 (`doc_2969`) | Wikipedia 1957–1999 | India's 1996 Earth resources satellite that also carried an instrument for X-ray astronomy | corregida a mano | 13 | 0.40 | 88 % | 3 |
| q28 | c46 | F-1 (satellite) (`doc_0735`) | Wikipedia 2000–2025 | vietnamese cube satellite launched from iss in july 2012 with low earth orbit and failed communication | LLM | 16 | 0.21 | 70 % | 3 |
| q29 | c47 | NepaliSat-1 (`doc_1263`) | Wikipedia 2000–2025 | Nepalese satellite launched from Virginia in 2019 to study the country's geography and develop advanced satellites | LLM | 16 | 0.37 | 82 % | 2 |
| q30 | c48 | NigComSat-1 (`doc_0375`) | Wikipedia 2000–2025 | Chinese company provided in-orbit delivery services for an international customer in Africa that was later replaced by another satellite. | LLM | 19 | 0.35 | 73 % | 3 |
| q31 | c49 | GSAT-5P (`doc_0585`) | Wikipedia 2000–2025 | Indian communications satellite lost in launch failure on December 25 2010 with 36 C band transponders | LLM | 16 | 0.27 | 91 % | 3 |
| q32 | c50 | Prisma (satellite project) (`doc_0610`) | Wikipedia 2000–2025 | Two small satellites launched by Swedish and French space agencies on Dnepr rocket in June 2010 for formation flying test | LLM | 20 | 0.23 | 82 % | 2 |
| q33 | c52 | Radiometric Calibration and Stability of the Landsat-8 Operational Land Imager (OLI) (`doc_3289`) | NTRS pilot | trends in visible bands of a satellite instrument after power cycling and launch changes over time | LLM | 16 | 0.33 | 90 % | 2 |
| q34 | c53 | GRAIL Launch Press Kit (1.4Mb) (`doc_3168`) | JPL PDFs | measuring lunar gravity field accurately to determine structure and thermal evolution of a terrestrial planet's interior | LLM | 16 | 0.17 | 100 % | 3 |
| q35 | c55 | Apollo 14 Press Kit (`doc_3227`) | Apollo press kits | radar signals bounced off the lunar surface to study regolith depth on the flight that tested a hand-pulled equipment cart | corregida a mano | 20 | 0.63 | 25 % | 2 |

Medias: 16.8 palabras por consulta, 65 % de términos en el fragmento, secuencia común máxima de 3 palabras.

## Consultas corregidas a mano en la revisión (13 de 35)

El resto son las consultas del modelo sin cambios.

| qid | Consulta del LLM | Consulta corregida | Motivo |
|---|---|---|---|
| q03 | Ukrainian Earth observation satellite launched by Tsyklon-3 rocket in August 1995 with attached Chilean payload | Ukrainian remote sensing spacecraft sent up in August 1995 whose Chilean companion payload never separated from it | copiaba 5 palabras seguidas del fragmento y nombraba el cohete |
| q06 | polar satellite launch vehicle failed its first mission on september 20th 1993 due to attitude control problem | Indian Earth imaging satellite built from an engineering model, lost in September 1993 when its rocket's first flight failed | copiaba 4 palabras seguidas y describía el cohete (que tiene su propio documento) en vez del satélite |
| q08 | Chinese space station crew handover sets new record for total taikonauts in space and includes four EVAs within six months was rejected. Here is a different one: | Chinese orbital station crew changeover with a record number of astronauts aboard and four spacewalks in their half-year stay | 27 palabras: el modelo añadió texto de relleno y copiaba 7 palabras seguidas |
| q12 | communications satellite launched from Kourou in November 2012 with Ariane rocket and geostationary orbit at 21.5 degrees east longitude | television satellite sent up from French Guiana in November 2012 to take over an older one's slot serving Europe | copiaba 4 palabras seguidas del fragmento |
| q13 | satellite launched from Italy in July 2022 for testing general relativity and geodynamics measurements | Italian laser-ranged satellite and its July 2022 successor for testing general relativity and geodynamics | dato incorrecto: el satélite no se lanzó desde Italia |
| q16 | communications satellite launched from Centre Spatial Guyanais in December 2016 with an Ariane ECA rocket and SSL technology | Brazilian communications satellite sent up from French Guiana in December 2016 on a European heavy rocket | copiaba 4 palabras seguidas del fragmento |
| q20 | ICESat-2 data from January 2019 used to estimate water depths in Antarctic lakes and ice shelf | satellite laser altimetry data from January 2019 used to estimate water depths in Antarctic lakes and ice shelf | trivial: contenía el nombre de la misión |
| q22 | launched by nasa in 1989 studied both infrared and microwave radiation from big bang remnants | earlier infrared astronomy missions compared with the sensitivity of NASA's 2009 all-sky survey telescope | copiaba 6 palabras seguidas y describía una misión anterior citada en el fragmento, no el documento |
| q24 | large mobile launch structure at Kennedy Space Center that supports Apollo spacecraft | service structure and umbilical tower at the launch complex used for the first crewed Apollo flight | ambigua: la descripción valía para cualquier press kit de Apollo |
| q25 | lunar module's ascent stage impacted the moon's surface during a seismometer recording event in December | timeline for discarding the lunar module, its crash on the Moon and the homeward burn of the third landing attempt | ambigua: valía también para otros vuelos Apollo |
| q26 | first crewed spacecraft to study space sickness in humans after a three day orbit around Earth | twin Soviet flights in 1962 where one cosmonaut spotted the other ship and came back early after a codeword mix-up | imprecisa: no describía el contenido principal del fragmento |
| q27 | Indian space agency launched a remote sensing satellite with X-ray astronomy instrument in 1996 for Earth resource study. | India's 1996 Earth resources satellite that also carried an instrument for X-ray astronomy | copiaba 4 palabras seguidas del fragmento |
| q35 | US space agency experiments using radar signals to study lunar surface properties and regolith depth in the late 1960s | radar signals bounced off the lunar surface to study regolith depth on the flight that tested a hand-pulled equipment cart | ambigua y con fecha incorrecta: el vuelo no fue en los años 60 |

## Candidatos descartados (21)

| Candidato | Documento | Fuente | Sim. otro doc. | Documento más parecido | Motivo |
|---|---|---|---|---|---|
| c03 | Progress 27 (`doc_2639`) | Wikipedia 1957–1999 | 0.86 | `doc_2643` | ambigua: el mismo texto aparece casi igual en otro documento |
| c04 | Kosmos 1974 (`doc_2658`) | Wikipedia 1957–1999 | 0.68 | `doc_2654` | ambigua: ficha de plantilla casi idéntica a la de otros satélites de la misma serie (solo cambian fechas y números) |
| c09 | NOAA-14 (`doc_2884`) | Wikipedia 1957–1999 | 0.75 | `doc_2850` | ambigua: el mismo texto aparece casi igual en otro documento |
| c10 | USA-54 (`doc_2750`) | Wikipedia 1957–1999 | 0.79 | `doc_2753` | ambigua: el mismo texto aparece casi igual en otro documento |
| c11 | Kosmos 1341 (`doc_2467`) | Wikipedia 1957–1999 | 0.59 | `doc_2471` | ambigua: ficha de plantilla casi idéntica a la de otros satélites de la misma serie (solo cambian fechas y números) |
| c13 | USA-263 (`doc_1029`) | Wikipedia 2000–2025 | 0.87 | `doc_1155` | ambigua: el mismo texto aparece casi igual en otro documento |
| c15 | Kosmos 2476 (`doc_0660`) | Wikipedia 2000–2025 | 0.79 | `doc_0664` | ambigua: el mismo texto aparece casi igual en otro documento |
| c26 | The Planetary Protection Strategy of Mars Sample Return Earth Return Orbiter Mission (`doc_3241`) | NTRS pilot | 0.61 | `doc_3239` | ambigua y poco informativa: agradecimientos y bibliografía; el corpus contiene otra versión del mismo artículo |
| c28 | After DART: Using the first full-scale test of a kinetic impactor to inform a future planetary defense mission (`doc_3306`) | NTRS pilot | 0.29 | `doc_3266` | sin contenido: el fragmento es solo bibliografía |
| c30 | Twenty Years of Terra MODIS Spatial Performance Using the Spectro-Radiometric Calibration Assembly (`doc_3295`) | NTRS pilot | 0.17 | `doc_3287` | sin contenido: el fragmento es solo bibliografía |
| c34 | Mars Reconnaissance Orbiter Arrival at Mars (984Kb) (`doc_3184`) | JPL PDFs | 0.87 | `doc_3186` | ambigua: el mismo texto aparece casi igual en otro documento |
| c35 | Mars Exploration Rover Landings (309KB) (`doc_3194`) | JPL PDFs | 0.97 | `doc_3197` | ambigua: el mismo texto aparece casi igual en otro documento |
| c36 | Deep Impact Launch (865Kb) (`doc_3188`) | JPL PDFs | 0.92 | `doc_3187` | ambigua: el mismo texto aparece casi igual en otro documento |
| c38 | Apollo 8 Press Kit (`doc_3222`) | Apollo press kits | 0.50 | `doc_3224` | ambigua: datos generales de la Luna y organigrama del programa, repetidos en los demás press kits de Apollo |
| c40 | Apollo 12 Press Kit (`doc_3225`) | Apollo press kits | 0.11 | `doc_3226` | ambigua: descripción del módulo lunar repetida en los demás press kits de Apollo |
| c41 | Ranger 7 (`doc_1817`) | Wikipedia 1957–1999 | 0.77 | `doc_1816` | ambigua: el mismo texto aparece casi igual en otro documento |
| c42 | USA-1 (satellite) (`doc_2563`) | Wikipedia 1957–1999 | 0.91 | `doc_2568` | ambigua: el mismo texto aparece casi igual en otro documento |
| c44 | Vanguard TV-3BU (`doc_1622`) | Wikipedia 1957–1999 | 0.69 | `doc_1641` | ambigua: descripción del cohete Vanguard compartida con los demás lanzamientos de la serie |
| c51 | OSIRIS-REx Entry, Descent, and Landing Performance (`doc_3264`) | NTRS pilot | 0.63 | `doc_3263` | ambigua: el corpus contiene dos documentos con el mismo título y contenido muy parecido |
| c54 | Quick Scatterometer (439KB) (`doc_3209`) | JPL PDFs | 0.25 | `doc_3199` | poco informativa: el fragmento es una lista de nombres del equipo científico |
| c56 | Apollo 11 Press Kit (`doc_3224`) | Apollo press kits | 0.74 | `doc_3222` | ambigua: descripción de la torre de lanzamiento repetida en los demás press kits de Apollo |

## Material para la revisión manual (10 consultas al azar)

La tabla para apuntar el resultado de la revisión está en `consultas/README.md`.

### q03 · Sich-1 (`doc_2939__0001`)

**Consulta:** Ukrainian remote sensing spacecraft sent up in August 1995 whose Chilean companion payload never separated from it

**Fragmento (inicio):**

> Sich-1 Mission type | Earth observation COSPAR ID | 1995-046A SATCAT no. | 23657 Spacecraft properties Spacecraft type | Okean-O1 Manufacturer | Yuzhmash Launch mass | 1,915 kilograms (4,222 lb) Start of mission Launch date | 31 August 1995, 06:49:59 ( 1995-08-31UTC06:49:59Z ) UTC Rocket | Tsyklon-3 Launch site | Plesetsk 32/2 End of mission Deactivated | 2001 Orbital parameters Reference system | Geocentric Regime | Low Earth Eccentricity | 0.0022 Perigee altitude | 659 kilometres (409 mi) Apogee altitude | 683 kilometres (424 mi) Inclination | 82.3 degrees Period | 98.7 minutes Epoch | 21 August 1995, 02:49:59 UTC Sich satellite series Sich-1 was the first Ukrainian Earth observation satel…

### q05 · Zond 4 (`doc_2056__0001`)

**Consulta:** first uncrewed test of a Soyuz spacecraft in an elliptical orbit around Earth in March 1968

**Fragmento (inicio):**

> Zond 4 Names | Soyuz 7K-L1 s/n 6 Mission type | Lunar flyby Spacecraft test Operator | OKB-1 COSPAR ID | 1968-013A SATCAT no. | 03134 Spacecraft properties Bus | Soyuz 7K-L1 Manufacturer | OKB-1 Launch mass | 4,425 kilograms (9,755 lb) Dimensions | 4.5 m x 2.2 m x 2.72 m Start of mission Launch date | 2 March 1968, 18:29:23 UTC Rocket | Proton-K / D Launch site | Baikonur 81/6 End of mission Disposal | deorbited/destroyed Decay date | 9 March 1968 ( 1968-03-09 ) Orbital parameters Reference system | Geocentric Regime | Elliptical orbit Perigee altitude | 200 kilometres (120 mi) Apogee altitude | 400,000 kilometres (250,000 mi) Inclination | 51.53° Zond program Zond 4 , part of the Soviet Zon…

### q08 · Shenzhou 15 (`doc_1429__0003`)

**Consulta:** Chinese orbital station crew changeover with a record number of astronauts aboard and four spacewalks in their half-year stay

**Fragmento (inicio):**

> launch, the spacecraft docked with the Tianhe core module 's forward docking port. The crew entered the station at 23:33 UTC on 29 November, and were greeted by the crew of Shenzhou 14. This marked the first Chinese crew handover in space, and set a new record for total taikonauts in space, at six. There was a five-day overlap between Shenzhou 15 and the previous mission before Shenzhou 14's departure on 4 December. During the mission, the Shenzhou 16 spacecraft remained on standby to serve as an emergency rescue vehicle. The Shenzhou 15 crew carried out four spacewalks , worked on payloads both inside and outside the station, and carried out other scientific work during the six-month missio…

### q10 · Interface Region Imaging Spectrograph (`doc_0833__0003`)

**Consulta:** spacecraft launched by NASA in 2013 that revealed complex features at the Sun's interface region

**Fragmento (inicio):**

> The charge-coupled device (CCD) detectors has 1/6 arcsecond pixels . IRIS will have an effective spatial resolution between 0.33 and 0.40 arcsecond and a maximum field of view (FoV) of 120 arcseconds. The far-ultraviolet channel covers 133.2-135.8 nm and 139.0-140.6 nm with an 0.04 nm resolution and an effective area of 2.8 cm 2 (0.43 sq in) . The near-ultraviolet channel covers 278.5-283.5 nm with an 0.08 nm resolution and an effective area of 0.3 cm 2 (0.047 sq in) . Slit-jaw imaging has four passbands : 133.5 nm and 140.0 nm with a 4 nm bandpass each; and 279.6 nm and 283.1 nm with a 0.4 nm bandpass each. IRIS has a high data rate (0.7 Mbit/s on average) so that the baseline cadence is 5 …

### q12 · Eutelsat 21B (`doc_0731__0001`)

**Consulta:** television satellite sent up from French Guiana in November 2012 to take over an older one's slot serving Europe

**Fragmento (inicio):**

> Eutelsat 21B Names | Eutelsat W6A (pre-launch) Eutelsat 21B (2012–present) Mission type | Communication Operator | Eutelsat COSPAR ID | 2012-062B SATCAT no. | 38992 Website | www .eutelsat .com /en /satellites /the-fleet /EUTELSAT-21B .html Mission duration | 15 years Spacecraft properties Bus | Spacebus 4000C3 Manufacturer | Thales Alenia Space Launch mass | 5,012 kilograms (11,050 lb) Start of mission Launch date | 10 November 2012, 21:05:07 ( 2012-11-10UTC21:05:07Z ) UTC Rocket | Ariane 5ECA Launch site | Kourou ELA-3 Contractor | Arianespace Orbital parameters Reference system | Geocentric Regime | Geostationary Longitude | 21.5° East (2012–present) Transponders Band | 40 Ku-band Eutelsa…

### q13 · LARES (satellite) (`doc_0749__0002`)

**Consulta:** Italian laser-ranged satellite and its July 2022 successor for testing general relativity and geodynamics

**Fragmento (inicio):**

> object known orbiting the Earth. The high density helps reduce disturbances from environmental factors such as solar radiation pressure. Scientific goals The main scientific target of the LARES mission is the measurement of the Lense–Thirring effect with an accuracy of about 1%, according to principal investigator Ignazio Ciufolini and the LARES scientific team, but the reliability of that estimate is contested. In contrast, a recent analysis of 3.5 years of laser-ranging data reported a claimed accuracy of about 4%. Critical remarks appeared later in the literature. Beyond the project's key mission, the LARES satellite may be used for other tests of general relativity as well as measurement…

### q17 · Inmarsat-6 F1 (`doc_1342__0001`)

**Consulta:** communications satellite with dual L-band and Ka-band capabilities launched on December 22 2021 from Tanegashima

**Fragmento (inicio):**

> Inmarsat-6 F1 Names | I6 F1 Mission type | Communications Operator | Inmarsat COSPAR ID | 3021-128A SATCAT no. | 50319 Mission duration | 15 years (planned) Spacecraft properties Bus | Eurostar 3000EOR Manufacturer | Airbus Defence and Space Launch mass | 5,470 kg (12,060 lb) Power | 21 kW Start of mission Launch date | 22 December 2021, 15:32 UTC Rocket | H-IIA 204 (F45) Launch site | Tanegashima , LA-Y1 Contractor | Mitsubishi Heavy Industries Orbital parameters Reference system | Geocentric orbit Regime | Geostationary orbit Transponders Band | L-band (ELERA) Ka-band (Global Xpress) INMARSAT Fleet Inmarsat-6 F1 is a communications satellite to be operated by the British satellite operator…

### q19 · Kepler Mission's Focal Plane Characterization Models Implementation (`doc_3283__0009`)

**Consulta:** importer classes for different types of models and their implementation in Java and MATLAB programming languages

**Fragmento (inicio):**

> pixel-based and nonpixel-based. Pixel-based models include flat field and two-d black; the data volume for these models is very large compared to nonpixel-based models. The import files for pixel-based models define a value for each pixel in the focal plane. Nonpixel-based models contain information that describes per-CCD parameters (i.e., geometry,5 read noise), per-readout chain parameters (i.e., readout linearity), and spacecraft-based parameters (i.e., roll times, spacecraft pointing). Nonpixel-based import files define only the parameters necessary to calculate the relevant effect. The importers are implemented as command-line tools and execute the Java main() method. The commandline ar…

### q32 · Prisma (satellite project) (`doc_0610__0001`)

**Consulta:** Two small satellites launched by Swedish and French space agencies on Dnepr rocket in June 2010 for formation flying test

**Fragmento (inicio):**

> Prisma Prisma satellite during integration Mission type | Technology demonstrator Operator | Swedish National Space Board , DLR , CNES COSPAR ID | Mango : 2010-028B Tango : 2010-028F SATCAT no. | Mango : 36599 Tango : 36827 Mission duration | 1 year planned 16 years, 4 months and 27 days elapsed Spacecraft properties Manufacturer | Saab Ericsson Space , Omnisys Instruments , ECAPS Launch mass | Mango : 145 kg (320 lb) Tango : 50 kg (110 lb) Dimensions | Mango : 80 cm × 130 cm (31 in × 51 in) Tango : 80 cm × 31 cm (31 in × 12 in) Power | Mango : 300 watts Tango : 90 watts Start of mission Launch date | 15 June 2010, 14:42:16 UTC ( 2010-06-15UTC14:42:16Z ) Rocket | Dnepr rocket Launch site | D…

### q34 · GRAIL Launch Press Kit (1.4Mb) (`doc_3168__0022`)

**Consulta:** measuring lunar gravity field accurately to determine structure and thermal evolution of a terrestrial planet's interior

**Fragmento (inicio):**

> and other worlds. The GRAIL mission will forward this scientific endeavor, creating the most accurate gravitational map of the moon to date. Previous space missions have mapped the gravity fields of asteroids, Venus, Mars, Jupiter, Saturn and Earth. Even Earth’s moon, the object of GRAIL’s attention, has had its gravity field measured on numerous occasions with varying degrees of success. But the accuracy of the GRAIL data will surpass by orders of magnitude that previously obtained, which will allow a new level of understanding about Earth’s nearest neighbor. If the moon were a smooth sphere of uniform density, there would be no need for a mission like GRAIL — it would measure no changes in…

