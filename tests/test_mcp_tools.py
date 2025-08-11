#!/usr/bin/env python3
"""
Test suite for SlideAgent MCP tools
Simple, clear tests for each MCP tool
"""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.server import (
    create_project,
    list_projects,
    get_project_info,
    list_themes,
    list_slide_templates,
    list_chart_templates,
    init_slide,
    init_chart,
    swap_theme,
    get_project_theme
)


def test_create_project():
    """Test that create_project creates the correct directory structure"""
    # Cleanup
    test_dir = Path("user_projects/test-project")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create project
    result = create_project("test-project", theme="acme_corp")
    assert "Created project" in result
    
    # Check directories exist
    assert test_dir.exists()
    assert (test_dir / "slides").exists()
    assert (test_dir / "plots").exists()
    assert (test_dir / "input").exists()
    assert (test_dir / "validation").exists()
    assert (test_dir / "theme").exists()
    
    # Check NO config.yaml
    assert not (test_dir / "config.yaml").exists()
    
    # Check theme files copied
    assert (test_dir / "theme" / "base.css").exists()
    assert (test_dir / "theme" / "acme_corp_theme.css").exists()
    assert (test_dir / "theme" / "acme_corp_style.mplstyle").exists()
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_create_project")


def test_get_project_theme():
    """Test that we can detect theme from theme folder"""
    # Setup
    test_dir = Path("user_projects/test-theme")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme", theme="barney")
    
    # Test theme detection
    theme = get_project_theme(test_dir)
    assert theme == "barney"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_get_project_theme")


def test_list_projects():
    """Test that list_projects returns project info without config.yaml"""
    # Setup
    test_dir = Path("user_projects/test-list")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-list", theme="acme_corp")
    
    # Test listing
    projects = list_projects()
    test_project = next((p for p in projects if p["name"] == "test-list"), None)
    
    assert test_project is not None
    assert test_project["theme"] == "acme_corp"
    assert test_project["slides_count"] == 0
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_list_projects")


def test_get_project_info():
    """Test that get_project_info works without config.yaml"""
    # Setup
    test_dir = Path("user_projects/test-info")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-info", theme="barney")
    
    # Test info retrieval
    info = get_project_info("test-info")
    
    assert info["name"] == "test-info"
    assert info["theme"] == "barney"
    assert info["slides_count"] == 0
    assert info["charts_count"] == 0
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_get_project_info")


def test_list_themes():
    """Test that list_themes returns available themes"""
    themes = list_themes()
    
    assert len(themes) > 0
    theme_names = [t["name"] for t in themes]
    assert "acme_corp" in theme_names
    assert "barney" in theme_names
    
    print("✓ test_list_themes")


def test_list_slide_templates():
    """Test that list_slide_templates returns templates with metadata"""
    templates = list_slide_templates()
    
    assert len(templates) > 0
    
    # Check essential templates exist
    template_names = [t["name"] for t in templates]
    assert any("00_title_slide" in name for name in template_names)
    assert any("01_base_slide" in name for name in template_names)
    
    # Check metadata exists
    first_template = templates[0]
    assert "path" in first_template
    assert "name" in first_template
    
    print("✓ test_list_slide_templates")


def test_list_chart_templates():
    """Test that list_chart_templates returns templates"""
    templates = list_chart_templates()
    
    assert len(templates) > 0
    
    # Check common chart types
    template_names = [t["name"] for t in templates]
    assert any("bar_chart" in name for name in template_names)
    assert any("line_chart" in name for name in template_names)
    
    print("✓ test_list_chart_templates")


def test_init_slide():
    """Test that init_slide creates slides with correct CSS paths"""
    # Setup
    test_dir = Path("user_projects/test-slide")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-slide", theme="acme_corp")
    
    # Create slide
    slide_path = init_slide(
        project="test-slide",
        number="01",
        template="slideagent_mcp/resources/templates/slides/00_title_slide.html",
        title="Test Title",
        subtitle="Test Subtitle"
    )
    
    assert "slide_01.html" in slide_path
    
    # Check content
    with open(slide_path, "r") as f:
        content = f.read()
    
    # Check CSS imports are correct
    assert '<link rel="stylesheet" href="../theme/base.css">' in content
    assert '<link rel="stylesheet" href="../theme/acme_corp_theme.css">' in content
    
    # Check replacements worked
    assert "Test Title" in content
    assert "Test Subtitle" in content
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_init_slide")


def test_init_slide_with_different_templates():
    """Test that various slide templates work correctly"""
    # Setup
    test_dir = Path("user_projects/test-templates")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-templates", theme="barney")
    
    # Test different templates
    templates_to_test = [
        "01_base_slide.html",
        "03_two_column_slide.html",
        "05_quote_slide.html"
    ]
    
    for i, template_name in enumerate(templates_to_test, 1):
        slide_path = init_slide(
            project="test-templates",
            number=str(i).zfill(2),
            template=f"slideagent_mcp/resources/templates/slides/{template_name}",
            title=f"Slide {i}"
        )
        
        assert Path(slide_path).exists()
        
        # Check theme CSS
        with open(slide_path, "r") as f:
            content = f.read()
        assert "barney_theme.css" in content
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_init_slide_with_different_templates")


