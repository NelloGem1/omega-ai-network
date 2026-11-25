# 💻 COMPUTER SCIENCE & INFORMATION TECHNOLOGY — MASTER FIELD MAP
*A comprehensive map of the entire CS/IT landscape: what each field is, the core concepts, tools, technologies, applications, prerequisites, and how the fields interconnect. Companion to `math_logic_map.md` and `ml_pipeline_guide.md` in this directory.*

> Version note: tool versions verified against official release pages as of **November 2026** (see Sources). Languages and frameworks move fast — check `endoflife.date` for current support windows before pinning versions.

---

## TABLE OF CONTENTS

1. [The Big Picture — How CS/IT Fits Together](#1-the-big-picture)
2. [Programming & Software Development](#2-programming--software-development)
3. [Algorithms & Data Structures](#3-algorithms--data-structures)
4. [Computer Architecture & Systems](#4-computer-architecture--systems)
5. [Data & Information Systems](#5-data--information-systems)
6. [Networking & Infrastructure](#6-networking--infrastructure)
7. [Specialized CS Fields](#7-specialized-cs-fields)
8. [Career Tracks & Specialization Map](#8-career-tracks)
9. [Beginner → Advanced Learning Roadmap](#9-learning-roadmap)
10. [Sources](#10-sources)

---

## 1. THE BIG PICTURE

CS is the theory of computation; IT is the engineering of systems that apply it. Everything below hangs off a few load-bearing ideas:

- **Abstraction layers**: transistors → logic gates → machine code → assembly → C → managed runtimes → application code. Each layer hides complexity below it.
- **The hardware/software contract**: the CPU executes instructions; compilers and interpreters translate high-level code into that instruction stream.
- **Data in motion vs. data at rest**: networks move data, storage persists it, databases structure it.
- **Scale forces trade-offs**: correctness vs. speed, consistency vs. availability, simplicity vs. flexibility — almost every design decision in this map is one of these trade-offs.

Master mental model:

```
APPLICATIONS (web apps, ML, games, OS)
    ↓ APIs / libraries / frameworks
LANGUAGES & RUNTIMES (Python, C++, JVM, Go, Node)
    ↓ compilation / interpretation
SYSTEM SOFTWARE (OS, compilers, DBMS, hypervisors)
    ↓ syscalls / drivers
HARDWARE (CPU, GPU, RAM, storage, NIC, sensors)
    ↑ connected by NETWORKS + PROTOCOLS
```

---

## 2. PROGRAMMING & SOFTWARE DEVELOPMENT

### 2.1 Core Concepts (language-agnostic)

| Concept | What it means | Why it matters |
|---|---|---|
| Variables & types | Named storage, static vs. dynamic typing | Memory layout, safety, performance |
| Control flow | `if/else`, loops, `switch`, exceptions | Program structure |
| Functions & scope | Reusable units, closures, recursion | Code organization, stack behavior |
| Data structures | Arrays, lists, maps, sets, trees, graphs | The bridge to §3 |
| OOP | Classes, inheritance, polymorphism, encapsulation | Modeling real systems; see design patterns below |
| FP | Pure functions, immutability, higher-order fns | Concurrency safety, testability |
| Concurrency | Threads, async/await, actors, coroutines | Modern multicore reality |
| Memory management | Stack vs. heap, GC vs. manual, RAII | Bugs, leaks, performance |
| Error handling | Exceptions, Result types, error codes | Robustness |
| Testing | Unit → integration → E2E, TDD, property-based | Confidence at scale |
| Debugging | breakpoints, profiling, logging, tracing | Finding what you can't see |

### 2.2 Major Languages (verified Nov 2026)

**Python 3.15.x** (current stable line; 3.14 and 3.13 still in security support; 3.10 reached EOL Oct 2026)
- *Paradigm*: multi-paradigm, dynamically typed, interpreted (CPython), JIT experiments ongoing
- *Strengths*: readability, huge ecosystem (PyPI ~500k+ packages), ML/data dominance, scripting, glue code
- *Weaknesses*: GIL limits CPU parallelism; slower than compiled languages
- *Key tools*: `venv`/`uv`, `pip`, `pytest`, `ruff`, `mypy`, `black`, `pandas`, `numpy`, `PyTorch`/`TensorFlow`, `Django`/`FastAPI`/`Flask`
- *Applications*: data science, ML, web backends, automation, scripting, education
- *Prereqs*: basic math, terminal literacy

**C (C17/C23)** — the lingua franca of systems
- *Paradigm*: imperative, statically typed, compiled, manual memory
- *Strengths*: minimal abstraction over hardware, ubiquitous, tiny runtime
- *Weaknesses*: memory bugs, undefined behavior, no safety net
- *Key tools*: `gcc`/`clang`, `make`/`cmake`, `gdb`, `valgrind`, `AddressSanitizer`
- *Applications*: OS kernels, embedded, compilers, drivers, performance-critical libraries
- *Prereqs*: comfort with pointers and bitwise thinking; ideally some assembly exposure

**C++ (C++23/26)** — C plus abstraction without runtime cost
- *Paradigm*: multi-paradigm (OOP, generic, functional-lite), zero-overhead principle
- *Strengths*: performance + modern features (RAII, templates, concepts, ranges, coroutines)
- *Weaknesses*: complexity, steep learning curve, footguns remain
- *Key tools*: `cmake`, `vcpkg`/`conan`, `clang`/`gcc`, `gdb`, `clang-tidy`, `sanitizers`, `Catch2`/`GoogleTest`
- *Applications*: game engines, browsers, trading systems, HPC, graphics, databases
- *Prereqs*: solid C, then modern C++ features incrementally

**Java (LTS: 21, 25; current non-LTS ~27)** — enterprise & Android
- *Paradigm*: OOP, statically typed, JVM bytecode, JIT-compiled, garbage collected
- *Strengths*: portability ("write once"), mature ecosystem, excellent tooling, strong typing
- *Weaknesses*: JVM memory footprint, verbosity, GC pauses (mitigated by ZGC/Shenandoah)
- *Key tools*: `javac`, `Maven`/`Gradle`, `Spring Boot`, `JUnit`, `IntelliJ IDEA`, `jshell`, `jlink`/`jpackage`
- *Applications*: enterprise backends, Android, big-data (Hadoop/Spark/Kafka), microservices
- *Prereqs*: OOP fundamentals; JVM memory model for advanced work

**JavaScript / TypeScript 7.x** — the web's native tongue
- *Paradigm*: multi-paradigm, dynamically typed (JS), optionally statically typed (TS), single-threaded event loop with Web Workers/Atomics
- *Strengths*: runs everywhere (browser, Node.js, edge, mobile via React Native, desktop via Electron/Tauri); largest package registry (npm)
- *Weaknesses*: weird coercion rules, `this` pitfalls, ecosystem churn
- *Key tools*: `Node.js` (LTS), `npm`/`pnpm`/`yarn`, `Vite`, `TypeScript`, `React`/`Vue`/`Svelte`, `Express`/`Fastify`/`NestJS`, `Vitest`/`Jest`, `ESLint`
- *Applications*: web frontends, web backends (Node), full-stack, CLI tools, serverless/edge functions
- *Prereqs*: HTML/CSS for web; the event loop model is the core mental model

**Rust 1.100.x** (latest ~1.100, Nov 2026) — safety without GC
- *Paradigm*: systems language, ownership + borrow checker, zero-cost abstractions, fearless concurrency
- *Strengths*: memory safety at C++ speed, excellent tooling (`cargo`, `rustup`, `clippy`)
- *Weaknesses*: steep ownership learning curve, compile times, smaller ecosystem than C++
- *Key tools*: `cargo`, `rustfmt`, `clippy`, `tokio` (async), `axum`, `serde`, `wasm-pack`
- *Applications*: systems tools, WASM, blockchain, CLI tools, embedded, performance backends (Discord, Cloudflare)
- *Prereqs*: C or C++ helps enormously; ownership model is the gate

**Go 1.27.x** (latest stable ~1.27.4, Nov 2026) — simplicity at scale
- *Paradigm*: statically typed, compiled, garbage collected, CSP-inspired concurrency (goroutines + channels)
- *Strengths*: fast compile, single binary deploys, built-in concurrency, huge stdlib
- *Weaknesses*: less expressive than Rust/C++, no generics until recently, opinionated
- *Key tools*: `go` toolchain, `go mod`, `gofmt`, `gin`/`echo`/`chi`, `grpc`, `Docker`/`K8s` ecosystem, `prometheus`/`pprof`
- *Applications*: cloud-native microservices, CLI tools, infrastructure (Docker, Kubernetes, Terraform are Go), networking tools
- *Prereqs*: C-family syntax familiarity; concurrency concepts

**Other notable languages**
- **Swift** — Apple platforms, memory-safe, modern concurrency
- **Kotlin** — Android + JVM, concise, null-safety, multiplatform
- **C#/.NET 10** — Microsoft ecosystem, game dev (Unity), enterprise, ASP.NET
- **PHP 8.x** — still powers ~75% of web servers; Laravel dominates legacy web
- **Ruby** — Rails for rapid web dev; declining but stable niche
- **Zig** — emerging C competitor, explicit control, no hidden control flow
- **Assembly (x86-64, ARM64)** — not a "language" for apps but essential for architecture/debugging (§4)

### 2.3 Software Engineering Practices

- **Version control**: Git (dominant) — commits, branches, merges, rebases, tags; hosting on GitHub/GitLab/Bitbucket; `git-flow` vs. trunk-based development
- **Build systems**: `make`, `CMake`, `Bazel` (Google-scale), `Maven`/`Gradle`, `cargo`, language-native tools
- **Package management**: `npm`/`pnpm`, `pip`/`uv`, `cargo`, `go mod`, `nuget`, `apt`/`brew`
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI, ArgoCD — build → test → deploy pipelines
- **Code review**: pull requests, pair programming, static analysis (`eslint`, `ruff`, `SonarQube`)
- **Documentation**: README, ADRs (architecture decision records), API docs (OpenAPI/Swagger), docstrings
- **Project management**: Agile/Scrum/Kanban, issue trackers (Linear, Jira, GitHub Issues)

### 2.4 Design Patterns

**Creational**: Factory, Abstract Factory, Singleton (use sparingly), Builder, Prototype
**Structural**: Adapter, Bridge, Composite, Decorator, Facade, Proxy
**Behavioral**: Observer, Strategy, Command, State, Template Method, Iterator, Mediator
**Architectural patterns**: MVC, MVP, MVVM, layered architecture, hexagonal/clean architecture, microservices, event-driven, serverless
- *Source of truth*: "Design Patterns" (Gamma et al., 1994) is dated but foundational; "A Philosophy of Software Design" (Ousterhout) and "Clean Architecture" (Martin) are modern classics.

### 2.5 Testing & Debugging

| Level | Scope | Tools |
|---|---|---|
| Unit | single function/class | `pytest`, `JUnit`, `vitest`, `Catch2`, `go test` |
| Integration | component interactions | test containers, `testcontainers` |
| E2E | whole system | Playwright, Cypress, Selenium |
| Property-based | generated inputs | `hypothesis` (Py), `quickcheck` |
| Performance | benchmarks | `criterion` (Rust), `pytest-benchmark`, `k6` |

- **Debugging tools**: `gdb`/`lldb`, IDE debuggers, `pdb`/`ipdb`, Chrome DevTools, `strace`, core dumps
- **Observability** (production debugging): structured logging, metrics (`Prometheus`), tracing (`OpenTelemetry`, Jaeger), profiling (`pprof`, `perf`, `py-spy`, `flamegraphs`)

### 2.6 DevOps & SRE

- **Infrastructure as Code**: Terraform, Pulumi, Ansible, CloudFormation
- **Containers**: Docker, Podman, containerd (see §6.4)
- **Orchestration**: Kubernetes, Docker Swarm, Nomad, serverless (AWS Lambda, Cloud Run, Vercel)
- **Monitoring**: Prometheus + Grafana, Datadog, New Relic, ELK/Loki stacks
- **Reliability**: SLOs/SLIs, error budgets, incident response, chaos engineering
- **Security in pipeline**: SAST/DAST, dependency scanning (`npm audit`, `dependabot`), secrets management (Vault)

**Prereqs**: programming fluency → version control → Linux basics → networking basics → cloud.

---

## 3. ALGORITHMS & DATA STRUCTURES

The mathematical core of CS. Everything in §2 and beyond is built from these.

### 3.1 Algorithmic Paradigms

- **Brute force** — try everything; fine for small n
- **Divide & conquer** — split, solve, merge (merge sort, quicksort, FFT)
- **Greedy** — locally optimal choice hoping for global (Dijkstra, Huffman)
- **Dynamic programming** — memoization/tabulation over overlapping subproblems (knapsack, LCS, edit distance)
- **Backtracking** — DFS with pruning (N-queens, Sudoku)
- **Graph traversal** — BFS, DFS, Dijkstra, A*, topological sort
- **Randomized** — quicksort pivot, hashing, Monte Carlo methods
- **Streaming/online** — process data once, bounded memory

### 3.2 Core Data Structures

| Structure | Access | Insert | Use cases |
|---|---|---|---|
| Array / contiguous list | O(1) index | O(n) insert | cache-friendly storage, matrices |
| Linked list | O(n) | O(1) at ends | queues, LRU caches |
| Stack / Queue | O(1) ends | O(1) | call stacks, BFS, undo, buffers |
| Hash table / map | O(1) avg | O(1) avg | indexing, caching, dedup; *every language's `dict`/`Map`* |
| Binary search tree / balanced BST | O(log n) | O(log n) | ordered data; `std::map`, `TreeMap` |
| Heap / priority queue | O(1) peek, O(log n) pop | O(log n) | scheduling, Dijkstra, top-k |
| Trie | O(k) per key | O(k) | autocomplete, routing tables, IP lookup |
| Bloom filter | O(1), false positives | O(1) | "definitely not present" checks (CDN, caches) |
| Disjoint-set (union-find) | ~O(1) | ~O(1) | Kruskal's MST, connected components |
| Segment tree / Fenwick | O(log n) range ops | O(log n) | range queries, competitive programming |

### 3.3 Trees

- **Binary trees**, **BSTs**, **AVL/red-black trees** (self-balancing; Java's `TreeMap`, C++ `std::map`)
- **Heaps** — binary heap, pairing heap
- **B-trees / B+ trees** — disk-friendly; the backbone of database indexes (§5)
- **Tries** — prefix trees
- **Segment trees, Fenwick trees** — range queries
- **Expression/parse trees** — ASTs (§7.1 compilers), calculators
- **Game trees / decision trees** — AI, ML (§ML companion doc)
- **kd-trees, R-trees** — spatial data, geo queries, vector search

### 3.4 Graphs

- **Representations**: adjacency matrix vs. adjacency list (list wins except dense graphs)
- **Traversals**: BFS (shortest unweighted), DFS (cycles, topo sort, connected components)
- **Shortest paths**: Dijkstra (non-negative weights), Bellman-Ford (negatives), Floyd-Warshall (all pairs), A* (heuristic-guided, pathfinding)
- **MST**: Kruskal, Prim
- **Flow networks**: Ford-Fulkerson, max-flow/min-cut
- **Graph algorithms in practice**: PageRank, social-network analysis, dependency resolution (package managers!), scheduling, compiler optimization

### 3.5 Sorting & Searching

- **Sorting**: bubble/selection/insertion (O(n²) — teaching only), merge sort (stable, O(n log n)), quicksort (fast average, O(n²) worst), heapsort (O(n log n) guaranteed), radix sort (linear for fixed-width keys), `sort`/`sorted` builtins in every language
- **Searching**: linear O(n), binary O(log n) (requires sorted data), hashing O(1) avg, interpolation search
- **Key insight**: complexity analysis (Big-O) lets you predict behavior at scale — learn it early

### 3.6 Complexity Theory (theory side)

- **P vs NP** — the most famous open problem in CS; implications for cryptography, optimization, ML
- **NP-completeness** — traveling salesman, SAT, graph coloring; guides when to use heuristics/approximation
- **Big-O / amortized / average vs. worst case**
- **Lower bounds, reductions**
- **Space-time trade-offs** — e.g., hash tables trade memory for speed

### 3.7 Advanced Topics

- **String algorithms**: KMP, Rabin-Karp, suffix trees/arrays, rolling hashes, regex engines
- **Numerical algorithms**: FFT, numerical integration, linear algebra (links to math map)
- **Probabilistic data structures**: Bloom filters, HyperLogLog, Count-Min sketch, LSH — approximate answers at massive scale
- **Computational geometry**: convex hulls, closest pair, Voronoi diagrams
- **Randomized algorithms**: Monte Carlo vs. Las Vegas, expected-case analysis

**Prereqs**: algebra (loops, recursion), basic proof skills; math map companion for formalization.

---

## 4. COMPUTER ARCHITECTURE & SYSTEMS

### 4.1 Hardware Fundamentals

- **CPU**: ALU, control unit, registers, instruction pipeline, superscalar execution, branch prediction, out-of-order execution
- **Instruction set architectures (ISAs)**: x86-64 (desktop/server dominant), ARM64 (mobile, Apple Silicon, servers growing), RISC-V (open ISA, education & embedded)
- **Cores & parallelism**: multicore, SIMD (vector instructions), SMT/hyperthreading, big.LITTLE mobile designs
- **Memory hierarchy**: registers → L1/L2/L3 cache → RAM → NVMe SSD → HDD. Cache lines, cache coherence (MESI), prefetching. *This is why "cache-friendly" code is 10-100x faster.*
- **Storage**: NAND flash, SSD controllers (FTL), wear leveling, HDDs, optical (legacy), persistent memory (Intel Optane discontinued but concept lives)
- **Buses & I/O**: PCIe, USB, SATA/NVMe, interrupts, DMA — how devices talk to CPU
- **GPU**: thousands of small cores for data-parallel work; CUDA (NVIDIA), ROCm (AMD), Metal (Apple), Vulkan/WebGPU (cross-platform); tensor cores for ML
- **Accelerators**: TPUs/NPUs for ML inference, FPGAs, ASICs
- **Embedded systems**: microcontrollers (ARM Cortex-M, AVR, ESP32, RISC-V), real-time constraints, bare-metal vs. RTOS (FreeRTOS, Zephyr)

### 4.2 Assembly Language

- Not what you write apps in — what you read when things break
- **x86-64 AT&T vs. Intel syntax**, calling conventions, stack frames
- **ARM64 assembly** for mobile/Apple Silicon
- Tools: `objdump`, `gdb`, `radare2`/`rizin`, `ghidra` (NSA's open-source RE suite)
- Critical for: reverse engineering, exploit dev, performance debugging, understanding what compilers emit

### 4.3 Operating Systems

- **Core concepts**: processes vs. threads, virtual memory (paging, segmentation), address spaces, context switching, system calls, interrupts/exceptions
- **Scheduling**: CFS (Linux), priorities, real-time scheduling
- **Memory management**: paging, TLB, swapping, `mmap`, kernel memory allocators (slab)
- **Filesystems**: ext4, XFS, Btrfs, APFS, NTFS, FAT/exFAT; VFS layer; journaling
- **I/O**: drivers, device files, `read/write/ioctl`, async I/O (io_uring, epoll/kqueue)
- **Security**: users/permissions, capabilities, namespaces, seccomp, SELinux/AppArmor
- **Synchronization**: mutexes, semaphores, condition variables, futexes, spinlocks; deadlock/starvation/livelock
- **Major OSes**: Linux (kernel ~6.x; distros: Ubuntu, Debian, Fedora, Arch), Windows (NT kernel), macOS (XNU = Mach + BSD), *BSDs, and embedded RTOSes
- **Unix philosophy**: small composable tools, pipes, "everything is a file"

### 4.4 Virtualization & the Cloud Substrate

- **Hypervisors**: Type 1 (bare-metal: KVM, Xen, ESXi, Hyper-V) vs. Type 2 (hosted: VirtualBox, VMware Workstation, QEMU)
- **VM mechanics**: hardware virtualization extensions (Intel VT-x, AMD-V), virtual memory → guest physical → host physical, virtio drivers
- **Containers** (OS-level virtualization): namespaces + cgroups; see Docker in §6.4
- **Cloud models**: IaaS/PaaS/SaaS; major providers AWS, Azure, GCP, plus Oracle/IBM/alibaba; on-prem OpenStack

### 4.5 Compiler & Runtime Theory (bridge to §7.1)

- **Pipeline**: lexing → parsing → semantic analysis → IR → optimization → codegen
- **Key optimizations**: constant folding, inlining, loop unrolling, vectorization, escape analysis, dead code elimination
- **JIT vs. AOT**: Java/.NET/.NET Native, V8 (JS), PyPy, HotSpot tiered compilation
- **Runtime systems**: GC algorithms (mark-sweep, copying, generational), stack unwinding, FFI

**Prereqs**: digital logic → data representation (bits, two's complement, floats) → ISA → OS concepts. CSAPP ("Computer Systems: A Programmer's Perspective") is *the* book — learn C first, then read it.

---

## 5. DATA & INFORMATION SYSTEMS

### 5.1 Databases

**Relational (SQL)**
- **Model**: tables, rows, columns, keys, normalization (1NF–BCNF), denormalization for speed
- **Query language**: SQL — `SELECT/JOIN/WHERE/GROUP BY`, window functions, CTEs, transactions (`ACID`)
- **Engines**: PostgreSQL (open-source king), MySQL/MariaDB, SQLite (embedded), SQL Server, Oracle
- **Internal machinery**: B+ tree indexes, query planner/optimizer, MVCC, WAL (write-ahead log), isolation levels (read committed → serializable), joins (hash/nested-loop/merge)
- **Advanced**: stored procedures, triggers, views, materialized views, partitioning, replication (primary-replica), sharding

**NoSQL**
- **Key-value**: Redis (in-memory, caching/queues), DynamoDB, Memcached
- **Document**: MongoDB, Couchbase, Firestore — JSON-like docs, flexible schema
- **Column-family**: Cassandra, HBase, ScyllaDB — massive write throughput, wide-column
- **Graph**: Neo4j, Amazon Neptune, ArangoDB — relationships as first-class citizens (social nets, fraud rings, recommendations)
- **Search engines** (specialized DBs): Elasticsearch/OpenSearch — inverted indexes, full-text + vector search
- **Time series**: InfluxDB, TimescaleDB, Prometheus TSDB — metrics/logs at scale

**NewSQL / distributed SQL**: CockroachDB, TiDB, YugabyteDB — SQL semantics + horizontal scale
**Vector databases**: pgvector, Pinecone, Weaviate, Milvus, Qdrant — embeddings for RAG/semantic search (§ML companion)

### 5.2 Data Warehousing & Analytics

- **OLTP vs. OLAP**: row-oriented transactional vs. columnar analytical
- **Warehouse architecture**: staging → cleaning → dimensional modeling (star/snowflake schemas) → marts
- **Schemas**: Kimball (bottom-up, dimensional) vs. Inmon (top-down, normalized)
- **ETL/ELT**: Extract-Transform-Load vs. Extract-Load-Transform; `dbt` for transformation-as-code
- **Columnar engines**: ClickHouse, Snowflake, BigQuery, Redshift, DuckDB (embedded analytics)
- **Data lakes/lakehouses**: object storage (S3) + Parquet/ORC/Avro + Delta Lake/Iceberg/Hudi (ACID on lake)
- **BI tools**: Tableau, Power BI, Looker, Metabase, Superset

### 5.3 Big Data & Distributed Processing

- **Hadoop ecosystem** (legacy but instructive): HDFS, MapReduce, YARN, Hive, HBase
- **Spark** — in-memory distributed compute; DataFrames, Spark SQL, MLlib, Structured Streaming; the industry standard for batch/stream ETL
- **Streaming**: Kafka (distributed log — the backbone of real-time data), Flink, Spark Streaming, Kinesis
- **Message queues**: RabbitMQ, NATS, Redis Streams, SQS — decoupling services
- **Orchestration**: Airflow, Dagster, Prefect — scheduling data pipelines
- **Coordination**: ZooKeeper, etcd — consensus for distributed systems (§6.3)

### 5.4 Data Engineering & Data Science

- **Data engineering**: ingestion, pipelines, quality (Great Expectations, dbt tests), governance, cataloging (DataHub, Amundsen)
- **Data science**: see `ml_pipeline_guide.md`; stack = Python/R + pandas/polars + notebooks (Jupyter, Deepnote) + viz (matplotlib, seaborn) + ML (scikit-learn, XGBoost, PyTorch)
- **Analytics engineering**: SQL-heavy middle ground between eng and DS
- **MLOps**: model versioning (MLflow), feature stores (Feast), deployment, monitoring/drift

### 5.5 Information Retrieval & Search

- **IR fundamentals**: inverted index, TF-IDF, BM25, vector space model, PageRank
- **Modern retrieval**: dense embeddings, hybrid search (keyword + vector), reranking (cross-encoders)
- **Applications**: web search, enterprise search, RAG for LLMs, recommender systems, e-commerce faceted search
- **Tools**: Elasticsearch, OpenSearch, Solr, Typesense, Meilisearch, Vespa

### 5.6 Knowledge Representation

- **Databases → knowledge graphs**: RDF, SPARQL, OWL, property graphs (Neo4j's Cypher)
- **Ontologies & taxonomies** for data integration and enterprise search

**Prereqs**: relational algebra → SQL → Linux/CLI → Python → distributed systems concepts for scale-out topics.

---

## 6. NETWORKING & INFRASTRUCTURE

### 6.1 Computer Networks

- **Layered models**: OSI (7 layers, academic) vs. TCP/IP (4 layers, practical)
- **Physical/link**: Ethernet, Wi-Fi (802.11), fiber, coax — CSMA/CD, switching vs. routing
- **Network layer**: IP (IPv4 exhaustion → IPv6), subnets/CIDR, NAT, ICMP/ping, ARP
- **Transport**: TCP (reliable, ordered — handshake, congestion control, retransmission) vs. UDP (fast, lossy — DNS, streaming, gaming); QUIC (HTTP/3, UDP-based, modern)
- **Application**: HTTP/HTTPS, DNS, DHCP, SMTP/IMAP/POP3, SSH, FTP/SFTP, WebSocket, gRPC
- **Core concepts**: latency vs. bandwidth, jitter, packet loss, MTU, routing (BGP, OSPF, RIP), firewalls, NAT traversal, CDN
- **Tools**: `curl`, `dig`/`nslookup`, `traceroute`/`mtr`, Wireshark/tshark, `nmap` (see TOOLS.md), `iptables`/`nftables`, `ss`/`netstat`

### 6.2 Security Networking (defensive side)

- TLS/SSL (handshake, certificates, PKI), VPNs (WireGuard, OpenVPN, IPsec), proxies, zero-trust architecture
- See `websec_research/` and `crypto_research/` in home directory for applied depth

### 6.3 Distributed Systems

- **Fundamental challenges**: partial failure, no global clock, network partitions — *"the network is reliable" is the fallacy that breaks everything*
- **Consistency models**: strong vs. eventual; CAP theorem (consistency, availability, partition tolerance — pick 2 under partition)
- **Consensus**: Paxos, Raft (etcd, Consul, TiKV), Byzantine fault tolerance
- **Replication**: leader-follower, multi-leader, leaderless (Dynamo-style); sync vs. async
- **Sharding/partitioning**: horizontal scale strategies, consistent hashing
- **Distributed transactions**: 2PC, sagas, outbox pattern; exactly-once is a lie — it's effectively-once via idempotency
- **Time**: logical clocks (Lamport, vector), TrueTime (Spanner), clock skew problems
- **Patterns**: microservices, service mesh (Istio/Linkerd), API gateways, sidecars, event sourcing, CQRS
- **Failure handling**: retries with backoff+jitter, circuit breakers, bulkheads, timeouts everywhere, health checks, chaos engineering
- **Key reads**: "Designing Data-Intensive Applications" (Kleppmann) — *the* book; DDIA covers most of §5 too

### 6.4 Virtualization, Containers & Cloud

- **Containers**: images (layered, immutable), containers (process isolation), registries (Docker Hub, GHCR, ECR); Docker/Podman/Buildah; rootless containers
- **Orchestration**: Kubernetes — pods, services, deployments, ReplicaSets, StatefulSets, ingress, ConfigMaps/Secrets, Helm charts, operators; K8s is the industry standard
- **Serverless**: FaaS (Lambda, Cloud Functions, Cloud Run), event-driven, cold starts, pay-per-invocation
- **Edge computing**: CDN workers (Cloudflare Workers), edge functions, low-latency geo-distribution
- **Cloud architecture**: regions/AZs, VPCs, IAM, load balancers, autoscaling groups, managed services (RDS, S3, SQS)
- **Multi-cloud & hybrid**: portability trade-offs, FinOps (cloud cost optimization)
- **Infrastructure as Code**: Terraform (declarative), Pulumi (programmatic), Ansible (config mgmt), Crossplane

### 6.5 APIs & Integration

- **API styles**: REST (resources, HTTP verbs, stateless), GraphQL (client-shaped queries), gRPC (protobuf, HTTP/2, streaming), WebSockets (bidirectional), Webhooks (callbacks), SOAP (legacy enterprise)
- **API design**: versioning, pagination, rate limiting, idempotency keys, HATEOAS, OpenAPI spec
- **Auth**: API keys, OAuth 2.0/OIDC, JWTs, mTLS, API gateways
- **Serialization**: JSON, YAML, TOML, Protocol Buffers, Avro, MessagePack
- **Webhooks & event-driven integration**: pub/sub, webhooks, event buses

**Prereqs**: TCP/IP basics → HTTP → Linux CLI → one cloud provider → Kubernetes for production depth.

---

## 7. SPECIALIZED CS FIELDS

### 7.1 Compilers & Language Implementation

- **Front end**: lexer/parser (recursive descent, LR/LL), ASTs, symbol tables, type checking, semantic analysis
- **Middle end**: IRs (SSA form), optimization passes, SSA construction
- **Back end**: instruction selection, register allocation, instruction scheduling, codegen
- **Runtime**: GC, JIT compilation, FFI, bytecode VMs (JVM, CPython, BEAM/Erlang, WASM)
- **Formal tools**: LLVM (the dominant compiler infrastructure), ANTLR (parser generator), Bison/Flex, tree-sitter (used by GitHub for syntax highlighting!)
- **Parsing in practice**: every linter, formatter, and IDE feature is a parser problem
- **Prereqs**: automata theory → formal languages → strong PL/systems background; "Crafting Interpreters" (Nystrom) is the best entry

### 7.2 Computer Graphics & Visualization

- **Pipeline**: model → vertex shader → rasterization → fragment shader → framebuffer; modern GPU pipeline (Vulkan/D3D12/Metal/WebGPU)
- **Math**: linear algebra (matrices, vectors, quaternions), projective geometry, homogeneous coordinates
- **Rendering**: rasterization vs. ray tracing; shading models (Phong/BRDF); global illumination; shadows; post-processing
- **APIs**: OpenGL (legacy but ubiquitous), Vulkan (explicit, modern), DirectX 12, Metal (Apple), WebGPU (web standard)
- **Game engines**: Unity (C#), Unreal (C++), Godot (GDScript/C#), Bevy (Rust), custom engines
- **Domains**: real-time graphics, scientific visualization, CAD, digital twins, VFX (Houdini), film rendering (RenderMan, Arnold)
- **Prereqs**: linear algebra + calculus → C/C++ or Rust → GPU APIs

### 7.3 Human-Computer Interaction (HCI)

- **Core topics**: usability heuristics (Nielsen's 10), cognitive load, Fitts's law, interaction paradigms (GUI, CLI, TUI, voice, AR/VR, brain-computer)
- **Design process**: user research (interviews, contextual inquiry), personas, journey maps, wireframing, prototyping (Figma), usability testing, A/B testing, accessibility (WCAG)
- **Input systems**: touch, gesture, eye-tracking, haptics
- **Emerging**: AR/VR (Vision Pro, Quest, WebXR), conversational UI, AI-augmented interfaces
- **Tools**: Figma, Framer, Principle; hot-swap testing on real users beats theory
- **Bridge fields**: UX design, product design, accessibility engineering, design systems

### 7.4 Game Development

- **Architecture**: game loop, entity-component-system (ECS), scene graphs, state machines, asset pipelines
- **Systems**: physics engines (Box2D, PhysX, Jolt), animation (skeletal, IK), pathfinding (navmeshes, A*), networking (client-server, lockstep, rollback netcode)
- **Rendering**: see §7.2; engines handle most of it
- **Content**: 3D modeling (Blender, Maya), texturing, audio (FMOD, Wwise), shaders
- **Engines**: Unity, Unreal Engine, Godot, custom; mobile (Unity dominates), console exclusivity
- **Monetization/business**: live-ops, F2P economies, esports — game dev is as much production management as code
- **Prereqs**: C++ or C# → math (linear algebra essential) → engine-specific learning

### 7.5 Quantum Computing

- **Basics**: qubits, superposition, entanglement, quantum gates, measurement collapse, no-cloning theorem
- **Algorithms**: Shor's (factoring → threatens RSA), Grover's (search speedup), quantum Fourier transform, variational algorithms (VQE, QAOA)
- **Hardware**: superconducting qubits (IBM, Google), trapped ions (IonQ, Quantinuum), photonic, neutral atoms, annealers (D-Wave)
- **Software stack**: Qiskit (IBM), Cirq (Google), PennyLane (ML integration), Q# (Microsoft); quantum simulators for small circuits
- **NISQ era reality**: noisy, ~1000 qubits, error correction unsolved at scale — hype vs. reality check needed
- **Applications (near-term)**: optimization, simulation (chemistry, materials), ML subroutines; cryptography impact is the big long-term story
- **Prereqs**: linear algebra (complex vector spaces) + probability + basic quantum mechanics

### 7.6 Theory of Computation

- **Formal languages & automata**: regular languages (DFAs/NFAs → regex), context-free (pushdown automata → parsing), decidability, Turing machines
- **Computability**: Turing-complete languages, halting problem, Rice's theorem, reductions
- **Complexity classes**: P, NP, PSPACE, EXP; NP-completeness proofs
- **Logic**: propositional & predicate logic, proof systems, Gödel's incompleteness
- **Why it matters**: what computers *can't* do; foundations of compilers, security (crypto relies on hardness assumptions), algorithms
- **Prereqs**: discrete math → logic → automata theory; companion to `math_logic_map.md`

### 7.7 Formal Methods & Verification

- **Model checking**: exhaustively verify finite-state systems (SPIN, NuSMV, TLA+)
- **Theorem proving**: Coq, Isabelle/HOL, Lean 4 *(installed on this system at ~/.elan/bin/lake)*, Agda/Idris (dependent types)
- **Specification languages**: TLA+ (Amazon uses it for DynamoDB/S3 design!), Alloy
- **Program verification**: Dafny, Why3, Frama-C; verified compilers (CompCert)
- **Applications**: aerospace (DO-178C), OS kernels (seL4 verified microkernel), crypto protocols, smart contracts
- **Practical value**: finding bugs before deployment in systems where failure is catastrophic

### 7.8 Other Specialized Areas

- **Bioinformatics**: sequence alignment (BLAST), genome assembly, phylogenetics, structural biology tools
- **Computational science**: HPC, numerical simulation, CFD, weather modeling (GPU-accelerated now), MPI/OpenMP
- **Cryptography**: symmetric (AES), asymmetric (RSA, ECC), hashes, protocols (TLS), zero-knowledge proofs; see `crypto_research/`
- **Information theory**: entropy, compression (Huffman, LZ77, arithmetic coding), channel capacity, error-correcting codes — the math of "how much can a channel carry"
- **Programming language theory**: type systems, lambda calculus, category theory connections
- **Computer vision**: image classification/detection, CNNs → transformers; OpenCV, PyTorch, ONNX runtime
- **Robotics**: ROS/ROS2, SLAM, motion planning, control theory, sensor fusion
- **Embedded/IoT**: microcontrollers, RTOS, edge AI (TinyML), protocols (MQTT, Zigbee, BLE)

---

## 8. CAREER TRACKS & SPECIALIZATION MAP

| Track | Core stack | Fields touched |
|---|---|---|
| Backend engineer | Python/Go/Java + SQL + Linux + cloud | §2, §5, §6 |
| Frontend engineer | TypeScript + React/Vue + CSS + browser APIs | §2 (JS/TS), §6 (HTTP) |
| Full-stack | both of the above + DevOps basics | §2, §5, §6 |
| Data engineer | Python/Scala + SQL/Spark/Kafka + Airflow | §5 |
| Data scientist / ML engineer | Python + pandas + PyTorch + MLOps | §5, §7.2-adjacent ML |
| DevOps / SRE / platform | Linux + K8s + Terraform + CI/CD + observability | §4, §6 |
| Security engineer | networks + crypto + web vulns + tooling | §4, §6, §7.8 crypto, see security docs |
| Systems engineer | C/C++/Rust + OS + arch + perf | §2, §3, §4 |
| Compiler/PL engineer | LLVM + formal methods | §7.1, §7.7 |
| Graphics/engine programmer | C++/Rust + math + GPU APIs | §7.2, §7.4 |
| Quant / HPC researcher | math + parallel computing + numerics | §3, §7.8 |
| Research scientist (CS theory) | automata, complexity, logic | §7.6, `math_logic_map.md` |

---

## 9. LEARNING ROADMAP — BEGINNER → ADVANCED

### Phase 0 — Foundations (weeks 1–8)
1. **How computers work at a high level**: bits, bytes, binary/hex, what a program is, files vs. processes
2. **A terminal**: navigate files, run commands, pipes, redirection (do this on Linux/WSL — see TOOLS.md)
3. **Pick ONE language and go deep**: Python (easiest path to applications) or C (best path to systems understanding)
4. **Basic math refresh**: algebra, logic, discrete structures (see `math_logic_map.md`)

### Phase 1 — Programming Fluency (months 2–6)
5. **Core CS**: variables, functions, control flow, error handling, basic OOP
6. **Data structures & algorithms**: start with arrays, lists, hash maps, stacks, queues, trees; learn Big-O alongside (§3)
7. **Version control**: Git daily — commits, branches, merges, PRs
8. **Build real projects**: CLI tools, small web apps, automation scripts — *shipping beats tutorials*
9. **Testing basics**: write tests for your projects from day one

### Phase 2 — Systems Literacy (months 6–12)
10. **A second language**: if you started Python → learn C; if you started C → learn Python for productivity
11. **Operating systems**: processes, memory, filesystems, syscalls — CSAPP chapters 1–9
12. **Networking**: TCP/IP, HTTP, DNS — enough to debug why things don't connect
13. **Databases**: SQL deeply (joins, indexing, transactions, normalization), then try MongoDB/Redis
14. **Linux mastery**: shell scripting, permissions, processes, `strace`, package management

### Phase 3 — Software Engineering (year 1–2)
15. **Design patterns & architecture**: layered, MVC, clean architecture; read "A Philosophy of Software Design"
16. **APIs & web dev**: REST, auth, databases-backed services; build and deploy a real app
17. **DevOps**: Docker → Kubernetes basics → CI/CD → monitoring; Terraform for IaC
18. **Cloud**: pick AWS/Azure/GCP, learn core services (compute, storage, DB, networking)
19. **Concurrency**: threads, async, distributed-system pitfalls (read DDIA)

### Phase 4 — Depth & Specialization (year 2+)
20. **Pick a specialization** from §8 matching your interests
21. **Compiler/architecture track**: assembly, ISA, OS kernel reading, LLVM tutorials
22. **Systems track**: Rust or C++ deep dive, performance profiling, memory layout
23. **Data track**: statistics + ML fundamentals → `ml_pipeline_guide.md` → MLOps
24. **Theory track**: automata → complexity → logic (Lean 4 is installed here for formalization!)
25. **Security track**: `websec_research/` + `crypto_research/` + practical labs (Juice Shop, DVWA, PortSwigger Academy — see TOOLS.md)

### Cross-cutting advice
- **Learn by building**: every phase should produce artifacts, not just notes
- **Read source code**: Go's stdlib, CPython, Rust compiler — real code teaches what textbooks can't
- **Depth over breadth**: 1 language + systems + one specialization beats shallow exposure to 10
- **Community**: open-source contributions, local meetups, conference talks (YouTube), RFCs for protocols
- **Tools of the trade**: your editor/IDE, debugger, profiler, git client, terminal multiplexer (`tmux`), dotfiles

---

## 9.5 FIELD INTERCONNECTION MAP

How the fields feed each other — the "why learn X before Y" graph:

```
Math & Logic (math_logic_map.md)
    └─► Algorithms & Data Structures (§3)
            ├─► Programming Languages (§2)  ← learn these together
            ├─► Compilers (§7.1)             ← needs PL theory + A&D
            └─► Computer Architecture (§4)   ← needs digital logic + A&D
                    ├─► Operating Systems   ← needs arch + concurrency
                    │       └─► Systems programming (C/Rust/Go)
                    │               └─► DevOps / Infrastructure (§6.4)
                    └─► Embedded / Robotics (§7.8)

Databases (§5)
    ├─► Requires: programming + data structures (indexes = trees)
    ├─► Enables: backend dev, data engineering, BI
    └─► Scales into: distributed systems (§6.3) via replication/sharding

Networking (§6.1)
    ├─► Requires: OS I/O + a little math (probability for congestion)
    ├─► Enables: distributed systems, cloud, security
    └─► Everything runs on networks — APIs (§6.5) are its application layer

Distributed Systems (§6.3)
    ├─► Requires: concurrency + networking + databases + failure thinking
    ├─► Is required by: cloud-native apps, big data, microservices
    └─► Theory roots: automata, logic (§7.6), formal methods (§7.7)

ML / AI (see ml_pipeline_guide.md)
    ├─► Requires: programming + linear algebra + probability + data systems
    ├─► Uses: GPUs (§4.1), vector DBs (§5.1), distributed training (§6.3)
    └─► Applied in: graphics (§7.2), robotics (§7.8), HCI (§7.3)

Security (websec_research/, crypto_research/)
    ├─► Requires: networking + systems + crypto fundamentals (§7.8)
    ├─► Applies to: every layer — web, OS, protocols, crypto
    └─► Quantum computing (§7.5) threatens current crypto → post-quantum crypto is an active field
```

**The shortest path to employability**: programming fluency (§2) → data structures (§3) → one backend or frontend stack → databases + networking → cloud/DevOps (§6). The shortest path to *depth*: C → CSAPP → OS → systems language (Rust/C++) → compilers/architecture.

---

## 10. GLOSSARY — CROSS-FIELD TERMS

Terms that appear across multiple sections:

| Term | Meaning | Where it shows up |
|---|---|---|
| **API** | Application Programming Interface — contract for code-to-code or service-to-service communication | §2 (libraries), §6.5 |
| **ABI** | Application Binary Interface — lower-level contract (calling conventions, struct layout) | §4 (assembly, C) |
| **Big-O** | Asymptotic complexity notation — how cost grows with input size | §3 everywhere |
| **Cache** | Fast memory layer between CPU and RAM; also used for KV stores | §4.1, §5.1 (Redis) |
| **Concurrency vs. parallelism** | Concurrency = managing many tasks (interleaved); parallelism = executing simultaneously | §2, §4.1 (cores), §6.3 |
| **Container** | OS-level isolation (namespaces + cgroups); lighter than a VM | §4.4, §6.4 |
| **Daemon** | Background process serving requests (Unix convention) | §4.3, §6 |
| **DSL** | Domain-Specific Language — SQL, CSS, regex, GraphQL, Makefiles | §5, §6.5, §7.1 |
| **ETL/ELT** | Extract-Transform-Load pipelines for data movement | §5.2, §5.3 |
| **FFI** | Foreign Function Interface — calling C from other languages | §2, §7.1 |
| **Garbage collection** | Automatic memory reclamation (JVM, Go, Python, C#) vs. manual (C/C++) vs. ownership (Rust) | §2, §4.3 |
| **Idempotent** | Operation safe to retry — same result on repeat | §6.3, §6.5 (API design) |
| **Index** | Data structure speeding lookups — B+ tree in DBs, inverted index in search | §3, §5 |
| **IPC** | Inter-Process Communication — pipes, sockets, shared memory | §4.3, §6 |
| **JIT** | Just-In-Time compilation — compile during execution (V8, JVM, .NET) | §2, §4.5 |
| **Kernel** | Core of the OS — manages hardware, syscalls | §4.3 |
| **Latency vs. throughput** | Time per operation vs. operations per second | §6.1, §6.3 |
| **Monolith vs. microservices** | One deployable vs. many small services | §2.4, §6.3 |
| **ORM** | Object-Relational Mapper — code objects ↔ SQL rows (Prisma, SQLAlchemy, Hibernate) | §2, §5 |
| **Protocol** | Agreed format/rules for communication (TCP, HTTP, TLS, gRPC) | §6.1, §6.5 |
| **Race condition** | Bug from uncontrolled concurrent access | §2, §4.3, §6.3 |
| **Serialization** | Converting data structures to bytes for storage/transmission | §5, §6.5 |
| **SHA / hash** | Cryptographic fingerprint function — integrity, dedup, passwords | §3 (hash tables), §7.8 (crypto) |
| **Side effect** | Observable effect beyond return value (I/O, mutation) — pure functions have none | §2 |
| **State machine** | Model of system as states + transitions — UI flows, protocols, games | §2.4, §7.4 |
| **Syscall** | User→kernel request (read, write, open, mmap) | §4.3 |
| **Throughput** | Work done per unit time | §6.1 |
| **Transaction** | ACID unit of DB work — all-or-nothing | §5.1 |
| **Type system** | Rules governing types — static/dynamic, strong/weak | §2 |
| **VM** | Virtual Machine — hardware-emulated computer (hypervisor) or managed runtime (JVM) | §4.4, §2 |
| **WAL** | Write-Ahead Log — durability mechanism in DBs | §5.1 |
| **Zero-downtime deploy** | Rolling/blue-green releases — no service interruption | §2.6, §6.4 |

---

## 11. SOURCES

Verified November 2026 against official sources:

- **Python releases**: python.org/downloads — 3.15.2 latest; 3.14/3.13 in security support; 3.10 EOL Oct 2026
- **Go releases**: go.dev/dl — go1.27.4 latest stable
- **Rust releases**: rust-lang.org / release radar — Rust 1.100.0 (Nov 12, 2026)
- **TypeScript releases**: typescriptlang.org / npm — TypeScript 7.0.2 (Go-native port era)
- **Java LTS**: Oracle/OpenJDK release cadence — JDK 21 (2023 LTS), JDK 25 (2025 LTS)
- **endoflife.date** — support-window data for all languages/runtimes
- **Kleppmann, "Designing Data-Intensive Applications" (2017)** — §5, §6.3 bible
- **CSAPP (Bryant & O'Hallaron)** — §4 canonical text
- **Nystrom, "Crafting Interpreters"** — §7.1 entry point
- **Gamma et al., "Design Patterns" (1994)**; **Ousterhout, "A Philosophy of Software Design" (2018)**; **Martin, "Clean Architecture" (2017)** — §2.4
- **RFCs**: rfc-editor.org — TCP/IP, HTTP, TLS specifications
- **OWASP CheatSheetSeries** (`~/CheatSheetSeries`) — security cross-reference
- **Local resources**: `~/websec_research/`, `~/crypto_research/`, `~/HackTricks/`, `~/TOOLS.md`

*Generated as a research artifact. Living document — update version numbers and tool names as the ecosystem evolves.*
