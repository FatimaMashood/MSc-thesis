# Physiological Synchrony and Collaboration: An Empirical Inquiry Using the Overcooked Game

**MSc Media Technology Thesis** — Leiden University (LIACS), October 2024

**Author:** Fatima Mashood  
**Supervisors:** Maarten Lamers & Max van Duijn (LIACS, Leiden University)

---

## Abstract

This research examines the relationship between physiological synchrony (PS) and collaboration within dyads engaged in *Overcooked* — a virtual kitchen simulation game. 14 participants were paired to form 7 dyads based on familiarity. PS was assessed by analysing participants' heart rate data, while the dyad's game score assessed collaboration during gameplay. Findings presented a weak yet positive relationship between PS and collaboration, while statistically insignificant. Additionally, familiarity between participants did not significantly affect PS or collaboration. These findings contribute to understanding PS and collaboration in virtual gaming environments while highlighting the influence of familiarity on such research.

**Keywords:** physiological synchrony · collaboration · overcooked · heart rate · dyadic interaction

---

## Research Questions

**Primary:** Does physiological synchrony, measured by heart rate alignment, correlate with collaboration within dyads in a virtual gameplay environment?

**Secondary:** Does familiarity between dyad members influence physiological synchrony and collaboration?

---

## Methodology

| Aspect | Detail |
|---|---|
| **Design** | Quasi-experimental |
| **Participants** | 14 participants → 7 dyads (3 familiar, 4 unfamiliar) |
| **Task** | 6 × 60-second game orders in Overcooked (cooperative kitchen game) |
| **Physiological Measure** | PPG finger sensors (Arduino) → IBI & BPM from 2 participants simultaneously |
| **Collaboration Measure** | Game score (dishes served per game order) |
| **PS Metric** | Maximum cross-correlation of IBI time series between dyad members |
| **Statistics** | Pearson's r, independent t-test, ANOVA, Shapiro-Wilk — performed in JASP |
| **Survey** | Post-experiment questionnaire via Qualtrics (demographics & familiarity) |

---

## Key Findings

- **PS vs. Collaboration:** Weak positive but non-significant correlation (r = 0.145, p = 0.361)
- **Familiarity:** No significant effect on PS (p = 0.582) or game score (p = 0.624)
- **Dyad Gender on PS:** Statistically significant effect (F = 6.892, p = 0.003) — same-gender dyads showed higher PS (Cohen's d = 1.034)
- **Dyad Gender on Collaboration:** No significant effect on game score (p = 0.266)

---

## Repository Contents

```
MSc thesis/
│
├── Masters_Thesis_Fatima_Mashood.pdf     # Full written thesis
├── Thesis_defence_presentation.pdf       # Defence presentation slides
└── Thesis_code.zip                       # All experiment & analysis code (see below)
```

### Code Structure (`Thesis_code.zip`)

```
Thesis_code/
│
├── sensor_read.py                        # Flask server reading Arduino PPG data via serial port
├── data_load.py                          # Data loading, IBI preprocessing & bandpass filtering
├── final_code.ipynb                      # Main analysis: cross-correlation, Pearson's r, plots
├── final_plots.ipynb                     # All result visualisation figures
├── qualtrics_processed.csv               # Processed questionnaire data (demographics, familiarity)
├── requirements.txt                      # Python dependencies
│
├── data/
│   └── Trial 01/ … Trial 07/            # Raw JSON pulse data (42 data points: 7 trials × 6 orders)
│       └── level-{N}@pulse_data.json    # BPM, IBI, signal for 2 sensors + game score
│
├── Jasp_code/
│   ├── Jasp_main_dataframe.jasp         # JASP: correlations, t-tests, ANOVA
│   └── Jasp_participant_info.jasp       # JASP: participant demographic analysis
│
├── overcooked-demo/                     # Modified Overcooked web app (forked from HumanCompatibleAI)
│   ├── docker-compose.yml
│   ├── server/app.py                    # Flask game server
│   └── server/game.py                  # Game logic
│
└── PulseSensorAmped_2_Sensors/          # Arduino & Processing code for dual PPG sensors
    ├── PulseSensorAmped_2_Sensors.ino   # Arduino sketch (dual sensor IBI/BPM output)
    └── PulseSensorAmpd_Processing_2_Sensors.pde  # Processing visualisation
```

---

## Tech Stack

| Category | Tools / Libraries |
|---|---|
| **Languages** | Python, Arduino (C++), Processing, JavaScript, Java |
| **Python Libraries** | `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `neurokit2`, `pandas`, `flask`, `pyserial` |
| **Statistical Analysis** | JASP |
| **Hardware** | Arduino + PulseSensor PPG sensors (dual-channel, 100 Hz) |
| **Game Platform** | Overcooked (Dockerised web app) |
| **Containerisation** | Docker / Docker Compose |
| **Notebooks** | Jupyter |

---

## Setup & Running the Experiment

### 1. Python environment

```bash
pip install -r requirements.txt
```

### 2. Start the Overcooked game (Docker)

```bash
cd overcooked-demo
./up.sh        # or: docker-compose up
```

Player 1 and Player 2 connect to the game server on the same network via their respective URLs.

### 3. Start the sensor server

Connect both PPG Arduino sensors, then:

```bash
python sensor_read.py
```

The server runs on `localhost:5050` and logs JSON pulse data per trial/level, triggered by the game UI.

### 4. Analysis

Open `final_code.ipynb` in Jupyter to reproduce the cross-correlation analysis and statistical results.  
Open `final_plots.ipynb` to regenerate all figures.

---

## References

- Makowski, D., et al. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods*, 53, 1689–1696.
- Overcooked base code: [HumanCompatibleAI/overcooked-demo](https://github.com/HumanCompatibleAI/overcooked-demo)

---

## License

This repository contains academic thesis work. Please cite appropriately if referencing this research.
