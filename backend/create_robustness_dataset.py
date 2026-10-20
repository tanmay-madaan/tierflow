"""
create_robustness_dataset.py — Generates backend/data/robustness_queries.csv.

Constructs 104 carefully curated queries across 8 distinct failure-mode test groups:
1. paraphrase_uncommon_wording (13)
2. unusual_syntax_vocabulary (13)
3. ambiguous_missing_context (13)
4. complex_no_keywords (13)
5. empty_whitespace (12)
6. nonsense_random_tokens (14)
7. short_difficult (13)
8. long_simple (13)

Ensures zero overlap with data/queries.csv, strict schema validation, and
defensible ground-truth separation.
"""

import csv
from pathlib import Path
import pandas as pd

BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
OUTPUT_FILE = DATA_DIR / "robustness_queries.csv"

# 1. Paraphrase with uncommon wording (13)
# Familiar tasks avoiding standard trigger verbs ('what is', 'explain', 'calculate')
GROUP_PARAPHRASE = [
    {
        "query": "State the sovereign seat of governance for the Japanese archipelago.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'What is the capital of Japan?'. Factual recall of Tokyo; solvable by smallest tier."
    },
    {
        "query": "Identify the biological macromolecule that conveys hereditary traits across generations.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'What is DNA?'. Single concept factual definition."
    },
    {
        "query": "Name the subatomic particle bearing negative electric charge situated in orbital shells.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'What is an electron?'. Basic scientific fact."
    },
    {
        "query": "Name the specific astronomical body around which the planet Neptune orbits.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'What does Neptune orbit?'. Direct factual recall (The Sun)."
    },
    {
        "query": "Narrate the physiological pathway through which chloroplasts convert captured photons into glucose.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'Explain photosynthesis'. Requires structured multi-sentence biological explanation."
    },
    {
        "query": "Delineate how an interpreted runtime manages dynamic heap allocations versus compile-time stack frames.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of stack vs heap memory management without standard buzzwords."
    },
    {
        "query": "Furnish a Python snippet that reverses a singly linked list without allocating auxiliary nodes.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of 'Reverse a linked list in-place'. Standard data structures coding task."
    },
    {
        "query": "Elucidate why minimizing convex loss functions guarantees convergence to an absolute minimum.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Conceptual machine learning optimization inquiry expressed with advanced vocabulary."
    },
    {
        "query": "Trace the operational disparities between relational schemas in normal form and denormalized document stores.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Paraphrase of SQL vs NoSQL comparison using academic wording."
    },
    {
        "query": "Dissect the theoretical distinctions between linearizability and serializability in distributed datastores.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Subtle concurrency and consistency models in distributed systems; requires deep technical precision."
    },
    {
        "query": "Formulate a fault-tolerant multi-master consensus scheme resistant to network partitions and Byzantine corruption.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Advanced distributed systems architecture request avoiding the common word 'design'."
    },
    {
        "query": "Conduct a mathematical derivation of the Black-Scholes partial differential equation from Ito calculus foundations.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Formal mathematical derivation in stochastic calculus."
    },
    {
        "query": "Deconstruct the zero-knowledge argument construction in Groth16 and detail how pairing-friendly elliptic curves ensure soundness.",
        "case_type": "paraphrase_uncommon_wording",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Cryptographic zero-knowledge proof analysis requiring deep domain expertise."
    }
]

