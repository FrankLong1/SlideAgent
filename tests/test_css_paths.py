#!/usr/bin/env python3
"""
Test CSS path resolution and naming consistency.

This test suite validates the critical CSS path resolution issues that have caused
problems in production, specifically:
- slide_base.css vs base.css naming inconsistencies
- Relative path resolution from slides/ to theme/
- CSS imports in generated HTML
- Self-contained project structure
"""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.server import (
    create_project,
    init_slide,
    swap_theme,
    SLIDE_BASE_CSS_NAME,
    SLIDE_BASE_CSS_SOURCE,
    REL_PATH_TO_THEME_FROM_SLIDES
)


def test_css_file_naming_constants():
    """Test that CSS naming constants are correct and consistent"""
    # Verify the constants match expected values
    assert SLIDE_BASE_CSS_NAME == "slide_base.css", f"Expected 'slide_base.css', got {SLIDE_BASE_CSS_NAME}"
    
    # Verify source file exists
    assert SLIDE_BASE_CSS_SOURCE.exists(), f"Source CSS file not found: {SLIDE_BASE_CSS_SOURCE}"
    
    # Verify relative path constant is correct
    assert REL_PATH_TO_THEME_FROM_SLIDES == "../theme", f"Wrong relative path: {REL_PATH_TO_THEME_FROM_SLIDES}"
    
    print("✓ CSS naming constants are correct")


def test_project_css_file_copying():
    """Test that slide_base.css is correctly copied to project theme folder"""
    # Setup
    test_dir = Path("user_projects/test-css-copy")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create project
    create_project("test-css-copy", theme="acme_corp")
    
    # Check that slide_base.css was copied (not base.css)
    slide_base_path = test_dir / "theme" / SLIDE_BASE_CSS_NAME
    base_css_path = test_dir / "theme" / "base.css"  # Old naming
    
    assert slide_base_path.exists(), f"slide_base.css not found: {slide_base_path}"
    assert not base_css_path.exists(), f"Found deprecated base.css file: {base_css_path}"
    
    # Verify content is actually CSS
    with open(slide_base_path) as f:
        content = f.read()
    assert len(content) > 100, "CSS file seems empty or too small"
    assert "/* " in content or "html" in content or "body" in content, "Doesn't look like CSS content"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ slide_base.css correctly copied to project theme folder")


def test_slide_css_imports():
    """Test that generated slides have correct CSS import paths"""
    # Setup
    test_dir = Path("user_projects/test-css-imports")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-css-imports", theme="barney")
    
    # Create a slide
    slide_path = init_slide(
        project="test-css-imports",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="CSS Import Test"
    )
    
    # Read slide content
    with open(slide_path) as f:
        content = f.read()
    
    # Check CSS imports use correct file names and paths
    expected_slide_base = f'<link rel="stylesheet" href="{REL_PATH_TO_THEME_FROM_SLIDES}/{SLIDE_BASE_CSS_NAME}">'
    expected_theme_css = f'<link rel="stylesheet" href="{REL_PATH_TO_THEME_FROM_SLIDES}/barney_theme.css">'
    
    assert expected_slide_base in content, f"Missing correct slide_base.css import: {expected_slide_base}"
    assert expected_theme_css in content, f"Missing theme CSS import: {expected_theme_css}"
    
    # Ensure deprecated base.css import is NOT present
    deprecated_import = f'<link rel="stylesheet" href="{REL_PATH_TO_THEME_FROM_SLIDES}/base.css">'
    assert deprecated_import not in content, f"Found deprecated base.css import: {deprecated_import}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Generated slides have correct CSS imports")


def test_css_paths_across_templates():
    """Test CSS paths are correct across different slide templates"""
    # Setup
    test_dir = Path("user_projects/test-css-templates")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-css-templates", theme="acme_corp")
    
    # Test various template types
    templates_to_test = [
        ("00_title_slide.html", "Title"),
        ("01_base_slide.html", "Base"),
        ("03_two_column_slide.html", "Two Column"),
        ("05_quote_slide.html", "Quote"),
        ("07_financial_data_table.html", "Table"),
    ]
    
    for i, (template_name, title) in enumerate(templates_to_test, 1):
        slide_path = init_slide(
            project="test-css-templates",
            number=str(i).zfill(2),
            template=f"slideagent_mcp/resources/templates/slides/{template_name}",
            title=f"{title} Test"
        )
        
        # Check CSS imports
        with open(slide_path) as f:
            content = f.read()
        
        # All templates should have consistent CSS imports
        slide_base_import = f'href="{REL_PATH_TO_THEME_FROM_SLIDES}/{SLIDE_BASE_CSS_NAME}"'
        theme_import = f'href="{REL_PATH_TO_THEME_FROM_SLIDES}/acme_corp_theme.css"'
        
        assert slide_base_import in content, f"Template {template_name} missing slide_base.css import"
        assert theme_import in content, f"Template {template_name} missing theme CSS import"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ All slide templates have consistent CSS imports")


