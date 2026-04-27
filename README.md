# SINTEF Deep Tech & Skill Radar

A collaborative team skill-mapping tool for SINTEF researchers. Each team member rates their interest and expertise across 30 deep-tech areas. Results are visualised as a shared radar chart and used to surface collaboration opportunities.

## Features

- **Submit / Update Profile** — rate 30 deep-tech areas (interest + expertise 0–5); one entry per person, updates in place
- **Team Radar** — interactive Plotly radar chart showing team averages; filters by individual members
- **Find Collaborators** — search profiles by tech area with a minimum score threshold
- **All Submissions** — browse, download CSV, or admin-wipe the dataset

## Tech stack

| Layer | Tech |
|---|---|
| UI | Gradio 6 |
| Storage | HuggingFace Datasets (private repo) |
| Charts | Plotly |
| Deploy | HuggingFace Spaces or local |

## Local setup

```bash
# copy and fill in credentials
cp .env.example .env

# install and run (requires uv)
uv run app.py
# opens at http://localhost:7861
```

## Environment variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | HuggingFace write token |
| `HF_USERNAME` | HuggingFace username |
| `DATASET_NAME` | Dataset repo name (default: `deep-tech-radar`) |

## Deep tech areas covered

AI/ML, IoT, Cybersecurity, Privacy Engineering, Green Computing, Digital Twins, Software Engineering, Cloud & Distributed Systems, Self-Adaptive Systems, Software Quality, Quantum Computing, Blockchain, Robotics, 5G, AR/VR, Bioinformatics, HPC, Formal Methods, HCI, NLP, Computer Vision, Federated Learning, XAI, MLOps, Smart Grid, Data Governance, Hardware Security, Post-Quantum Cryptography, Model-Driven Engineering, DevSecOps.
