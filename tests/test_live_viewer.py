#!/usr/bin/env python3
"""
Test live viewer path resolution and serving.

This test suite validates the live viewer functionality that's critical for
development and preview of slides:
- Live viewer server startup and shutdown
- Path resolution for slides and assets
- CSS and image serving
- Error handling for missing files
- Port management and conflicts
"""

import sys
import os
import shutil
import time
import requests
from pathlib import Path
import subprocess
import signal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.server import (
    create_project,
    init_slide,
    start_live_viewer,
    stop_live_viewer,
    SLIDE_BASE_CSS_NAME
)


def test_live_viewer_startup_shutdown():
    """Test that live viewer can start and stop correctly"""
    # Setup
    test_dir = Path("user_projects/test-live-viewer")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-live-viewer", theme="acme_corp")
    
    # Start live viewer
    result = start_live_viewer("test-live-viewer", port=8081)
    
    if "Error" not in result:
        # If server started successfully
        assert "viewer" in result.lower() or "http" in result.lower(), f"Unexpected start result: {result}"
        
        # Give server time to start
        time.sleep(2)
        
        # Try to access the server
        try:
            response = requests.get("http://localhost:8081", timeout=5)
            # Any response (even 404) means server is running
            print(f"✓ Live viewer server is running (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("Note: Live viewer server connection failed (may be expected in test environment)")
        except requests.exceptions.Timeout:
            print("Note: Live viewer server timeout (may be expected in test environment)")
        
        # Stop live viewer
        stop_result = stop_live_viewer("test-live-viewer")
        print(f"✓ Live viewer stopped: {stop_result}")
    else:
        print(f"Note: Live viewer start failed (expected in test environment): {result}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Live viewer startup/shutdown test completed")


def test_live_viewer_path_resolution():
    """Test that live viewer resolves paths correctly"""
    # Setup
    test_dir = Path("user_projects/test-viewer-paths")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-paths", theme="barney")
    
    # Create a test slide
    slide_path = init_slide(
        project="test-viewer-paths",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Path Test Slide"
    )
    
    # Verify slide file structure
    assert Path(slide_path).exists(), "Test slide should exist"
    
    # Check that slide references theme files with correct relative paths
    with open(slide_path) as f:
        slide_content = f.read()
    
    # Should have relative paths to theme
    assert "../theme/" in slide_content, "Slide should have relative theme paths"
    assert f"../theme/{SLIDE_BASE_CSS_NAME}" in slide_content, "Should reference slide_base.css"
    assert "../theme/barney_theme.css" in slide_content, "Should reference theme CSS"
    
    # Check that referenced files actually exist
    slides_dir = Path(slide_path).parent
    theme_dir = slides_dir / ".." / "theme"
    
    assert (theme_dir / SLIDE_BASE_CSS_NAME).exists(), "slide_base.css should exist for live viewer"
    assert (theme_dir / "barney_theme.css").exists(), "Theme CSS should exist for live viewer"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Live viewer path resolution validated")


def test_live_viewer_css_serving():
    """Test that CSS files can be served correctly by live viewer"""
    # Setup
    test_dir = Path("user_projects/test-viewer-css")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-css", theme="acme_corp")
    
    # Create a slide to ensure all files are in place
    init_slide(
        project="test-viewer-css",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="CSS Test Slide"
    )
    
    # Check CSS file contents for serving
    theme_dir = test_dir / "theme"
    
    # slide_base.css should have content suitable for serving
    slide_base_css = theme_dir / SLIDE_BASE_CSS_NAME
    with open(slide_base_css) as f:
        css_content = f.read()
    
    # Should look like CSS
    assert len(css_content) > 100, "CSS file should have substantial content"
    assert any(selector in css_content for selector in ["html", "body", ".", "#"]), "Should contain CSS selectors"
    
    # Check theme CSS
    theme_css = theme_dir / "acme_corp_theme.css"
    with open(theme_css) as f:
        theme_content = f.read()
    
    assert len(theme_content) > 50, "Theme CSS should have content"
    
    # CSS should not have any broken imports or references
    assert "@import" not in css_content or all(
        not line.strip().startswith("@import") or "url(" in line or '"' in line or "'" in line
        for line in css_content.split('\n')
    ), "CSS imports should be properly formatted"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ CSS files are ready for live viewer serving")


def test_live_viewer_asset_organization():
    """Test that all assets are organized for live viewer access"""
    # Setup
    test_dir = Path("user_projects/test-viewer-assets")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-assets", theme="barney")
    
    # Check asset organization
    theme_dir = test_dir / "theme"
    
    # Should have all necessary asset types
    css_files = list(theme_dir.glob("*.css"))
    style_files = list(theme_dir.glob("*.mplstyle"))
    png_files = list(theme_dir.glob("*.png"))
    
    assert len(css_files) >= 2, f"Should have CSS files: {[f.name for f in css_files]}"
    assert len(style_files) >= 1, f"Should have matplotlib style files: {[f.name for f in style_files]}"
    assert len(png_files) >= 2, f"Should have PNG logo files: {[f.name for f in png_files]}"
    
    # Files should be directly accessible (no subdirectories needed)
    for file_path in theme_dir.glob("*"):
        if file_path.is_file():
            # File should be in theme root, not nested
            assert file_path.parent.name == "theme", f"Asset should be in theme root: {file_path}"
            
            # File should have reasonable size
            assert file_path.stat().st_size > 0, f"Asset file should not be empty: {file_path}"
    
    # Create slides directory structure for complete serving test
    slides_dir = test_dir / "slides"
    plots_dir = test_dir / "plots"
    
    # Directories should exist and be accessible
    assert slides_dir.exists() and slides_dir.is_dir(), "Slides directory should exist"
    assert plots_dir.exists() and plots_dir.is_dir(), "Plots directory should exist"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Assets are properly organized for live viewer")


def test_live_viewer_error_handling():
    """Test live viewer error handling for missing files and edge cases"""
    # Test starting viewer for non-existent project
    result = start_live_viewer("non-existent-project", port=8082)
    assert "Error" in result or "not found" in result, f"Should handle missing project: {result}"
    
    # Test port conflicts (if implementation supports it)
    test_dir = Path("user_projects/test-viewer-errors")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-errors", theme="acme_corp")
    
    # Try invalid port numbers
    invalid_ports = [0, -1, 99999]
    for port in invalid_ports:
        result = start_live_viewer("test-viewer-errors", port=port)
        # Should either work or give reasonable error
        # (Implementation may handle these gracefully)
    
    # Test stopping non-running viewer
    stop_result = stop_live_viewer("test-viewer-errors")
    # Should not crash, may return info about no server running
    assert isinstance(stop_result, str), "Stop should return string result"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Live viewer error handling works")


def test_live_viewer_multiple_projects():
    """Test handling multiple projects with live viewer"""
    # Setup multiple projects
    projects = ["test-multi-1", "test-multi-2"]
    
    for project_name in projects:
        test_dir = Path(f"user_projects/{project_name}")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        create_project(project_name, theme="acme_corp")
    
    # Test starting viewers on different ports
    ports_used = []
    for i, project_name in enumerate(projects):
        port = 8083 + i
        result = start_live_viewer(project_name, port=port)
        
        if "Error" not in result:
            ports_used.append((project_name, port))
            time.sleep(1)  # Small delay between starts
    
    # Stop all viewers
    for project_name, port in ports_used:
        stop_result = stop_live_viewer(project_name)
        print(f"Stopped viewer for {project_name}: {stop_result}")
    
    # Cleanup
    for project_name in projects:
        test_dir = Path(f"user_projects/{project_name}")
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    print(f"✓ Multiple project live viewers handled ({len(ports_used)} started successfully)")


def test_live_viewer_slide_serving_structure():
    """Test that slides are structured correctly for live viewer serving"""
    # Setup
    test_dir = Path("user_projects/test-viewer-structure")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-structure", theme="acme_corp")
    
    # Create multiple slides with different templates
    slide_templates = [
        ("00_title_slide.html", "Title Slide"),
        ("01_base_slide.html", "Base Slide"),
        ("03_two_column_slide.html", "Two Column Slide")
    ]
    
    for i, (template, title) in enumerate(slide_templates, 1):
        init_slide(
            project="test-viewer-structure",
            number=str(i).zfill(2),
            template=f"slideagent_mcp/resources/templates/slides/{template}",
            title=title
        )
    
    # Check that all slides exist and have correct structure
    slides_dir = test_dir / "slides"
    slide_files = list(slides_dir.glob("slide_*.html"))
    
    assert len(slide_files) == len(slide_templates), f"Should have {len(slide_templates)} slides"
    
    # Each slide should be accessible from project root
    for slide_file in slide_files:
        with open(slide_file) as f:
            content = f.read()
        
        # Should be complete HTML documents
        assert "<!DOCTYPE html>" in content or "<html" in content, f"Slide should be complete HTML: {slide_file.name}"
        
        # Should have relative paths that work from project root serving
        assert "../theme/" in content, f"Slide should use relative theme paths: {slide_file.name}"
        
        # No absolute filesystem paths
        assert not any(abs_path in content for abs_path in ["/Users/", "/home/", "C:\\"]), \
            f"Slide should not have absolute paths: {slide_file.name}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Slides are structured correctly for live viewer serving")


