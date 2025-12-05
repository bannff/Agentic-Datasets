# Exemplary Clojure Codebases - "North Star" Projects

This document curates the most exemplary Clojure/ClojureScript codebases that the community consistently points to as "north star" examples of idiomatic, well-structured Clojure code.

## 🌟 Tier 1: Production-Scale Applications

These are large, battle-tested applications that demonstrate Clojure at scale.

### Metabase
- **Repository**: https://github.com/metabase/metabase
- **Stars**: 39,000+
- **What It Is**: Open-source business intelligence tool
- **Why It's Exemplary**:
  - Large-scale Clojure application in production at thousands of companies
  - Clean separation of concerns
  - Excellent test coverage
  - Shows how to structure a complex application
  - Good example of Clojure + ClojureScript full-stack
- **Learn**: Architecture, namespacing at scale, database abstractions, API design

### Logseq
- **Repository**: https://github.com/logseq/logseq
- **Stars**: 35,000+
- **What It Is**: Knowledge management and collaboration platform
- **Why It's Exemplary**:
  - Modern ClojureScript application
  - Demonstrates Datascript usage
  - Local-first architecture patterns
  - Shows complex state management
- **Learn**: ClojureScript patterns, Datascript, local-first design

### Penpot
- **Repository**: https://github.com/penpot/penpot
- **Stars**: 35,000+
- **What It Is**: Open-source design and prototyping platform (Figma alternative)
- **Why It's Exemplary**:
  - Large ClojureScript frontend
  - Complex UI state management
  - SVG manipulation
  - Real-time collaboration
- **Learn**: Large ClojureScript apps, canvas/SVG, real-time features

---

## 🌟 Tier 2: Foundational Libraries

These are the libraries that define idiomatic Clojure. Reading their source is like reading a masterclass.

### Ring
- **Repository**: https://github.com/ring-clojure/ring
- **Stars**: 3,800+
- **Author**: James Reeves (weavejester)
- **What It Is**: HTTP server abstraction
- **Why It's Exemplary**:
  - Defines the Ring spec that all Clojure web apps use
  - Beautifully simple design
  - Perfect example of data-oriented programming
  - Request/response as plain maps
- **Learn**: Data-oriented design, middleware pattern, simplicity

### Compojure
- **Repository**: https://github.com/weavejester/compojure
- **Stars**: 4,100+
- **Author**: James Reeves (weavejester)
- **What It Is**: Routing library for Ring
- **Why It's Exemplary**:
  - Elegant macro design
  - Composable routing
  - Clean, readable source
- **Learn**: Macro design, DSL creation, composability

### DataScript
- **Repository**: https://github.com/tonsky/datascript
- **Stars**: 5,500+
- **Author**: Nikita Prokopov (tonsky)
- **What It Is**: Immutable in-memory database
- **Why It's Exemplary**:
  - Datomic-style database in pure Clojure/ClojureScript
  - Elegant implementation of Datalog
  - Perfect example of immutable data structures
  - Well-documented and readable
- **Learn**: Database internals, Datalog, immutable data patterns

### Re-frame
- **Repository**: https://github.com/day8/re-frame
- **Stars**: 5,500+
- **What It Is**: ClojureScript state management framework
- **Why It's Exemplary**:
  - Defines the standard for ClojureScript SPAs
  - Excellent documentation with rationale
  - Clean event/subscription model
  - Effects and coeffects system
- **Learn**: State management, event sourcing patterns, ClojureScript architecture

### Reagent
- **Repository**: https://github.com/reagent-project/reagent
- **Stars**: 4,700+
- **What It Is**: Minimalistic React wrapper
- **Why It's Exemplary**:
  - Elegant use of Clojure's atom for React state
  - Hiccup syntax for components
  - Demonstrates Clojure's interop capabilities
- **Learn**: React interop, hiccup, reactive programming

---

## 🌟 Tier 3: Infrastructure & Tools

### Babashka
- **Repository**: https://github.com/babashka/babashka
- **Stars**: 4,200+
- **Author**: Michiel Borkent (borkdude)
- **What It Is**: Native Clojure scripting runtime
- **Why It's Exemplary**:
  - GraalVM native compilation
  - SCI (Small Clojure Interpreter) implementation
  - Shows how to build tooling in Clojure
- **Learn**: GraalVM, interpreters, CLI tools

### Clj-kondo
- **Repository**: https://github.com/clj-kondo/clj-kondo
- **Stars**: 1,700+
- **Author**: Michiel Borkent (borkdude)
- **What It Is**: Static analyzer and linter
- **Why It's Exemplary**:
  - Fast static analysis
  - Extensible architecture
  - GraalVM compilation
- **Learn**: Static analysis, AST walking, tooling

### Riemann
- **Repository**: https://github.com/riemann/riemann
- **Stars**: 4,200+
- **What It Is**: Network event stream processor
- **Why It's Exemplary**:
  - Production monitoring system
  - Demonstrates core.async
  - Stream processing patterns
- **Learn**: Stream processing, monitoring, core.async

### XTDB (formerly Crux)
- **Repository**: https://github.com/xtdb/xtdb
- **Stars**: 2,500+
- **Organization**: JUXT
- **What It Is**: Bitemporal database
- **Why It's Exemplary**:
  - Complex database implementation
  - Bitemporal data model
  - Multiple storage backends
  - Well-architected Clojure project
- **Learn**: Database design, bitemporality, system architecture

---

## 🌟 Tier 4: Full-Stack Frameworks & Templates

