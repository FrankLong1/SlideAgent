#!/usr/bin/env python3
"""Comprehensive tests for refactored SlideAgent MCP tools"""

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

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    # Test getting non-existent project
    result = server.get_projects("nonexistent_project_12345")
    assert len(result) == 0, "Should return empty list for non-existent project"
    print("✓ Non-existent project returns empty list")
    
    # Test getting non-existent theme
    result = server.get_themes("fake_theme_xyz")
    assert len(result) == 0, "Should return empty list for non-existent theme"
    print("✓ Non-existent theme returns empty list")
    
    # Test invalid template type
    try:
        server.get_templates("invalid_type")
        assert False, "Should raise error for invalid template type"
    except ValueError as e:
        assert "Must be 'slides', 'reports', or 'charts'" in str(e)
        print("✓ Invalid template type raises error")
    
    # Test init_from_template with non-existent project
    result = server.init_from_template(
        project="nonexistent_project",
        resource_type="slide",
        name="01"
    )
    assert "Error" in result, "Should return error for non-existent project"
    print("✓ init_from_template handles non-existent project")
    
    # Test init_from_template with invalid resource type
    result = server.init_from_template(
        project="test_refactor",
        resource_type="invalid_type",
        name="test"
    )
    assert "Error" in result, "Should return error for invalid resource type"
    print("✓ init_from_template handles invalid resource type")

def test_multiple_slides_reports():
    """Test creating multiple slides and reports"""
    print("\n=== Testing Multiple Content Creation ===")
    
    # Create multiple slides
    for i in range(1, 4):
        result = server.init_from_template(
            project="test_refactor",
            resource_type="slide",
            name=str(i).zfill(2),
            title=f"Slide {i}",
            subtitle=f"Subtitle for slide {i}",
            section=f"Section {(i-1)//2 + 1}"
        )
        assert Path(result).exists(), f"Slide {i} not created"
    print("✓ Created 3 slides successfully")
    
    # Create multiple report pages
    for i in range(1, 3):
        result = server.init_from_template(
            project="test_refactor",
            resource_type="report",
            name=str(i).zfill(2),
            title=f"Report Page {i}",
            subtitle=f"Analysis section {i}"
        )
        assert Path(result).exists(), f"Report page {i} not created"
    print("✓ Created 2 report pages successfully")
    
    # Verify files have correct names
    slides_dir = Path("user_projects/test_refactor/slides")
    slide_files = list(slides_dir.glob("slide_*.html"))
    assert len(slide_files) >= 3, f"Expected at least 3 slides, found {len(slide_files)}"
    
    reports_dir = Path("user_projects/test_refactor/report_pages")
    report_files = list(reports_dir.glob("report_*.html"))
    assert len(report_files) >= 2, f"Expected at least 2 reports, found {len(report_files)}"
    print("✓ Files have correct naming convention")

def test_chart_creation():
    """Test various chart creation scenarios"""
    print("\n=== Testing Chart Creation ===")
    
    # Create chart without template (uses boilerplate)
    result = server.init_from_template(
        project="test_refactor",
        resource_type="chart",
        name="revenue_chart"
    )
    assert Path(result).exists(), "Chart not created"
    
    # Check chart is executable
    import stat
    file_stat = Path(result).stat()
    assert file_stat.st_mode & stat.S_IXUSR, "Chart should be executable"
    print("✓ Chart created with boilerplate and is executable")
    
    # Check chart has correct imports
    content = Path(result).read_text()
    assert "PlotBuddy" in content, "Chart should import PlotBuddy"
    assert "matplotlib" in content, "Chart should import matplotlib"
    print("✓ Chart has correct imports")

def test_project_info_fields():
    """Test project info with different field filters"""
    print("\n=== Testing Project Info Fields ===")
    
    # Get all fields
    all_info = server.get_projects("test_refactor")
    assert len(all_info) == 1
    project = all_info[0]
    
    expected_fields = ["name", "path", "theme", "slides_count", "charts_count"]
    for field in expected_fields:
        assert field in project, f"Missing field: {field}"
    print("✓ All expected fields present")
    
    # Get only specific fields
    filtered = server.get_projects("test_refactor", fields=["name", "theme"])
    assert len(filtered) == 1
    assert "name" in filtered[0]
    assert "theme" in filtered[0]
    assert "slides_count" not in filtered[0], "Filtered out fields should not be present"
    print("✓ Field filtering works correctly")

