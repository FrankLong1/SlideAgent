# SlideAgent Test Suite

This directory contains comprehensive tests for all SlideAgent functionality, covering areas that are critical for the system to work properly but weren't previously tested.

## Test Files Overview

### Core Functionality Tests

1. **`test_constants.py`** - Tests server.py constants and path resolvers
   - Directory path constants validation
   - CSS and theme file naming constants
   - Path resolver functions and precedence
   - Backward compatibility with legacy paths

2. **`test_css_paths.py`** - Tests CSS path resolution and naming consistency
   - `slide_base.css` vs `base.css` naming issues
   - Relative path resolution from slides/ to theme/
   - CSS imports in generated HTML
   - Self-contained project structure

3. **`test_template_discovery.py`** - Tests template listing and metadata loading
   - Template discovery across user/system directories
   - Template content validation
   - Metadata consistency and structure
   - Error handling for missing/corrupted templates

4. **`test_project_structure.py`** - Tests project creation and file management
   - Proper directory structure creation
   - Theme file copying and organization
   - Project self-containment (no external dependencies)
   - File permissions and accessibility

5. **`test_theme_management.py`** - Tests theme switching and file management
   - Theme discovery and validation
   - Theme switching and file updates
   - Asset management (CSS, logos, matplotlib styles)
   - Slide updates after theme changes

6. **`test_live_viewer.py`** - Tests live viewer path resolution and serving
   - Live viewer server startup/shutdown
   - Path resolution for slides and assets
   - CSS and image serving
   - Port management and conflicts

### Existing Tests (Updated)

7. **`test_mcp_tools.py`** - Tests MCP tool functionality (updated for CSS naming)
   - Fixed `base.css` vs `slide_base.css` references
   - MCP tool integration tests
   - Project management operations

8. **`test_plotbuddy.py`** - Tests PlotBuddy chart generation
   - Theme integration with charts
   - Chart generation and saving

## Running Tests

### Run All Tests
```bash
# Using the comprehensive test runner
uv run python tests/run_all_tests.py

# Or run individual test files
uv run python tests/test_css_paths.py
uv run python tests/test_constants.py
# etc.
```

### Run Tests Without uv
```bash
# Make sure you have the right Python environment activated
python tests/test_css_paths.py
python tests/test_constants.py
# etc.
```

## What These Tests Catch

### CSS Path Issues
- Inconsistencies between `slide_base.css` and `base.css` naming
- Broken relative paths from slides to theme assets
- Missing CSS imports in generated HTML
- Theme switching not updating CSS references

### Template Problems
- Missing or corrupted template files
- Incorrect template metadata
- Template discovery failures
- Path resolution issues across different directories

### Project Structure Issues
- Incomplete project directory creation
- Missing theme files in projects
- Broken self-containment (external dependencies)
- File permission problems

### Theme Management Problems
- Theme switching failures
- Incomplete theme file updates
- Asset inconsistencies after theme changes
- Logo and style file management issues

### Live Viewer Issues
- Server startup/shutdown failures
- Path resolution problems
- Asset serving issues
- Port conflicts

## Test Design Principles

1. **Comprehensive Coverage** - Tests cover both positive and negative cases
2. **Real-World Scenarios** - Tests based on actual issues encountered in production
3. **Edge Case Testing** - Tests handle unusual project names, missing files, etc.
4. **Error Validation** - Tests ensure proper error messages and graceful handling
5. **Self-Contained** - Tests clean up after themselves and don't interfere with each other
6. **Fast Execution** - Tests are designed to run quickly for frequent validation

## Adding New Tests

When adding new functionality to SlideAgent:

1. **Add tests to existing files** if the functionality fits an existing category
2. **Create new test files** for entirely new functionality areas
3. **Update `run_all_tests.py`** to include new test files
4. **Follow the naming convention**: `test_<functionality_area>.py`
5. **Include both positive and negative test cases**
6. **Add proper docstrings** explaining what each test validates

## Troubleshooting Test Failures

### Common Issues

1. **MCP Dependencies** - Make sure `uv sync` has been run
2. **Directory Permissions** - Tests create/delete directories in `user_projects/`
3. **Port Conflicts** - Live viewer tests may conflict with running servers
4. **File System State** - Some tests depend on clean initial state

### Debugging Failed Tests

1. **Run individual test files** to isolate issues
2. **Check test output** for specific assertion failures
3. **Verify environment setup** (dependencies, permissions)
4. **Look for leftover test directories** that might cause conflicts

## Test Coverage Areas

These tests specifically cover critical areas that weren't tested before:

✅ **CSS Path Resolution** - The slide_base.css vs base.css naming issue  
✅ **Template Discovery** - Finding and validating templates across directories  
✅ **Project Self-Containment** - Ensuring projects work independently  
✅ **Theme Management** - Complete theme switching functionality  
✅ **Live Viewer Integration** - Server and asset serving functionality  
✅ **Constants Validation** - Core system constants and path resolvers  

This comprehensive test suite ensures that SlideAgent works reliably across all its core functionality areas.