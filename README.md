# covidminer
Text Mining Emergent Library for Information Extraction from Medical Notes in Spanish during COVID-19 pandemic


The script `demo.py` is the minimal code example in Python 3.


```
from gems.covid import MedNotesMiner
import simplejson as json

covid_symptoms = 'resources/sintomas.csv'
covid_sampling = 'resources/muestras.txt'
covid_seeker = MedNotesMiner(text_string, covid_symptoms, covid_sampling)
covid_seeker.check_symptoms()
covid_seeker.check_sampling()

covid_insights =  json.dumps(covid_seeker.clues)
print(covid_insights)
```

Gives:

```
{
  "texto": "NOTA DE INGRESO.\n\nPACIENTE MASCULINO DE 63 ANOS DE EDAD, QUIEN ACUDE POR SUS PROPIOS MEDIOS SIN FAMILIAR ACOMPANANTE.\nMOTIVO DE INGRESO: DIFICULTAD RESPIRATORIA.\n\nANTECEDENTES PERSONALES PATOLOGICOS. ENFERMEDADES CRONICO-DEGENERATIVAS:REFIERE DIABETES TIPO 2 DE 20 ANOS DE EVOLUCION\nTRATADA CON METFORMINA/GILBENCLAMIDA 1 CADA 8 HORAS, HIPERTENSION ARTERIAL SISTEMICA DE 20 ANOS DE EVOLUCION\nENTRATAMIENTO CON LOSARTAN 1 TABLETA CADA 12 HORAS. QUIRURGICOS: AMIGDALECTOMIA A LOS 8 ANOS DE EDAD REALIZADA EN EL\nHOSPITAL INFANTIL DE MEXICO SIN COMPLICACIONES , CIRUGIA DE TABIQUE NASAL HACE 10 ANOS , CIRUGIA EN OIDO IZQUIERDO HACE 30\n\nANOS NO RECUERDA MOTIVO SIN EMBARGO DERIVADO DE ELLO EL PACIENTE USA APARATO AUXILIAR PARA LA AUDICION, NIEGA ALERGICOS Y\nTRANSFUSIONALES. ETILISMO POSITIVO DESDE LOS 14 ANOS DE EDAD HASTA LOS 23 ANOS CON PATRON DE CONSUMO SEMANAL HASTA LA\nEMBRIAGUEZ SUSPENDIDO HACE 10 ANOS, TABAQUISMO POSITIVO DESDE LOS 14 ANOS DE EDAD A RAZON DE 1 CAJETILLA AL DIA SUSPENDIDO\nHACE 10 ANOS. TOXICOMANIAS INTERROGADAS Y NEGADAS.\n\nANTECEDENTES INFECTO CONTAGIOSOS PACIENTE CON ANTECEDENTE DE VIAJE A QUINTANA ROO HACE 20 DIAS. PACIENTE QUE NO CUENTA CON\nVACUNA DE INFLUENZA.\n\nPADECIMIENTO ACTUAL: INICIA EL DIA 21 OE MARZO CON ATAQUE AL ESTADO GENERAL UNA SEMANA DESPUES SE AGREGO FIEBRE\n\nCUANTIFICADA DE 37 * C ASI COMO ALTERACIONES DEL GUSTO Y EL OLFATO Y DISNEA DE MEDIANOS ESFUERZOS POR LO QUE ACUDE CON\nMEDICO PARTICULAR QUIEN INDICA MUPIROCINA (DEBIDO A MORDEDURA DE PERRO DEL DIA 16 DE MARZO) Y PARACETAMOL INDICANDO\nCONFINAMIENTO DESDE EL DIA 29 DE MARZO HASTA EL DIA DE HOY QUE PRESENTA AUMENTO DE LA DISNEA MOTIVO ACUDE A ESTA UNIDAD\nHOSPITALARIA PARA SU VALORACION.\n\nALA EXPLORACION FISICA: CON LOS SIGNOS VITALES: 120/70 MMHG. FRECUENCIA CARDIACA: 109 LPM. FRECUENCIA RESPIRATORIA: 22 RPM.\n\nSAT. O2 77 %. TEMP: 36.3°C\n\nALA EXPLORACION FISICA, SE ENCUENTRA PACIENTE DESPIERTO, ORIENTADO EN TIEMPO PERSONA Y ESPACIO. FUNCIONES MENTALES SUPERIORES\nCONSERVADAS, TEGUMENTOS MODERADAMENTE DESHIDRATADOS. CRANEO: SIN PALPAR ENDOSTOSIS NI EXOSTOSIS Y SIN DETECTAR\nCREPITACIONES. APARATO AUDITIVO AUXILIAR IZQUIERDO, PUPILAS ISOCORICAS Y NORMORREFLEXICAS, ESCLEROTICAS SIN HIPEREMIA . NARINAS\nPERMEABLES, MUCOSAS ORALES DESHIDRATADAS. PUPILAS ISOCORICAS Y NORMORREFLEXICAS A ESTIMULO LUMINOSO. CUELLO INTEGRO, LARGO,\nCILINDRICO Y SIN ADENOMEGALIAS CERVICALES, SIN DATOS DE INGURGITACION YUGULAR. TORAX INTEGRO, NORMOLINEO CON AUMENTO DELOS\nMOVIMIENTOS DE AMPLEXION AMPLEXACION, HIPOVENTILADO EN EN AREAS BASALES DE FORMA BILATERAL AUSCULTANDOSE ESTERTORES FINOS,\nNO SE AUSCULTAN SIBILANCIAS, INTEGRANDO SINDROME PLEUROPULMONAR DE TIPO CONSOLIDACION. AREA CARDIACA CON RUIDOS RITMICOS\n\nY SINCRONICOS CON AUMENTO DE TONO E INTENSIDAD. ABDOMEN GLOBOSO A EXPENSAS DE PANICULO ADIPOSO, PERISTALSIS DISMINUIDA EN\nFRECUENCIA E INTENSIDAD, SIN PALPAR VISCEROMEGALIAS, PUNTOS URETRALES MEDIOS NEGATIVOS. EXTREMIDADES TORACICAS INTEGRAS Y SIN\nALTERACIONES EN SUS ARCOS DE MOVILIDAD, LLENADO CAPILAR 2 SEGUNDOS. EXTREMIDADES INFERIORES: SIN EDEMA, CON PULSOS\nPERIFERICOS PRESENTES EN BUEN TONO INTENSIDAD, CON LLENADO CAPILAR INMEDIATO Y PRESENCIA DE LESION EN PIERNA IZQUIERDA DE 4 CM\nCON SECRECION DE FIBRINA SIN DATOS DE INFECCION AL MOMENTO DELA EXPLORACION.\n\nPACIENTE DE LA SEPTIMA DECADA DE LA VIDA QUIEN CUMPLE CON DEFINICION OPERACIONAL PARA CASO SOSPECHOSO POR COVID-19,\nPRESENTANDO SATURACION DE OXIGENO AL 77% ADEMAS DE DATOS CLINICOS DE DIFICULTAD RESPIRATORIA, POR LO QUE SE DECIDE SU\nINGRESO AL SERVICIO DE URGENCIAS , PARA CONTINUAR CON PROTOCOLO DE ESTUDIO. Q-SOFA DE 1 PUNTO. NEWS-2 6 PUNTOS, LO QUE INDICA\nNECESIDAD DE MANEJO INTRAHOSPITALARIO. PACIENTE QUE PRESENTA HERIDA ANTIGUA POR MORDEDURA DE PERRO EN EXTREMIDAD PELVICA\nIZQUIERDA LIMPIA SIN DATOS DE INFECCION.\n\nSE INICIA MANEJO CON OXIGENO SUPLEMENTARIO CON BOLSA RESERVORIO ADEMAS DE SOLUCIONES CRISTALOIDES POR VIA PERIFERICA.\nOMEPRAZOL 40 MG. IV CADA 24 HRS. AZITROMICINA 500 MG. VO CADA 24 HRS. OSELTAMIVIR 75 MG, VO CADA 12 HRS. SE SOLICITAN Y SE\n\nTOMAN MUESTRAS PARA ESTUDIOS DE LABORATORIO, ASI COMO PANEL RESPIRATORIO PRUEBA PARA COVID 19 Y SE SOLICITA RADIOGRAFIA DE\nTORAX. DE IGUAL FORMA, SE LLENA FORMATO DE ESTUDIO EPIDEMIOLOGICO TANTO PARA INFLUENZA COMO PARA COVID-19. DEBIDO ALA\nSINTOMATOLOGIA DEL PACIENTE, NO SE DESCARTA MANEJO AVANZADO DE LA VIA AEREA A CORTO PLAZO, POR LO QUE SE INFORMA AL\nPACIENTE. SE REPORTA PACIENTE GRAVE CON PRONOSTICO RESERVADO A EVOLUCION NO EXCENTO DE COMPLICACIONES.\n\nIMPRESIONES DIAGNOSTICAS:\n\n1.INFECCION DE VIAS RESPIRATORIAS BAJAS\n\nNEUMONIA ATIPICA. 6 PUNTOS DE NEWS 2 RIESGO MODERADO. Q SOFA 1 PUNTO, CASO SOSPECHOSO PARA COVID 19\n2. DIABETES TIPO 2 EN TRATAMIENTO\n\n3. HIPERTENSION ARTERIAL SISTEMICA EN TRATAMIENTO",
  "síntomas": {
    "fiebre": [
      {
        "mención": "...semana despues se agrego fiebre  cuantificada de 37 * c...",
        "wikidata": "https://www.wikidata.org/wiki/Q38933"
      }
    ],
    "disnea": [
      {
        "mención": "...y el olfato y disnea de medianos esfuerzos por...",
        "wikidata": "https://www.wikidata.org/wiki/Q188008"
      },
      {
        "mención": "...presenta aumento de la disnea motivo acude a esta...",
        "wikidata": "https://www.wikidata.org/wiki/Q188008"
      }
    ],
    "dificultad respiratoria": [
      {
        "mención": "...acompanante. motivo de ingreso: dificultad respiratoria.  antecedentes personales patologicos. enfermedades...",
        "wikidata": "https://www.wikidata.org/wiki/Q188008"
      },
      {
        "mención": "...de datos clinicos de dificultad respiratoria, por lo que se...",
        "wikidata": "https://www.wikidata.org/wiki/Q188008"
      }
    ]
  },
  "muestreos": [
    {
      "mención": "...solicitan y se  toman muestras para estudios de laboratorio..."
    }
  ]
}
```

