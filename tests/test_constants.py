#!/usr/bin/env python3
"""
Test server.py constants and path resolvers.

This test suite validates the constants and path resolution functionality
that's critical for SlideAgent's file system organization:
- Directory path constants validation
- CSS file naming constants
- Theme file naming constants  
- Path resolver functions
- Directory precedence and fallbacks
- Backward compatibility with legacy paths
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.server import (
    # Directory constants
    BASE_DIR,
    USER_PROJECTS_DIR,
    USER_RESOURCES_DIR,
    USER_THEMES_DIR,
    USER_TEMPLATES_DIR,
    SYSTEM_RESOURCES_DIR,
    SYSTEM_THEMES_DIR,
    SYSTEM_SLIDE_TEMPLATES_DIR,
    SYSTEM_CHART_TEMPLATES_DIR,
    LEGACY_PROJECTS_DIR,
    LEGACY_THEMES_DIR,
    
    # CSS constants
    SLIDE_BASE_CSS_NAME,
    REPORT_BASE_CSS_NAME,
    SLIDE_BASE_CSS_SOURCE,
    REPORT_BASE_CSS_SOURCE,
    REL_PATH_TO_THEME_FROM_SLIDES,
    REL_PATH_TO_THEME_FROM_REPORTS,
    
    # Theme constants
    THEME_CSS_SUFFIX,
    THEME_STYLE_SUFFIX,
    THEME_ICON_LOGO_SUFFIX,
    THEME_TEXT_LOGO_SUFFIX,
    
    # Resolver functions
    resolve_projects_dir,
    resolve_slide_template_dirs,
    resolve_chart_template_dirs,
    resolve_theme_dirs
)


def test_base_directory_constant():
    """Test that BASE_DIR constant points to correct location"""
    # Should point to project root (parent of slideagent_mcp)
    assert BASE_DIR.exists(), f"BASE_DIR doesn't exist: {BASE_DIR}"
    assert BASE_DIR.is_dir(), f"BASE_DIR is not a directory: {BASE_DIR}"
    
    # Should contain expected project structure
    expected_items = ["slideagent_mcp", "user_projects", "tests"]
    for item in expected_items:
        item_path = BASE_DIR / item
        assert item_path.exists(), f"Expected item not found in BASE_DIR: {item_path}"
    
    # Should be absolute path
    assert BASE_DIR.is_absolute(), f"BASE_DIR should be absolute: {BASE_DIR}"
    
    print(f"✓ BASE_DIR correctly points to: {BASE_DIR}")


def test_system_directory_constants():
    """Test system directory constants point to correct locations"""
    # System resources should be inside slideagent_mcp
    assert SYSTEM_RESOURCES_DIR.exists(), f"System resources dir missing: {SYSTEM_RESOURCES_DIR}"
    assert "slideagent_mcp" in str(SYSTEM_RESOURCES_DIR), f"System resources should be in slideagent_mcp: {SYSTEM_RESOURCES_DIR}"
    
    # System templates should exist
    assert SYSTEM_SLIDE_TEMPLATES_DIR.exists(), f"System slide templates missing: {SYSTEM_SLIDE_TEMPLATES_DIR}"
    assert SYSTEM_CHART_TEMPLATES_DIR.exists(), f"System chart templates missing: {SYSTEM_CHART_TEMPLATES_DIR}"
    
    # Should contain actual template files
    slide_templates = list(SYSTEM_SLIDE_TEMPLATES_DIR.glob("*.html"))
    chart_templates = list(SYSTEM_CHART_TEMPLATES_DIR.glob("*.py"))
    
    assert len(slide_templates) > 0, f"No slide templates found in: {SYSTEM_SLIDE_TEMPLATES_DIR}"
    assert len(chart_templates) > 0, f"No chart templates found in: {SYSTEM_CHART_TEMPLATES_DIR}"
    
    print(f"✓ System directories exist with {len(slide_templates)} slide, {len(chart_templates)} chart templates")


def test_user_directory_constants():
    """Test user directory constants point to correct locations"""
    # User directories should be in project root
    assert "user_projects" in str(USER_PROJECTS_DIR), f"Wrong user projects dir: {USER_PROJECTS_DIR}"
    assert "user_resources" in str(USER_RESOURCES_DIR), f"Wrong user resources dir: {USER_RESOURCES_DIR}"
    
    # Should be under BASE_DIR
    assert BASE_DIR in USER_PROJECTS_DIR.parents, f"User projects should be under BASE_DIR: {USER_PROJECTS_DIR}"
    assert BASE_DIR in USER_RESOURCES_DIR.parents, f"User resources should be under BASE_DIR: {USER_RESOURCES_DIR}"
    
    # User subdirectories
    assert USER_THEMES_DIR == USER_RESOURCES_DIR / "themes", f"Wrong user themes path: {USER_THEMES_DIR}"
    assert USER_TEMPLATES_DIR == USER_RESOURCES_DIR / "templates", f"Wrong user templates path: {USER_TEMPLATES_DIR}"
    
    # Create directories if they don't exist (for testing)
    USER_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    USER_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"✓ User directory constants are correctly structured")


def test_css_naming_constants():
    """Test CSS file naming constants are correct"""
    # CSS file names should be consistent
    assert SLIDE_BASE_CSS_NAME == "slide_base.css", f"Wrong slide CSS name: {SLIDE_BASE_CSS_NAME}"
    assert REPORT_BASE_CSS_NAME == "report_base.css", f"Wrong report CSS name: {REPORT_BASE_CSS_NAME}"
    
    # CSS source paths should exist
    assert SLIDE_BASE_CSS_SOURCE.exists(), f"Slide CSS source missing: {SLIDE_BASE_CSS_SOURCE}"
    
    # Should be in system templates directory
    assert SYSTEM_SLIDE_TEMPLATES_DIR in SLIDE_BASE_CSS_SOURCE.parents, \
        f"Slide CSS should be in slide templates dir: {SLIDE_BASE_CSS_SOURCE}"
    
    # Relative paths should be correct
    assert REL_PATH_TO_THEME_FROM_SLIDES == "../theme", f"Wrong relative path from slides: {REL_PATH_TO_THEME_FROM_SLIDES}"
    assert REL_PATH_TO_THEME_FROM_REPORTS == "../theme", f"Wrong relative path from reports: {REL_PATH_TO_THEME_FROM_REPORTS}"
    
    print("✓ CSS naming constants are correct")


def test_theme_naming_constants():
    """Test theme file naming constants are correct"""
    # Theme suffixes should be consistent
    assert THEME_CSS_SUFFIX == "_theme.css", f"Wrong theme CSS suffix: {THEME_CSS_SUFFIX}"
    assert THEME_STYLE_SUFFIX == "_style.mplstyle", f"Wrong theme style suffix: {THEME_STYLE_SUFFIX}"
    assert THEME_ICON_LOGO_SUFFIX == "_icon_logo.png", f"Wrong icon logo suffix: {THEME_ICON_LOGO_SUFFIX}"
    assert THEME_TEXT_LOGO_SUFFIX == "_text_logo.png", f"Wrong text logo suffix: {THEME_TEXT_LOGO_SUFFIX}"
    
    # Test suffix construction
    theme_name = "test_theme"
    expected_files = [
        f"{theme_name}{THEME_CSS_SUFFIX}",
        f"{theme_name}{THEME_STYLE_SUFFIX}",
        f"{theme_name}{THEME_ICON_LOGO_SUFFIX}",
        f"{theme_name}{THEME_TEXT_LOGO_SUFFIX}"
    ]
    
    expected_result = [
        "test_theme_theme.css",
        "test_theme_style.mplstyle",
        "test_theme_icon_logo.png",
        "test_theme_text_logo.png"
    ]
    
    assert expected_files == expected_result, f"Theme file naming inconsistent: {expected_files}"
    
    print("✓ Theme naming constants are correct")


def test_projects_directory_resolver():
    """Test projects directory resolution function"""
    projects_dir = resolve_projects_dir()
    
    # Should always return user projects directory
    assert projects_dir == USER_PROJECTS_DIR, f"Should return user projects dir: {projects_dir}"
    
    # Should be absolute path
    assert projects_dir.is_absolute(), f"Projects dir should be absolute: {projects_dir}"
    
    # Should be under BASE_DIR
    assert BASE_DIR in projects_dir.parents, f"Projects dir should be under BASE_DIR: {projects_dir}"
    
    print(f"✓ Projects directory resolver returns: {projects_dir}")


def test_slide_template_dirs_resolver():
    """Test slide template directories resolution with precedence"""
    template_dirs = resolve_slide_template_dirs()
    
    # Should return at least system directory
    assert len(template_dirs) > 0, "Should find at least one slide template directory"
    assert SYSTEM_SLIDE_TEMPLATES_DIR in template_dirs, "Should include system slide templates"
    
    # All returned directories should exist
    for template_dir in template_dirs:
        assert template_dir.exists(), f"Template directory should exist: {template_dir}"
        assert template_dir.is_dir(), f"Template path should be directory: {template_dir}"
    
    # Should contain HTML files
    total_templates = sum(len(list(d.glob("*.html"))) for d in template_dirs)
    assert total_templates > 0, "Template directories should contain HTML files"
    
    # If user templates exist, they should come first
    user_slide_dir = USER_TEMPLATES_DIR / "slides"
    if user_slide_dir.exists() and user_slide_dir in template_dirs:
        user_index = template_dirs.index(user_slide_dir)
        system_index = template_dirs.index(SYSTEM_SLIDE_TEMPLATES_DIR)
        assert user_index < system_index, "User templates should have priority over system"
    
    print(f"✓ Slide template resolver found {len(template_dirs)} directories with {total_templates} templates")


def test_chart_template_dirs_resolver():
    """Test chart template directories resolution with precedence"""
    template_dirs = resolve_chart_template_dirs()
    
    # Should return at least system directory
    assert len(template_dirs) > 0, "Should find at least one chart template directory"
    assert SYSTEM_CHART_TEMPLATES_DIR in template_dirs, "Should include system chart templates"
    
    # All returned directories should exist
    for template_dir in template_dirs:
        assert template_dir.exists(), f"Chart template directory should exist: {template_dir}"
        assert template_dir.is_dir(), f"Chart template path should be directory: {template_dir}"
    
    # Should contain Python files
    total_templates = sum(len(list(d.glob("*.py"))) for d in template_dirs)
    assert total_templates > 0, "Chart template directories should contain Python files"
    
    # Check precedence if user templates exist
    user_chart_dir = USER_TEMPLATES_DIR / "charts"
    if user_chart_dir.exists() and user_chart_dir in template_dirs:
        user_index = template_dirs.index(user_chart_dir)
        system_index = template_dirs.index(SYSTEM_CHART_TEMPLATES_DIR)
        assert user_index < system_index, "User chart templates should have priority over system"
    
    print(f"✓ Chart template resolver found {len(template_dirs)} directories with {total_templates} templates")


def test_theme_dirs_resolver():
    """Test theme directories resolution with precedence"""
    theme_dirs = resolve_theme_dirs()
    
    # Should find at least some theme directories
    assert len(theme_dirs) > 0, "Should find at least one theme directory"
    
    # All returned directories should exist
    for theme_dir in theme_dirs:
        assert theme_dir.exists(), f"Theme directory should exist: {theme_dir}"
        assert theme_dir.is_dir(), f"Theme path should be directory: {theme_dir}"
    
    # Should contain theme subdirectories
    total_themes = 0
    for theme_dir in theme_dirs:
        theme_subdirs = [d for d in theme_dir.iterdir() if d.is_dir()]
        total_themes += len(theme_subdirs)
    
    assert total_themes > 0, "Theme directories should contain theme subdirectories"
    
    # Check that essential themes exist somewhere
    all_theme_names = []
    for theme_dir in theme_dirs:
        for theme_subdir in theme_dir.iterdir():
            if theme_subdir.is_dir():
                all_theme_names.append(theme_subdir.name)
    
    essential_themes = ["acme_corp", "barney"]
    for essential in essential_themes:
        assert essential in all_theme_names, f"Missing essential theme: {essential}"
    
    print(f"✓ Theme resolver found {len(theme_dirs)} directories with {total_themes} themes")


def test_legacy_directory_constants():
    """Test legacy directory constants for backward compatibility"""
    # Legacy constants should be defined (even if directories don't exist)
    assert LEGACY_PROJECTS_DIR is not None, "Legacy projects dir should be defined"
    assert LEGACY_THEMES_DIR is not None, "Legacy themes dir should be defined"
    
    # Should be under BASE_DIR
    assert BASE_DIR in LEGACY_PROJECTS_DIR.parents, f"Legacy projects should be under BASE_DIR: {LEGACY_PROJECTS_DIR}"
    assert BASE_DIR in LEGACY_THEMES_DIR.parents, f"Legacy themes should be under BASE_DIR: {LEGACY_THEMES_DIR}"
    
    # Should have correct names
    assert "projects" in str(LEGACY_PROJECTS_DIR), f"Legacy projects dir should contain 'projects': {LEGACY_PROJECTS_DIR}"
    assert "themes" in str(LEGACY_THEMES_DIR), f"Legacy themes dir should contain 'themes': {LEGACY_THEMES_DIR}"
    
    print("✓ Legacy directory constants are properly defined")


def test_path_constant_relationships():
    """Test that path constants have correct relationships"""
    # System paths should be under slideagent_mcp
    slideagent_mcp_dir = BASE_DIR / "slideagent_mcp"
    
    assert slideagent_mcp_dir in SYSTEM_RESOURCES_DIR.parents, \
        f"System resources should be under slideagent_mcp: {SYSTEM_RESOURCES_DIR}"
    assert slideagent_mcp_dir in SYSTEM_SLIDE_TEMPLATES_DIR.parents, \
        f"System slide templates should be under slideagent_mcp: {SYSTEM_SLIDE_TEMPLATES_DIR}"
    
    # User paths should be under BASE_DIR but not under slideagent_mcp
    assert BASE_DIR in USER_PROJECTS_DIR.parents, f"User projects should be under BASE_DIR: {USER_PROJECTS_DIR}"
    assert slideagent_mcp_dir not in USER_PROJECTS_DIR.parents, \
        f"User projects should NOT be under slideagent_mcp: {USER_PROJECTS_DIR}"
    
    # CSS source should be in slide templates directory
    assert SLIDE_BASE_CSS_SOURCE.parent == SYSTEM_SLIDE_TEMPLATES_DIR, \
        f"Slide CSS source should be in slide templates dir: {SLIDE_BASE_CSS_SOURCE}"
    
    print("✓ Path constants have correct relationships")


def test_constant_immutability():
    """Test that important constants maintain expected values"""
    # These constants should not change as they affect file system layout
    critical_constants = {
        "SLIDE_BASE_CSS_NAME": "slide_base.css",
        "THEME_CSS_SUFFIX": "_theme.css",
        "THEME_STYLE_SUFFIX": "_style.mplstyle",
        "REL_PATH_TO_THEME_FROM_SLIDES": "../theme"
    }
    
    for const_name, expected_value in critical_constants.items():
        actual_value = globals()[const_name]
        assert actual_value == expected_value, \
            f"Critical constant changed: {const_name} = {actual_value}, expected {expected_value}"
    
    print(f"✓ {len(critical_constants)} critical constants maintain expected values")


def test_resolver_error_handling():
    """Test that resolvers handle missing directories gracefully"""
    # Resolvers should not crash even if some directories don't exist
    try:
        projects_dir = resolve_projects_dir()
        assert projects_dir is not None, "Projects resolver should return a path"
        
        slide_dirs = resolve_slide_template_dirs()
        assert isinstance(slide_dirs, list), "Slide template resolver should return a list"
        
        chart_dirs = resolve_chart_template_dirs()
        assert isinstance(chart_dirs, list), "Chart template resolver should return a list"
        
        theme_dirs = resolve_theme_dirs()
        assert isinstance(theme_dirs, list), "Theme resolver should return a list"
        
    except Exception as e:
        assert False, f"Resolvers should handle missing directories gracefully: {e}"
    
    print("✓ Resolvers handle missing directories gracefully")


def run_all_tests():
    """Run all constants and resolver tests"""
    tests = [
        test_base_directory_constant,
        test_system_directory_constants,
        test_user_directory_constants,
        test_css_naming_constants,
        test_theme_naming_constants,
        test_projects_directory_resolver,
        test_slide_template_dirs_resolver,
        test_chart_template_dirs_resolver,
        test_theme_dirs_resolver,
        test_legacy_directory_constants,
        test_path_constant_relationships,
        test_constant_immutability,
        test_resolver_error_handling
    ]
    
    print("\nRunning Constants and Resolver Tests")
    print("=" * 50)
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error - {e}")
            failed.append(test.__name__)
    
    print("=" * 50)
    if not failed:
        print(f"✅ All {len(tests)} constants and resolver tests passed!")
        return True
    else:
        print(f"❌ {len(failed)} tests failed: {', '.join(failed)}")
        return False


if __name__ == "__main__":
    # Make sure we're in the right directory
    os.chdir(Path(__file__).parent.parent)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)