def test_init_chart():
    """Test that init_chart creates chart files correctly"""
    # Setup
    test_dir = Path("user_projects/test-chart")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-chart", theme="acme_corp")
    
    # Test with template
    chart_path = init_chart(
        project="test-chart",
        name="revenue_chart",
        template="slideagent_mcp/resources/templates/charts/bar_chart.py"
    )
    
    assert "revenue_chart.py" in chart_path
    assert Path(chart_path).exists()
    
    # Check content
    with open(chart_path, "r") as f:
        content = f.read()
    
    # Check PlotBuddy import
    assert "from slideagent_mcp.utils.plot_buddy import PlotBuddy" in content
    # Check it uses from_project_config (after our fix)
    assert "PlotBuddy.from_project_config()" in content
    
    # Test without template (minimal)
    minimal_path = init_chart(
        project="test-chart",
        name="minimal_chart"
    )
    
    assert Path(minimal_path).exists()
    with open(minimal_path, "r") as f:
        content = f.read()
    assert "PlotBuddy.from_project_config()" in content
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_init_chart")


def test_swap_theme():
    """Test that swap_theme correctly changes theme files and updates slides"""
    # Setup
    test_dir = Path("user_projects/test-swap")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-swap", theme="acme_corp")
    
    # Create a slide first
    init_slide(
        project="test-swap",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Test"
    )
    
    # Check initial theme
    assert get_project_theme(test_dir) == "acme_corp"
    assert (test_dir / "theme" / "acme_corp_theme.css").exists()
    
    # Swap theme
    result = swap_theme("test-swap", "barney")
    assert "Updated" in result
    
    # Check new theme files exist
    assert (test_dir / "theme" / "barney_theme.css").exists()
    assert (test_dir / "theme" / "barney_style.mplstyle").exists()
    
    # Check old theme files removed (except base.css)
    assert not (test_dir / "theme" / "acme_corp_theme.css").exists()
    assert (test_dir / "theme" / "base.css").exists()  # Should be preserved
    
    # Check slide was updated
    with open(test_dir / "slides" / "slide_01.html", "r") as f:
        content = f.read()
    
    assert "barney_theme.css" in content
    assert "acme_corp_theme.css" not in content
    
    # Check theme detection
    assert get_project_theme(test_dir) == "barney"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_swap_theme")


def test_error_handling():
    """Test that tools handle errors correctly"""
    # Test non-existent project
    try:
        get_project_info("non-existent-project")
        assert False, "Should have raised error"
    except ValueError as e:
        assert "not found" in str(e)
    
    # Test invalid theme in swap
    test_dir = Path("user_projects/test-errors")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-errors", theme="acme_corp")
    
    result = swap_theme("test-errors", "non-existent-theme")
    assert "Error" in result
    assert "not found" in result
    
    # Test duplicate project
    result = create_project("test-errors", theme="acme_corp")
    assert "Error" in result
    assert "already exists" in result
    
    # Test invalid template
    result = init_slide(
        project="test-errors",
        number="01",
        template="non-existent.html",
        title="Test"
    )
    assert "Error" in result
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_error_handling")


def test_theme_detection_error():
    """Test that get_project_theme raises error when no theme found"""
    # Create a project then remove theme files
    test_dir = Path("user_projects/test-no-theme")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    (test_dir / "theme").mkdir()
    
    # No theme CSS files
    try:
        get_project_theme(test_dir)
        assert False, "Should have raised error"
    except ValueError as e:
        assert "No theme CSS file found" in str(e)
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_theme_detection_error")


def test_slide_numbering():
    """Test that slide numbering works with different formats"""
    # Setup
    test_dir = Path("user_projects/test-numbering")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-numbering", theme="acme_corp")
    
    # Test different number formats
    formats = [
        ("1", "slide_01.html"),
        ("01", "slide_01.html"),
        ("slide_01", "slide_01.html"),
        ("10", "slide_10.html"),
        ("slide_10", "slide_10.html")
    ]
    
    for input_num, expected_name in formats:
        result = init_slide(
            project="test-numbering",
            number=input_num,
            template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
            title="Test"
        )
        assert expected_name in result
        assert Path(result).exists()
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ test_slide_numbering")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_create_project,
        test_get_project_theme,
        test_list_projects,
        test_get_project_info,
        test_list_themes,
        test_list_slide_templates,
        test_list_chart_templates,
        test_init_slide,
        test_init_slide_with_different_templates,
        test_init_chart,
        test_swap_theme,
        test_error_handling,
        test_theme_detection_error,
        test_slide_numbering
    ]
    
    print("\nRunning SlideAgent MCP Tests")
    print("=" * 40)
    
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
    
    print("=" * 40)
    if not failed:
        print(f"✅ All {len(tests)} tests passed!")
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