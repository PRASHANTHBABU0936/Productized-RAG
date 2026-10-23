

# Document 1

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 1,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_001.png"
}
```

Content:
PAGE 1

SELECTABLE TEXT:
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
6502812
Pulmo-TS2ONN: A Novel Triple Scale Self
Operational Neural Network for Pulmonary
Disorder Detection Using Respiratory Sounds
Arka Roy , Graduate Student Member, IEEE, Udit Satija , Senior Member, IEEE, and Saurabh Karmakar
Abstract— Pulmonary disorders (PDs) are one of the substan-
tial hazards to human life, which can be diagnosed by a variety
of clinical modalities, including peak flowmeter and spirometry
measurements, chest auscultation-based respiratory sound (RS)
measurements, etc. Analyzing the acoustic RS measurements
is one of the inexpensive yet essential diagnostic methods for
identifying PDs as these RSs are correlated with structural flaws
of the lungs that occur due to PDs. Additionally, the development
of the digital stethoscope facilitates the continuous measurement
of acoustic RSs of any individual, which can be exploited to
identify a variety of PDs. In this article, we have proposed a triple
time-frequency feature set driven triple-scale self-operational
neural network (TS2ONN) architecture, namely Pulmo-TS2ONN,
to classify a wide spectrum of PDs using the RSs. The proposed
pulmo-TS2ONN comprises three major stages: preprocessing,
triplet time-frequency feature set (TTFFS) extraction, and finally
classification of seven class PDs by using TS2ONN architecture
which utilizes the improved nonlinear neural backbone of self-
operational neural network (SONN) in place of the linear neural
architecture used in conventional deep learning (DL) networks.
Upon experimental evaluation, the proposed framework out-
performs the existing noteworthy research works by achieving
the highest performance rates of 98.88%, 98.27%, and 99.84%
for accuracy, sensitivity, and specificity, respectively. Lastly, the
proposed framework is implemented on a quad-core ARM-A7-
based Raspberry Pi-4 microcontroller, allowing the possibility of
translating the research into real clinical situations for RS-based
PD screening.
Index Terms— Auscultation measurements, classification, pul-
monary
disorders
(PDs),
respiratory
sounds
(RSs),
self-
operational neural network (SONN).
I. INTRODUCTION
P
ULMONARY disorders (PDs) have become one of the
leading causes of global mortality, killing more than
Manuscript received 10 September 2023; revised 13 February 2024;
accepted 25 February 2024. Date of publication 18 March 2024; date of cur-
rent version 27 March 2024. This work was supported in part by the National
Mission on Interdisciplinary Cyber-Physical System (NM-ICPS), Technology
Innovation Hub (TIH) Project, IIT Patna, under Grant TIH/EE/SVTA/010; and
in part by the Ministry of Education (MoE), Government of India, through
the Prime Minister’s Research Fellowship (PMRF) Program, under Grant
PMRF ID: 2702854. The Associate Editor coordinating the review process was
Dr. Lin Xu. (Corresponding author: Udit Satija.)
Arka Roy and Udit Satija are with the Department of Electrical Engineering,
Indian Institute of Technology Patna, Patna, Bihar 801106, India (e-mail:
arka_2121ee34@iitp.ac.in; udit@iitp.ac.in).
Saurabh Karmakar is with the Department of Pulmonary Medicine, All India
Institute of Medical Sciences (AIIMS) Patna, Patna 801507, India (e-mail:
drsaurabhkarmakar@gmail.com).
Digital Object Identifier 10.1109/TIM.2024.3378206
8 million people across the globe [1]. As a result of air pol-
lution and an aging population, the prevalence of PDs among
the elderly and the general population has been increasing
significantly each year [2]. One of the latest reports published
by the world health organization has classified the following
diseases as “Big Five” PDs, which are lower respiratory
tract infection (LRTI), chronic obstructive pulmonary disease
(COPD), asthma, tuberculosis (TB), and lung cancer [3].
Pulmonologists use different diagnostic modalities, such as
spirometric [4] and peak flowmeter-based measurements [5],
photoplethysmogram [6], FeNO tests [7], chest X-rays, etc.,
to assess the condition of the lungs. However, most of
these modalities are either highly dependent on patient effort,
laborious, or very costly [7]. However, respiratory sounds
(RSs) heard during chest auscultation are still used as a key
diagnostic modality to identify any abnormalities present in
the lungs, as these RS characteristics change drastically if
any anatomical flaw occurs in the lungs as a result of the
manifestation of PDs [4], [8]. Wheeze and crackle are two of
the most common adventitious lung sounds. Wheeze is a high-
pitch adventitious event that can be observed in the expiration
cycle of acoustic RS measurements if the air pathways get
clogged by sputum, mucus, and other secretary substances [5]
in case of COPD, and asthma. Whereas, crackle is an explosive
and discontinuous sound that occurs in the inspiratory phases
of the breathing cycle and is related to interstitial lung illnesses
such as chronic bronchitis, pneumonia, and lung fibrosis [9].
Therefore, these RS measurements can be exploited for the
identification of different respiratory anomalies of lungs [10].
In this regard, the digital stethoscopes enable continuous
recording of the individuals’ RS measures, which may then be
used to identify a variety of PDs [10], [11], [12]. Therefore,
creating automated algorithms based on artificial intelligence
(AI) in conjunction with the RSs would be very helpful in the
early diagnosis of a number of respiratory disorders.
A. Related Works on RS-Based PD Detection
Since the outburst of COVID-19, several scientific investi-
gations into developing various cough and RS measurement-
based audio-bio-markers to evaluate respiratory health have
been conducted by researchers worldwide, as these sounds
are highly connected with structural defects in the lungs [13].
However, the majority of these studies concentrate on
1557-9662 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 2

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 2,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_002.png"
}
```

