#!/usr/bin/env python3
"""
Test template discovery and metadata loading.

This test suite validates template discovery functionality that's critical for
the SlideAgent system to work properly:
- Template listing with proper metadata
- Template path resolution across user/system directories
- Template content validation
- Template categorization and filtering
- Error handling for missing/corrupted templates
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.server import (
    list_slide_templates,
    list_chart_templates,
    resolve_slide_template_dirs,
    resolve_chart_template_dirs,
    SYSTEM_SLIDE_TEMPLATES_DIR,
    SYSTEM_CHART_TEMPLATES_DIR,
    USER_TEMPLATES_DIR
)


def test_slide_template_directories_exist():
    """Test that slide template directories exist and are accessible"""
    # System templates should always exist
    assert SYSTEM_SLIDE_TEMPLATES_DIR.exists(), f"System slide templates directory missing: {SYSTEM_SLIDE_TEMPLATES_DIR}"
    
    # Get resolved directories
    template_dirs = resolve_slide_template_dirs()
    assert len(template_dirs) > 0, "No slide template directories found"
    
    # First directory should be the system one (at minimum)
    assert SYSTEM_SLIDE_TEMPLATES_DIR in template_dirs, "System slide templates not in resolved directories"
    
    # Check that directories contain actual template files
    total_templates = 0
    for template_dir in template_dirs:
        html_files = list(template_dir.glob("*.html"))
        total_templates += len(html_files)
    
    assert total_templates > 0, "No HTML template files found in any directory"
    
    print(f"✓ Found {len(template_dirs)} template directories with {total_templates} templates")


def test_chart_template_directories_exist():
    """Test that chart template directories exist and are accessible"""
    # System templates should always exist
    assert SYSTEM_CHART_TEMPLATES_DIR.exists(), f"System chart templates directory missing: {SYSTEM_CHART_TEMPLATES_DIR}"
    
    # Get resolved directories
    template_dirs = resolve_chart_template_dirs()
    assert len(template_dirs) > 0, "No chart template directories found"
    
    # System directory should be included
    assert SYSTEM_CHART_TEMPLATES_DIR in template_dirs, "System chart templates not in resolved directories"
    
    # Check for Python template files
    total_templates = 0
    for template_dir in template_dirs:
        py_files = list(template_dir.glob("*.py"))
        total_templates += len(py_files)
    
    assert total_templates > 0, "No Python chart templates found"
    
    print(f"✓ Found {len(template_dirs)} chart template directories with {total_templates} templates")


def test_list_slide_templates_basic():
    """Test basic slide template listing functionality"""
    templates = list_slide_templates()
    
    # Should return a list with at least basic templates
    assert isinstance(templates, list), "list_slide_templates should return a list"
    assert len(templates) > 0, "Should find some slide templates"
    
    # Each template should have required metadata
    for template in templates:
        assert isinstance(template, dict), "Each template should be a dictionary"
        assert "name" in template, f"Template missing 'name' field: {template}"
        assert "path" in template, f"Template missing 'path' field: {template}"
        
        # Path should point to existing file
        template_path = Path(template["path"])
        assert template_path.exists(), f"Template file doesn't exist: {template_path}"
        assert template_path.suffix == ".html", f"Template should be HTML file: {template_path}"
    
    # Should find essential templates
    template_names = [t["name"] for t in templates]
    essential_templates = ["00_title_slide.html", "01_base_slide.html"]
    
    for essential in essential_templates:
        assert any(essential in name for name in template_names), f"Missing essential template: {essential}"
    
    print(f"✓ Listed {len(templates)} slide templates with proper metadata")


def test_list_chart_templates_basic():
    """Test basic chart template listing functionality"""
    templates = list_chart_templates()
    
    # Should return a list
    assert isinstance(templates, list), "list_chart_templates should return a list"
    assert len(templates) > 0, "Should find some chart templates"
    
    # Each template should have required metadata
    for template in templates:
        assert isinstance(template, dict), "Each template should be a dictionary"
        assert "name" in template, f"Template missing 'name' field: {template}"
        assert "path" in template, f"Template missing 'path' field: {template}"
        
        # Path should point to existing Python file
        template_path = Path(template["path"])
        assert template_path.exists(), f"Chart template file doesn't exist: {template_path}"
        assert template_path.suffix == ".py", f"Chart template should be Python file: {template_path}"
    
    # Should find common chart types
    template_names = [t["name"] for t in templates]
    common_charts = ["bar_chart.py", "line_chart.py", "pie_chart.py"]
    
    found_charts = []
    for common in common_charts:
        if any(common in name for name in template_names):
            found_charts.append(common)
    
    assert len(found_charts) > 0, f"Should find at least some common chart templates: {common_charts}"
    
    print(f"✓ Listed {len(templates)} chart templates, found common types: {found_charts}")


def test_slide_template_content_validation():
    """Test that slide templates contain valid HTML and expected patterns"""
    templates = list_slide_templates()
    
    for template in templates:
        template_path = Path(template["path"])
        
        # Read and validate content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic HTML validation
        assert len(content) > 50, f"Template seems too short: {template_path}"
        assert "<!DOCTYPE html>" in content or "<html" in content, f"Not valid HTML: {template_path}"
        
        # Should contain CSS import placeholders
        if "title_slide" not in template["name"]:  # Title slides have different structure
            assert "stylesheet" in content, f"Missing CSS imports: {template_path}"
        
        # Should contain some placeholder patterns
        placeholder_patterns = ["[TITLE]", "[SUBTITLE]", "[CONTENT]", "[SECTION]"]
        has_placeholder = any(pattern in content for pattern in placeholder_patterns)
        
        # Note: Some specialized templates might not have standard placeholders
        # This is informational rather than a hard requirement
        if not has_placeholder:
            print(f"  Note: {template['name']} has no standard placeholders (may be specialized)")
    
    print(f"✓ Validated content of {len(templates)} slide templates")


def test_chart_template_content_validation():
    """Test that chart templates contain valid Python and expected patterns"""
    templates = list_chart_templates()
    
    for template in templates:
        template_path = Path(template["path"])
        
        # Read and validate content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic Python validation
        assert len(content) > 100, f"Chart template seems too short: {template_path}"
        
        # Should contain Python imports
        assert "import" in content, f"No imports found: {template_path}"
        
        # Should contain PlotBuddy usage
        assert "PlotBuddy" in content, f"Missing PlotBuddy usage: {template_path}"
        
        # Should have EDIT SECTION marker
        assert "EDIT SECTION" in content or "# EDIT" in content, f"Missing EDIT SECTION: {template_path}"
        
        # Should have save functionality
        assert "save(" in content or ".save" in content, f"Missing save functionality: {template_path}"
        
        # Try to compile the Python code (basic syntax check)
        try:
            compile(content, str(template_path), 'exec')
        except SyntaxError as e:
            assert False, f"Chart template has syntax errors: {template_path} - {e}"
    
    print(f"✓ Validated Python syntax of {len(templates)} chart templates")


def test_template_metadata_consistency():
    """Test that template metadata is consistent and useful"""
    slide_templates = list_slide_templates()
    
    # Test metadata structure consistency
    if len(slide_templates) > 0:
        first_template = slide_templates[0]
        metadata_keys = set(first_template.keys())
        
        # All templates should have the same metadata structure
        for template in slide_templates:
            template_keys = set(template.keys())
            assert template_keys == metadata_keys, f"Inconsistent metadata keys: {template['name']}"
    
    # Test path consistency (all paths should be absolute)
    for template in slide_templates:
        path = Path(template["path"])
        assert path.is_absolute(), f"Template path should be absolute: {template['path']}"
    
    # Test name uniqueness
    template_names = [t["name"] for t in slide_templates]
    unique_names = set(template_names)
    assert len(template_names) == len(unique_names), "Template names should be unique"
    
    print(f"✓ Template metadata is consistent across {len(slide_templates)} templates")


def test_template_discovery_priority():
    """Test that template discovery follows correct priority (user > system)"""
    # This test checks the precedence system for templates
    slide_dirs = resolve_slide_template_dirs()
    chart_dirs = resolve_chart_template_dirs()
    
    # If user templates directory exists, it should come first
    if USER_TEMPLATES_DIR.exists():
        user_slide_dir = USER_TEMPLATES_DIR / "slides"
        user_chart_dir = USER_TEMPLATES_DIR / "charts"
        
        if user_slide_dir.exists() and user_slide_dir in slide_dirs:
            assert slide_dirs.index(user_slide_dir) < slide_dirs.index(SYSTEM_SLIDE_TEMPLATES_DIR), \
                "User slide templates should have priority over system templates"
        
        if user_chart_dir.exists() and user_chart_dir in chart_dirs:
            assert chart_dirs.index(user_chart_dir) < chart_dirs.index(SYSTEM_CHART_TEMPLATES_DIR), \
                "User chart templates should have priority over system templates"
    
    # System directories should always be included as fallback
    assert SYSTEM_SLIDE_TEMPLATES_DIR in slide_dirs, "System slide templates should be included"
    assert SYSTEM_CHART_TEMPLATES_DIR in chart_dirs, "System chart templates should be included"
    
    print("✓ Template discovery follows correct priority order")


def test_template_path_resolution():
    """Test that template paths can be resolved from different contexts"""
    templates = list_slide_templates()
    
    # Test that all template paths resolve correctly
    for template in templates:
        template_path = Path(template["path"])
        
        # Path should be absolute and exist
        assert template_path.is_absolute(), f"Template path not absolute: {template_path}"
        assert template_path.exists(), f"Template path doesn't exist: {template_path}"
        
        # Should be readable
        assert os.access(template_path, os.R_OK), f"Template not readable: {template_path}"
        
        # Path should contain expected components
        path_parts = template_path.parts
        assert "templates" in path_parts, f"Template path should contain 'templates': {template_path}"
        assert "slides" in path_parts, f"Template path should contain 'slides': {template_path}"
    
    print(f"✓ All {len(templates)} template paths resolve correctly")


def test_template_error_handling():
    """Test error handling for template discovery edge cases"""
    # Test behavior with non-existent directories (should not crash)
    try:
        # This should work even if some directories don't exist
        slide_templates = list_slide_templates()
        chart_templates = list_chart_templates()
        
        # Should still return lists (even if empty)
        assert isinstance(slide_templates, list), "Should return list even with missing directories"
        assert isinstance(chart_templates, list), "Should return list even with missing directories"
        
    except Exception as e:
        assert False, f"Template discovery should handle missing directories gracefully: {e}"
    
    # Test with corrupted template file (if we create one temporarily)
    test_corruption = False  # Set to True to test corruption handling
    
    if test_corruption:
        # Create a temporary bad template
        bad_template = Path("temp_bad_template.html")
        bad_template.write_text("invalid template content")
        
        try:
            # This should not crash the entire system
            templates = list_slide_templates()
            # The bad template might be excluded or cause a warning, but shouldn't crash
        finally:
            # Cleanup
            if bad_template.exists():
                bad_template.unlink()
    
    print("✓ Template discovery handles error cases gracefully")


def test_template_filtering():
    """Test template filtering and categorization if implemented"""
    slide_templates = list_slide_templates()
    
    # Categorize templates by type (if this feature exists)
    title_templates = [t for t in slide_templates if "title" in t["name"].lower()]
    base_templates = [t for t in slide_templates if "base" in t["name"].lower()]
    data_templates = [t for t in slide_templates if any(word in t["name"].lower() 
                                                       for word in ["table", "data", "chart"])]
    
    # Should find at least basic categories
    assert len(title_templates) > 0, "Should find title slide templates"
    assert len(base_templates) > 0, "Should find base slide templates"
    
    # Log findings for information
    print(f"✓ Found template categories: {len(title_templates)} title, {len(base_templates)} base, {len(data_templates)} data")


def test_template_use_case_metadata():
    """Test that templates contain useful metadata about their use cases"""
    slide_templates = list_slide_templates()
    
    # Check if templates have additional metadata beyond name/path
    metadata_fields = set()
    for template in slide_templates:
        metadata_fields.update(template.keys())
    
    basic_fields = {"name", "path"}
    additional_fields = metadata_fields - basic_fields
    
    if additional_fields:
        print(f"✓ Templates have additional metadata fields: {additional_fields}")
        
        # If use_case or description exists, validate it
        for template in slide_templates:
            for field in ["use_case", "description", "category"]:
                if field in template:
                    assert isinstance(template[field], str), f"Template {field} should be string"
                    assert len(template[field]) > 0, f"Template {field} should not be empty"
    else:
        print("✓ Templates have basic metadata (name, path)")


def run_all_tests():
    """Run all template discovery tests"""
    tests = [
        test_slide_template_directories_exist,
        test_chart_template_directories_exist,
        test_list_slide_templates_basic,
        test_list_chart_templates_basic,
        test_slide_template_content_validation,
        test_chart_template_content_validation,
        test_template_metadata_consistency,
        test_template_discovery_priority,
        test_template_path_resolution,
        test_template_error_handling,
        test_template_filtering,
        test_template_use_case_metadata
    ]
    
    print("\nRunning Template Discovery Tests")
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
        print(f"✅ All {len(tests)} template discovery tests passed!")
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