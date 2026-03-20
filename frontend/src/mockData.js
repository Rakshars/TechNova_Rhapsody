export const MOCK_RESPONSE = {
  candidate_name: "Arjun Mehta",
  target_role: "Machine Learning Engineer",
  skills_matched: [
    "Python", "NumPy", "Pandas", "SQL", "Git",
    "REST APIs", "Data Visualization", "Statistics"
  ],
  skills_missing: [
    "PyTorch", "MLflow", "Docker", "Kubernetes",
    "Transformer Models", "Feature Engineering", "A/B Testing"
  ],
  learning_path: [
    { step: 1, title: "PyTorch Fundamentals", description: "Learn tensors, autograd, and building neural nets from scratch. Bridges your NumPy knowledge directly to deep learning.", duration: "2 weeks", type: "Core Skill", priority: "High" },
    { step: 2, title: "Feature Engineering & Data Pipelines", description: "Hands-on practice transforming raw features, encoding categoricals, and building sklearn pipelines for production.", duration: "1 week", type: "Applied Practice", priority: "High" },
    { step: 3, title: "Transformer Models (HuggingFace)", description: "Understand attention mechanisms, fine-tune BERT/T5 on domain tasks using the HuggingFace Trainer API.", duration: "2 weeks", type: "Advanced Topic", priority: "Medium" },
    { step: 4, title: "MLflow — Experiment Tracking", description: "Log experiments, compare runs, register and version your trained models in a local or remote MLflow server.", duration: "3 days", type: "Tooling", priority: "Medium" },
    { step: 5, title: "Docker for ML Engineers", description: "Containerize training scripts and inference servers. Write Dockerfiles, multi-stage builds, and docker-compose setups.", duration: "1 week", type: "DevOps Essentials", priority: "Medium" },
    { step: 6, title: "A/B Testing & Statistical Inference", description: "Design controlled experiments, compute power/sample-size, and interpret p-values correctly in a product context.", duration: "1 week", type: "Applied Practice", priority: "Medium" }
  ],
  reasoning: "Arjun already has a strong foundation in Python and data manipulation (Pandas, NumPy, SQL), which accelerates the learning curve significantly. The pathway prioritises PyTorch first because it is the primary framework listed in the JD and unlocks all subsequent deep learning modules. Feature Engineering is placed second because it directly addresses the most common gap seen in junior-to-mid ML transitions. Transformer models are sequenced after PyTorch mastery to avoid cognitive overload. MLflow and Docker are ordered as tooling concerns rather than conceptual blockers. Estimated total learning time: 7–8 weeks."
}