Content:
PAGE 2

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
diagnosing adventitious RSs such as ronchi, crackle, wheeze,
etc., rather than PDs [11], [14], [15]. In recent years, only a
few studies have employed RS to identify a wide spectrum of
PDs [16], [17], [18] with the help of different machine learning
(ML) and deep learning (DL) architectures.
Additionally, most of these works have used only the
ICBHI challenge database [9] to evaluate their frameworks.
The ICBHI database has a total of seven different disease
categories (COPD, asthma, pneumonia, upper respiratory tract
infection (URTI), bronchiectasis (BRON), bronchiolitis, and
LRTI) along with a healthy category, and thereby these works
can be classified into two categories: 1) three-class PD classifi-
cation (healthy, chronic, nonchronic disease); and 2) six-class
PD classification (asthma and LRTI excluded).
1) Three-Class PD Classification:
Perna [18] used mel-
frequency cepstral coefficient (MFCC) representation
in conjunction with a standard convolutional neural
network (CNN) architecture to classify the RSs into
three categories: healthy, chronic (BRON, COPD, and
asthma), and nonchronic disease classes (pneumonia,
bronchiolitis, and URTI). By employing this technique,
the authors achieved the highest classification rate of
82%. Pham et al. [11] exploited a CNN architecture
with a mixture of multiple experts (CNN-MoEs), which
was trained using a teacher-student learning framework,
to categorize the RSs into three classes using the mel
spectrogram time-frequency representation (TFR). Using
this framework they achieved a specificity of 82% and a
sensitivity of 96%. However, this three-class PD classi-
fication becomes less relevant when real-time AI-based
diagnostic systems are considered, as the patient or the
physician is more concerned with finding out the precise
diagnosis, i.e., the particular PD that the individual is
afflicted with [8] and [16].
2) Six-Class PD Classification: To make the RS-based PD
classification problem more meaningful from the clini-
cal perspective, Basu and Rana [19] proposed a gated
recurrent unit (GRU) based recurrent neural backbone
to categorize the RSs of the ICBHI database into six
diseased groups, and achieved an accuracy of 95.67%.
ICBHI database is an imbalanced database, having a
large number of RS recordings in COPD class. To miti-
gate this class imbalance issue, García-Ordás et al. [20]
investigated the possibility of using a variational autoen-
coder to strengthen the minority classes. Following this,
a CNN model was trained to classify the RSs into six
categories, which attained a specificity of 98.6% and a
sensitivity of 98.8%. Similarly, Shuvo et al. [16] used
the empirical mode decomposition (EMD) technique to
decompose the RS into intrinsic mode functions (IMFs)
and chose the IMF which has the highest correlation
with the original RS. Thereafter, scalogram TFR was
extracted from the chosen IMF and fed to standard
lightweight CNN (LCNN) architecture which has four
convolution layers, six dense layers, and 3.8 million
trainable parameters. Finally, utilizing this architecture,
the authors have achieved an accuracy of 98.7%, a speci-
ficity of 100.0%, and a sensitivity of 98.6%. Since
asthma is one of the minority PD classes in the ICBHI
database, none of the research took this into account for
the PD classification task.
Tripathy et al. [21] used only the KAUH database to classify
healthy, pneumonia, COPD, and asthmatic RSs using differ-
ent ML classifiers such as support vector machine (SVM),
multilayer perceptron (MLP), light gradient boosting machine
(LGBM) in conjugation with the spectro-temporal features
extracted from the empirical wavelet transform (EWT)-
decomposed IMFs. However, they achieved an inferior accu-
racy rate of 74.15% for the four-class disease classifica-
tion task. Apart from this, recently, a few researchers have
combined the RSs from other publicly available databases
(KAUH database [10], and RespiratoryDatabase@TR [12])
with the RSs of ICBHI database to create a custom larger
database for PD classification. Shi et al. [17] combined the
RSs of RespiratoryDatabase@TR and ICBHI to classify the
asthmatic, healthy, pneumonia, and COPD cases by employing
a two-stream transformer, multiresolution channel and spatial
attention-based DL architecture. By employing this frame-
work, the authors achieved 91.56% accuracy on the combined
RS database.
Thereby, it is evident that the majority of studies either
concentrate on a single database for PD classification or take
into account a subset of the several PD classes to perform the
classification task. Therefore, it is more relevant to exploit all
publicly available databases to create a robust PD classification
framework that covers a larger number of PDs. In this context,
Roy and Satija [8] utilized all three public RS databases to
perform a seven-class PD classification task (LRTI excluded)
for the first time, by modifying the existing inception module
of GoogLeNet architecture to a lightweight inception model,
called RDLINet. By training the RDLINet architecture in
conjunction with the mel spectrogram TFRs in an end-to-end
fashion, the authors achieved the highest accuracy of 96.6%,
a sensitivity of 96.2%, and a specificity of 98%, respectively.
B. Objective and Key Contribution
Due to the similarity of the symptoms across different PDs,
it is challenging for a pulmonologist to diagnose the condition
just based on the auscultation sounds [22]. Even a skilled
doctor might make a mistake while making inferences from the
auscultation due to the similarities between RSs [22] if they do
not employ additional astute diagnostic methods. In general,
it is advised to go for additional tests such as spirometric mea-
sures [12], peak-flowmeter-based measures [5], etc., to confirm
the disease condition, however, several disadvantages are asso-
ciated with these modalities as discussed earlier.
Therefore, the main objective of the proposed framework
is to create an efficient DL framework in conjunction with
different TFRs extracted from the RSs, which can be used
as an assistive diagnostic modality for PD identification.
In this article, we propose a triplet time-frequency feature
set (TTFFS)-based triple scale self-operational neural network
(TS2ONN), namely the Pulmo-TS2ONN for the efficient cat-
egorizing of PDs using the RSs.
Additionally, this work is a technical extension of our
previous work published in 18th edition of IEEE International
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 3

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 3,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_003.png"
}
```

Content:
PAGE 3

SELECTABLE TEXT:
ROY et al.: PULMO-TS2ONN: A NOVEL TRIPLE SCALE SONN FOR PD DETECTION USING RSs
6502812
Symposium on Medical Measurements and Applications
(MeMeA) [23], where we exploited the potential of the
recently developed heterogeneous neural model of self-
operational neural network (SONN) [24] for RS based asthma
classification and showed that the SONN surpasses the per-
formance of an existing homogeneous linear neural model
of vanilla CNNs [23]. In this article, we have proposed
a multiscale representation of the SONN to process and
extract compact class-specific embedding representation from
the TTFFS extracted from input RSs for seven-class PD
classification. Further, we have implemented the proposed
framework in a Raspberry Pi-4 microcontroller that enables
the prospect of translating this research into a real-life clinical
scenario for PD screening using RS measurements. To the
best of our knowledge, this is the first work that utilizes the
multiscale representation of the aforementioned nonlinear deep
neural network architecture: SONN, for RS-based seven-class
PD categorization. The major contributions of this research
are.
1) Investigating the potential of triplet TFR-based TTFFS
that contains mel spectrogram, constant-Q transform
(CQT), and MFCC representations extracted from the
RSs for the detection of PDs.
2) On the contrary to the existing DL models used in [8]
and [23], etc., which exploit single stream neural design,
we have developed a novel triple-scale TTFFS process-
ing model by employing the multiscale representation
of SONN architecture for the first time and fused their
compact embedding repressions to classify the PDs
efficiently.
3) Extensive evaluation of the proposed framework on the
three publicly available databases and comparative anal-
ysis with existing vanilla CNN-based transfer learning
networks in terms of different performance parameters.
4) On-device implementation of the proposed PD classifi-
cation framework using a low-resource Raspberry pi-4
microcontroller.
The rest of the article is organized as: Section II describes a
brief overview of the databases used to evaluate the classifica-
tion performance of the proposed Pulmo-TS2ONN. Section III
includes a detailed discussion on each of the stages of the
proposed framework; Section IV discusses the performance
evaluation and comparison of the proposed framework with
the existing state-of-the-art (SOTA) techniques; and finally,
Section V concludes the research.
II. DETAILS OF DATABASE
This section describes the three publicly available RS
databases: 1) ICBHI challenge database [9]; 2) King Abdullah
University Hospital (KAUH) RS sound database [10]; and
3) RespiratoryDatabase@TR (RD@TR) [12], that have been
utilized to develop the proposed Pulmo-TS2ONN framework
for the detection of PDs. Table I provides a comprehensive
description of all three databases, which includes demographic
information of the subjects, acquisition devices used to collect
the RSs, and various PD classes. In this research, we have
combined the following PD classes such as asthma, COPD,
BRON, pneumonia, bronchiolitis, URTI, and healthy, to create
Fig. 1.
Block diagram of the proposed Pulmo-TS2ONN framework for PD
classification using RSs.
a bigger data repository for developing a seven-class PD
categorization framework. Additionally, we have presented a
brief description of the clinical background of each of the
seven PDs in Table II.
III. PROPOSED FRAMEWORK
The proposed framework includes three major stages:
1) preprocessing of the input RS; 2) TTFFS creation; and
3) PD identification using the proposed triple-scale SONN
(TS2ONN) architecture, namely the Pulmo-TS2ONN. Fig. 1
illustrates the block diagram of the proposed Pulmo-TS2ONN
framework. Sections III-A–III-C include a thorough explana-
tion of each of the aforementioned major stages.
A. Preprocessing
The preprocessing stage begins with resampling the input
RS (rsip[u]) to 4 kHz rate [8], [14] and then framing the
resampled RS (rsre[u]) into 5 s length frames ( fl) while
maintaining an overlap (ol) of 50% with the subsequent frame
rsp
frm[u] = rsre

fl · p · ol + u

,
p = 0, 1, 2, . . . , P
(1)
where rsp
frm[u] and P denote the pth segmented frame of
resampled RS, and the total number of segmented frames
respectively. Thereafter, a discrete Fourier transform (DFT)
based low-frequency baseline wandering component (BWC)
0–1 Hz eliminating filter [29] is employed on each of the
segmented frames (rsp
frm[u]). The DFT index (k) for f Hz
frequency is calculated as k = ⌈( f · U/fs)⌉, where fs and U
refer to the sampling frequency of lung sound signal, and the
total number of DFT points in the segmented frame (rsp
frm[u]),
respectively. Thereafter, the DFT indices corresponding to
BW noise are set to zero. Therefore, the BWC eliminated
signal (rsp
bwce[u]) can be obtained by taking the inverse DFT
of the thresholded DFT vector ( ˜RSp
frm[k]). The mathematical
foundation for BWC elimination is described as [29]: The DFT
of the pth segmented frame (rsp
frm[u]) is calculated as
RSp
frm[k] =
U−1
X
u=0
rsp
frm[u]e
−j2πU.K.
U
(2)
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 4

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 4,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_004.png"
}
```