def test_theme_swapping():
    """Test theme swapping with file updates"""
    print("\n=== Testing Theme Swapping ===")
    
    # Get initial theme
    project_info = server.get_projects("test_refactor")[0]
    initial_theme = project_info["theme"]
    
    # Find a different theme to swap to
    all_themes = server.get_themes()
    other_theme = None
    for theme in all_themes:
        if theme["name"] != initial_theme:
            other_theme = theme["name"]
            break
    
    if other_theme:
        # Swap theme
        result = server.swap_theme("test_refactor", other_theme)
        assert "Updated" in result, "Theme swap should succeed"
        
        # Verify theme changed
        new_info = server.get_projects("test_refactor")[0]
        assert new_info["theme"] == other_theme, "Theme should be updated"
        
        # Check slides were updated
        slides_dir = Path("user_projects/test_refactor/slides")
        if slides_dir.exists():
            for slide in slides_dir.glob("*.html"):
                content = slide.read_text()
                assert f"{other_theme}_theme.css" in content, "Slide CSS should be updated"
        
        print(f"✓ Theme swapped from {initial_theme} to {other_theme}")
    else:
        print("⚠ Only one theme available, skipping swap test")

def test_outline_templates():
    """Test outline template creation"""
    print("\n=== Testing Outline Templates ===")
    
    # Create slides outline
    result = server.init_from_template(
        project="test_refactor",
        resource_type="outline",
        name="slides_outline",
        template="outline_slides.md",
        title="Test Presentation",
        author="Test Author",
        theme="acme_corp",
        date="2024-01-01"
    )
    assert Path(result).exists(), "Slides outline not created"
    
    content = Path(result).read_text()
    assert "Test Presentation" in content, "Title not replaced in outline"
    assert "Test Author" in content, "Author not replaced in outline"
    assert "agent_distribution" in content, "Outline should include agent distribution"
    print("✓ Slides outline created with placeholders replaced")
    
    # Create report outline
    result = server.init_from_template(
        project="test_refactor",
        resource_type="outline",
        name="report_outline",
        template="outline_report.md",
        title="Test Report",
        author="Test Corp",
        theme="acme_corp",
        date="2024-01-01"
    )
    assert Path(result).exists(), "Report outline not created"
    print("✓ Report outline created successfully")

def test_get_multiple_resources():
    """Test getting multiple resources at once"""
    print("\n=== Testing Multiple Resource Queries ===")
    
    # Get multiple themes
    themes = server.get_themes(["acme_corp", "barney", "nonexistent"])
    theme_names = [t["name"] for t in themes]
    assert "acme_corp" in theme_names, "Should find acme_corp"
    assert "nonexistent" not in theme_names, "Should not find nonexistent"
    print(f"✓ Found {len(themes)} themes from list query")
    
    # Get multiple projects
    projects = server.get_projects(["test_refactor", "fake_project"])
    assert len(projects) == 1, "Should only find existing project"
    assert projects[0]["name"] == "test_refactor"
    print("✓ Multiple project query works")
    
    # Get multiple templates
    templates = server.get_templates("slides", ["01_base_slide", "00_title_slide"])
    template_names = [t["name"] for t in templates]
    print(f"✓ Found {len(templates)} templates from list query")

def main():
    """Run all comprehensive tests"""
    print("Running comprehensive tests for refactored SlideAgent MCP tools...")
    
    # Clean up test project if exists
    test_project = Path("user_projects/test_refactor")
    if test_project.exists():
        shutil.rmtree(test_project)
    
    # Create test project first
    server.create_project("test_refactor", theme="acme_corp")
    
    tests = [
        test_edge_cases,
        test_multiple_slides_reports,
        test_chart_creation,
        test_project_info_fields,
        test_theme_swapping,
        test_outline_templates,
        test_get_multiple_resources
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed.append(test.__name__)
    
    if failed:
        print(f"\n❌ {len(failed)} tests failed: {failed}")
        return 1
    else:
        print("\n✅ All comprehensive tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())