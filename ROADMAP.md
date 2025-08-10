# SlideAgent MCP Architecture Roadmap

## 🎯 Vision
Transform SlideAgent into a fully self-contained MCP package that can be installed globally and used from any directory, while maintaining clean separation between system resources and user customizations.

## 🏗️ Target Architecture
```
SlideAgent/
├── slideagent_mcp/              # SELF-CONTAINED MCP PACKAGE (system space)
│   ├── server.py               # MCP server logic
│   ├── resources/              # All system resources
│   │   ├── templates/
│   │   │   ├── slides/         # All slide templates (from src/slides/slide_templates/)
│   │   │   ├── charts/         # All chart templates (from src/charts/chart_templates/)
│   │   │   └── outlines/       # Outline templates (from markdown_templates/)
│   │   ├── themes/
│   │   │   ├── core/           # Built-in themes (from themes/examples/)
│   │   │   │   ├── acme_corp/
│   │   │   │   ├── goldman_sachs/
│   │   │   │   ├── barney/
│   │   │   │   └── bdt_msd/
│   │   │   └── registry.yaml   # Theme metadata
│   │   ├── base.css            # Core styling (from src/slides/base.css)
│   │   └── prompts/
│   │       ├── system.md       # Main instructions (from CLAUDE.md)
│   │       ├── outline.md      # Outline generation prompts
│   │       └── agents.yaml     # Agent generation prompts
│   ├── utils/
│   │   ├── pdf_generator.js    # PDF generation utility
│   │   ├── live_viewer.js      # Live preview server
│   │   └── plot_buddy.py       # Chart generation class
│   └── __init__.py
│
├── user_resources/              # USER CUSTOM RESOURCES (user space)
│   ├── templates/
│   │   ├── slides/              # User slide templates
│   │   └── charts/              # User chart templates
│   └── themes/                  # User themes
│       ├── example_theme_1/
│       ├── example_theme_2/
│       ├── example_theme_3/
│       └── .gitkeep
│
├── user_projects/               # GENERATED PRESENTATIONS (user space)
│   ├── coreweave-s1/
│   ├── figma-s1-analysis/
│   └── ...
│
├── .mcp.json                    # MCP configuration
├── requirements.txt             # Python dependencies
├── package.json                 # Node dependencies
└── README.md                    # Documentation
```

## 📋 Migration Tasks

### Phase 1: Restructure Resources ✅
- [ ] Move `src/slides/slide_templates/*` → `slideagent_mcp/resources/templates/slides/`
- [ ] Move `src/charts/chart_templates/*` → `slideagent_mcp/resources/templates/charts/`
- [ ] Move `src/slides/base.css` → `slideagent_mcp/resources/base.css`
- [ ] Move `src/charts/utils/plot_buddy.py` → `slideagent_mcp/utils/`
- [ ] Move `themes/examples/*` → `slideagent_mcp/resources/themes/core/`
- [ ] Create `user_resources/` with `templates/slides`, `templates/charts`, and `themes/`
- [ ] Move `themes/private/*` → `user_resources/themes/`
- [ ] Move `markdown_templates/*` → `slideagent_mcp/resources/templates/outlines/`
- [ ] Convert `CLAUDE.md` → `slideagent_mcp/resources/prompts/system.md`
- [ ] Create `slideagent_mcp/resources/prompts/outline.md` from outline generation sections
- [ ] Create `slideagent_mcp/resources/prompts/agents.yaml` from agent prompt patterns

### Phase 2: Update MCP Server
- [ ] Listing behavior for themes/templates: aggregate from both user and system simultaneously; skip missing/empty user dirs gracefully; error if system resources are missing/unreadable
- [ ] Update `server.py` to use new resource paths
- [ ] Implement resource discovery (themes + templates from both system and custom)
- [ ] Add MCP resource endpoints for templates/themes/prompts
- [ ] Update path resolution to check custom directories first, then fall back to system
- [ ] Fix CSS/asset paths in generated slides to reference new locations

### Phase 3: Package Distribution
- [ ] Create `pyproject.toml` for pip installation
- [ ] Set up package manifest to include all resources
- [ ] Create installation script that sets up custom directories
- [ ] Test global installation: `pip install slideagent-mcp`
- [ ] Test usage from arbitrary directory after global install