Content:
PAGE 4

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
TABLE I
BRIEF DESCRIPTION OF THE THREE PUBLICLY AVAILABLE DATABASES
TABLE II
BRIEF DESCRIPTION OF THE DIFFERENT PDS
rsp
bwce[u] = 1
U
U−1
X
k=0
˜RSp
frm[k]e
j2πU.K.
U
(3)
where
˜RSp
frm[k] denotes the thresholded DFT index vector
derived from RSp
frm[k].
˜RSp
frm[k] = [0, 0, . . . , 0, RSp
frm[k +
1], . . . , RSp
frm[U−k −1], 0, . . . , 0, 0]. Lastly, the rsp
bwce[u] sig-
nal is normalized between the range of [−1, 1] by employing
the following equation: rsp
nrm[u] = (rsp
bwce[u]/ max |rsp
bwce[u]|),
where rsp
nrm[u] denotes the pth normalized frame of RS.
Additionally, we have adopted several data augmentation tech-
niques, such as time stretching, noise addition, pitch shifting,
etc., [8], to increase the number of samples in the minority
class (all the PD classes except COPD [8]).
B. Triplet Time-Frequency Feature Set (TTFFS)
According to the literature, analyzing the RS signal is highly
difficult owing to its high nonstationary character, which con-
tains fluctuating frequency components over time [8]. There-
fore, it is essential to transform the signal from one domain
to another to obtain the comprehensive information present
in the signal. In this aspect, transforming the time-domain
RS to the time-frequency domain will help in capturing the
time-varying spectral characteristics of the signal [11]. In this
article, we have used an exhaustive set of TFRs from each
of the normalized RS segments (rsp
nrm[u]), such as: 1) mel
spectrogram; 2) constant Q transform (CQT) spectrogram; and
3) MFCCs, to create the TTFFS.
1) Mel Spectrogram: Firstly, the short-time Fourier trans-
form (STFT) [30] (S p
rs[h, f ]) is calculated from each of
the normalized RS segments (rsp
nrm[u]) using the following
equation [23]:
S p
rs

h, f

=
U−1
X
u=0
rsp
nrm[u] · W[u −hH] · e−j 2πu f
U
(4)
W[u] = 0.54 −0.46 · cos
 2πu
wl −1

(5)
where W[u] is the Hamming window with 1024 samples (wl),
with hop-length (H) of 524 samples. Thereafter, we project
the Hertz frequency ( f ) to mel-scale frequency ( fmel) for
constructing the mel-filter banks by employing the following
equation [31]:
fmel = 2595 · log

1 +
f
700

.
(6)
In this work, we have considered 64 mel-bands. To extract
the mel-spectrogram (XMelSpec), the triangular mel-filters are
multiplied with each STFT frame (S p
rs[h, f ]) [31].
2) CQT Spectrogram: CQT [32], [33] is one of the most
commonly used audio TFRs [11] which is utilized for music
analysis [32], adventitious RS event detection [11], etc. It imi-
tates the way the human hearing system functions. CQT com-
prises Z number of filters which have a center frequency of fz
and a bandwidth of z, respectively. The mathematical relation
between the bandwidth of the filters can be expressed as [32]:
z = (21/Z)z · min, where min and Z represent the filter
bandwidth containing the lowest center frequency, and the
number of filters per octave, respectively. Additionally, the
quality factor (Q) can be expressed as [32]: Q = fz/z. The
Q-factors are constant across all frequency bins. Suppose the
sampling frequency is fs, then the window length (wl) of each
bin can be expressed as a function of the index of the bin (z)
wl(z) = fs
z
= Q fs
fz
(7)
where ( fs/fz) illustrates the total number of samples analyzed
in each cycle at fz. Therefore, the frequency in digital domain
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 5

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 5,
  "content_type": "page_text_plus_ocr",
  "image_count": 3,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_005.png"
}
```

Content:
PAGE 5

SELECTABLE TEXT:
ROY et al.: PULMO-TS2ONN: A NOVEL TRIPLE SCALE SONN FOR PD DETECTION USING RSs
6502812
Fig. 2.
MFCC extraction process from the normalized RS.
turn out as (2πQ/wl(z)). In this article, to extract the CQT,
we have used the Hamming window. Thereby, the CQT can
be computed as [32]
CQTp
rs[z, m]=
1
wl(z)
wl(z)−1
X
u=0
rsp
nrm[u] · W[z, u −m] · e−j 2πQuω
wl (z) .
(8)
Finally, we take the squared magnitude of the CQTp
rs[z, m] to
get the CQT spectrogram TFR (XCQT).
3) MFCC: MFCC [34] is one of the most widely used
audio feature representations for RS analysis [11]. Fig. 2
illustrates the block diagram of the MFCC extraction process.
To extract the MFCC feature, first the normalized RS (rsp
nrm[u])
is segmented into small frames (rsi[u]) with 1024 samples
with 50% overlap, and a Hamming window (W[u]) is applied
on each of the frames as [34]: yi[u] = rsi[u] · W[u], where
yi[u] denotes the transformed output signal generated from
the corresponding frame rsi[u]. Thereafter, the DFT-based
squared magnitude spectrum ( ˜Y i[k]) is computed for each of
the transformed output (yi[u]). Mathematically, this process
can be expressed as
˜Y i[k] =

X
u
yi[u]e
−j2πU.K.
U

2
.
(9)
These magnitude spectrum frames are then passed through the
triangular mel-filter banks, which are defined by a constant
mel-frequency ( fmel) interval [34]. Finally, a log transforma-
tion followed by a discrete cosine transform (DCT) is applied
to the mel-filter bank projected magnitude spectrum to select
the MFCC coefficients [34]. In this article, we have considered
30 mel-filters to construct the MFCC feature (XMFCC).
The temporal visualization, mel spectrogram, CQT spec-
trogram, and MFCC TFR visualization of RSs from healthy
subject is shown in Fig. 3(a)–(d), for BRON affected case in
Fig. 3(e)–(h), for bronchiolitis in Fig. 3(i)–(l), for asthmatic
case in Fig. 3(m)–(p), for pneumonia affected subject in
Fig. 3(q)–(t), for URTI in Fig. 3(u)–(x), and lastly for COPD
affected subject in Fig. 3(y)–(β).
C. Model Architecture of the Proposed Pulmo-TS2ONN
In this subsection, we discuss the architectural details of the
proposed Pulmo-TS2ONN model utilized for PD classifica-
tion. In contrast to our previously published work: AsTFSONN
[23], where the neural network comprises only a single stream
operational neural network design to extract features from
Fig. 3.
Illustrates the temporal visualization, mel spectrogram, CQT
spectrogram, and MFCC TFRs of (a)–(d) healthy subject’s RS, (e)–(h) BRON,
(i)–(l) Bronchiolitis, (m)–(p) Asthma, (q)–(t) Pneumonia, (u)–(x) URTI, and
(y)–(β) COPD affected subject’s RS.
Fig. 4.
Illustrates the internal architecture of the proposed Pulmo-TS2ONN
model.
mel spectrogram TFR, the proposed Pulmo-TS2ONN model
uses three self-operational neutral scales to extract compact
feature representation from each of the three TFRs present in
the TTFFS. In contrast to the standard CNN, which utilizes
a linear perceptron model to extract features from the input
tensor, the proposed self-operational neural scales (SONSs)
employ the generative operational perceptron model (GOPM)
of the SONN framework [24] to increase nonlinearity into the
neural model [23]. Figs. 4 and 5 illustrate the model archi-
tecture of the proposed Pulmo-TS2ONN and SONS block,
respectively. The details of each block used to construct the
Pulmo-TS2ONN model are described below.
1) Self-Operational Neutral Scales: The main backbone of
the SONS comprises the SONN layer, tanh activation layer,
max-pooling (MP) layer, and 2-D global average pooling layer
(GAP).
1) SONN Layer: The limitation of vanilla operational neu-
ral networks (VONNs) [35], is the requirement for a
predefined library of operators and the need to search
within that library to discover the ideal set of operators,
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 6

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 6,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_006.png"
}
```