## As a Lightweight Web service

Functionality can be lso used through lightweight web services implemented with Flask. However, the use of a professional Web Server Gateway Interface for professional applications is recommended.

Having installed and configured what is necessary (see Dependencies section and docs/devnotes), you can run the server with the following command:


```
$python app.py

 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
INFO:  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Then, with the server running you can now make POST requests sending PDF files.

![HTTP POST request example](docs/post.png)


## Dependencies

For Python 3 dependencies see `requirements.txt`. A quick installation with pip is recommended.

```
pip install  -r requirements.txt
```

In addition to the Python 3 libraries it is required to install [tesseract] (https://github.com/tesseract-ocr/tesseract/wiki) and [Poppler] (https://poppler.freedesktop.org/) for OCR support.

Mac:

```
$brew install tesseract
$brew install tesseract-esp
$brew install poppler
```

linux:

```
$sudo apt install tesseract-ocr
$sudo apt-get install tesseract-ocr-spa
sudo add-apt-repository -y ppa:cran/poppler
sudo apt-get update
sudo apt-get install -y libpoppler-cpp-dev
```

## Built With

* [Wikidata](https://www.wikidata.org/) - The free knowledge base with 82,849,340 data items that anyone can edit.
* [Tesseract](https://github.com/tesseract-ocr/tesseract/wiki) - An open source text recognition (OCR) Engine.
* [Flask](https://rometools.github.io/rome/) - The Python micro framework for building web applications.


## Authors

**Alejandro Molina-Villegas**

* [dblp](https://dblp.uni-trier.de/pers/hd/m/Molina=Villegas:Alejandro)
* [orcid](https://orcid.org/0000-0001-9398-8844)
* [CONACyT-CentroGeo](http://mid.geoint.mx/site/integrante/id/15.html)

See also the list of [contributors]() who participate in this project.

## Institutions

  * [CentroGeo](https://www.centrogeo.org.mx/) - Centro de Investigación en Ciencias de Información Geoespacial.
  * [GeoInt](http://www.geoint.mx/) - Laboratorio Nacional de Geointeligencia.
  * [DataLab](http://datalab.geoint.mx/site/contacto.html#Core_Members) - DataLab

## License

This project is licensed under the MIT License - see the [LICENSE](docs/LICENSE) file for details. 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



