# Austrian Legal Documents Database (arch_pdfs)

This directory contains a comprehensive collection of Austrian legal documents organized in a hierarchical structure for the Normo Legal Assistant system.

## Directory Structure

```
arch_pdfs/
├── 01_Data base documents/
│   ├── 00_Bundesgesetze/                    # Federal Laws
│   │   ├── 1_AT_0_0_GE_*.pdf              # Federal Laws (Gesetze)
│   │   └── 2_AT_0_0_VE_*.pdf              # Federal Regulations (Verordnungen)
│   │
│   ├── 01-02_Bundesländer- Gesetze und Verordnungen/  # State Laws and Regulations
│   │   ├── 01.Wien/                       # Vienna
│   │   │   ├── 1_AT_W_W_GE_*.pdf         # Vienna Laws
│   │   │   └── 2_AT_W_W_VE_*.pdf         # Vienna Regulations
│   │   │
│   │   └── 04. OBERÖSTERREICH/            # Upper Austria
│   │       ├── 1_AT_OOE_0_GE_*.pdf       # Upper Austria Laws
│   │       └── 2_AT_OOE_0_VE_*.pdf       # Upper Austria Regulations
│   │
│   ├── 03_OIB Richtlinien/                # OIB Guidelines
│   │   ├── 2019/                          # 2019 Edition
│   │   │   └── 3_AT_0_0_OIB_*.pdf
│   │   └── 2023/                          # 2023 Edition (Current)
│   │       └── 3_AT_0_0_OIB_*.pdf
│   │
│   └── 04_ÖNORM/                          # Austrian Standards
│       └── 4_AT_0_0_OEN_*.pdf
│
└── Data base List with Links- work in progress.docx
```

## Document Naming Convention

The PDF files follow a standardized naming pattern:

```
{level}_{country}_{state}_{type}_{category}_{title}_{year}.pdf
```

### Pattern Breakdown:
- **Level**: Document hierarchy level (1-4)
  - `1` = Laws (Gesetze)
  - `2` = Regulations (Verordnungen) 
  - `3` = OIB Guidelines
  - `4` = ÖNORM Standards

- **Country**: `AT` = Austria

- **State**: State identifier
  - `0` = Federal level
  - `W` = Vienna (Wien)
  - `OOE` = Upper Austria (Oberösterreich)

- **Type**: Document type
  - `0` = General
  - `W` = Vienna specific
  - `OOE` = Upper Austria specific

- **Category**: Document category
  - `GE` = Laws (Gesetze)
  - `VE` = Regulations (Verordnungen)
  - `OIB` = OIB Guidelines
  - `OEN` = ÖNORM Standards

- **Title**: Descriptive title of the document

- **Year**: Publication year

## Document Categories

### 1. Federal Laws (00_Bundesgesetze)
- **BauKG** - Construction Coordination Law
- **GewO 1994** - Trade Regulation 1994
- **AStV** - Workplace Ordinance
- **BauV** - Construction Worker Protection Ordinance

### 2. State Laws and Regulations (01-02_Bundesländer)

#### Vienna (01.Wien)
- **BO für Wien** - Building Code for Vienna
- **WGarG 2008** - Vienna Garage Law 2008
- **WAZG 2006** - Vienna Elevator Law 2006
- **Wiener Baumschutzgesetz** - Vienna Tree Protection Law
- **Spielplatzverordnung** - Playground Ordinance

#### Upper Austria (04. OBERÖSTERREICH)
- **Bauordnung 1994** - Building Code 1994
- **Bautechnikgesetz 2013** - Building Technology Law 2013
- **Raumordnungsgesetz 1994** - Spatial Planning Law 1994
- **Abfallwirtschaftsgesetz 2009** - Waste Management Law 2009
- **Bodenschutzgesetz 1991** - Soil Protection Law 1991

### 3. OIB Guidelines (03_OIB Richtlinien)
Current version: **2023 Edition**

#### OIB Guidelines by Topic:
- **OIB-RL 1** - Mechanical Strength and Stability
- **OIB-RL 2** - Fire Protection
  - 2.1 - Fire Protection for Commercial Buildings
  - 2.2 - Fire Protection for Garages and Parking Decks
  - 2.3 - Fire Protection for High-Rise Buildings (>22m)
- **OIB-RL 3** - Hygiene, Health and Environmental Protection
- **OIB-RL 4** - Usage Safety and Accessibility
- **OIB-RL 5** - Sound Protection
- **OIB-RL 6** - Energy Saving and Thermal Protection

### 4. Austrian Standards (04_ÖNORM)
- **ÖNORM B 1600** - Barrier-Free Construction
- **ÖNORM B 1800** - Area and Volume Calculation
- **ÖNORM B 5371** - Stairs, Railings and Parapets

## Usage in Normo System

The Normo Legal Assistant uses this structured database to:

1. **Categorize Queries**: Automatically determine which document categories are relevant
2. **Targeted Retrieval**: Search within specific document types (laws vs. regulations vs. guidelines)
3. **Regional Context**: Understand if query is about federal, state, or local regulations
4. **Version Management**: Use current versions (2023 OIB guidelines) when available
5. **Comprehensive Coverage**: Provide complete legal context across all relevant document types

## Document Processing

The system processes these documents by:
- Extracting text content and metadata
- Creating searchable embeddings
- Maintaining document hierarchy information
- Tracking document versions and updates
- Providing accurate citations with page numbers

## Maintenance

- **Updates**: New documents should follow the naming convention
- **Versions**: Keep both old and new versions when updating (e.g., OIB 2019 and 2023)
- **Metadata**: Document metadata is automatically generated during processing
- **Indexing**: The system automatically detects and processes new/changed documents

## Integration

This database integrates with:
- **Vector Store**: For semantic search and retrieval
- **Planner Agent**: For query categorization and document selection
- **Retriever Agent**: For targeted document retrieval
- **Summarizer Agent**: For context-aware responses with proper citations