Content:
PAGE 6

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
Fig. 5.
Illustrates internal architecture of SONS.
are addressed by the GOPM designed for SONN [36].
Due to the excellent nonlinearity and reduced compu-
tational cost, SONNs outperform classic VONNs [24],
[36]. Let us consider, X ∈RA×B×Cin represents an
input tensor with height A, width B, and depth Cin.
Additionally, FCout indicates the Cth
out kernel of a layer.
The traditional perceptron model of CNN is homoge-
neous and linear as it uses simple dot product-based
multiplication and addition operations, namely the con-
volution operation [35]. In this case, the input tensor
(X) is convoluted with FCout which is followed by the
addition of a bias term (BCout). This process can be
mathematically described as
XCout =
A,B,Cin
X
a,b,cin=1
FCout(a, b, cin) · X(a, b, cin) + BCout
= FT
Cout · X + BCout
(10)
where XCout ∈RA×B×Cout denotes the output feature
map which is then passed through some activation
function to introduce the nonlinearity. To enhance the
nonlinearity of the conventional perceptron model of the
CNNs, Kiranyaz et al. [35] introduced VONN archi-
tecture, comprising a new perceptron model, namely
the GOPM, which can exploit different sorts of nonlin-
ear mathematical operators while processing any input
features from a predefined library of such operators.
Thus, the operation of VONN can similarly be written
as [35]
XCout = β{FCout, X} + BCout
(11)
where β operator indicates the predefined dictionary
of several nonlinear mathematical functions sinusoid
(sin{·}), cosine (cos{·}), hyperbolic (sinh{·},
tanh{·}),
exponential (exp{·}), etc. [35]. Since this β operator is
not fixed, we must learn it during the training phase,
which necessitates an extremely time-consuming search
procedure. As a result, the training time increases to
a great extent [35]. The VONN layer turns into a
standard CNN layer when the β operator is a dot
product.
However, in the case of SONN, a novel generative neural
backbone is used which can create any arbitrary nonlin-
ear function for each kernel element using a truncated
Mac-Laurin series expansion during the training phase,
which helps to mitigate the searching process of the
nonlinear functions from a predefined dictionary and the
high training time issue of VONN [23]
β
 FCout,1, FCout,2 . . . , FCout,v, X

=
V
X
v=1
FT
Cout,v · X v
= FT
Cout,1X + FT
Cout,2X 2 + . . . , +FT
Cout,V X V
(12)
where X v is vth power of the input tensor X and FCout,v
denotes the learnable kernel weights corresponding to
each X v, which will be learned by gradient descent
based backpropagation scheme. Therefore, the GOPM
present in the SONN transforms the input tensor by the
following equation:
XCout =
V
X
v=1
FT
Cout,v · X v + BCout.
(13)
In this article, we have selected the SONN as the main
building element of the SONS block due to its neural
architecture’s (GOPM) capability to produce improved
nonlinear representations from the input tensors over
traditional CNNs and VONNs.
2) Tanh Activation Layer: The goal of the activation func-
tion is to further nonlinearize the SONN output (XCout).
In this article, we have employed tanh nonlinear activa-
tion [24], which is mathematically described as
tanh(XCout) = eXCout −e−XCout
eXCout + e−XCout ·
(14)
3) MP Layer: The activation block’s output is subsequently
passed through the 2-D-MP block to reduce the dimen-
sionality and capture the local features by retaining the
maximum value of the feature map present in a window
with a specified pool size, which is moved with the
specified stride [8].
4) GAP Layer: The GAP layer is used to generate the final
1-D output embedding from each of the TFRs, processed
through the three cascaded SONN layers present in
SONS. GAP layer reduces the trainable parameter size
and prevents over-fitting [37].
In this article, we have used three scales of SONS and each of
the SONSs further contains a cascade of three SONN layers,
followed by a hyperbolic tangent (tanh) nonlinear activation
and a max-pooling layer after each of the SONN layers,
as shown in Fig. 5. Finally, a 2-D GAP [37] is employed to
extract a 1-D embedding output vector as the final outcome of
SONSs. Therefore, the series of cascaded operations employed
in ith SONS (ζ SONSi{·}) can be formalized from Fig. 5 as
ζ SONSi
XTTFFSi
	
= ζ GAP
ζ MPζ tanhζ SONN
ζ MPζ tanh
×ζ SONN
ζ MPζ tanhζ SONN
XTTFFSi
				
(15)
where XTTFFSi, ζ SONN, ζ tanh, ζ MP, and ζ GAP denote the ith TFR
element present in the TTFFS, and the functional operation of
the SONN layer, tanh activation layer, the MP layer, and lastly,
the GAP layer, respectively. In this study, three SONN layers
have a uniform filter dimension (Fd) of 3 × 3, with filter
number (Fm
n ) of 16, 32, and 128, respectively. Additionally,
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 7

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 7,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_007.png"
}
```

Content:
PAGE 7

SELECTABLE TEXT:
ROY et al.: PULMO-TS2ONN: A NOVEL TRIPLE SCALE SONN FOR PD DETECTION USING RSs
6502812
TABLE III
DESCRIPTION OF THE TOTAL LEARNABLE PARAMETER SIZE OF
THE PULMO-TS2ONN
we have utilized the Mac-Laurin series truncation factor (v)
of 3 for the SONN layers. Finally, the GAP layer is used to
generate the 1-D output embedding from each of the TFRs,
processed through the three cascaded SONN layers present in
each of the SONS. Thereby, the 1-D-embedding generation
process from each of the TFR elements present in the TTFFS
using SONSs can be mathematically described as
EMelSpec = ζ SONS1
XMelSpec
	
(16)
ECQT = ζ SONS2
XCQT
	
(17)
EMFCC = ζ SONS3{ XMFCC}
(18)
where {EMelSpecy, ECQT, EMFCC} ∈R128×1 denote the 1-D-
embedding output generated from the triplet TFR set using
SONSs.
Thereafter,
these
1-D
embeddings
are
concatenated
with
each
other
to
form
another
fused
1-D
vector
(Econcat ∈R384×1) using the following method: Econcat =
[EMelSpec; ECQT; EMFCC], which is then passed through the
Gaussian error linear unit (GeLU) activation layer [38] and
dropout layer with a dropout factor of 0.2. Following that,
we utilize a fully connected dense layer (FCDL) with 100 neu-
rons, GeLU activation, dropout rate of 0.2. The mathematical
description for these dense layers is given below [38]
Zfc = GeLU(Xfc · Wfc + Bfc)
(19)
where Xfc, Zfc, Wfc, and Bfc denote the input-output vector,
weights, and biases of the FCDL, respectively. Lastly, a clas-
sification layer with seven neurons and softmax activation [8]
is used to get the class-specific probability values. Table III
describes the total number of learnable parameters required to
construct the Pulmo-TS2ONN model.
Finally, the Pulmo-
TS2ONN model is trained using a gradient descent-based
weight updation approach by minimizing the categorical cross-
entropy (CCE) loss function [8].
TABLE IV
OPTIMAL SIMULATION PARAMETERS OF PULMO-TS2ONN
IV. RESULT AND DISCUSSION
In this section, we compare the quantitative and qualitative
performance of the proposed Pulmo-TS2ONN framework with
some of the noteworthy prior works on RS-based seven-class
PD classification.
A. Performance Parameters
To evaluate the performance of the proposed framework,
we have used several standard performance metrics, such as
accuracy (acu) [8], [39] specificity (spc) [39], sensitivity (sns)
or recall (rcl) [8], precision (prc) [39], and F1-score [39]. All
of these metrics can be calculated from the below-mentioned
confusion matrix obtained while testing the framework [40].
Let us consider, the (7 × 7) confusion matrix for seven class
PD classification is given as:


C1,1
C1,2
· · ·
C1,7
C2,1
C2,2
· · ·
C2,7
...
...
...
...
C7,1
C7,2
· · ·
C7,7


where Cm,m corresponds to the correctly categorized sample,
and Cm,n(m̸ = n) refers to the samples that belong to the
mth PD class, however incorrectly classified as nth PD class.
Therefore, the equations of the metrics for the mth PD class
are provided as [40] and [39]: acu(%) = (TPm + TNm/TPm +
TNm+FNm+FPm)×100%, sns/rcl(%) = (TPm/TPm+FNm)×
100%, spc(%) = (TNm/TNm + FPm) × 100%, prc(%) =
(TPm/TPm + FPm) × 100%, and F1 −score(%) = (2 ×
prc × rcl/prc + rcl) × 100%, where TPm, TNm, FPm, and FNm
denote the true positive, true negative, false positive, and false
negative of mth class, respectively and can be obtained as [8]:
TPm = Cm,m, FNm = P7
n=1,n̸=m Cn,m, FPm = P7
n=1,n̸=m Cm,n,
TNm = P7
n=1
P7
k=1 Cn,k −TPm −FPm −FNm.
B. Performance Evaluation
The performance of the proposed Pulmo-TS2ONN is
assessed by training and testing the model using a fivefold
cross-validation approach. Initially, all RSs from the three
different databases were combined and then split into an
80%–20% training and testing set. Additionally, we generate
the validation set using 10% of the data from the training
set. The optimal simulation parameters used to train the
proposed Pulmo-TS2ONN are shown in Table IV, which have
been selected using the GridSearchCV-based hyperparameter
optimization framework [41]. Fig. 6(a) and (b) shows the
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 8

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 8,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_008.png"
}
```

