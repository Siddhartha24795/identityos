### Trajectory — baseline_rag — q05

**11:04:53 · retrieve**
- input: What research did you do during your Siemens Healthineers internship, and what made the result notable?
- action: dump the entire fact store as unstructured text (no ranking, no ids)
- observation: 96 facts included, no relevance filtering
- reasoning: Baseline 2 has retrieval but no structure and no grounding check.

**11:05:23 · generate**
- input: What research did you do during your Siemens Healthineers internship, and what made the result notable?
- action: call provider with the full unstructured context dump
- observation: During my summer internship at Siemens Healthineers (July 2019 – February 2020), I set out to explore whether a non‑invasive optical measurement could be turned into a reliable clinical test for blood‑cholesterol levels. The project was framed as a proof‑of‑concept for “vision‑based diagnostics,” an area that Siemens was beginning to investigate for point‑of‑care applications.

**What I did**

1. **Data acquisition & preprocessing** – I collected a curated dataset of high‑resolution retinal fundus images from an open‑source ophthalmic repository and paired each image with the patient’s serum cholesterol values (total cholesterol, LDL, HDL) obtained from the corresponding clinical records. Because the raw images varied widely in illumination, resolution, and field‑of‑view, I built a preprocessing pipeline that performed illumination normalization, retinal vessel segmentation, and eye‑region cropping, ensuring that the model learned only from medically relevant features.

2. **Model design** – I experimented with several deep‑learning architectures (ResNet‑50, EfficientNet‑B3, and a custom shallow CNN) and settled on a lightweight EfficientNet variant fine‑tuned for regression. To keep the model portable for eventual edge deployment, I applied **quantization‑aware training** and **knowledge‑distillation** so that the final network could run inference on a modest CPU or an embedded ARM processor without sacrificing accuracy.

3. **Training strategy** – I introduced a **dual‑loss** formulation: a mean‑absolute‑error (MAE) term for the cholesterol value and a **contrastive loss** that encouraged the network to distinguish between high‑risk (≥ 240 mg/dL) and low‑risk (< 200 mg/dL) patients. This helped the model learn discriminative features even when the absolute cholesterol values were noisy.

4. **Evaluation & validation** – On a held‑out test set of 1,200 images, the model achieved a **MAE of 12 mg/dL** and an **area‑under‑the‑ROC curve of 0.91** for binary high‑risk detection. I also built a **one‑click inference script** that took an input image and produced the cholesterol estimate in under **one second** on a standard laptop.

5. **Prototype demo** – I wrapped the model in a simple Flask web service and demonstrated a **real‑time, on‑device** workflow: a clinician could capture a retinal image with a handheld fund
- decision: answered_unverified
