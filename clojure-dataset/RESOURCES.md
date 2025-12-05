# Clojure/ClojureScript Training Dataset Resources

This document catalogs all resources gathered for the comprehensive Clojure/ClojureScript training dataset.

## 1. Core Clojure Language

### 1.1 Language Fundamentals
- **Syntax**: S-expressions, reader macros, special forms
- **Data Structures**: Lists, Vectors, Maps, Sets (immutable, persistent)
- **Namespaces**: require, use, import, refer
- **Functions**: defn, fn, partial, comp, threading macros
- **Destructuring**: Sequential, associative, nested patterns
- **Polymorphism**: Protocols, multimethods, records, types

### 1.2 Clojure Reference Topics
- Special forms: def, if, do, let, quote, var, fn, loop, recur, throw, try
- Reader macros: ', `, ~, ~@, #', #_, ^, @, #()
- Metadata handling
- Java interop: ., .., new, doto, proxy, reify

### 1.3 clojure.spec.alpha
- Predicates and specs: s/def, s/valid?, s/conform
- Spec combinators: s/and, s/or, s/keys, s/coll-of, s/cat, s/alt
- Function specs: s/fdef with :args, :ret, :fn
- Generators and testing: s/gen, s/exercise
- Explain and error handling

## 2. Clojure Style Guide

### 2.1 Source Code Layout
- 2 spaces indentation (no tabs)
- 80 character line limit (soft), 120 (hard)
- Vertically align function arguments
- One space between closing parens

### 2.2 Naming Conventions
- kebab-case for functions and variables
- *earmuffs* for dynamic vars
- bang! suffix for side-effects
- question-mark? suffix for predicates
- ->Type for type constructors
- map->Type for map constructors

### 2.3 Idiomatic Patterns
- Prefer threading macros: ->, ->>
- Use when vs (if x y nil)
- Use when-not vs (if x nil y)
- Use if-let, when-let for binding + conditional
- Avoid anonymous functions for named operations
- Use comp/partial for function composition

## 3. ClojureScript

### 3.1 JavaScript Interop
- js/ namespace for globals
- aget/aset for arrays
- Dot notation for method calls
- #js reader literal for JS objects/arrays
- clj->js and js->clj conversions

### 3.2 Advanced Compilation
- :advanced optimization levels
- Externs files
- :foreign-libs configuration

## 4. Web Frontend Libraries