Content:
PAGE 8

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
Fig. 6.
(a) and (b) Loss and accuracy curve of proposed Pulmo-TS2ONN
for seven class PD detection.
Fig. 7.
Fold-wise variation of performance parameters.
TABLE V
CLASS-SPECIFIC
PERFORMANCE
PARAMETERS
OBTAINED
THROUGH
FIVEFOLD CROSS-VALIDATION OF THE PULMO-TS2ONN MODEL
loss and accuracy curves of our proposed Pulmo-TS2ONN
model for both the training and validation phases. It can
be observed from Fig. 6(b), that the Pulmo-TS2ONN model
achieves excellent accuracy without overfitting the model.
To illustrate the supremacy of the proposed Pulmo-TS2ONN
framework, we have also provided the fold-wise classification
results in Fig. 7. It can be seen from the figure, that our model
archives high accuracy rates in each of the folds. The average
acu, spc, sns, and prc achieved by the Pulmo-TS2ONN are
98.88%, 99.84%, 98.27%, and 98.78%, respectively.
To assess the effectiveness of the class-specific classifica-
tion, we also performed a statistical analysis of the class-
wise performance parameter calculation. Table V illustrates
the variation in classification metrics for each of the individual
classes of PDs obtained from the fivefold cross-validation of
the proposed Pulmo-TS2ONN model.
We have also provided the class-wise receiver operator
characteristics (ROC) curve obtained by testing the Pulmo-
TS2ONN model using the test TTFFS, in Fig. 8. It can
be observed that each of the individual ROC curves yields
a high area under the curve (AUC) value. This, in a way,
represents that the proposed Pulmo-TS2ONN model provides
high classification performance for each of the disease classes.
Fig. 8.
ROC curve obtained from the proposed Pulmo-TS2ONN model.
Fig. 9.
Illustrates normalized confusion matrix for seven-class PD classifi-
cation using Pulmo-TS2ONN.
Fig. 10.
Database-wise classification performance using the proposed
Pulmo-TS2ONN framework.
To prove the efficacy of our proposed framework, we have
provided the normalized confusion matrix of the seven-class
PD classification in Fig. 9. From Fig. 9, it is evident that the
misclassification rate for each of the classes is very low.
Further, we have provided the database-wise classifica-
tion performance in Fig. 10 which illustrates that the pro-
posed framework archives decent performance for each of
the databases. From Fig. 10, it can be seen that the Pulmo-
TS2ONN achieves an accuracy of 97.40%, 99.62%, and
99.62% for ICBHI, KAUH, and RD@TR databases.
Additionally, Fig. 11(a) and (b) illustrates the performance
of the proposed framework in terms of efficient class-specific
feature extraction using a 2-D t-distributed stochastic neighbor
embedding (t-SNE) [42] visualization. We have projected both
the raw TTFFS and the SONS-driven concatenated embed-
dings (Econcat) to the 2-D-t-SNE plane in Fig. 11(a) and (b),
respectively. It can be seen that initially, all the raw TTFFS fea-
tures from different disease classes were randomly scattered in
the 2-D t-SNE plane; however, our proposed Pulmo-TS2ONN
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 9

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 9,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_009.png"
}
```

Content:
PAGE 9

SELECTABLE TEXT:
ROY et al.: PULMO-TS2ONN: A NOVEL TRIPLE SCALE SONN FOR PD DETECTION USING RSs
6502812
Fig. 11.
2-D-tSNE feature plot of (a) Raw TTFFS and (b) SONS-driven
concatenated embeddings (Econcat).
TABLE VI
QUANTITATIVE PERFORMANCE COMPARISON OF THE PROPOSED
PULMO-TS2ONN WITH OTHER BAS
is able to extract distinct feature representation from each
class, and as a result, it aids in the formation of distinct clusters
in the 2-D t-SNE plane.
C. Ablation Study of Different Impacting Design Parameters
This section includes the impact of various design parameter
choices that affect the overall classification performance of the
Pulmo-TS2ONN framework.
1) Selection of Optimal Number of SONS Blocks and TFRs:
The SONS blocks that extract compact feature representations
from the TTFFS, are one of the key backbone DL blocks of our
proposed Pulmo-TS2ONN architecture. In this article, we have
utilized three TFRs in conjunction with three SONS blocks
to construct the TS2ONN architecture. However, finding an
optimal number of SONS blocks and the optimal choice of
TFR becomes an essential factor. To study the aforementioned
aspects, we created six baseline architecture (BA) designs,
three (BA 1, 2, 3) of which employ a single TFR and a
single SONS, while the other three (BA 4, 5, 6) use two
TFRs and two SONSs. To ensure a fair comparison, we kept
the architectural specifications of the SONS same across all
BAs and used a fivefold cross-validation-based training-testing
strategy to compare their performance with our proposed
Pulmo-TS2ONN in Table VI. Table VI demonstrates that using
TTFFs with three SONS block-based Pumo-TS2ONN archi-
tecture yields the highest classification rates compared to other
BA architectures that use either a single TFR or a combination
of two TFRs. Additionally, to illustrate the efficacy of the
Pulmo-TS2ONN, a 2-D-tSNE feature visualization for each
of the BAs has been shown in Fig. 12(a)–(f), respectively.
As we compare the t-SNE feature visualization performance
of Pulmo-TS2ONN shown in Fig. 11(b) with the other t-SNEs
Fig. 12.
2-D t-SNE visualization of features extracted from (a) BA 1,
(b) BA 2, (c) BA 3, (d) BA 4, (e) BA 5, and (f) BA 6, respectively.
Fig. 13.
Effect of processing length of input RS on overall classification
performance of the Pulmo-TSONN framework.
of the BAs shown in Fig. 12(a)–(f), it is evident that Pulmo-
TS2ONN outperforms the BAs in terms of the creation of
class-specific clusters.
2) Selection of Optimal RS Processing Length: Due to the
presence of nonstationary spectral components in RSs, many
researchers focus on employing TFRs for RS classification.
However, as the RS features appear in the RS time series
sequentially, it is crucial to ascertain how the processing length
affects classification performance. To illustrate the effect of
processing length on the classification performance we have
provided a comparative study in Fig. 13(a). We have uniformly
varied the processing length from 5 to 15 s and noted the
classification metrics in each case. From Fig. 13, it can be seen
that with 5 s processing length, the proposed Pulmo-TS2ONN
yields the highest accuracy, however, with the increase in the
processing length, the performance of the Pulmo-TS2ONN
deteriorates drastically.
D. Performance Evaluation on Real-Time Data
In this section, we examine the performance of the pro-
posed framework on real-time RS data collected from the
subjects affected with PD, admitted to the pulmonary medicine
department of All India Institute of Medical Sciences Patna.
Due to the limited availability of patients, we have acquired
RSs of 20 s length from two COPD (annotated with PID-01,
and 02), and two asthmatic patients (PID-03, and 04) using
Littmann 3200 digital stethoscope and transferred the signals
to a laptop over Bluetooth using the Littmann1 StethAssist2
1Registered trademark.
2Trademarked.
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 10

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 10,
  "content_type": "page_text_plus_ocr",
  "image_count": 2,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_010.png"
}
```