### Fulcro
- **Repository**: https://github.com/fulcrologic/fulcro
- **Stars**: 1,500+
- **Author**: Tony Kay
- **What It Is**: Full-stack web framework
- **Why It's Exemplary**:
  - Complete solution for full-stack Clojure apps
  - Graph-based data model
  - Excellent documentation and videos
- **Learn**: Full-stack architecture, normalized state, graph APIs

### Biff
- **Repository**: https://github.com/jacobobryant/biff
- **Stars**: 1,100+
- **Author**: Jacob O'Bryant
- **What It Is**: Full-stack web framework
- **Why It's Exemplary**:
  - Modern, batteries-included framework
  - Uses XTDB for database
  - Great example of opinionated Clojure
- **Learn**: Modern Clojure patterns, XTDB integration, full-stack apps

### Luminus
- **Repository**: https://github.com/luminus-framework/luminus
- **Website**: http://www.luminusweb.net/
- **What It Is**: Web application template
- **Why It's Exemplary**:
  - Comprehensive project generator
  - Shows how to compose libraries
  - Well-documented patterns
- **Learn**: Project structure, library composition, web best practices

---

## 🌟 Tier 5: Utility Libraries (Clean Code Examples)

### Metosin Libraries
Metosin produces some of the most polished Clojure libraries:

- **Malli** (https://github.com/metosin/malli) - Schema validation
- **Reitit** (https://github.com/metosin/reitit) - Data-driven routing
- **Jsonista** (https://github.com/metosin/jsonista) - Fast JSON
- **Muuntaja** (https://github.com/metosin/muuntaja) - Content negotiation

### Weavejester Libraries
James Reeves' libraries are consistently excellent:

- **Integrant** (https://github.com/weavejester/integrant) - Lifecycle management
- **Hiccup** (https://github.com/weavejester/hiccup) - HTML templating
- **Ragtime** (https://github.com/weavejester/ragtime) - Database migrations
- **Duct** (https://github.com/duct-framework/duct) - Application framework

### Other Notable Libraries

- **next.jdbc** (https://github.com/seancorfield/next-jdbc) - Modern JDBC wrapper by Sean Corfield
- **HoneySQL** (https://github.com/seancorfield/honeysql) - SQL as data
- **Specter** (https://github.com/redplanetlabs/specter) - Data navigation

---

## 📚 How to Study These Codebases

### For Beginners
1. Start with **Compojure** - small, readable, excellent macros
2. Read **Ring** - understand the foundation of Clojure web
3. Study **Reagent** - learn ClojureScript patterns

### For Intermediate Developers
1. Dive into **DataScript** - understand immutable database design
2. Study **Re-frame** - master state management
3. Read **Malli** or **Reitit** - see data-driven design

### For Advanced Developers
1. Explore **Metabase** - see production-scale architecture
2. Study **XTDB** - understand database internals
3. Read **Babashka** - learn about GraalVM and interpreters

---

## 🔧 Quick Clone Commands

```bash
# Tier 1 - Production Applications
git clone https://github.com/metabase/metabase.git
git clone https://github.com/logseq/logseq.git
git clone https://github.com/penpot/penpot.git

# Tier 2 - Foundational Libraries
git clone https://github.com/ring-clojure/ring.git
git clone https://github.com/weavejester/compojure.git
git clone https://github.com/tonsky/datascript.git
git clone https://github.com/day8/re-frame.git
git clone https://github.com/reagent-project/reagent.git

# Tier 3 - Infrastructure & Tools
git clone https://github.com/babashka/babashka.git
git clone https://github.com/clj-kondo/clj-kondo.git
git clone https://github.com/riemann/riemann.git
git clone https://github.com/xtdb/xtdb.git

# Tier 4 - Full-Stack
git clone https://github.com/fulcrologic/fulcro.git
git clone https://github.com/jacobobryant/biff.git

# Tier 5 - Utility Libraries
git clone https://github.com/metosin/malli.git
git clone https://github.com/metosin/reitit.git
git clone https://github.com/weavejester/integrant.git
git clone https://github.com/seancorfield/next-jdbc.git
```

---

## 🎯 Key Authors to Follow

These developers consistently produce exemplary Clojure code:

| Author | GitHub | Known For |
|--------|--------|-----------|
| James Reeves | [@weavejester](https://github.com/weavejester) | Ring, Compojure, Integrant, Hiccup |
| Michiel Borkent | [@borkdude](https://github.com/borkdude) | Babashka, clj-kondo, SCI |
| Nikita Prokopov | [@tonsky](https://github.com/tonsky) | DataScript, Rum, AnyBar |
| Sean Corfield | [@seancorfield](https://github.com/seancorfield) | next.jdbc, HoneySQL, clj-new |
| Tony Kay | [@awkay](https://github.com/awkay) | Fulcro |
| Tommi Reiman | Metosin team | Malli, Reitit, Compojure-api |
| Rich Hickey | [@richhickey](https://github.com/richhickey) | Clojure itself, Datomic |
| Alex Miller | [@puredanger](https://github.com/puredanger) | Clojure core team |

---

## 📖 Additional Resources

- **Awesome Clojure**: https://github.com/razum2um/awesome-clojure
- **Clojure Toolbox**: https://www.clojure-toolbox.com/
- **Practical.li**: https://practical.li/clojure/
- **Clojure Style Guide**: https://github.com/bbatsov/clojure-style-guide
- **Clojure Design Patterns**: Study the source of libraries listed above
