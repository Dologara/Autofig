# Phase 3 – Dynamic Generation and Visualization

Objective:
Phase 3 focuses on transforming Autofig from a static YAML-driven tool into a dynamic, interactive system. Users will be able to define their network topology on the fly, visualize connections, and generate configurations automatically using the templates created in earlier phases.

------------------------------------------------------------
1. Phase Goals
------------------------------------------------------------
- Enable users to dynamically choose how many routers, multilayer switches, and access switches to include.
- Offer the option to either:
  • Use an existing predefined topology (from /data/topologies/)
  • Or create a custom one interactively.
- Provide a basic visualization feature to display the generated topology.
- Maintain full compatibility with the existing generation engine and templates.

------------------------------------------------------------
2. System Enhancements
------------------------------------------------------------
- Introduce a new CLI-based interactive builder that guides the user through:
  • Selecting the number of each device type
  • Assigning names or using auto-generated names (R1, SW1, MLS1, etc.)
  • Choosing default vendor templates (e.g., Cisco)
  • Defining simple topology structure (auto-connect or manual connections)
- Build in-memory YAML structures and export them as temporary topology files.
- Integrate visualization support using Python libraries (e.g., networkx, matplotlib, or graphviz).

------------------------------------------------------------
3. Implementation Plan
------------------------------------------------------------
- Create a new module: core/cli_builder.py
  • Handles user input and topology creation
- Optional module: core/visualizer.py
  • Renders a simple graph of the topology and saves it as an image
- Extend generator.py to:
  • Accept generated topology data directly from cli_builder
  • Continue using Jinja2 templates for final configuration rendering

------------------------------------------------------------
4. User Workflow
------------------------------------------------------------
Example dynamic generation flow:
  1. Launch Autofig
  2. Select "Dynamic Build" mode
  3. Specify number of routers, switches, and multilayer switches
  4. Decide whether to use defaults or custom parameters
  5. Optionally generate a topology visualization
  6. Confirm and run configuration generation
  7. Output files are created under /outputs/ with timestamp and topology name

------------------------------------------------------------
5. Tools and Libraries
------------------------------------------------------------
Add to requirements.txt:
  • networkx
  • matplotlib
  • rich  (optional, for colored CLI output)

------------------------------------------------------------
6. Folder and Module Structure
------------------------------------------------------------
core/
 ├── generator.py        → existing engine
 ├── cli_builder.py      → new interactive CLI module
 ├── visualizer.py       → optional topology visualization
 └── utils.py            → helper functions (validation, naming, merging)

------------------------------------------------------------
7. Milestones
------------------------------------------------------------
3.1 – CLI prompts for device count and topology selection
3.2 – YAML builder for dynamic topologies
3.3 – Integration with generator.py for config generation
3.4 – Visualization prototype using networkx
3.5 – CLI polish and usability improvements

------------------------------------------------------------
8. Expected Outcome
------------------------------------------------------------
By the end of Phase 3, Autofig will evolve from a script-based generator into a user-driven platform. The system will support interactive topology creation, optional visualization, and automated configuration generation — all using the existing template architecture. This phase lays the groundwork for future enhancements like global vs. local YAML separation and GUI-based topology management.

------------------------------------------------------------
Next Step
------------------------------------------------------------
→ Phase 4: Data Separation and Schema Validation