Content:
PAGE 10

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
Fig. 14.
Illustrates (a) experimental set-up of the RS data acquisi-
tion, (b) acquisition sites, and (c) visualization of RS data collected from
PID-01, 03.
TABLE VII
CLASSIFICATION PERFORMANCE ON REAL-TIME ACQUIRED RS DATA
software. Additionally, we have collected RS signals from
six healthy subjects (PID-05 to PID-10). Fig. 14(a) illustrates
the experimental setup, Fig. 14(b) depicts the different RS
acquisition sites, and Fig. 14(c) shows the visualization of
RS data collected from PID-01 and PID-03, respectively. The
classification performance of the proposed Pulmo-TS2ONN
on the real-time recorded RS data is tabulated in Table VII.
E. On-Board Implementation of Pulmo-TS2ONN
The implementation of this PD classification algorithm on a
low-resource embedded processor not only opens up possibil-
ities for Internet of Medical Things (IoMT) applications [43],
but it also enables the direction of developing personalized
respiratory health monitoring systems [44]. However, the large
parameter size and high computational complexity hinder the
deployability of these DL-based frameworks on a low-resource
microcontroller [44]. In this article, the proposed Pulmo-
TS2ONN framework has been successfully implemented on
an ARM-A7 quad-core Broadcom BCM2711 microcontroller,
popularly known as the Raspberry Pi-4, which runs at 1.5 GHz
clock and comprises 4 GB of RAM. Fig. 15(a) illustrates the
experimental setup of the microcontroller, and Fig. 15(b)–(d)
shows the sample classification results of Pulmo-TS2ONN.
The end-to-end PD classification pipeline was first trained
on the Google Colab Pro+ platform and then subsequently,
the model weights were transferred to the microcontroller.
In addition to that, necessary libraries such as numpy, librosa,
Fig. 15.
(a) On-board implementation setup of Pulmo-TS2ONN using
Raspberry Pi-4 microcontroller and (b)–(d) illustrates the sample classification
results.
TABLE VIII
COMPARATIVE RESULTS OF THE PROPOSED PULMO-TS2ONN MODEL
WITH FINE-TUNED DEEP TRANSFER LEARNING MODELS
torch, etc., were also installed in the microcontroller to run
the developed Pulmo-TS2ONN algorithm. Upon experimen-
tation, it has been seen that the Pulmo-TS2ONN requires a
latency of 3.48 ± 0.27 s and a peak memory requirement of
15.2924 ± 0.0018 MB to categorize one RS segment. This
indicates that the proposed framework can be translated into
a real-life clinical scenario for PD screening using the RS
measurements.
F. Performance Comparison
1) Comparison With SOTA Fine-Tuned Transfer Learning
DL Frameworks: We have compared our proposed framework
with the existing transfer learning-based DL models such as
ResNet-50, MobileNet, and ShuffleNetV2, which have been
re-trained using the fine-tuning mechanism to classify seven
PD categories. Table VIII depicts the comparative study of
the proposed Pulmo-TS2ONN model with different fine-tuned
transfer learning models in terms of several model assessment
metrics. From Table VIII, it is evident that our SONS-driven
Pulmo-TS2ONN model outperforms each of the fine-tuned
transfer learning models by achieving the highest classification
rates. Therefore, it can also be argued that the use of enhanced
nonlinear GOPM helps to attain such higher classification
performance than the existing CNN models, where the primary
neural backbone is the linear perceptron model. Additionally,
Table VIII also illustrates that the parameter size and the total
number of floating point operations required (FLOPs) for the
proposed Pulmo-TS2ONN model are 0.414 million (M) and
0.0055 gillion (G) only, which are significantly less than any
of the fine-tuned transfer learning models.
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 11

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 11,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_011.png"
}
```

Content:
PAGE 11

SELECTABLE TEXT:
ROY et al.: PULMO-TS2ONN: A NOVEL TRIPLE SCALE SONN FOR PD DETECTION USING RSs
6502812
TABLE IX
PERFORMANCE COMPARISON OF PROPOSED PULMO-TS2ONN WITH EXISTING SOTA TECHNIQUES ON RS-BASED PD CLASSIFICATION
2) Comparison With SOTA Techniques on RS-Based PD
Classification: In this section, we compare our proposed
Pulmo-TS2ONN framework with some noteworthy prior
works on RS-based PD classification. Table IX illustrates
the comparative performance of the Pulmo-TS2ONN with
other existing works on RS-based disease detection using
different publicly available databases [9], [10], [12]. Most of
the works have considered a single database for multiclass
PD classification (either four-class or six-class). In the case of
ICBHI database, Basu and Rana [19], and Shuvo et al. [16]
achieved decent accuracy on six-class disease classification;
however, Shi et al. [17] achieved 91.56% accuracy when
the RS data of ICBHI and RespiratoryDatabase@TR was
combined for four-class classification. While performing the
same four-class classification with KAUH database, Tripa-
thy et al. [21] achieved an inferior accuracy rate. Roy and
Satija et al. [8] only performed seven-class classification
by employing all three databases. However, it is evident
from Table IX that the proposed Pulmo-TS2ONN framework
surpasses all the existing SOTA techniques on RS-based
seven-class PD detection by achieving the highest accuracy
of 98.88%.
G. Performance Comparison of on-Device Implementation
To illustrate the efficacy of the proposed framework in terms
of deployability on low-compute hardware, we have imple-
mented different DL-based PD classification pipelines, such
as LCNN [16], RDLINet [8], etc., for seven-class PD classifi-
cation task and implemented on Raspberry pi-4. We have mea-
sured the peak memory usage and latency to classify one RS
segment and presented the same in Table X. We can see that
both latency and peak memory usage for LCNN [16] are high,
as the iterative-EMD-based scalogram generation process is
time-consuming. Additionally, we can observe that our Pulmo-
TS2ONN requires slightly higher memory and latency than our
previously published RDLINet [8]. This behavior is obvious
as Pulmo-TS2ONN requires a total of three TFR extraction
and the model parameter size is higher than RDLINet [8].
In contrast to RDLINet, the Pulmo-TS2ONN demonstrates a
TABLE X
PERFORMANCE
COMPARISON
OF
THE
PROPOSED
PULMO-TS2ONN
FRAMEWORK WITH EXISTING WORKS BASED ON THE PARAMETERS
OBTAINED AFTER ON-DEVICE IMPLEMENTATION
notable enhancement in overall accuracy (with a 2.28%) as
well as class-wise PD classification accuracy, which specif-
ically adds a substantial clinical value to enhance diagnosis
and enable accurate medication recommendations [22]. Thus,
despite the trade-offs of somewhat longer processing time
and peak memory utilization compared to RDLINet, the
cumulative therapeutic advantages considerably surpass these
concerns.
V. CONCLUSION
In this article, we investigate the potential of the TS2ONN
architecture in conjunction with the fusion of the triple TFR-
based TTFFS extracted from RSs. By utilizing our proposed
Pulmo-TS2ONN framework, we surpassed the SOTA algo-
rithms for RS-based seven-class PD detection utilizing three
publicly accessible databases, achieving the highest accuracy
of 98.88%. The suggested framework also demonstrates the
advantages of TS2ONN architecture over vanilla pretrained
CNNs that employ basic linear perceptron design by attaining
higher classification rates with fewer parameters. Our future
research will focus on the impact of different factors, such as
the presence of heart sound interference and ambient noise in
RS, that may have a detrimental effect on PD classification
and how to suppress these noise elements to obtain better
outcomes. Furthermore, the successful deployment of the pro-
posed Pulmo-TS2ONN on a Raspberry Pi-4 microcontroller
shows the possibility of developing an on-device point-of-care
system for diagnosing and screening various PDs in real-world
clinical situations based on RSs.
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 12

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 12,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\page_images\\page_012.png"
}
```