### Phase 4: Enhanced Features
- [ ] Add `slideagent init` command to set up custom directories in any project
- [ ] Implement theme inheritance (custom themes extending system themes)
- [ ] Add template marketplace/registry concept
- [ ] Create `slideagent://` URI scheme for resource references
- [ ] Add resource versioning and update mechanism

## 🎯 Key Design Principles

### 1. **Clean Separation**
- **System Space** (`slideagent_mcp/`): Never edited by users, updated via package manager
- **User Space** (`user_resources/`, `user_projects/`): User's customizations and work

### 2. **Resource Resolution Order**
Applies when resolving a single named resource (e.g., picking a template by name), not when listing. For listing behavior, see 2a.
1. Check `user_resources/` (e.g., `user_resources/themes/`, `user_resources/templates/...`) first
2. Fall back to `slideagent_mcp/resources/` for built-ins
3. Return error if not found in either location

### 2a. **Listing Behavior (Themes/Templates)**
- For listing (`list_themes`, `list_slide_templates`, `list_chart_templates`), aggregate results from both `user_resources/*` and `slideagent_mcp/resources/*` concurrently without prioritization.
- If `user_resources/*` subdirectories are missing or empty, skip them and continue; return a simple message stating there are no user templates/themes.
- If system resource directories are missing or unreadable, return an error (fatal configuration issue).

### 3. **Backward Compatibility**
- Existing projects continue to work
- Gradual migration path for current users
- Can run in both "local project" and "global MCP" modes

### 4. **MCP Resources as First-Class Citizens**
```python
# Resources exposed via MCP protocol
@resource(uri="slideagent://templates/slides")
@resource(uri="slideagent://themes/core")  
@resource(uri="slideagent://prompts/system")
```

## 🚀 Benefits After Migration

### For Users
- **Zero Setup**: `pip install slideagent-mcp && claude mcp add slideagent`
- **Works Anywhere**: Create presentations in any directory
- **Easy Customization**: Drop themes in `user_resources/themes/`, templates in `user_resources/templates/...`
- **Version Control Friendly**: Clear boundaries between system and user files

### For Development
- **Single Package**: Everything in `slideagent_mcp/` for distribution
- **Clean Testing**: Test against known system resources
- **Easy Updates**: Update package without touching user customizations
- **Clear Dependencies**: System resources bundled, user resources separate

### For Distribution
- **PyPI Ready**: `pip install slideagent-mcp`
- **NPM Ready**: `npm install -g slideagent-mcp` (if we want Node version)
- **Self-Contained**: All resources included in package
- **Update Path**: `pip upgrade slideagent-mcp` updates system resources only

## 📅 Timeline

### Week 1-2: Phase 1 (Restructure)
- Move all resources to new structure
- Update import paths
- Test existing functionality

### Week 3: Phase 2 (MCP Updates)
- Update server.py for new paths
- Implement resource discovery
- Add MCP resource endpoints

### Week 4: Phase 3 (Package & Test)
- Create package configuration
- Test global installation
- Documentation updates

### Future: Phase 4 (Enhancements)
- Advanced features as needed
- Community feedback integration
- Template marketplace

## 🎉 Success Criteria

1. **Can install globally**: `pip install slideagent-mcp` works
2. **Can use anywhere**: Works from any directory after `claude mcp add slideagent`
3. **Clean separation**: System and user resources clearly separated
4. **Backward compatible**: Existing projects continue to work
5. **User friendly**: Custom themes/templates are easy to add and manage

## 🔄 Migration Strategy

1. Create new branch `more_mcp`
2. Restructure directories according to plan
3. Update all import paths and references
4. Test thoroughly with existing projects
5. Document changes in README
6. Merge when stable


# Separately
we want init project to also make a copy of the theme folder into the project, and then the html slides in the project reference this copy of the css themes that live in the same project folder, that way the whole project is pretty stnadarlone and can be copied and pasted without breaking things uecause it's weirdly referncing the css within the MCP folder or eventhe user projects or user themes

---

*This roadmap represents the next evolution of SlideAgent, transforming it from a project-based tool to a globally-available MCP service while maintaining flexibility for customization.*