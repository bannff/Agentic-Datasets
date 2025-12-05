#!/bin/bash
# Clone Exemplary Clojure Codebases
# This script clones the most highly-regarded Clojure repositories for study

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_DIR="${SCRIPT_DIR}/repos"

echo "🚀 Cloning Exemplary Clojure Codebases"
echo "======================================="
echo ""

# Create repos directory
mkdir -p "$REPOS_DIR"
cd "$REPOS_DIR"

# Function to clone if not exists
clone_repo() {
    local url=$1
    local name=$(basename "$url" .git)
    
    if [ -d "$name" ]; then
        echo "⏭️  Skipping $name (already exists)"
    else
        echo "📦 Cloning $name..."
        git clone --depth 1 "$url"
        echo "✅ Cloned $name"
    fi
}

echo ""
echo "📚 Tier 1: Production-Scale Applications"
echo "----------------------------------------"
clone_repo "https://github.com/metabase/metabase.git"
clone_repo "https://github.com/logseq/logseq.git"
clone_repo "https://github.com/penpot/penpot.git"

echo ""
echo "📚 Tier 2: Foundational Libraries"
echo "---------------------------------"
clone_repo "https://github.com/ring-clojure/ring.git"
clone_repo "https://github.com/weavejester/compojure.git"
clone_repo "https://github.com/tonsky/datascript.git"
clone_repo "https://github.com/day8/re-frame.git"
clone_repo "https://github.com/reagent-project/reagent.git"

echo ""
echo "📚 Tier 3: Infrastructure & Tools"
echo "----------------------------------"
clone_repo "https://github.com/babashka/babashka.git"
clone_repo "https://github.com/clj-kondo/clj-kondo.git"
clone_repo "https://github.com/riemann/riemann.git"
clone_repo "https://github.com/xtdb/xtdb.git"

echo ""
echo "📚 Tier 4: Full-Stack Frameworks"
echo "---------------------------------"
clone_repo "https://github.com/fulcrologic/fulcro.git"
clone_repo "https://github.com/jacobobryant/biff.git"

echo ""
echo "📚 Tier 5: Utility Libraries (Metosin)"
echo "--------------------------------------"
clone_repo "https://github.com/metosin/malli.git"
clone_repo "https://github.com/metosin/reitit.git"
clone_repo "https://github.com/metosin/jsonista.git"
clone_repo "https://github.com/metosin/muuntaja.git"

echo ""
echo "📚 Tier 5: Utility Libraries (Weavejester)"
echo "------------------------------------------"
clone_repo "https://github.com/weavejester/integrant.git"
clone_repo "https://github.com/weavejester/hiccup.git"
clone_repo "https://github.com/weavejester/ragtime.git"

echo ""
echo "📚 Tier 5: Utility Libraries (Other)"
echo "-------------------------------------"
clone_repo "https://github.com/seancorfield/next-jdbc.git"
clone_repo "https://github.com/seancorfield/honeysql.git"
clone_repo "https://github.com/redplanetlabs/specter.git"

echo ""
echo "✨ Done! All repositories cloned to: $REPOS_DIR"
echo ""
echo "📖 Recommended reading order:"
echo "   1. compojure (small, readable macros)"
echo "   2. ring (foundation of Clojure web)"
echo "   3. reagent (ClojureScript patterns)"
echo "   4. datascript (immutable database design)"
echo "   5. re-frame (state management)"
echo "   6. malli/reitit (data-driven design)"
echo "   7. metabase (production architecture)"