### 4.1 Reagent
- **Purpose**: React wrapper using Hiccup syntax
- **Components**: Form-1 (functions), Form-2 (closures), Form-3 (lifecycle)
- **State**: r/atom, r/cursor, deref (@) in render triggers re-render
- **Hiccup**: [:tag {:attrs} children...], CSS shortcuts (:div.class#id)
- **Lifecycle**: :component-did-mount, :component-will-unmount, etc.

```clojure
;; Form-1: Simple function component
(defn greeting [name]
  [:h1 "Hello, " name])

;; Form-2: Component with local state
(defn counter []
  (let [count (r/atom 0)]
    (fn []
      [:div
       [:p "Count: " @count]
       [:button {:on-click #(swap! count inc)} "+"]])))

;; Form-3: Full lifecycle control
(defn canvas-component []
  (r/create-class
    {:component-did-mount (fn [this] ...)
     :reagent-render (fn [] [:canvas#my-canvas])}))
```

### 4.2 Re-frame
- **Purpose**: State management framework (6 dominoes)
- **Flow**: Event → Effect Handler → Coeffect → Event Handler → DB → Subscription → View
- **Events**: (rf/dispatch [:event-id data])
- **Handlers**: (rf/reg-event-db :event-id (fn [db [_ data]] ...))
- **Effects**: (rf/reg-event-fx :event-id (fn [{:keys [db]} [_ data]] {:db new-db :dispatch [...]}))
- **Subscriptions**: (rf/reg-sub :sub-id (fn [db _] (:key db)))
- **Views**: (let [data @(rf/subscribe [:sub-id])] [:div data])

```clojure
;; Event registration
(rf/reg-event-db
  :initialize
  (fn [_ _]
    {:users [] :loading? false}))

;; Event with effects
(rf/reg-event-fx
  :fetch-users
  (fn [{:keys [db]} _]
    {:db (assoc db :loading? true)
     :http-xhrio {:method :get
                  :uri "/api/users"
                  :on-success [:users-loaded]
                  :on-failure [:api-error]}}))

;; Subscription with computation
(rf/reg-sub
  :active-users
  :<- [:users]
  (fn [users _]
    (filter :active? users)))
```

## 5. Data Validation

### 5.1 Malli
- **Purpose**: Data-driven schemas with runtime validation
- **Syntax**: Vector-based schema definitions
- **Validation**: m/validate, m/explain
- **Coercion**: Transform data to match schema
- **Generation**: Create test data from schemas

```clojure
(require '[malli.core :as m]
         '[malli.error :as me])

;; Schema definitions
(def User
  [:map
   [:name :string]
   [:email [:re #"^[^\s@]+@[^\s@]+\.[^\s@]+$"]]
   [:age [:and :int [:> 0] [:< 150]]]
   [:roles [:set [:enum :admin :user :guest]]]])

;; Validation
(m/validate User {:name "Alice" :email "alice@example.com" :age 30 :roles #{:user}})
;; => true

;; Error explanation
(-> (m/explain User {:name 123})
    me/humanize)
;; => {:name ["should be a string"], :email ["missing required key"], ...}

;; Function schemas
(def my-fn
  (m/=> [:-> :int :int :int]
        (fn [a b] (+ a b))))
```

## 6. Routing

### 6.1 Reitit
- **Purpose**: Data-driven routing for Clojure/ClojureScript
- **Routes**: Nested vectors with path, data map
- **Path params**: :path-params in request
- **Coercion**: Automatic parameter parsing/validation
- **Middleware**: Ring-compatible middleware chains

```clojure
(require '[reitit.ring :as ring]
         '[reitit.coercion.malli :as malli])

(def routes
  [["/api"
    ["/users" {:get {:handler list-users}
               :post {:handler create-user
                      :parameters {:body User}}}]
    ["/users/:id" {:get {:handler get-user
                         :parameters {:path [:map [:id :int]]}}
                   :put {:handler update-user}
                   :delete {:handler delete-user}}]]])

(def app
  (ring/ring-handler
    (ring/router routes
      {:data {:coercion malli/coercion
              :middleware [wrap-params wrap-json]}})))
```

## 7. Database

### 7.1 next.jdbc
- **Purpose**: Modern JDBC wrapper
- **Connection**: get-datasource, get-connection
- **Queries**: execute!, execute-one!, plan
- **Transactions**: with-transaction
- **Connection pooling**: HikariCP integration

```clojure
(require '[next.jdbc :as jdbc]
         '[next.jdbc.result-set :as rs])

;; Define datasource
(def ds (jdbc/get-datasource
          {:dbtype "postgresql"
           :host "localhost"
           :dbname "mydb"
           :user "user"
           :password "pass"}))

;; Execute queries
(jdbc/execute! ds ["SELECT * FROM users WHERE active = ?" true])

;; Single result
(jdbc/execute-one! ds ["SELECT * FROM users WHERE id = ?" 1])

;; With options
(jdbc/execute! ds ["SELECT * FROM users"]
  {:builder-fn rs/as-unqualified-maps})

;; Transactions
(jdbc/with-transaction [tx ds]
  (jdbc/execute! tx ["UPDATE accounts SET balance = balance - ? WHERE id = ?" 100 1])
  (jdbc/execute! tx ["UPDATE accounts SET balance = balance + ? WHERE id = ?" 100 2]))

;; Reducible result set (lazy, memory efficient)
(into []
  (map :users/name)
  (jdbc/plan ds ["SELECT name FROM users"]))
```

### 7.2 HoneySQL
- **Purpose**: SQL as Clojure data structures
- **Queries**: Maps representing SQL
- **Helpers**: Thread-first friendly functions
- **Parameterization**: Automatic SQL injection prevention

```clojure
(require '[honey.sql :as sql]
         '[honey.sql.helpers :as h])

;; Map-based queries
(sql/format {:select [:id :name :email]
             :from [:users]
             :where [:and
                     [:= :active true]
                     [:> :age 18]]
             :order-by [[:created_at :desc]]
             :limit 10})
;; => ["SELECT id, name, email FROM users WHERE (active = ?) AND (age > ?) ORDER BY created_at DESC LIMIT ?" true 18 10]

;; Helper-based queries
(-> (h/select :id :name)
    (h/from :users)
    (h/where [:= :status "active"])
    (h/order-by [:name :asc])
    sql/format)

;; Insert
(-> (h/insert-into :users)
    (h/columns :name :email)
    (h/values [["Alice" "alice@example.com"]
               ["Bob" "bob@example.com"]])
    sql/format)

;; Update
(-> (h/update :users)
    (h/set {:name "New Name"
            :updated_at :%now})
    (h/where [:= :id 1])
    sql/format)

;; Delete
(-> (h/delete-from :users)
    (h/where [:= :id 1])
    sql/format)
```

### 7.3 XTDB
- **Purpose**: Immutable, bitemporal database with Datalog queries
- **Bitemporality**: Valid-time and transaction-time tracking
- **Queries**: EDN Datalog with :find, :where, :in, :rules
- **Transactions**: put, delete, match, evict operations
- **Sources**: https://v1-docs.xtdb.com/

```clojure
(require '[xtdb.api :as xt])

;; Start node (in-memory for dev)
(def node (xt/start-node {}))

;; Put documents
(xt/submit-tx node
  [[::xt/put {:xt/id :user/1 :name "Alice" :age 30}]
   [::xt/put {:xt/id :user/2 :name "Bob" :age 25}]])
(xt/sync node)

;; Query with Datalog
(xt/q (xt/db node)
      '{:find [?name ?age]
        :where [[?e :name ?name]
                [?e :age ?age]
                [(>= ?age 25)]]})
;; => #{["Alice" 30] ["Bob" 25]}

;; Get entity by ID
(xt/entity (xt/db node) :user/1)
;; => {:xt/id :user/1 :name "Alice" :age 30}

;; Pull syntax
(xt/q (xt/db node)
      '{:find [(pull ?e [:name :age])]
        :where [[?e :xt/id]]})

;; Bitemporal: query at past valid-time
(xt/entity (xt/db node #inst "2024-01-01") :user/1)

;; Entity history
(xt/entity-history (xt/db node) :user/1 :desc {:with-docs? true})

;; Conditional transaction with match
(xt/submit-tx node
  [[::xt/match :user/1 {:xt/id :user/1 :name "Alice" :age 30}]
   [::xt/put {:xt/id :user/1 :name "Alice" :age 31}]])
```

## 8. Application Architecture

### 8.1 Integrant
- **Purpose**: Dependency injection and lifecycle management
- **Config**: EDN map with component keys
- **References**: ig/ref for dependencies
- **Lifecycle**: init-key, halt-key!, suspend-key, resume-key

```clojure
(require '[integrant.core :as ig])

;; Configuration
(def config
  {:db/connection {:host "localhost" :port 5432 :name "mydb"}
   :http/server {:port 3000 :handler (ig/ref :app/handler)}
   :app/handler {:db (ig/ref :db/connection)}})

;; Initialize components
(defmethod ig/init-key :db/connection [_ {:keys [host port name]}]
  (create-connection-pool host port name))

(defmethod ig/init-key :http/server [_ {:keys [port handler]}]
  (start-server {:port port :handler handler}))

(defmethod ig/init-key :app/handler [_ {:keys [db]}]
  (create-ring-handler db))

;; Shutdown components
(defmethod ig/halt-key! :db/connection [_ conn]
  (.close conn))

(defmethod ig/halt-key! :http/server [_ server]
  (.stop server))

;; Start system
(def system (ig/init config))

;; Stop system
(ig/halt! system)
```

### 8.2 Ring
- **Purpose**: HTTP server abstraction
- **Handlers**: Functions taking request, returning response
- **Middleware**: Higher-order functions wrapping handlers
- **Request**: Map with :uri, :request-method, :headers, :body
- **Response**: Map with :status, :headers, :body

```clojure
;; Basic handler
(defn handler [request]
  {:status 200
   :headers {"Content-Type" "text/plain"}
   :body "Hello, World!"})

;; Middleware
(defn wrap-logging [handler]
  (fn [request]
    (println "Request:" (:uri request))
    (let [response (handler request)]
      (println "Response:" (:status response))
      response)))

(defn wrap-json [handler]
  (fn [request]
    (let [response (handler request)]
      (-> response
          (assoc-in [:headers "Content-Type"] "application/json")
          (update :body json/write-str)))))

;; Compose middleware
(def app
  (-> handler
      wrap-json
      wrap-logging))

;; Async handler
(defn async-handler [request respond raise]
  (future
    (try
      (respond {:status 200 :body "Async response"})
      (catch Exception e
        (raise e)))))
```

## 9. Testing

### 9.1 clojure.test
- **Core**: deftest, is, are, testing
- **Fixtures**: use-fixtures for setup/teardown
- **Assertions**: =, thrown?, instance?

```clojure
(require '[clojure.test :refer [deftest is testing are use-fixtures]])

(deftest basic-arithmetic-test
  (testing "addition"
    (is (= 4 (+ 2 2)))
    (is (= 0 (+ -1 1))))
  
  (testing "multiplication"
    (are [x y result] (= result (* x y))
      2 3 6
      0 5 0
      -1 -1 1)))

(deftest exception-test
  (is (thrown? ArithmeticException (/ 1 0))))

;; Fixtures
(defn db-fixture [f]
  (setup-test-db)
  (f)
  (teardown-test-db))

(use-fixtures :each db-fixture)
```

### 9.2 kaocha
- Configuration-driven test runner
- Watch mode, filtering, parallel execution
- Integration with various test frameworks

## 10. Concurrency

### 10.1 Core Concurrency
- **Atoms**: Uncoordinated, synchronous state
- **Refs**: Coordinated, synchronous state (STM)
- **Agents**: Uncoordinated, asynchronous state
- **Vars**: Thread-local bindings

```clojure
;; Atoms
(def counter (atom 0))
(swap! counter inc)
(reset! counter 0)
@counter

;; Refs with STM
(def account-a (ref 1000))
(def account-b (ref 2000))

(dosync
  (alter account-a - 100)
  (alter account-b + 100))

;; Agents
(def logger (agent []))
(send logger conj "Log entry")
(await logger)
@logger
```

### 10.2 core.async
- **Channels**: Communication primitives
- **go blocks**: Lightweight threads
- **Operations**: <!, >!, alts!, timeout

```clojure
(require '[clojure.core.async :refer [go chan <! >! <!! >!! close! alts! timeout]])

;; Basic channel
(def ch (chan 10))

;; Blocking operations (outside go blocks)
(>!! ch "message")
(<!! ch)

;; Non-blocking in go blocks
(go
  (>! ch "async message")
  (let [msg (<! ch)]
    (println "Received:" msg)))

;; Timeout and alts
(go
  (let [[val port] (alts! [ch (timeout 1000)])]
    (if (= port ch)
      (println "Got:" val)
      (println "Timeout!"))))

;; Pipelines
(def input (chan))
(def output (chan))

(go-loop []
  (when-let [v (<! input)]
    (>! output (* v 2))
    (recur)))
```

## 11. Common Patterns

### 11.1 Error Handling
```clojure
;; Try-catch
(try
  (risky-operation)
  (catch ExceptionInfo e
    (handle-app-error (ex-data e)))
  (catch Exception e
    (handle-generic-error e))
  (finally
    (cleanup)))

;; ex-info for rich errors
(throw (ex-info "Operation failed"
         {:type :validation-error
          :field :email
          :value "invalid"}))
```

### 11.2 Component Pattern
```clojure
;; Record-based components
(defprotocol Database
  (query [this sql params])
  (execute [this sql params]))

(defrecord PostgresDB [connection]
  Database
  (query [this sql params]
    (jdbc/execute! connection (into [sql] params)))
  (execute [this sql params]
    (jdbc/execute-one! connection (into [sql] params))))

;; Constructor
(defn ->postgres-db [config]
  (->PostgresDB (jdbc/get-datasource config)))
```

### 11.3 Transducers
```clojure
;; Composable transformations
(def xf
  (comp
    (filter even?)
    (map #(* % 2))
    (take 5)))

;; Apply to collections
(into [] xf (range 100))
;; => [0 4 8 12 16]

;; Apply to channels
(def ch (chan 10 xf))
```

## 12. Build Tools

### 12.1 deps.edn / Clojure CLI
```clojure
{:paths ["src" "resources"]
 :deps {org.clojure/clojure {:mvn/version "1.11.1"}
        metosin/reitit {:mvn/version "0.7.0"}
        metosin/malli {:mvn/version "0.13.0"}}
 :aliases
 {:dev {:extra-paths ["dev"]
        :extra-deps {cider/cider-nrepl {:mvn/version "0.30.0"}}}
  :test {:extra-paths ["test"]
         :extra-deps {lambdaisland/kaocha {:mvn/version "1.87.1366"}}}
  :build {:deps {io.github.clojure/tools.build {:git/tag "v0.9.6"}}
          :ns-default build}}}
```

### 12.2 shadow-cljs (ClojureScript)
```clojure
;; shadow-cljs.edn
{:source-paths ["src"]
 :dependencies [[reagent "1.2.0"]
                [re-frame "1.3.0"]]
 :builds
 {:app {:target :browser
        :output-dir "public/js"
        :asset-path "/js"
        :modules {:main {:init-fn app.core/init}}}}}
```

## Libraries to Include

### Must Have (Core)
- [x] Clojure Core
- [x] clojure.spec.alpha
- [x] Clojure Style Guide

### Frontend
- [x] Reagent
- [x] Re-frame
- [ ] Fulcro (advanced)

### Routing & HTTP
- [x] Reitit
- [x] Ring
- [ ] Compojure (alternative)
- [ ] Pedestal (alternative)

### Data
- [x] Malli
- [x] next.jdbc
- [x] HoneySQL
- [x] XTDB (bitemporal database)

### Architecture
- [x] Integrant
- [ ] Mount
- [ ] Component

### Concurrency
- [x] core.async (basic)
- [ ] Manifold

### Testing
- [x] clojure.test
- [ ] Kaocha

### Build
- [x] deps.edn
- [x] shadow-cljs

## Dataset Structure

The final dataset will contain:
1. **Concept explanations**: Clear explanations of Clojure concepts
2. **Code examples**: Idiomatic code snippets with explanations
3. **Best practices**: Style guide recommendations
4. **Library usage**: How to use popular libraries
5. **Patterns**: Common design patterns in Clojure
6. **Troubleshooting**: Common errors and solutions
7. **Comparisons**: Clojure vs other languages for concepts
