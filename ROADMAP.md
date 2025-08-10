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
├── custom_themes/               # USER CUSTOM THEMES (user space)
│   └── .gitkeep                # Empty initially, users add their themes here
│
├── custom_templates/            # USER CUSTOM TEMPLATES (user space)
│   └── .gitkeep                # Empty initially, users add their templates here
│
├── projects/                    # GENERATED PRESENTATIONS (user space)
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
- [ ] Move `themes/private/*` → `custom_themes/`
- [ ] Move `markdown_templates/*` → `slideagent_mcp/resources/templates/outlines/`
- [ ] Convert `CLAUDE.md` → `slideagent_mcp/resources/prompts/system.md`
- [ ] Create `slideagent_mcp/resources/prompts/outline.md` from outline generation sections
- [ ] Create `slideagent_mcp/resources/prompts/agents.yaml` from agent prompt patterns

### Phase 2: Update MCP Server
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
- **User Space** (`custom_*/`, `projects/`): User's customizations and work

### 2. **Resource Resolution Order**
1. Check `custom_themes/` or `custom_templates/` first
2. Fall back to `slideagent_mcp/resources/` for built-ins
3. Return error if not found in either location

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
- **Easy Customization**: Drop themes in `custom_themes/`, templates in `custom_templates/`
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

---

*This roadmap represents the next evolution of SlideAgent, transforming it from a project-based tool to a globally-available MCP service while maintaining flexibility for customization.*