# 2. Unusual syntax / vocabulary (13)
# Inverted sentence order, archaic vocabulary, passive constructions
GROUP_UNUSUAL_SYNTAX = [
    {
        "query": "The capital of the French Republic: name it.",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Inverted syntax requesting Paris; trivial factual lookup."
    },
    {
        "query": "By whom was penicillin originally discovered in the year 1928?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Passive voice historical question (Alexander Fleming)."
    },
    {
        "query": "A binary digit, in common parlance, by what contracted moniker is it known?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Archaic/verbose phrasing for 'What is a bit?'."
    },
    {
        "query": "Which noble gas hath the lowest atomic mass upon the periodic table?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Archaic syntax for Helium."
    },
    {
        "query": "Should a service encounter abrupt termination upon dereferencing a nil pointer, depict the recovery mechanism.",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Conditional inversion discussing panic/recover or SIGSEGV handling."
    },
    {
        "query": "Of hash tables and balanced binary search trees, which exhibite superior temporal bounds for arbitrary key access?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Archaic phrasing comparing O(1) vs O(log n) lookups."
    },
    {
        "query": "Whence arises the phenomenon known as vanishing gradient during the training of deep recursive networks?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Non-standard interrogative ('Whence') for machine learning concept."
    },
    {
        "query": "Upon what foundational premise does the Shannon-Nyquist sampling theorem rest regarding continuous signal discretization?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Formal academic syntax for signal processing theorem."
    },
    {
        "query": "In Python, provided a dictionary of string keys to integer tallies, how might one invert keys and values safely?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Unusual conversational syntax for a dictionary inversion task."
    },
    {
        "query": "In an asynchronous distributed setting beset with arbitrary Byzantine failures, by what formal reasoning is consensus impossible?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "FLP theorem / Byzantine consensus inquiry framed in elevated prose."
    },
    {
        "query": "Beholding a monolithic software edifice of 20 million lines, delineate an evolutionary blueprint toward autonomous bounded contexts.",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Metaphorical literary phrasing for large-scale microservices refactoring architecture."
    },
    {
        "query": "Wherefore does the spectral gap of a normalized graph Laplacian govern the mixing time of a continuous-time Markov random walk?",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Archaic adverb ('Wherefore') with deep spectral graph theory and stochastic processes."
    },
    {
        "query": "Unto a payment processing substrate handling 50,000 requests per second, prescribe an idempotency and two-phase commit architecture.",
        "case_type": "unusual_syntax_vocabulary",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "High-throughput financial systems architecture framed with archaic prepositional syntax."
    }
]

# 3. Ambiguous requests with missing context (13)
# Underspecified inputs where task difficulty depends on unprovided context.
# Ground truth cannot be defensibly assigned; expected routing action is MEDIUM fallback.
GROUP_AMBIGUOUS = [
    {
        "query": "Fix the bug.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Completely missing code and error trace. Requires conversational clarification."
    },
    {
        "query": "Make it faster.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing reference subject, baseline metrics, and programming environment."
    },
    {
        "query": "Which one is better?",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing items to compare and evaluation criteria."
    },
    {
        "query": "Write the test.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing function or specification to be tested."
    },
    {
        "query": "Is this secure?",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing code snippet, architectural diagram, or threat model."
    },
    {
        "query": "Process the data.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing dataset schema, source format, and intended transformation."
    },
    {
        "query": "Optimize the model.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Ambiguous whether hyperparameter tuning, quantization, or re-architecture is desired."
    },
    {
        "query": "Deploy it.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing infrastructure target (AWS, GCP, K8s, bare metal) and application artifact."
    },
    {
        "query": "What went wrong here?",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing log output, stack trace, or system state description."
    },
    {
        "query": "Refactor this.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing source code and refactoring target guidelines."
    },
    {
        "query": "Calculate the result.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing formula, variables, or input dataset."
    },
    {
        "query": "Check the difference.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Missing candidate objects or metrics to contrast."
    },
    {
        "query": "Review this implementation.",
        "case_type": "ambiguous_missing_context",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "No code provided to review."
    }
]