def test_theme_swap_css_consistency():
    """Test that theme swapping maintains CSS path consistency"""
    # Setup
    test_dir = Path("user_projects/test-css-swap")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-css-swap", theme="acme_corp")
    
    # Create a slide
    slide_path = init_slide(
        project="test-css-swap",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Theme Swap Test"
    )
    
    # Verify initial state
    with open(slide_path) as f:
        content = f.read()
    assert "acme_corp_theme.css" in content
    assert f"{SLIDE_BASE_CSS_NAME}" in content
    
    # Swap theme
    swap_theme("test-css-swap", "barney")
    
    # Check updated slide
    with open(slide_path) as f:
        content = f.read()
    
    # Should have new theme CSS but same slide_base.css
    assert "barney_theme.css" in content, "Theme CSS not updated"
    assert "acme_corp_theme.css" not in content, "Old theme CSS still present"
    assert f"{SLIDE_BASE_CSS_NAME}" in content, "slide_base.css reference lost"
    
    # Verify files exist
    assert (test_dir / "theme" / SLIDE_BASE_CSS_NAME).exists(), "slide_base.css file missing after swap"
    assert (test_dir / "theme" / "barney_theme.css").exists(), "New theme CSS missing"
    assert not (test_dir / "theme" / "acme_corp_theme.css").exists(), "Old theme CSS not removed"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Theme swapping maintains CSS path consistency")


def test_css_self_containment():
    """Test that projects are self-contained with all CSS files"""
    # Setup
    test_dir = Path("user_projects/test-css-self-contained")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-css-self-contained", theme="barney")
    
    # Create a slide
    init_slide(
        project="test-css-self-contained",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Self-Containment Test"
    )
    
    # Verify all required CSS files exist in project
    theme_dir = test_dir / "theme"
    
    required_files = [
        SLIDE_BASE_CSS_NAME,  # Core slide CSS
        "barney_theme.css",   # Theme-specific CSS
        "barney_style.mplstyle",  # Matplotlib theme
        "barney_icon_logo.png",   # Icon logo
        "barney_text_logo.png"    # Text logo
    ]
    
    for file_name in required_files:
        file_path = theme_dir / file_name
        assert file_path.exists(), f"Required file missing: {file_path}"
    
    # Verify slide can be opened with relative paths
    slide_path = test_dir / "slides" / "slide_01.html"
    with open(slide_path) as f:
        content = f.read()
    
    # All referenced files should exist relative to slide location
    import re
    css_refs = re.findall(r'href="([^"]+\.css)"', content)
    img_refs = re.findall(r'src="([^"]+\.png)"', content)
    
    for css_ref in css_refs:
        if css_ref.startswith("../"):  # Relative path
            resolved_path = (slide_path.parent / css_ref).resolve()
            assert resolved_path.exists(), f"CSS reference broken: {css_ref} -> {resolved_path}"
    
    # Check for any absolute paths (should be avoided)
    assert not any("/slideagent_mcp/" in ref for ref in css_refs), "Found absolute paths to system CSS"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Projects are self-contained with all CSS files")


def test_css_path_edge_cases():
    """Test edge cases in CSS path handling"""
    # Test with project names containing special characters
    test_cases = [
        "test-project-with-dashes",
        "test_project_with_underscores", 
        "testprojectwithoutspaces"
    ]
    
    for project_name in test_cases:
        test_dir = Path(f"user_projects/{project_name}")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        # Create and test project
        create_project(project_name, theme="acme_corp")
        
        # Verify CSS files copied correctly
        assert (test_dir / "theme" / SLIDE_BASE_CSS_NAME).exists(), f"CSS missing for project: {project_name}"
        
        # Create slide and verify paths
        slide_path = init_slide(
            project=project_name,
            number="01",
            template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
            title="Edge Case Test"
        )
        
        with open(slide_path) as f:
            content = f.read()
        
        # Paths should still be relative and correct
        assert f'href="../theme/{SLIDE_BASE_CSS_NAME}"' in content, f"Wrong CSS path for project: {project_name}"
        
        # Cleanup
        shutil.rmtree(test_dir)
    
    print("✓ CSS paths handle edge cases correctly")


def test_missing_css_error_handling():
    """Test proper error handling when CSS files are missing"""
    # Create project but manually remove CSS files
    test_dir = Path("user_projects/test-css-missing")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-css-missing", theme="acme_corp")
    
    # Remove slide_base.css
    css_file = test_dir / "theme" / SLIDE_BASE_CSS_NAME
    css_file.unlink()
    
    # Try to create a slide - should handle gracefully
    slide_path = init_slide(
        project="test-css-missing",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Missing CSS Test"
    )
    
    # Slide should still be created (MCP tools are robust)
    assert Path(slide_path).exists(), "Slide creation should succeed even with missing CSS"
    
    # But CSS reference should still be in HTML (for when CSS is restored)
    with open(slide_path) as f:
        content = f.read()
    assert f"{SLIDE_BASE_CSS_NAME}" in content, "CSS reference should still be in HTML"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Graceful handling of missing CSS files")


def run_all_tests():
    """Run all CSS path tests"""
    tests = [
        test_css_file_naming_constants,
        test_project_css_file_copying,
        test_slide_css_imports,
        test_css_paths_across_templates,
        test_theme_swap_css_consistency,
        test_css_self_containment,
        test_css_path_edge_cases,
        test_missing_css_error_handling
    ]
    
    print("\nRunning CSS Path Resolution Tests")
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
        print(f"✅ All {len(tests)} CSS path tests passed!")
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