Content:
PAGE 12

SELECTABLE TEXT:
6502812
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 73, 2024
REFERENCES
[1] S. M. Levine and D. D. Marciniuk, “Global impact of respiratory
disease: What can we do, together, to make a difference?” Chest,
vol. 161, no. 5, pp. 1153–1154, 2022.
[2] J. L. Schneider, J. H. Rowe, C. Garcia-de-Alba, C. F. Kim, A. H. Sharpe,
and M. C. Haigis, “The aging lung: Physiology, disease, and immunity,”
Cell, vol. 184, no. 8, pp. 1990–2019, Apr. 2021.
[3] A. A. Cruz, Global Surveillance, Prevention and Control of Chronic Res-
piratory Diseases: A Comprehensive Approach. Geneva, Switzerland:
World Health Organization, 2007.
[4] S. Trivedy, M. Goyal, P. R. Mohapatra, and A. Mukherjee, “Design
and development of smartphone-enabled spirometer with a disease
classification system using convolutional neural network,” IEEE Trans.
Instrum. Meas., vol. 69, no. 9, pp. 7125–7135, Sep. 2020.
[5] A. B. Bhome, “COPD in India: Iceberg or volcano?” J. Thoracic
Disease, vol. 4, no. 3, p. 298, 2012.
[6] B. Roy, A. Roy, J. K. Chandra, and R. Gupta, “I-PRExT: Photoplethys-
mography derived respiration signal extraction and respiratory rate
tracking using neural networks,” IEEE Trans. Instrum. Meas., vol. 70,
pp. 1–9, 2021.
[7] National Institutes of Health, National Asthma Education and Prevention
Program, Expert Panel Report III: Guidelines for the Diagnosis and
Management of Asthma, Bethesda, MD, USA, 1997.
[8] A. Roy and U. Satija, “RDLINet: A novel lightweight inception network
for respiratory disease classification using lung sounds,” IEEE Trans.
Instrum. Meas., vol. 72, pp. 1–13, 2023.
[9] B. Rocha et al., “A respiratory sound database for the development of
automated classification,” in Proc. Int. Conf. Biomed. Health Informat.
Singapore: Springer, 2017, pp. 33–37.
[10] M. Fraiwan, L. Fraiwan, B. Khassawneh, and A. Ibnian, “A dataset
of lung sounds recorded from the chest wall using an electronic
stethoscope,” Data Brief, vol. 35, Apr. 2021, Art. no. 106913.
[11] L. Pham, H. Phan, R. Palaniappan, A. Mertins, and I. McLoughlin,
“CNN-MoE based framework for classification of respiratory anomalies
and lung disease detection,” IEEE J. Biomed. Health Informat., vol. 25,
no. 8, pp. 2938–2947, Aug. 2021.
[12] G. Altan, Y. Kutlu, Y. Garbi, A. Ö. Pekmezci, and S. Nural, “Multimedia
respiratory database (RespiratoryDatabase@TR): Auscultation sounds
and chest X-rays,” Natural Eng. Sci., vol. 2, no. 3, pp. 59–72, Oct. 2017.
[13] L. Silva et al., “COVID-19 respiratory sound analysis and classification
using audio textures,” Frontiers Signal Process., vol. 2, Oct. 2022,
Art. no. 986293.
[14] J. Acharya and A. Basu, “Deep neural network for respiratory sound
classification in wearable devices enabled by patient specific model
tuning,” IEEE Trans. Biomed. Circuits Syst., vol. 14, no. 3, pp. 535–544,
Jun. 2020.
[15] T. Nguyen and F. Pernkopf, “Lung sound classification using co-tuning
and stochastic normalization,” IEEE Trans. Biomed. Eng., vol. 69, no. 9,
pp. 2872–2882, Sep. 2022.
[16] S. B. Shuvo, S. N. Ali, S. I. Swapnil, T. Hasan, and M. I. H. Bhuiyan,
“A lightweight CNN model for detecting respiratory diseases from lung
auscultation sounds using EMD-CWT-based hybrid scalogram,” IEEE J.
Biomed. Health Informat., vol. 25, no. 7, pp. 2595–2603, Jul. 2021.
[17] L. Shi, J. Zhang, B. Yang, and Y. Gao, “Lung sound recognition method
based on multi-resolution interleaved net and time-frequency feature
enhancement,” IEEE J. Biomed. Health Informat., vol. 27, no. 10,
pp. 4768–4779, Oct. 2023.
[18] D. Perna, “Convolutional neural networks learning from respiratory
data,” in Proc. IEEE Int. Conf. Bioinf. Biomed. (BIBM), Dec. 2018,
pp. 2109–2113.
[19] V. Basu and S. Rana, “Respiratory diseases recognition through respi-
ratory sound with the help of deep neural network,” in Proc. 4th Int.
Conf. Comput. Intell. Netw. (CINE), Feb. 2020, pp. 1–6.
[20] M. T. García-Ordás, J. A. Benítez-Andrades, I. García-Rodríguez,
C. Benavides, and H. Alaiz-Moretón, “Detecting respiratory pathologies
using convolutional neural networks and variational autoencoders for
unbalancing data,” Sensors, vol. 20, no. 4, p. 1214, Feb. 2020.
[21] R. K. Tripathy, S. Dash, A. Rath, G. Panda, and R. B. Pachori,
“Automated detection of pulmonary diseases from lung sound signals
using fixed-boundary-based empirical wavelet transform,” IEEE Sensors
Lett., vol. 6, no. 5, pp. 1–4, May 2022.
[22] A. Mondal, P. Bhattacharya, and G. Saha, “Detection of lungs status
using morphological complexities of respiratory sounds,” Sci. World J.,
vol. 2014, pp. 1–9, Mar. 2014.
[23] A. Roy and U. Satija, “AsTFSONN: A unified framework based on
time-frequency domain self-operational neural network for asthmatic
lung sound classification,” in Proc. IEEE Int. Symp. Med. Meas. Appl.
(MeMeA), Jun. 2023, pp. 1–6.
[24] M. U. Zahid, S. Kiranyaz, and M. Gabbouj, “Global ECG clas-
sification by self-operational neural networks with feature injec-
tion,” IEEE Trans. Biomed. Eng., vol. 70, no. 1, pp. 205–215,
Jan. 2023.
[25] M. Sarkar, I. Madabhavi, N. Niranjan, and M. Dogra, “Auscultation
of the respiratory system,” Ann. Thoracic Med., vol. 10, no. 3, p. 158,
2015.
[26] S. A. H. Tabatabaei, P. Fischer, H. Schneider, U. Koehler, V. Gross,
and K. Sohrabi, “Methods for adventitious respiratory sound analyzing
applications based on smartphones: A survey,” IEEE Rev. Biomed. Eng.,
vol. 14, pp. 98–115, 2021.
[27] S. Reichert, R. Gass, C. Brandt, and E. Andrès, “Analysis of respiratory
sounds: State of the art,” Clin. Med. Circulatory, Respiratory Pulmonary
Med., vol. 2, Jan. 2008, Art. no. CCRPM.S530.
[28] S. A. F. Jaffery, S. Aziz, M. U. Khan, S. Z. H. Naqvi, M. Faraz, and
A. Usman, “An automated system for the classification of bronchiolitis
and bronchiectasis diseases using lung sound analysis,” in Proc. Int.
Conf. Robot. Autom. Ind. (ICRAI), Mar. 2023, pp. 1–6.
[29] U. Satija, B. Ramkumar, and M. S. Manikandan, “Real-time signal
quality-aware ECG telemetry system for IoT-based health care moni-
toring,” IEEE Internet Things J., vol. 4, no. 3, pp. 815–823, Jun. 2017.
[30] B. Bahmei, E. Birmingham, and S. Arzanpour, “CNN-RNN and data
augmentation using deep convolutional generative adversarial network
for environmental sound classification,” IEEE Signal Process. Lett.,
vol. 29, pp. 682–686, 2022.
[31] I. Ozer, “Pseudo-colored rate map representation for speech emotion
recognition,” Biomed. Signal Process. Control, vol. 66, Apr. 2021,
Art. no. 102502.
[32] J. C. Brown, “Calculation of a constant Q spectral transform,” J. Acoust.
Soc. Amer., vol. 89, no. 1, pp. 425–434, Jan. 1991.
[33] B. Gfeller, C. Frank, D. Roblek, M. Sharifi, M. Tagliasacchi, and
M. Velimirovic, “SPICE: Self-supervised pitch estimation,” IEEE/ACM
Trans. Audio, Speech, Language Process., vol. 28, pp. 1118–1128, 2020.
[34] Z.
K.
Abdul
and
A.
K.
Al-Talabani,
“Mel
frequency
cepstral
coefficient and its applications: A review,” IEEE Access, vol. 10,
pp. 122136–122158, 2022.
[35] S. Kiranyaz, T. Ince, A. Iosifidis, and M. Gabbouj, “Operational neural
networks,” Neural Comput. Appl., vol. 32, no. 11, pp. 6645–6668,
Jun. 2020.
[36] S. Kiranyaz, J. Malik, H. B. Abdallah, T. Ince, A. Iosifidis, and
M. Gabbouj, “Self-organized operational neural networks with gener-
ative neurons,” Neural Netw., vol. 140, pp. 294–308, Aug. 2021.
[37] M.
Lin,
Q.
Chen,
and
S.
Yan,
“Network
in
network,”
2013,
arXiv:1312.4400.
[38] D. Hendrycks and K. Gimpel, “Gaussian error linear units (GELUs),”
2016, arXiv:1606.08415.
[39] S. Das, D. Jyotishi, and S. Dandapat, “Automated detection of heart
valve diseases using stationary wavelet transform and attention-based
hierarchical LSTM network,” IEEE Trans. Instrum. Meas., vol. 72,
pp. 1–10, 2023.
[40] T. Kautz, B. M. Eskofier, and C. F. Pasluosta, “Generic perfor-
mance measure for multiclass-classifiers,” Pattern Recognit., vol. 68,
pp. 111–125, Aug. 2017.
[41] M. Saini, U. Satija, and M. D. Upadhayay, “DSCNN-CAU: Deep-
learning-based mental activity classification for IoT implementation
toward portable BCI,” IEEE Internet Things J., vol. 10, no. 10,
pp. 8944–8957, May 2023.
[42] L. Van der Maaten and G. Hinton, “Visualizing data using t-SNE,”
J. Mach. Learn. Res., vol. 9, no. 11, pp. 1–27, 2008.
[43] M. Saini, D. Kumar, and U. Satija, “Edge of medical things implemen-
tation for deep learning-based cognitive task recognition,” IEEE Internet
Things Mag., vol. 5, no. 3, pp. 56–60, Sep. 2022.
[44] D. Pal, S. Mukhopadhyay, and R. Gupta, “Two-stage classifier for
resource constrained on-board cardiac arrhythmia detection,” IEEE
Trans. Instrum. Meas., vol. 72, pp. 1–10, 2023.
Authorized licensed use limited to: Indian Institute of Information Tech - Bhagalpur. Downloaded on September 08,2025 at 14:07:23 UTC from IEEE Xplore.  Restrictions apply.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 13

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 4,
  "content_type": "table",
  "table_index": 1
}
```

Content:
TABLE FOUND ON PAGE 4
TABLE INDEX: 1

TABLE MARKDOWN:
|    |    |    |    |
|:---|:---|:---|:---|
|    |    |    |    |

---


# Document 14

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 7,
  "content_type": "table",
  "table_index": 1
}
```