# 4. Multi-step reasoning / coding without obvious trigger keywords (13)
# Advanced problems stripped of words like 'algorithm', 'design', 'calculate', 'prove', 'step by step'
GROUP_COMPLEX_NO_KEYWORDS = [
    {
        "query": "A distributed ledger receives updates simultaneously from nodes across the Atlantic; clocks are out of sync by up to 200ms and messages can arrive out of order. We must guarantee that every replica processes balance transfers in the exact same sequence.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Logical clocks / Paxos consensus task completely avoiding trigger keywords."
    },
    {
        "query": "Two processes increment a shared counter 100,000 times concurrently on a multicore CPU without locks. The final value is 142,391 instead of 200,000. Show the exact assembly instructions and cache coherence states responsible for the missing counts.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Low-level concurrency race condition and MESI cache protocol analysis."
    },
    {
        "query": "A language accepts sequences of balanced parentheses where each opening bracket must be closed by the matching symbol, but brackets can be nested up to arbitrary depth. Can a finite automaton accept this language? Show why.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Pumping Lemma proof for non-regularity of Dyck language; requires theoretical CS formal reasoning."
    },
    {
        "query": "A database node crashes halfway through writing a 64KB page to disk during a transaction commit. How does write-ahead logging with ARIES recover the state upon restart?",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Database crash recovery (Analysis, Redo, Undo phases of ARIES) without explicit keywords."
    },
    {
        "query": "We have an unweighted graph where every vertex has degree at least d. Must there exist a cycle of length at least d + 1? Provide the argument.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Extremal graph theory problem using maximal path arguments."
    },
    {
        "query": "An attacker intercepts ciphertext produced by AES-CBC where the initialization vector is predictable. Show how they can confirm whether an arbitrary plaintext block matches a guess.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Cryptographic chosen-plaintext attack against predictable IVs in CBC mode."
    },
    {
        "query": "In a peer-to-peer network with 10,000 nodes where nodes leave without warning, we want lookups to succeed with high probability in at most logarithmic hops. Describe the routing table structure.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Distributed Hash Table (Chord/Kademlia) routing mechanics without trigger keywords."
    },
    {
        "query": "A machine learning pipeline trains a classifier where 99.5% of labels are negative. Accuracy is 99.4% but the business is losing millions because false negatives go undetected. Propose an appropriate loss formulation and evaluation strategy.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Severe class imbalance problem addressing focal loss, PR-AUC, and cost-sensitive classification."
    },
    {
        "query": "A recursive function computes Fibonacci numbers in exponential time due to repeated subproblems. Transform it into a linear-time version using bottom-up tabulation in JavaScript.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Classic dynamic programming transformation without using the word 'algorithm'."
    },
    {
        "query": "A microservice returns HTTP 504 Gateway Timeout only when upstream traffic spikes above 2,000 requests per second, while CPU utilization remains below 20%. Where is the bottleneck likely situated?",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Connection pool exhaustion / socket starvation debugging inquiry."
    },
    {
        "query": "Given a collection of intervals on a timeline, merge all overlapping ranges so that no two output ranges intersect. Output the merged intervals in order.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Classic interval merging programming task without buzzwords."
    },
    {
        "query": "A neural model produces high training loss that fluctuates wildly between batches and eventually becomes NaN after 500 steps. What learning rate adjustment or normalization technique should be applied?",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Exploding gradients diagnostic and mitigation (gradient clipping, warmups)."
    },
    {
        "query": "Given an array of integers with both positive and negative values, find the contiguous sub-array with the maximum sum.",
        "case_type": "complex_no_keywords",
        "ground_truth_tier": "MEDIUM",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Kadane's algorithm task stated without mentioning 'algorithm' or 'Kadane'."
    }
]

# 5. Empty and whitespace-only inputs (12)
# Zero or whitespace-only inputs. Ground truth does not exist; safe fallback is MEDIUM.
GROUP_EMPTY_WHITESPACE = [
    {
        "query": "",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Completely empty string; fallback guard must trigger."
    },
    {
        "query": " ",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Single space character."
    },
    {
        "query": "   ",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Three space characters."
    },
    {
        "query": "\t",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Single horizontal tab character."
    },
    {
        "query": "\t\t\t",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Multiple tab characters."
    },
    {
        "query": "\n",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Single newline character."
    },
    {
        "query": "\n\n\n",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Multiple newline characters."
    },
    {
        "query": "\r\n",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Windows CRLF newline."
    },
    {
        "query": "\r\n\r\n",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Double Windows CRLF newline."
    },
    {
        "query": "   \t   \n   ",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Mixed spaces, tabs, and newline."
    },
    {
        "query": "\t \r\n \t",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Mixed whitespace sequence with tabs and carriage returns."
    },
    {
        "query": "               ",
        "case_type": "empty_whitespace",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Long sequence of 15 space characters."
    }
]

