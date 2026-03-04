"""Reasoning Framework Registry.

This package organizes 40 prompt engineering frameworks into
category-based submodules for maintainability. Adding or retiring
a framework is as simple as editing a single category file.

Submodules:
- base: TaskCategory, FRAMEWORK_REGISTRY, ReasoningFramework ABC
- zero_shot: Role, Emotion, S2A, SimToM, RaR, Self-Ask
- thought_generation: CoT, StepBack, ThoT, TabCoT, Contrastive, Complexity, Active, Analogical, Directional
- decomposition: ToT, LtM, PoT, SoT, P&S, Faithful, RoT
- ensembling: SC, DENSE, MoRE, Meta-CoT, Paraphrasing
- self_criticism: Reflexion, Maieutic, CoVe, Self-Refine, Self-Cal, RCoT, Cumulative
- advanced: ReAct, GoT, RAP, CoD, BoT, CoTable
"""

# Base classes and registry
from .base import (
    TaskCategory,
    FRAMEWORK_REGISTRY,
    ReasoningFramework,
    get_framework,
    list_frameworks,
)

# Zero-Shot Techniques
from .zero_shot import (
    RolePrompting,
    EmotionPrompting,
    System2Attention,
    SimToM,
    RephraseAndRespond,
    SelfAsk,
)

# Thought Generation
from .thought_generation import (
    ChainOfThought,
    StepBack,
    ThreadOfThought,
    TabCoT,
    ContrastiveCoT,
    ComplexityBased,
    ActivePrompting,
    Analogical,
    DirectionalStimulus,
)

# Decomposition
from .decomposition import (
    TreeOfThoughts,
    LeastToMost,
    ProgramOfThoughts,
    SkeletonOfThought,
    PlanAndSolve,
    FaithfulCoT,
    RecursionOfThought,
)

# Ensembling
from .ensembling import (
    SelfConsistency,
    DemonstrationEnsembling,
    MixtureOfReasoning,
    MetaCoT,
    PromptParaphrasing,
)

# Self-Criticism
from .self_criticism import (
    Reflexion,
    Maieutic,
    ChainOfVerification,
    SelfRefine,
    SelfCalibration,
    ReverseCoT,
    CumulativeReasoning,
)

# Advanced / Agent-Adjacent
from .advanced import (
    ReAct,
    GraphOfThoughts,
    ReasoningViaPlanning,
    ChainOfDensity,
    BufferOfThoughts,
    ChainOfTable,
)

__all__ = [
    # Base
    "TaskCategory",
    "FRAMEWORK_REGISTRY",
    "ReasoningFramework",
    "get_framework",
    "list_frameworks",
    # Zero-Shot
    "RolePrompting",
    "EmotionPrompting",
    "System2Attention",
    "SimToM",
    "RephraseAndRespond",
    "SelfAsk",
    # Thought Generation
    "ChainOfThought",
    "StepBack",
    "ThreadOfThought",
    "TabCoT",
    "ContrastiveCoT",
    "ComplexityBased",
    "ActivePrompting",
    "Analogical",
    "DirectionalStimulus",
    # Decomposition
    "TreeOfThoughts",
    "LeastToMost",
    "ProgramOfThoughts",
    "SkeletonOfThought",
    "PlanAndSolve",
    "FaithfulCoT",
    "RecursionOfThought",
    # Ensembling
    "SelfConsistency",
    "DemonstrationEnsembling",
    "MixtureOfReasoning",
    "MetaCoT",
    "PromptParaphrasing",
    # Self-Criticism
    "Reflexion",
    "Maieutic",
    "ChainOfVerification",
    "SelfRefine",
    "SelfCalibration",
    "ReverseCoT",
    "CumulativeReasoning",
    # Advanced
    "ReAct",
    "GraphOfThoughts",
    "ReasoningViaPlanning",
    "ChainOfDensity",
    "BufferOfThoughts",
    "ChainOfTable",
]
