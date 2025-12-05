# Clojure/ClojureScript Training Dataset

A comprehensive, high-quality dataset for training AI models to become expert Clojure and ClojureScript developers.

## Overview

| Metric | Value |
|--------|---------|
| **Total Examples** | 106 |
| **Format** | JSONL (OpenAI conversation format) |
| **Libraries Covered** | 17+ |
| **Languages** | Clojure, ClojureScript |

## Dataset Structure

```
clojure-dataset/
├── raw/                          # Individual topic files
│   ├── 01-clojure-core.jsonl    # Core language (12 examples)
│   ├── 02-clojure-style.jsonl   # Style guide (6 examples)
│   ├── 03-reagent.jsonl         # Reagent UI (6 examples)
│   ├── 04-reframe.jsonl         # Re-frame state (6 examples)
│   ├── 05-malli.jsonl           # Malli schemas (6 examples)
│   ├── 06-reitit.jsonl          # Reitit routing (5 examples)
│   ├── 07-nextjdbc.jsonl        # next.jdbc DB (5 examples)
│   ├── 08-honeysql.jsonl        # HoneySQL DSL (6 examples)
│   ├── 09-integrant.jsonl       # Integrant lifecycle (6 examples)
│   ├── 10-ring.jsonl            # Ring HTTP (5 examples)
│   ├── 11-core-async.jsonl      # core.async (3 examples)
│   ├── 12-spec.jsonl            # clojure.spec (3 examples)
│   ├── 13-testing.jsonl         # Testing (3 examples)
│   ├── 14-clojurescript.jsonl   # CLJS fundamentals (8 examples)
│   ├── 15-fulcro.jsonl          # Fulcro full-stack (8 examples)
│   ├── 16-deps-cli.jsonl        # deps.edn & CLI (8 examples)
│   └── 17-xtdb.jsonl            # XTDB bitemporal DB (10 examples)
├── processed/                    # Pipeline output (empty)
├── sources/                      # Raw documentation (empty)
├── combined-seed.jsonl          # Master file (106 examples)
├── RESOURCES.md                 # Documentation sources
└── README.md                    # This file
```

## Topics Covered

### Core Clojure
- **Language Fundamentals**: Data structures, sequences, functions, destructuring
- **Concurrency**: Atoms, refs, agents, core.async channels
- **Macros**: Writing and debugging macros
- **Spec**: Schema definitions, validation, generative testing
- **Testing**: deftest, fixtures, property-based testing

### ClojureScript
- **JavaScript Interop**: Calling JS functions, property access, type hints
- **Build Tools**: Shadow-cljs, Figwheel, advanced compilation
- **DOM Manipulation**: Direct DOM and Google Closure library
- **State Management**: Atoms, Reagent atoms, Re-frame, DataScript
- **NPM Integration**: Using npm packages in CLJS

### Web Development
- **Ring**: HTTP handlers, middleware, request/response maps
- **Reitit**: Data-driven routing, coercion, middleware
- **Reagent**: React wrapper, components, lifecycle
- **Re-frame**: 6 dominoes, subscriptions, effects, coeffects
- **Fulcro**: Components, queries, mutations, Pathom, RAD

### Data & Database
- **next.jdbc**: SQL execution, result sets, transactions, connection pooling
- **HoneySQL**: SQL DSL, composable queries, helpers
- **Malli**: Schemas, coercion, generation, instrumentation
- **XTDB**: Bitemporal database, Datalog queries, immutable history

### System Architecture
- **Integrant**: Lifecycle management, configuration, refs
- **deps.edn**: Dependencies, aliases, profiles
- **tools.build**: Uberjars, deployment, custom tasks
- **CLI Tools**: nREPL, CIDER, global tools

## Data Format

Each entry follows the OpenAI conversation format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "How do I create a Reagent component?"
    },
    {
      "role": "assistant",
      "content": "Reagent components can be created as functions...\n\n```clojure\n(defn my-component []\n  [:div \"Hello\"])\n```"
    }
  ]
}
```

## Usage

### With the Datasets Pipeline

```bash
# Create pipeline config
cat > examples/pipeline.clojure.yaml << 'EOF'
dataset:
  name: clojure-expert
  version: "1.0.0"

source:
  type: file
  path: clojure-dataset/combined-seed.jsonl

transforms:
  - type: validate
    schema: openai-chat

output:
  format: jsonl
  path: output/clojure-expert.jsonl
EOF

# Run pipeline
agentic-datasets run-config examples/pipeline.clojure.yaml
```

### Direct Use

```python
import json

# Load the dataset
examples = []
with open('clojure-dataset/combined-seed.jsonl', 'r') as f:
    for line in f:
        examples.append(json.loads(line))

print(f"Loaded {len(examples)} training examples")

# Example structure
print(examples[0]['messages'][0]['content'])  # User question
print(examples[0]['messages'][1]['content'])  # Assistant answer
```

### Fine-tuning (OpenAI)

```bash
# Upload for fine-tuning
openai api files.create -f clojure-dataset/combined-seed.jsonl -p fine-tune

# Create fine-tune job
openai api fine_tuning.jobs.create \
  -t <file-id> \
  -m gpt-3.5-turbo
```

## Quality Characteristics

### Coverage
- ✅ Core language features and idioms
- ✅ Major ecosystem libraries (Reagent, Re-frame, Malli, Reitit, etc.)
- ✅ Full-stack development (Fulcro)
- ✅ Database access patterns
- ✅ Build tooling and deployment
- ✅ Testing methodologies

### Code Quality
- ✅ Idiomatic Clojure style
- ✅ Proper namespace organization
- ✅ Real-world patterns and anti-patterns
- ✅ Production-ready examples
- ✅ Error handling and edge cases

### Format Quality
- ✅ Valid JSONL structure
- ✅ Consistent conversation format
- ✅ Well-formatted code blocks
- ✅ Clear explanations with context

## Extending the Dataset

### Add More Examples

1. Create a new JSONL file in `raw/`:
```bash
touch raw/17-new-topic.jsonl
```

2. Add examples in the conversation format:
```json
{"messages":[{"role":"user","content":"Question"},{"role":"assistant","content":"Answer"}]}
```

3. Rebuild combined file:
```bash
cat raw/*.jsonl > combined-seed.jsonl
```

### Validate

```python
import json
with open('combined-seed.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except:
            print(f"Error line {i}")
```

## Documentation Sources

See [RESOURCES.md](RESOURCES.md) for the complete list of official documentation sources used to create this dataset.

## License

This dataset is created from publicly available documentation and examples. Individual library licenses apply to their respective code samples.

## Contributing

To expand this dataset:

1. Add examples for uncovered libraries (Lacinia, Pedestal, etc.)
2. Add more advanced patterns for existing libraries
3. Add troubleshooting and debugging scenarios
4. Add migration guides (e.g., Leiningen → deps.edn)

---

**Created for training AI models to become Clojure experts.**