# 6. Nonsense strings, random tokens, text with unrecognized vocabulary (14)
# Incoherent tokens or random strings. Ground truth tier is NONE; safe fallback is MEDIUM.
GROUP_NONSENSE = [
    {
        "query": "asdfghjkl qwertyuiop",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Standard QWERTY keyboard row smash."
    },
    {
        "query": "zxcvbnmpoiuytrewqasdfghjkl",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Single continuous keyboard mash token."
    },
    {
        "query": "a8f23bc99401fe37b12d5930e44",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Random hexadecimal hash string."
    },
    {
        "query": "...???!!!;;;---:::***",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Pure punctuation characters with zero alphanumeric tokens."
    },
    {
        "query": "flibber gibber wobber gloop trazzle plink",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Syntactically plausible pseudo-words (nonce tokens) with no semantic meaning."
    },
    {
        "query": "the of and to a in that is was he for it with as his on be at",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Stopword soup with no predicate, verb phrase, or coherent semantic intent."
    },
    {
        "query": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Repeated single-character string."
    },
    {
        "query": "1234567890 0987654321 5555555555",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Arbitrary integer sequence without mathematical operator or problem statement."
    },
    {
        "query": "blorp zazzle quux fribble snark",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Random jargon / metasyntactic nonsense syllables."
    },
    {
        "query": "/// \\\\\\ &&& %%% $$$ ### @@@",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Non-alphanumeric special character clusters."
    },
    {
        "query": "xkcd 99482 jfkldsa; 3910398 !!",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Mixed alphanumeric noise with trailing punctuation."
    },
    {
        "query": "lorem ipsum dolor sit amet consectetur adipiscing elit",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Latin placeholder text with no instructions or query intent."
    },
    {
        "query": "null undefined NaN void 0 [object Object]",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Programming null/sentinel tokens dumped without context."
    },
    {
        "query": "!@#$%^&*()_+=-`~[]{}|;':\",./<>?",
        "case_type": "nonsense_random_tokens",
        "ground_truth_tier": "NONE",
        "expected_routing_tier": "MEDIUM",
        "has_defensible_ground_truth": False,
        "labelling_notes": "Full keyboard symbol row."
    }
]

# 7. Short but genuinely difficult requests (13)
# Under 50 chars or brief words, but mathematically/theoretically advanced requiring LARGE
GROUP_SHORT_DIFFICULT = [
    {
        "query": "Prove P != NP.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Extremely short (14 chars) Millennium Prize problem. Requires deepest reasoning model."
    },
    {
        "query": "Derive the Navier-Stokes equations.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Short (35 chars) rigorous fluid dynamics continuum mechanics derivation."
    },
    {
        "query": "Is Chaitin's constant Omega computable?",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Algorithmic information theory inquiry regarding uncomputable halting probabilities."
    },
    {
        "query": "Solve Einstein's field equations for a Kerr metric.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "General relativity rotating black hole tensor calculation."
    },
    {
        "query": "Prove Gödel's First Incompleteness Theorem.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Formal mathematical logic proof via Gödel numbering and self-reference."
    },
    {
        "query": "Construct a non-measurable set of real numbers.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Measure theory construction of Vitali set requiring Axiom of Choice."
    },
    {
        "query": "Prove the Poincaré conjecture for 3-manifolds.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Ricci flow with surgery topology proof (Perelman)."
    },
    {
        "query": "Does ZFC have a transitive model?",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Axiomatic set theory and model theory question on inaccessible cardinals."
    },
    {
        "query": "Derive the Bekenstein-Hawking entropy formula.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Quantum field theory in curved spacetime derivation."
    },
    {
        "query": "Prove Fermat's Last Theorem for n = 3.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Euler's algebraic number theory proof using Eisenstein integers."
    },
    {
        "query": "Is the Collatz conjecture decidable?",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Computability theory question on whether generalized 3x+1 problems are undecidable."
    },
    {
        "query": "Derive Bellman's equation for continuous-time POMDPs.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Stochastic optimal control with partial observability."
    },
    {
        "query": "Prove the Riemann hypothesis for function fields.",
        "case_type": "short_difficult",
        "ground_truth_tier": "LARGE",
        "expected_routing_tier": "LARGE",
        "has_defensible_ground_truth": True,
        "labelling_notes": "Weil's theorem for curves over finite fields in algebraic geometry."
    }
]

