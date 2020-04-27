# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas


from tmining.covid import MedNotesMiner, CovidJsonParser
from tmining.report import PlotGenerator
import simplejson as json


texto_urgencia ='''
Paciente masculino de 52 afios de edad, quien acude a esta unidad acompajiado de familiar por sus propios medios.
Motivo de ingreso: Dificultad respiratoria.

Antecedentes Personales Patolégicos. Enfermedades Crénico-Degenerativas: diabetes mellitus tipo 2 desde hace 2 afios ocn mal apego a
tratamiento ocn metformina 850 c/ 12 hrs. Alergias, traumaticos, hospitalizaciones interrogados y negados. Tabaquismo, alcoholismo,
toxicomanias; interrogadas y negadas.

Padecimiento actual: Cuenta con antecedente de comienzo dia 26 de marzo 2020 con odinofagia sin fiebre ni tos ni rinorrea ni otros agregados
por lo que acude a medico privado el cual dio tratamiento el cual no recuerda, sin presentar mejoria, posteriormente inicia el dia 27 de

marzo 2020, con exacerbacion del cuadro, agregandose cefalea tos fiebre no cuantificada se toma antipiretico y siente leve mejoria de la
sintomatologia el dia 30 de marzo 2020 comienza con odinofagia intensa mialgias artralgias ataque al estado general y tos irritativa a la
espiracion profunda , refieriendo disnea de pequefios esfuerzos motivo por el cual acude a valoracion medica.

Ala Exploracién Fisica: Con los Signos Vitales: 110/60 mmHg. Frecuencia Cardiaca: 84 Ipm. Frecuencia respiratoria: 36 respiraciones por minuto.
SatO2 80%sin oxigeneo suplementario con oxigeno suplementario con mascarilla 5 Ipm 92%. Temp: 37.1 °C.

Paciente con presencia d epolipnea, orientado en tiempo, lugar y espacio. Funciones mentales superiores conservadas. Tegumentos
deshidratados. Craneo: Sin palpar endostosis ni exostosis y sin detectar crepitaciones. Pupilas Isocéricas y normorrefléxicas, escleréticas sin
hiperemia, Narinas permeables, mucosas orales deshidratadas. Cuello integro, corto, cilindrico y sin adenomegalias cervicales, sin datos de
ingurgitacién yugular. Térax integro, con polipnea aumento de la transmisién vocal hipoventilacién de lado izquierdo basal con presencia de
estertores finos de predominio de lado derecho, sin integrar ningun sindrome pleuropulmonar. Area cardiaca con ruidos ritmicos y sincrénicos
pero con aumento de tono e intensidad, Abdomen globoso a expensas de paniculo adiposo, normoperistalsis, sin palpar visceromegalias ni
despertar puntos dolorosos a la palpacién profunda, timpanismo en todo marco colénico. Extremidades tordcicas integras y sin alteraciones en
sus arcos de movilidad, llenado capilar 2 segundos. Extremidades inferiores: sin edema, con pulsos periféricos presentes y sincrénicos, con
llenado capilar 4 segundos.

PARACLINICOS.
gasometria que reporta: PH 7.49 CO2 26 LACT 1.3 HCO3 19 BE -3.5

BH CREATCIN 164 FA 124.5 TRIG 239 AC URI 4.1 GLUC 298 ALB 3.5 TP 10.9 TPT 28.06 INR 1.07 FIBRINOGENO 850 NA 133 K 3.95 FOSF 1.9
CREAT 1 UREA 57.5 BUN 26.39 ALB 3.5

EGO GLUC 500 CET NEGATIVO ERIT 0.03 PORT 701 LEUC 0-5 PCMP ERIT 0-5 PCM

RX DE TORAX con presencia de infiltrados basales de predominio derecho

Paciente de la quinta década de la vida quien presenta, seguin definicién operacional: datos clinicos para caso sospechoso por COVID-19, por lo

que se ingresa a zona de aislados, para continuar con protocolo de estudio. SOFA de 3 puntos con 7% de mortalidad CURB 65 2 con 2 puntos
riesgo moderado 6.8% PSI DE 72 PUNTOS CLASE Ii MORTALIDAD 0.9% PAFI 216.6 por lo que cursa con una insuficncia respiratoria moderada. Se
inicia manejo con soluciones cristaloides, quinolona de tercera generacion, inhibidor de neuroaminidasa, antipirético, cloroquina, heparina de

bajo peso molecular, agregandose quinolona por proceso infeccioso a nivel urinario. Se realiza estudio epidemiologico para COVID-19. Se reporta
paciente grave con pronéstico reservado a evolucién no excento de complicaciones.

Impresiones diagnosticas:

1.- SEPSIS SOFA 3 PUNTOS CURB 65 DE 2 PUNTOS PSI CLASE II
Neumonia Atipica/ CASO SOSPECHOSO POR COVID-19

2.Ineuficiencia respiratorias moderada PAFI 216.6
3.desequilibrio acido base:

acidosis metabolica no compensada

alcalemia

4. Diabtetes Mellitus tipo 2 Descontrolada


Resultados de Laboratorio


AMY_AMY, 49.2, U/L, 28/100,

BILIRRUBINAS

PFH_BIl, 0.5, mg/dl, 0,2/1,

CALCIO TOTAL

ES2_CA, 8.7, mg/dl, 8,4/10,2,


TRIG_TRIG, 239,23, mg/dl,
Péptido Natiuretico (BNP) Cuantitativa Prueba Rapida
PCP_OBS, SIN MUESTRA, -,
Dimero D Cuantitativo prueba rapida
PCP_OBS, SIN MUESTRA, -,
PROCALCITONINA

IGM_NOTA, SIN REACTIVO, -,
BIOMETRIA HEMATICA
BH_NOTA, SIN MUESTRA, -,
GASOMETRIA ARTERIAL
GASO_THbe, 10.6,

EXAMEN GENERAL DE ORINA
EGO_BAC, ESCASAS, x campo, 0/64,


EN ESPERA DE RECABAR MUESTRAS PARA PANEL VIRAL Y COVID 19.
'''

covid_seeker = MedNotesMiner(texto_urgencia)
covid_seeker.check_covid19()
covid_seeker.check_symptoms()
covid_seeker.check_sampling()
covid_seeker.check_comorbidities()

covid_insights =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
print(covid_insights)

parser = CovidJsonParser()
print(parser.symptoms_occurrences(covid_seeker.clues))

# cooccurrences plot from data table obtained from symptoms_occurrences
plot_gen = PlotGenerator()
csv_path = 'data/cooccurrences_of_symptoms.csv'
plot_gen.cooccurrences(csv_path)
