import requests
import bs4
from bs4 import BeautifulSoup

"""url="https://www.medpluslab.com/pathalogy-byAlphabet"
r=requests.get(url)
soup=BeautifulSoup(r.content,'html.parser')
k=soup.find_all('a')
l=[]
for i in k:
    if(i.find('span',itemprop="name")!=None):
        l.append(i.get('title'))
print(l)"""
def list_of_medical_tests():
    return(['ABSOLUTE BASOPHIL COUNT', 'ABSOLUTE EOSINOPHIL COUNT', 'ABSOLUTE LYMPHOCYTE COUNT', 'ABSOLUTE MONOCYTE COUNT', 'ABSOLUTE NEUTROPHIL COUNT', 'ACID PHOSPHATASE', 'ACTIVATED PARTIAL THROMBOPLASTIN TIME ', 'ADRENOCORTICOTROPHIC HORMONE ', 'ALANINE AMINOTRANSFERASE ', 'ALBUMIN/GLOBULIN RATIO', 'ALKALINE PHOSPHATASE', 'ALLERGY PROFILE - FOOD ALLERGENS', 'ALPHA 1 ANTITRYPSIN', 'AMA-M2 ANTIBODY', 'ANCA (ANTI NEUTROPHILIC CYTOPLASMIC ANTIBODIES) TITRES - IFA METHOD', 'ANCA (ANTI NEUTROPHILIC CYTOPLASMIC ANTIBODY) QUALITATIVE - IFA METHOD', 'ANCA-MYELOPEROXIDASE', 'ANCA-SERINE PROTEINASE 3', 'ANDROSTENEDIONE', 'ANTI CARDIOLIPIN IgA ANTIBODY', 'ANTI CARDIOLIPIN IgG ANTIBODY', 'ANTI CARDIOLIPIN IgM ANTIBODY', 'ANTI CENTOMERE PROTEIN B ANTIBODY', 'ANTI ECHINOCOCCUS IgG ANTIBODY', 'ANTI GLIADIN IgA ANTIBODY', 'ANTI GLIADIN IgG ANTIBODY', 'ANTI JO-1 ANTIBODY', 'ANTI LKM ANTIBODY ', 'ANTI MITOCHONDRIAL ANTIBODY ', 'ANTI MITOCHONDRIAL ANTIBODY QUALITATIVE - IFA METHOD', 'ANTI NUCLEAR ANTIBODY (ANA)', 'ANTI NUCLEAR ANTIBODY QUALITATIVE - IFA METHOD', 'ANTI NUCLEAR ANTIBODY TITRES - IFA METHOD', 'ANTI PCNA ANTIBODY', 'ANTI PHOSPHOLIPID IgG ANTIBODY', 'ANTI PHOSPHOLIPID IgM ANTIBODY', 'ANTI PM-SCL ANTIBODY', 'ANTI RIBOPROTEIN', 'ANTI Rho52 ANTIBODY', 'ANTI SCL-70 ANTIBODY', 'ANTI SMITH (Sm) ANTIBODY', 'ANTI SMOOTH MUSCLE ANTIBODY (ASMA) TITRES - IFA METHOD', 'ANTI SMOOTH MUSCLE ANTIBODY QUALITATIVE - IFA METHOD', 'ANTI SPERM ANTIBODY', 'ANTI SS -A IgG ANTIBODY', 'ANTI SS- B IgG ANTIBODY ', 'ANTI STREPTOLYSIN O (ASO) TITRE', 'ANTI THROMBIN III ANTIGEN', 'ANTI THYROGLOBULIN ANTIBODY ', 'ANTI THYROPEROXIDASE ANTIBODY ', 'ANTI dsDNA ANTIBODY ', 'ANTI dsDNA ANTIBODY QUALITATIVE - IFA METHOD', 'ANTI dsDNA ANTIBODY TITRES - IFA METHOD', 'ANTI nRNP/SM ANTIBODY', 'APOLIPOPROTEIN A1 ', 'APOLIPOPROTEIN A1/B RATIO', 'APOLIPOPROTEIN B ', 'ASPARTATE AMINOTRANSFERASE ', 'B TYPE NATRIURETIC PEPTIDE', 'BLOOD ARSENIC LEVEL', 'BLOOD GROUP & RH FACTOR', 'BLOOD LEAD ', 'BLOOD PERIPHERAL SMEAR EXAMINATION', 'BLOOD UREA NITROGEN', 'BRUCELLA ANTIBODY SCREEN', 'BRUCELLA IgG ANTIBODY', 'BRUCELLA IgM ANTIBODY', 'BUN/CREATININE RATIO', 'C-PEPTIDE', 'C-REACTIVE PROTEIN (CRP)', 'CA 15-3', 'CA 19-9', 'CA-125', 'CALCIUM CREATININE RATIO', 'CARCINO EMBRYONIC ANTIGEN ', 'CD3 ABSOLUTE COUNT', 'CD3/CD4/CD8 COUNT', 'CD4 ABSOLUTE COUNT', 'CD4/CD8 COUNT', 'CHIKUNGUNYA IgM ANTIBODY', 'CHOLINESTERASE', 'CMV DNA QUALITATIVE PCR', 'CMV DNA QUANTITATIVE PCR', 'COMPLEMENT 3 (C3)', 'COMPLEMENT 4 (C4)', 'COMPLETE BLOOD COUNT & ESR', 'COMPLETE BLOOD PICTURE', 'COMPLETE STOOL EXAMINATION', 'COMPLETE URINE ANALYSIS ', 'COOMBS TEST - DIRECT', 'COOMBS TEST - INDIRECT', 'CREATINE KINASE (CK)', 'CREATINE KINASE MB FRACTION (CK-MB)', 'CREATININE CLEARANCE TEST', 'CYCLIC CITRULLINATED PEPTIDE ANTIBODY', 'CYCLOSPORINE LEVEL', 'CYSTICERCOSIS IgG ANTIBODY', 'CYTOMEGALO VIRUS IgG ANTIBODY', 'CYTOMEGALO VIRUS IgM ANTIBODY', 'D-DIMER', 'DEHYDROEPIANDROSTERONE ', 'DEHYDROEPIANDROSTERONE SULPHATE ', 'DENGUE IgG ANTIBODY', 'DENGUE IgG ANTIBODY RAPID CARD TEST', 'DENGUE IgM ANTIBODY', 'DENGUE IgM ANTIBODY RAPID CARD TEST', 'DIFFERENTIAL COUNT (DC)', 'DIGOXIN LEVEL', 'DIRECT BILIRUBIN', 'Dengue NS1 Antigen Elisa', 'Dengue NS1 Antigen card', 'ERYTHROCYTE COUNT ', 'ERYTHROCYTE SEDIMENTATION RATE (ESR)', 'ERYTHROPOIETIN (EPO)', 'ESTRADIOL (E2)', 'FACTOR IX', 'FACTOR V', 'FACTOR V LEIDEN MUTATION (SCREENING)', 'FACTOR VIII', 'FASTING BLOOD GLUCOSE', 'FASTING URINE GLUCOSE', 'FIBRINOGEN', 'FIBRINOGEN DEGRADATION PRODUCT (FDP)', 'FOLLICLE STIMULATING HORMONE (FSH)', 'FREE PROSTATE SPECIFIC ANTIGEN', 'FREE TESTOSTERONE', 'FREE THYROXINE (FT4)', 'FREE TRIIODOTHYRONINE (FT3)', 'GAMMA GLUTAMYL TRANSFERASE (GGT)', 'GLOMERULAR BASEMENT MEMBRANE IgG ANTIBODY ', 'GLUCOSE 6 PHOSPHATE DEHYDROGENASE (G6PD)', 'GROWTH HORMONE ', 'HAPTOGLOBIN', 'HDL CHOLESTEROL', 'HELICOBACTER PYLORI IgA ANTIBODY', 'HELICOBACTER PYLORI IgG ANTIBODY', 'HELICOBACTER PYLORI IgM ANTIBODY', 'HEMOGLOBIN (Hb)', 'HEMOGLOBIN A1c', 'HEMOGLOBIN ELECTROPHORESIS', 'HEPATITIS A VIRUS ANTIBODY (HAV) - TOTAL ', 'HEPATITIS A VIRUS IgM ANTIBODY (HAV- IgM)', 'HEPATITIS B CORE ANTIBODY - TOTAL (HBcAb-Total)', 'HEPATITIS B CORE IgM ANTIBODY (ANTI HBc - IgM)', 'HEPATITIS B ENVELOPE ANTIBODY ', 'HEPATITIS B ENVELOPE ANTIGEN ', 'HEPATITIS B SURFACE ANTIBODY (ANTI HBs)', 'HEPATITIS B SURFACE ANTIGEN (HBsAG)', 'HEPATITIS B SURFACE ANTIGEN RAPID CARD TEST', 'HEPATITIS B VIRUS DNA QUALITATIVE PCR', 'HEPATITIS B VIRUS QUANTITATIVE PCR ', 'HEPATITIS C VIRUS (HCV) ANTIBODY', 'HEPATITIS C VIRUS GENOTYPE', 'HEPATITIS C VIRUS QUALITATIVE PCR', 'HEPATITIS C VIRUS QUANTITATIVE PCR', 'HEPATITIS C VIRUS RAPID CARD TEST', 'HEPATITIS E VIRUS IgG ANTIBODY (HEV IgG)', 'HEPATITIS E VIRUS IgM ANTIBODY (HEV IgM)', 'HERPES SIMPLEX VIRUS 1 & 2 IgG ANTIBODY', 'HERPES SIMPLEX VIRUS 1 & 2 IgM ANTIBODY', 'HERPES SIMPLEX VIRUS 1 IgG ANTIBODY', 'HERPES SIMPLEX VIRUS 1 IgM ANTIBODY', 'HERPES SIMPLEX VIRUS 2 IgG ANTIBODY', 'HERPES SIMPLEX VIRUS 2 IgM ANTIBODY', 'HIGH SENSITIVITY CRP (hsCRP)', 'HIV 1 & 2 ANTIBODY', 'HIV 1 & 2 ANTIBODY - RAPID CARD METHOD', 'HIV 1 RNA QUALITATIVE PCR', 'HIV 1 RNA QUANTITATIVE PCR', 'HIV WESTERN BLOT', 'HOMOCYSTEINE', 'IMMUNOGLOBULIN A (IgA)', 'IMMUNOGLOBULIN E (IgE) ', 'IMMUNOGLOBULIN G (IgG)', 'IMMUNOGLOBULIN M (IgM)', 'INDIRECT, DIRECT & TOTAL BILIRUBIN ', 'INFECTIOUS MONONUCLEOSIS TEST', 'INHIBIN B', 'INSULIN LIKE GROWTH FACTOR (IGF-1)', 'INTACT PARATHYROID HORMONE', 'INTERFERON GAMMA ASSAY', 'INTERLEUKIN-6 (IL-6)', 'IONIZED CALCIUM', 'LDL CHOLESTEROL', 'LDL/HDL CHOLESTEROL RATIO', 'LEPTOSPIRA IgG ANTIBODY ', 'LEPTOSPIRA IgG ANTIBODY RAPID CARD TEST', 'LEPTOSPIRA IgM ANTIBODY ', 'LEPTOSPIRA IgM ANTIBODY RAPID CARD TEST', 'LIPOPROTEIN a ', 'LUPUS ANTICOAGULANT', 'LUTEINISING HORMONE ', 'MALARIA FALCIPARUM AND VIVAX ANTIGEN (V & F)', 'MALARIAL PARASITE IDENTIFICATION ', 'MEAN CORPUSCULAR HEMOGLOBIN  (MCH)', 'MEAN CORPUSCULAR HEMOGLOBIN CONCENTRATION (MCHC)', 'MEAN CORPUSCULAR VOLUME(MCV)', 'MEAN PLATELET VOLUME (MPV)', 'MEASLES IgG ANTIBODY', 'MEASLES IgM ANTIBODY ', 'METH HEMOGLOBIN', 'MICROALBUMIN/CREATININE RATIO', 'MICROFILARIA ANTIGEN', 'MULLERIAN INHIBITING SUBSTANCE', 'MUMPS IgG ANTIBODY', 'MUMPS IgM ANTIBODY', 'MYCOBACTERIUM TUBERCULOSIS QUALITATIVE PCR ', 'NUCLEOSOMES', 'Non HDL Cholesterol', 'PACKED CELL VOLUME (PCV)', 'PAPP-A LEVEL', 'PARIETAL CELL ANTIBODY', 'PLASMA LACTATE', 'PLATELET COUNT', 'POST PRANDIAL BLOOD GLUCOSE', 'POST PRANDIAL URINE GLUCOSE', 'PROCALCITONIN', 'PROSTATE SPECIFIC ANTIGEN ', 'PROSTATIC ACID PHOSPHATASE', 'PROTEIN C ACTIVITY', 'PROTEIN S ACTIVITY', 'PROTHROMBIN TIME (PT)', 'QBC MALARIA TEST', 'RANDOM BLOOD GLUCOSE', 'RANDOM URINE GLUCOSE', 'RAPID PLASMA REAGIN TEST', 'RBC FOLATE', 'RETICULOCYTE COUNT', 'RH ANTIBODY - TITRE', 'RHEUMATOID FACTOR ', 'RHEUMATOID FACTOR IgG ANTIBODY', 'RHEUMATOID FACTOR IgM ANTIBODY', 'RUBELLA VIRUS IgG ANTIBODY', 'RUBELLA VIRUS IgM ANTIBODY', 'SALMONELLA TYPHI IgG ANTIBODY', 'SALMONELLA TYPHI IgM ANTIBODY', 'SERUM ADA LEVEL', 'SERUM ALBUMIN', 'SERUM ALCOHOL LEVEL', 'SERUM ALDOLASE', 'SERUM ALDOSTERONE', 'SERUM ALPHA FETO PROTEIN', 'SERUM ALUMINIUM', 'SERUM AMMONIA ', 'SERUM AMYLASE', 'SERUM ANGIOTENSIN CONVERTING ENZYME', 'SERUM BICARBONATE ', 'SERUM CALCITONIN', 'SERUM CALCIUM', 'SERUM CERULOPLASMIN', 'SERUM CHLORIDE', 'SERUM COPPER', 'SERUM CORTISOL', 'SERUM CREATININE', 'SERUM FERRITIN', 'SERUM FOLATE ', 'SERUM FREE BETA HCG  ', 'SERUM GASTRIN', 'SERUM GLOBULIN', 'SERUM INSULIN', 'SERUM IRON', 'SERUM LACTATE DEHYDROGENASE ', 'SERUM LIPASE', 'SERUM LITHIUM ', 'SERUM MAGNESIUM', 'SERUM PHOSPHORUS', 'SERUM POTASSIUM', 'SERUM PROGESTERONE', 'SERUM PROLACTIN', 'SERUM PROTEIN ELECTROPHORESIS', 'SERUM SODIUM', 'SERUM THYROGLOBULIN', 'SERUM TOTAL BETA HCG ', 'SERUM TRANSFERRIN', 'SERUM TRIGLYCERIDES', 'SERUM UREA', 'STOOL FOR OCCULT BLOOD', 'TACROLIMUS LEVEL', 'THROMBIN TIME', 'THYROID STIMULATING HORMONE (TSH)', 'TOTAL AND DIFFERENTIAL COUNT (TC & DC)', 'TOTAL BILIRUBIN', 'TOTAL CHOLESTEROL', 'TOTAL IRON BINDING CAPACITY (TIBC)', 'TOTAL SERUM PROTEIN', 'TOTAL TESTOSTERONE', 'TOTAL THYROXINE (TT4)', 'TOTAL TRIIODOTHYRONINE (TT3)', 'TOTAL/HDL CHOLESTEROL RATIO', 'TOXOPLASMA GONDII IgG ANTIBODY', 'TOXOPLASMA GONDII IgM ANTIBODY', 'TRANSFERRIN SATURATION ', 'TREPONEMA PALLIDUM HEMAGGLUTINATION (TPHA)', 'TROPONIN - T', 'TROPONIN I QUALITATIVE ', 'UNCONJUGATED ESTRIOL (E3)', 'UREA/CREATININE RATIO', 'URIC ACID', 'URINARY COPPER', 'URINE AMPHETAMINES', 'URINE AMYLASE', 'URINE ARSENIC LEVEL', 'URINE BARBITURATES', 'URINE BENZODIAZEPINES', 'URINE CALCIUM', 'URINE CANNABINOIDS', 'URINE CATECHOLAMINES', 'URINE CHLORIDE', 'URINE COCAINE ', 'URINE CORTISOL', 'URINE CREATININE (24 HRS)', 'URINE CULTURE', 'URINE ECSTASY/MDMA ', 'URINE EPINEPHRINE', 'URINE HYDROXY INDOLE ACETIC ACID ', 'URINE METHODONE ', 'URINE MICROALBUMIN (24 HRS)', 'URINE MICROALBUMIN SPOT MEASUREMENT', 'URINE OPIATES SCREEN', 'URINE PHENCYCLIDINE ', 'URINE PHOSPHORUS', 'URINE POTASSIUM', 'URINE PROTEIN (24 HRS)', 'URINE PROTEIN CREATININE RATIO ', 'URINE PROTEIN ELECTROPHORESIS', 'URINE QUALITATIVE BETA HCG ', 'URINE SODIUM', 'URINE UREA - SPOT MEASUREMENT', 'URINE URIC ACID (24 HRS)', 'URINE URIC ACID - SPOT MEASUREMENT', 'Unsaturated Iron Binding Capacity (UIBC)', 'VARICELLA ZOSTER IgG ANTIBODY', 'VARICELLA ZOSTER IgM ANTIBODY', 'VITAMIN B12 ', 'VLDL CHOLESTEROL', 'WBC COUNT ', 'WIDAL TEST'])