Content:
TABLE FOUND ON PAGE 7
TABLE INDEX: 1

TABLE MARKDOWN:
|    |    |    |    |
|----|----|----|----|

---


# Document 15

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 8,
  "content_type": "table",
  "table_index": 1
}
```

Content:
TABLE FOUND ON PAGE 8
TABLE INDEX: 1

TABLE MARKDOWN:
|    |    |
|:---|:---|
|    |    |
|    |    |
|    |    |

---


# Document 16

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 8,
  "content_type": "table",
  "table_index": 2
}
```

Content:
TABLE FOUND ON PAGE 8
TABLE INDEX: 2

TABLE MARKDOWN:
|    |    |    |
|----|----|----|

---


# Document 17

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 9,
  "content_type": "table",
  "table_index": 1
}
```

Content:
TABLE FOUND ON PAGE 9
TABLE INDEX: 1

TABLE MARKDOWN:
|    |    |    |    |
|----|----|----|----|

---


# Document 18

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 10,
  "content_type": "table",
  "table_index": 1
}
```

Content:
TABLE FOUND ON PAGE 10
TABLE INDEX: 1

TABLE MARKDOWN:
|    |    |    |    |
|----|----|----|----|

---


# Document 19

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 3,
  "content_type": "image",
  "image_index": 1,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_003_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 3
IMAGE INDEX: 1
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_003_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 20

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 5,
  "content_type": "image",
  "image_index": 1,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_005_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 5
IMAGE INDEX: 1
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_005_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 21

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 5,
  "content_type": "image",
  "image_index": 2,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_005_image_2.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 5
IMAGE INDEX: 2
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_005_image_2.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 22

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 5,
  "content_type": "image",
  "image_index": 3,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_005_image_3.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 5
IMAGE INDEX: 3
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_005_image_3.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 23

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 6,
  "content_type": "image",
  "image_index": 1,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_006_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 6
IMAGE INDEX: 1
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_006_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 24

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 8,
  "content_type": "image",
  "image_index": 1,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_008_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 8
IMAGE INDEX: 1
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_008_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 25

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 10,
  "content_type": "image",
  "image_index": 1,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_010_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 10
IMAGE INDEX: 1
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_010_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 26

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds.pdf",
  "page_number": 10,
  "content_type": "image",
  "image_index": 2,
  "image_path": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\parsed_pdf_output\\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\\extracted_images\\page_010_image_2.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 10
IMAGE INDEX: 2
IMAGE PATH: D:\mm-rag-full-stack-genai-bootcamp-1.0-master\mm-rag-full-stack-genai-bootcamp-1.0-master\data\parsed_pdf_output\Pulmo-TS2ONN_A_Novel_Triple_Scale_Self_Operational_Neural_Network_for_Pulmonary_Disorder_Detection_Using_Respiratory_Sounds\extracted_images\page_010_image_2.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---