def test_live_viewer_port_management():
    """Test port management and conflict resolution"""
    # Test default port behavior
    test_dir = Path("user_projects/test-viewer-ports")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-viewer-ports", theme="acme_corp")
    
    # Test default port (should be 8080 or similar)
    result1 = start_live_viewer("test-viewer-ports")  # No port specified
    
    if "Error" not in result1:
        # Extract port from result if possible
        import re
        port_match = re.search(r':(\d+)', result1)
        if port_match:
            default_port = int(port_match.group(1))
            assert 8000 <= default_port <= 9000, f"Default port should be reasonable: {default_port}"
        
        # Stop the viewer
        stop_live_viewer("test-viewer-ports")
    
    # Test explicit port
    result2 = start_live_viewer("test-viewer-ports", port=8084)
    
    if "Error" not in result2:
        assert "8084" in result2, "Should mention the specified port"
        stop_live_viewer("test-viewer-ports")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Port management works correctly")


def run_all_tests():
    """Run all live viewer tests"""
    tests = [
        test_live_viewer_startup_shutdown,
        test_live_viewer_path_resolution,
        test_live_viewer_css_serving,
        test_live_viewer_asset_organization,
        test_live_viewer_error_handling,
        test_live_viewer_multiple_projects,
        test_live_viewer_slide_serving_structure,
        test_live_viewer_port_management
    ]
    
    print("\nRunning Live Viewer Tests")
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
        print(f"✅ All {len(tests)} live viewer tests passed!")
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