<!--
SOURCE: Siddhartha_IIT_CTO_JinnLabs.pdf (Siddhartha Mishra's own resume)
Transcribed for IdentityOS v1 ingestion. Each bullet under a "## CATEGORY"
header becomes one Fact, with this file + line context as provenance.
Used with the data owner's consent (Siddhartha is both the user and subject).
-->

## EMPLOYMENT
Chief Technical Officer, Jinn Labs, Remote India, Nov 2025 - Present.
Owns end-to-end AI feature development from multi-camera ingestion to real-time inference for live retail-intelligence products.
Architected a real-time CV platform processing 2000+ RTSP streams in parallel across heterogeneous cameras, codecs, and video formats.
Built a fault-tolerant FFmpeg ingestion layer handling transcoding, frame extraction, reconnection, and backpressure under sustained load.
Built VLM-based suspicious-event detection over live video, flagging theft, loitering, and anomalous behavior in real time with temporal context across frames.
Adapted VLMs/LLMs efficiently using LoRA, QLoRA, and soft-prompting to specialize models per use case at a fraction of full fine-tuning cost.
Defined evaluation frameworks pairing offline metrics with live ground-truth validation, POS-occupancy eval at approximately 87% accuracy, tracked release over release.
Drove inference optimization via quantization, pruning, distillation, mixed precision, ONNX/TensorRT, and batching to cut GPU cost while holding accuracy.
Deployed the same workloads on the edge (NVIDIA Jetson Nano and AGX Orin) and cloud, owning the edge-vs-cloud partitioning strategy.
Leads a 35+ member cross-functional team (CV/ML research, edge and cloud infra, backend, frontend) as Head of Engineering and Innovation, owning hiring, roadmap, architecture review, and delivery.
Staff Computer Vision Researcher, Samsung Research (AR Core Team), Noida India, Sep 2023 - Nov 2025.
Designed and deployed AI agents using LangChain, Vertex AI, CrewAI, and Firebase Studio, integrating with n8n to automate workflows.
Developed an on-device visual assistant to replace Gemini API usage in Samsung's "Circle to Search" feature using NanoVLM for real-time image understanding, RAG for retrieving contextual facts, and MCP to generate diverse responses.
Worked on "Generative Image Dynamics": generating a seamlessly looping video from a single image in 3 seconds, versus the best existing time of around 17 seconds, by interpreting spectral volumes as image-space modal bases that approximate object dynamics.
Applied quantization, pruning, and distillation to run the Generative Image Dynamics solution on-device on mobile phones.
Worked on Augmented Reality using ARCore and computer vision techniques including height detection, dimension detection, live stickers, emoji, doodle, and touchless doodling.
Led a team of 15 developers with end-to-end ownership of development at Samsung Research.
Senior Software Engineer, Qualcomm, Hyderabad India, Mar 2021 - Aug 2023.
On the AI-ML IoT Framework Team (Mar 2023 - Aug 2023), wrote plugins for object detection and tracking with different colored bounding boxes per object plus trajectory prediction, using GStreamer, TensorFlow Lite, ByteTrack, C++, and C.
On the Wearables IoT Tech Team (Mar 2021 - Feb 2023), did HAL development for smartwatch display, wrist tilt, brightness, and orientation, plus Android apps, VTS unit testing, and log-analysis automation scripts.
Applied ML techniques to sensor data for tilt detection, automated sleep alarms, and cardiovascular health monitoring.
Increased smartwatch battery backup by around 40% using a dual-processor concept that offloaded display and controls to a secondary processor.
Mentored interns and other developers, with end-to-end ownership of feature requests at Qualcomm.
Software Engineer, Amdocs, Pune India, Aug 2020 - Feb 2021, on Billing and RTB teams.
Did API development, bug resolution, fraud detection, and revenue forecasting using Java, Python, Mockito, Postman, MySQL, machine learning, and NLP.
Created an environment of bug resolution within 24 hours at Amdocs.
Guest sessions and hackathon judging for GLA University and others, Remote, Sept 2020 - Present.
Provides competitive-coding and data-science mentoring, shaping thousands of students a year and bridging the gap between institutions and the tech industry.
Intern, Siemens Healthineers, Remote, July 2019 - Feb 2020.
Built cholesterol prediction from eye images using machine learning and image processing, giving a one-click, one-second prediction with no blistering required.
Instructor, Digiimento Education Pvt. Ltd, Delhi India, Dec 2017 - June 2018.
Mentored students and created content for GATE CSE.
Full Stack Developer, Wheelseye Technology, Gurgaon India, Sept 2017 - Dec 2017.
Developed APIs for live tracking of trucks and notifications using Java, JavaScript, and Python, and suggested dynamic routes based on real-time traffic analysis and driver behavior.
Full Stack Developer, Scrum Technology, Delhi India, June 2016 - Aug 2017.
Built websites for various clients using Java, JavaScript, HTML, and CSS, and applied predictive caching to pre-cache likely-visited elements for faster load times.
Intern, IIT BHU, Varanasi India, June 2015 - July 2015.
Built proxy-less internet access over LAN/WAN.

## EDUCATION
M.Tech, Artificial Intelligence, IIT (ISM) Dhanbad, 2018-2020. Research on medical image processing using Cycle GAN.
B.Tech, Computer Science and Engineering, KNIT Sultanpur, 2012-2016.
Intermediate, PCM Mathematics, CBSE Varanasi, 2010-2011.
High School, PCM Mathematics, CBSE Varanasi, 2008-2009.

## SKILL
Artificial Intelligence, Deep Learning, Machine Learning, Image Processing, Computer Vision, Natural Language Processing.
Augmented Reality, ARCore, Large Language Models, VLMs, RAG, MCP, LangChain.
Python, NumPy, Pandas, Matplotlib, SQL, Android, Java, C++, C, Git, Perforce.
System Design, Leadership, JavaScript, HTML, CSS, Hardware Abstraction Layer, Linux, Shell Scripting.
PyTorch, TensorFlow, Internet of Things, Agentic AI, Quantization, Pruning, Distillation.

## ACHIEVEMENT
Top Ranker in GATE, four separate times.
Selected for scientist positions at ISRO, BARC, NIELIT, DRDO, BDL, and the Cabinet Secretariat.
2nd Prize, Japan Hackathon 2021, representing India.
2nd Prize, IMLEAP (Siemens Healthineers Hackathon).
Finalist, Mercedes-Benz Hackathon, Techgium (L&T Infotech) Hackathon, and Code Gladiator Coding Competition.
Sports Secretary 2015-2016 and Captain of the IIT Dhanbad Cricket Team; represented IIT Dhanbad at Inter-IIT in 2018 and 2019.
Headed four student chapters simultaneously: IEI, CSI, ISTE, and DrishtiCone.
Lead organizer of the Sports and Technical fest at KNIT Sultanpur.
3rd Prize, Ramanujan Mathematics Olympiad, 2010.

## PROJECT
Generative Image Dynamics: single-image-to-looping-video generation in 3 seconds versus a 17-second prior state of the art, at Samsung Research.
On-device NanoVLM visual assistant replacing Gemini API calls in Samsung's Circle to Search feature.
Real-time computer-vision platform at Jinn Labs ingesting 2000+ concurrent RTSP streams with VLM-based suspicious-event detection.
Object detection and tracking plugins with trajectory prediction for Qualcomm's AI-ML IoT Framework.
Dual-processor smartwatch power management architecture at Qualcomm, increasing battery backup by about 40%.
Cholesterol prediction from eye images using machine learning and image processing at Siemens Healthineers.
M.Tech thesis: medical image processing using Cycle GAN at IIT (ISM) Dhanbad.