# 8. Long but genuinely simple requests (13)
# Verbose, conversational, high word count, multi-sentence narrative, but trivial factual content for SMALL
GROUP_LONG_SIMPLE = [
    {
        "query": "Hello there friendly virtual assistant! I was sitting in my living room yesterday evening drinking tea and reading a book about European geography and history. While gazing out at the rainy weather, I suddenly realized that for the life of me I could not recall what municipal city officially serves as the seat of government and capital of the nation of France. Could you kindly remind me what that city is?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "78 words / 419 chars, but asks for the capital of France. Needs SMALL."
    },
    {
        "query": "I hope you are doing well today. My eight-year-old child just came home from elementary school with a basic science quiz sheet and asked me a question that I want to double-check before giving them the answer. The question on their worksheet is simply asking for the standard chemical molecular formula that scientists use to represent pure water. What is that formula?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "67 words / 369 chars, asks for H2O. Solvable by smallest tier."
    },
    {
        "query": "Throughout the late twentieth century, space exploration represented one of the most visible frontiers of human technological achievement, culminating in the Apollo lunar missions conducted by NASA. Speaking specifically of the Apollo 11 mission that touched down on the Moon in July of 1969, who was the first human astronaut to step onto the lunar surface?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "59 words / 358 chars, asks for Neil Armstrong."
    },
    {
        "query": "I am putting together a general trivia night contest for my local community center this coming weekend and I need to verify the answer key for our round on basic biology and anatomy. The question I wrote down is: what is the name of the primary organ inside the human circulatory system that pumps oxygenated blood throughout the body?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "61 words / 333 chars, asks for the heart."
    },
    {
        "query": "While browsing the internet and reading articles about personal computer hardware from the 1990s and early 2000s, I kept seeing the acronym CPU mentioned in almost every single paragraph describing computer components. Could you please just tell me what the three letters in the acronym CPU stand for in plain English?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "53 words / 324 chars, asks for Central Processing Unit."
    },
    {
        "query": "Good morning assistant! I am currently making my weekly grocery shopping list and planning out some basic home baking recipes for the weekend. I want to bake a traditional loaf of plain white sandwich bread from scratch. Could you list the four very basic primary ingredients typically needed to make simple bread dough?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "55 words / 326 chars, asks for flour, water, yeast, salt."
    },
    {
        "query": "In our seventh-grade social studies curriculum, we are currently learning about the geographical landscape of the North American continent. One of the study questions asks about the sovereign nations that share direct land borders with the United States. What are the two countries that directly border the continental United States?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "53 words / 333 chars, asks for Canada and Mexico."
    },
    {
        "query": "Hello! I am reading a historical fiction novel set during the Renaissance in Florence and Venice, and the characters keep talking about the monetary currency they use for commerce and trade. In modern times, what is the official currency used across Italy and most member nations of the European Union?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "51 words / 303 chars, asks for the Euro."
    },
    {
        "query": "I am working on a simple crossword puzzle in the Sunday morning newspaper and I am stuck on a clue that says 'The closest planet in our solar system to the Sun, 7 letters'. Could you please provide the name of that planet so I can complete the puzzle?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "50 words / 256 chars, asks for Mercury."
    },
    {
        "query": "My friend and I were having a friendly debate over lunch about classic English literature and playwrights of the Elizabethan era. We were specifically discussing the famous tragedy involving the Prince of Denmark and the quote 'To be or not to be'. Who was the author who wrote the play Hamlet?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "53 words / 295 chars, asks for William Shakespeare."
    },
    {
        "query": "While looking up basic astronomical facts about our solar system for an introductory science quiz, I came across information regarding the atmospheric composition and distinctive reddish coloration of our neighboring fourth planet from the Sun. What is the common name of this planet known as the Red Planet?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "49 words / 309 chars, asks for Mars."
    },
    {
        "query": "I am setting up a basic home network router and reading through the manufacturer setup guide booklet that came inside the retail packaging box. The instructions refer multiple times to an IP address. In simple terms, what does the abbreviation IP stand for in network technology?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "46 words / 281 chars, asks for Internet Protocol."
    },
    {
        "query": "Can you please tell me in one short word or number how many distinct days are contained in a standard non-leap calendar year according to the modern Gregorian calendar system used across most of the world today?",
        "case_type": "long_simple",
        "ground_truth_tier": "SMALL",
        "expected_routing_tier": "SMALL",
        "has_defensible_ground_truth": True,
        "labelling_notes": "38 words / 215 chars, asks for 365."
    }
]

