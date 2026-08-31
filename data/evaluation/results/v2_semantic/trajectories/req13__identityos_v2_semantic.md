### Trajectory — identityos_v2_semantic — req13

**09:52:43 · retrieve**
- input: Languages — English, Hindi, Kannada preferred
- action: embedding-similarity retrieval (fastembed): top 8 facts, 0 beliefs
- observation: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.
[resume:044] (verified fact) Augmented Reality, ARCore, Large Language Models, VLMs, RAG, MCP, LangChain.
[resume:024] (verified fact) Software Engineer, Amdocs, Pune India, Aug 2020 - Feb 2021, on Billing and RTB teams.
[resume:031] (verified fact) Instructor, Digiimento Education Pvt. Ltd, Delhi India, Dec 2017 - June 2018.
[resume:043] (verified fact) Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing.
[resume:037] (verified fact) Intern, IIT BHU, Varanasi India, June 2015 - July 2015.
[resume:050] (verified fact) 2nd Prize, Japan Hackathon 2021, representing India.
[resume:045] (verified fact) Python, NumPy, Pandas, Matplotlib, SQL, Android, Java, C++, C, Git, Perforce.

**09:52:43 · generate**
- input: Languages — English, Hindi, Kannada preferred
- action: call provider with cited, confidence-annotated context
- observation: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.

**09:52:43 · verify**
- input: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.
- action: per-sentence grounding check (same verifier as lexical identityos_v2)
- observation: coverage=1.00 confidence=0.99
- confidence: 0.99

**09:52:43 · bucket**
- input: [dossier_excerpts:007] (verified fact) Siddhartha's own dossier states he is fluent in English and Hindi but not yet fluent in Kannada.
- action: derive fit bucket from coverage+confidence+polarity (same bucketing.py as lexical)
- observation: partial
- decision: partial
