#!/usr/bin/env python3
"""Test the refactored SlideAgent MCP tools"""

import sys
import os
import shutil
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the MCP decorator since we're testing without MCP
class MockMCP:
    def tool(self):
        def decorator(func):
            return func
        return decorator
    def run(self):
        pass

# Replace MCP imports
sys.modules['mcp'] = type(sys)('mcp')
sys.modules['mcp.server'] = type(sys)('mcp.server')
sys.modules['mcp.server.fastmcp'] = type(sys)('mcp.server.fastmcp')
sys.modules['mcp.server.fastmcp'].FastMCP = lambda x: MockMCP()

# Now import our server
from slideagent_mcp import server

def test_create_project():
    """Test creating a new project"""
    print("\n=== Testing create_project ===")
    
    # Clean up test project if exists
    test_project = Path("user_projects/test_refactor")
    if test_project.exists():
        shutil.rmtree(test_project)
    
    result = server.create_project("test_refactor", theme="acme_corp")
    print(f"Result: {result}")
    
    # Check project was created
    assert test_project.exists(), "Project directory not created"
    assert (test_project / "slides").exists(), "Slides directory not created"
    assert (test_project / "report_pages").exists(), "Report pages directory not created"
    assert (test_project / "theme").exists(), "Theme directory not created"
    assert (test_project / ".theme").exists(), ".theme file not created"
    
    theme_name = (test_project / ".theme").read_text().strip()
    assert theme_name == "acme_corp", f"Wrong theme saved: {theme_name}"
    
    print("✓ create_project works!")
    return True

def test_get_projects():
    """Test getting project information"""
    print("\n=== Testing get_projects ===")
    
    # Get all projects
    all_projects = server.get_projects()
    print(f"Found {len(all_projects)} projects")
    
    # Get specific project
    test_projects = server.get_projects("test_refactor")
    assert len(test_projects) == 1, "Should find exactly one test project"
    assert test_projects[0]["name"] == "test_refactor"
    
    # Get multiple specific projects
    multi = server.get_projects(["test_refactor", "nonexistent"])
    assert len(multi) == 1, "Should only find existing project"
    
    # Test with fields filter
    filtered = server.get_projects("test_refactor", fields=["name", "theme"])
    assert "name" in filtered[0] and "theme" in filtered[0]
    assert "path" not in filtered[0], "Filtered fields should not include path"
    
    print("✓ get_projects works!")
    return True

def test_get_themes():
    """Test getting theme information"""
    print("\n=== Testing get_themes ===")
    
    # Get all themes
    all_themes = server.get_themes()
    print(f"Found {len(all_themes)} themes")
    assert len(all_themes) > 0, "Should find some themes"
    
    # Get specific theme
    acme = server.get_themes("acme_corp")
    assert len(acme) == 1, "Should find acme_corp theme"
    assert acme[0]["name"] == "acme_corp"
    
    # Get multiple themes
    multi = server.get_themes(["acme_corp", "barney"])
    print(f"Found themes: {[t['name'] for t in multi]}")
    
    print("✓ get_themes works!")
    return True

def test_get_templates():
    """Test getting template information"""
    print("\n=== Testing get_templates ===")
    
    # Get all slide templates
    slides = server.get_templates("slides")
    print(f"Found {len(slides)} slide templates")
    assert len(slides) > 0, "Should find slide templates"
    
    # Get specific template
    base_slide = server.get_templates("slides", "01_base_slide")
    assert len(base_slide) <= 1, "Should find at most one base slide"
    
    # Test other types
    reports = server.get_templates("reports")
    charts = server.get_templates("charts")
    print(f"Found {len(reports)} report templates, {len(charts)} chart templates")
    
    print("✓ get_templates works!")
    return True

def test_init_from_template():
    """Test initializing content from templates"""
    print("\n=== Testing init_from_template ===")
    
    # Test creating a slide
    slide_result = server.init_from_template(
        project="test_refactor",
        resource_type="slide",
        name="01",
        title="Test Slide",
        subtitle="Testing the refactor",
        section="Test Section"
    )
    print(f"Created slide: {slide_result}")
    assert Path(slide_result).exists(), "Slide file not created"
    
    # Check content has placeholders replaced
    content = Path(slide_result).read_text()
    assert "Test Slide" in content, "Title not replaced"
    assert "Testing the refactor" in content, "Subtitle not replaced"
    
    # Test creating a chart
    chart_result = server.init_from_template(
        project="test_refactor",
        resource_type="chart",
        name="test_chart"
    )
    print(f"Created chart: {chart_result}")
    assert Path(chart_result).exists(), "Chart file not created"
    
    # Test creating outline
    outline_result = server.init_from_template(
        project="test_refactor",
        resource_type="outline",
        name="outline",
        template="outline_slides.md",
        title="Test Project",
        author="Test Author",
        theme="acme_corp"
    )
    print(f"Created outline: {outline_result}")
    
    print("✓ init_from_template works!")
    return True

def test_swap_theme():
    """Test swapping project theme"""
    print("\n=== Testing swap_theme ===")
    
    # Check if barney theme exists
    barney_themes = server.get_themes("barney")
    if not barney_themes:
        print("⚠ Barney theme not found, skipping swap test")
        return True
    
    result = server.swap_theme("test_refactor", "barney")
    print(f"Swap result: {result}")
    
    # Verify theme was changed
    test_project = Path("user_projects/test_refactor")
    theme_name = (test_project / ".theme").read_text().strip()
    assert theme_name == "barney", f"Theme not updated: {theme_name}"
    
    print("✓ swap_theme works!")
    return True

def main():
    """Run all tests"""
    print("Testing refactored SlideAgent MCP tools...")
    
    tests = [
        test_create_project,
        test_get_projects,
        test_get_themes,
        test_get_templates,
        test_init_from_template,
        test_swap_theme
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
    
    if failed:
        print(f"\n❌ {len(failed)} tests failed: {failed}")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())