ALL_GROUPS = [
    GROUP_PARAPHRASE,
    GROUP_UNUSUAL_SYNTAX,
    GROUP_AMBIGUOUS,
    GROUP_COMPLEX_NO_KEYWORDS,
    GROUP_EMPTY_WHITESPACE,
    GROUP_NONSENSE,
    GROUP_SHORT_DIFFICULT,
    GROUP_LONG_SIMPLE
]

def build_robustness_dataset():
    records = []
    idx = 1
    for grp in ALL_GROUPS:
        for item in grp:
            row = {
                "id": f"ROB-{idx:03d}",
                "query": item["query"],
                "case_type": item["case_type"],
                "ground_truth_tier": item["ground_truth_tier"],
                "expected_routing_tier": item["expected_routing_tier"],
                "has_defensible_ground_truth": str(item["has_defensible_ground_truth"]),
                "labelling_notes": item["labelling_notes"]
            }
            records.append(row)
            idx += 1

    df_rob = pd.DataFrame(records)

    # Validation checks
    assert 80 <= len(df_rob) <= 120, f"Total queries {len(df_rob)} outside expected range [80, 120]"
    
    # Check no duplicate IDs
    assert df_rob["id"].nunique() == len(df_rob), "Duplicate IDs detected"

    # Check non-empty/whitespace queries have no exact duplicates
    non_empty = df_rob[df_rob["case_type"] != "empty_whitespace"]
    assert non_empty["query"].nunique() == len(non_empty), "Duplicate query found in non-empty categories"

    # Cross-check against queries.csv to ensure ZERO overlap
    prod_csv = DATA_DIR / "queries.csv"
    if prod_csv.exists():
        df_prod = pd.read_csv(prod_csv)
        prod_set = set(df_prod["query"].str.strip().str.lower())
        rob_set = set(non_empty["query"].str.strip().str.lower())
        overlap = prod_set & rob_set
        assert len(overlap) == 0, f"Data leakage detected! Overlapping queries: {overlap}"
        print(f"[Validation Passed] Zero overlap with queries.csv ({len(prod_set)} prod queries checked).")

    # Write to CSV
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "query", "case_type", "ground_truth_tier",
        "expected_routing_tier", "has_defensible_ground_truth", "labelling_notes"
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[Success] Written {len(records)} robustness queries to {OUTPUT_FILE}")
    print("\nBreakdown by case_type:")
    for ct, count in df_rob["case_type"].value_counts().items():
        print(f"  - {ct:30s}: {count}")

    print("\nBreakdown by ground_truth_tier:")
    for gt, count in df_rob["ground_truth_tier"].value_counts().items():
        print(f"  - {gt:10s}: {count}")

    print(f"\nDefensible Ground Truth queries: {(df_rob['has_defensible_ground_truth'] == 'True').sum()}")
    print(f"Non-defensible / Fallback queries: {(df_rob['has_defensible_ground_truth'] == 'False').sum()}")

if __name__ == "__main__":
    build_robustness_dataset()
