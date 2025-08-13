#!/usr/bin/env python3
"""
Test theme switching and file management.

This test suite validates theme management functionality that's critical for
maintaining consistent branding across presentations:
- Theme discovery and listing
- Theme file validation
- Theme switching and file updates  
- Theme asset management (CSS, logos, matplotlib styles)
- Slide updates after theme changes
- Error handling for missing themes
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
    list_themes,
    swap_theme,
    get_project_theme,
    resolve_theme_dirs,
    SLIDE_BASE_CSS_NAME,
    THEME_CSS_SUFFIX,
    THEME_STYLE_SUFFIX,
    THEME_ICON_LOGO_SUFFIX,
    THEME_TEXT_LOGO_SUFFIX
)


def test_theme_discovery_and_listing():
    """Test that themes are properly discovered and listed"""
    themes = list_themes()
    
    # Should find themes
    assert len(themes) > 0, "Should discover at least some themes"
    assert isinstance(themes, list), "list_themes should return a list"
    
    # Each theme should have proper metadata
    for theme in themes:
        assert isinstance(theme, dict), "Each theme should be a dictionary"
        assert "name" in theme, f"Theme missing name field: {theme}"
        assert "path" in theme, f"Theme missing path field: {theme}"
        
        # Theme path should exist
        theme_path = Path(theme["path"])
        assert theme_path.exists(), f"Theme directory doesn't exist: {theme_path}"
        assert theme_path.is_dir(), f"Theme path is not a directory: {theme_path}"
    
    # Should find essential themes
    theme_names = [t["name"] for t in themes]
    essential_themes = ["acme_corp", "barney"]
    
    for essential in essential_themes:
        assert essential in theme_names, f"Missing essential theme: {essential}"
    
    print(f"✓ Discovered {len(themes)} themes: {theme_names}")


def test_theme_directory_resolution():
    """Test that theme directories are resolved in correct priority order"""
    theme_dirs = resolve_theme_dirs()
    
    assert len(theme_dirs) > 0, "Should find at least one theme directory"
    
    # All directories should exist
    for theme_dir in theme_dirs:
        assert theme_dir.exists(), f"Theme directory should exist: {theme_dir}"
        assert theme_dir.is_dir(), f"Theme path should be directory: {theme_dir}"
    
    # Should contain actual theme subdirectories
    total_themes = 0
    for theme_dir in theme_dirs:
        theme_subdirs = [d for d in theme_dir.iterdir() if d.is_dir()]
        total_themes += len(theme_subdirs)
    
    assert total_themes > 0, "Theme directories should contain theme subdirectories"
    
    print(f"✓ Found {len(theme_dirs)} theme directories with {total_themes} themes")


def test_theme_file_validation():
    """Test that theme files are complete and valid"""
    themes = list_themes()
    
    for theme in themes:
        theme_name = theme["name"]
        theme_path = Path(theme["path"])
        
        # Check required theme files exist
        required_files = [
            f"{theme_name}{THEME_CSS_SUFFIX}",
            f"{theme_name}{THEME_STYLE_SUFFIX}",
            f"{theme_name}{THEME_ICON_LOGO_SUFFIX}",
            f"{theme_name}{THEME_TEXT_LOGO_SUFFIX}"
        ]
        
        for file_name in required_files:
            file_path = theme_path / file_name
            assert file_path.exists(), f"Missing theme file: {file_path}"
            
            # Check file has content
            file_size = file_path.stat().st_size
            if file_path.suffix in ['.css', '.mplstyle']:
                assert file_size > 50, f"Theme text file too small: {file_path} ({file_size} bytes)"
            elif file_path.suffix == '.png':
                assert file_size > 100, f"Theme PNG too small: {file_path} ({file_size} bytes)"
        
        # Validate CSS content
        css_file = theme_path / f"{theme_name}{THEME_CSS_SUFFIX}"
        with open(css_file) as f:
            css_content = f.read()
        
        assert len(css_content) > 100, f"CSS content too short: {css_file}"
        assert any(selector in css_content for selector in [".", "#", "html", "body"]), \
            f"CSS doesn't contain selectors: {css_file}"
        
        # Validate matplotlib style content
        style_file = theme_path / f"{theme_name}{THEME_STYLE_SUFFIX}"
        with open(style_file) as f:
            style_content = f.read()
        
        assert len(style_content) > 20, f"Matplotlib style too short: {style_file}"
        # Should contain matplotlib configuration
        assert any(keyword in style_content for keyword in ["axes", "figure", "font", "#"]), \
            f"Matplotlib style doesn't contain expected config: {style_file}"
    
    print(f"✓ Validated files for {len(themes)} themes")


def test_theme_switching_basic():
    """Test basic theme switching functionality"""
    # Setup
    test_dir = Path("user_projects/test-theme-switch")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create project with initial theme
    create_project("test-theme-switch", theme="acme_corp")
    
    # Verify initial theme
    initial_theme = get_project_theme(test_dir)
    assert initial_theme == "acme_corp", f"Wrong initial theme: {initial_theme}"
    
    # Check initial theme files exist
    theme_dir = test_dir / "theme"
    assert (theme_dir / "acme_corp_theme.css").exists(), "Initial theme CSS should exist"
    assert (theme_dir / SLIDE_BASE_CSS_NAME).exists(), "slide_base.css should exist"
    
    # Switch to different theme
    result = swap_theme("test-theme-switch", "barney")
    assert "Updated" in result or "Success" in result, f"Theme switch should succeed: {result}"
    
    # Verify theme changed
    new_theme = get_project_theme(test_dir)
    assert new_theme == "barney", f"Theme should be changed to barney: {new_theme}"
    
    # Check new theme files exist
    assert (theme_dir / "barney_theme.css").exists(), "New theme CSS should exist"
    assert (theme_dir / "barney_style.mplstyle").exists(), "New theme style should exist"
    assert (theme_dir / "barney_icon_logo.png").exists(), "New theme icon logo should exist"
    assert (theme_dir / "barney_text_logo.png").exists(), "New theme text logo should exist"
    
    # Check old theme files removed
    assert not (theme_dir / "acme_corp_theme.css").exists(), "Old theme CSS should be removed"
    
    # slide_base.css should be preserved
    assert (theme_dir / SLIDE_BASE_CSS_NAME).exists(), "slide_base.css should be preserved"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Basic theme switching works correctly")


def test_theme_switching_with_slides():
    """Test that theme switching updates existing slides"""
    # Setup
    test_dir = Path("user_projects/test-theme-switch-slides")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-switch-slides", theme="acme_corp")
    
    # Create slides with different templates
    slide_files = []
    for i, template in enumerate([
        "00_title_slide.html",
        "01_base_slide.html", 
        "03_two_column_slide.html"
    ], 1):
        slide_path = init_slide(
            project="test-theme-switch-slides",
            number=str(i).zfill(2),
            template=f"slideagent_mcp/resources/templates/slides/{template}",
            title=f"Test Slide {i}"
        )
        slide_files.append(slide_path)
    
    # Verify initial theme in slides
    for slide_path in slide_files:
        with open(slide_path) as f:
            content = f.read()
        assert "acme_corp_theme.css" in content, f"Slide should reference initial theme: {slide_path}"
        assert f"{SLIDE_BASE_CSS_NAME}" in content, f"Slide should reference slide_base.css: {slide_path}"
    
    # Switch theme
    swap_theme("test-theme-switch-slides", "barney")
    
    # Check that all slides were updated
    for slide_path in slide_files:
        with open(slide_path) as f:
            content = f.read()
        
        assert "barney_theme.css" in content, f"Slide should reference new theme: {slide_path}"
        assert "acme_corp_theme.css" not in content, f"Slide should not reference old theme: {slide_path}"
        assert f"{SLIDE_BASE_CSS_NAME}" in content, f"Slide should still reference slide_base.css: {slide_path}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"✓ Theme switching updated {len(slide_files)} slides correctly")


def test_theme_detection_from_files():
    """Test that project theme can be detected from theme files"""
    # Setup
    test_dir = Path("user_projects/test-theme-detection")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-detection", theme="barney")
    
    # Should detect theme from files (no config.yaml needed)
    detected_theme = get_project_theme(test_dir)
    assert detected_theme == "barney", f"Should detect barney theme: {detected_theme}"
    
    # Test with different theme
    swap_theme("test-theme-detection", "acme_corp")
    detected_theme = get_project_theme(test_dir)
    assert detected_theme == "acme_corp", f"Should detect changed theme: {detected_theme}"
    
    # Test error case - remove theme files
    theme_dir = test_dir / "theme"
    for css_file in theme_dir.glob("*_theme.css"):
        css_file.unlink()
    
    try:
        get_project_theme(test_dir)
        assert False, "Should raise error when no theme CSS found"
    except ValueError as e:
        assert "No theme CSS file found" in str(e), f"Wrong error message: {e}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Theme detection from files works correctly")


def test_theme_asset_consistency():
    """Test that theme assets are consistent after switching"""
    # Setup
    test_dir = Path("user_projects/test-theme-consistency")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-consistency", theme="acme_corp")
    
    # Function to check theme consistency
    def check_theme_consistency(expected_theme):
        theme_dir = test_dir / "theme"
        
        # All theme-specific files should match the theme name
        theme_files = [
            f"{expected_theme}_theme.css",
            f"{expected_theme}_style.mplstyle", 
            f"{expected_theme}_icon_logo.png",
            f"{expected_theme}_text_logo.png"
        ]
        
        for file_name in theme_files:
            file_path = theme_dir / file_name
            assert file_path.exists(), f"Theme file missing: {file_path}"
        
        # No files from other themes should exist
        for file_path in theme_dir.glob("*_theme.css"):
            theme_name = file_path.name.replace("_theme.css", "")
            assert theme_name == expected_theme, f"Found wrong theme CSS: {file_path}"
        
        # slide_base.css should always exist
        assert (theme_dir / SLIDE_BASE_CSS_NAME).exists(), "slide_base.css should always exist"
    
    # Check initial consistency
    check_theme_consistency("acme_corp")
    
    # Switch themes multiple times
    themes_to_test = ["barney", "acme_corp", "barney"]
    
    for theme_name in themes_to_test:
        swap_theme("test-theme-consistency", theme_name)
        check_theme_consistency(theme_name)
    
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"✓ Theme asset consistency maintained through {len(themes_to_test)} switches")


def test_theme_error_handling():
    """Test error handling for theme operations"""
    # Test with non-existent project
    result = swap_theme("non-existent-project", "acme_corp")
    assert "Error" in result or "not found" in result, f"Should handle missing project: {result}"
    
    # Test with non-existent theme
    test_dir = Path("user_projects/test-theme-errors")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-errors", theme="acme_corp")
    
    result = swap_theme("test-theme-errors", "non-existent-theme")
    assert "Error" in result or "not found" in result, f"Should handle missing theme: {result}"
    
    # Original theme should be preserved
    theme = get_project_theme(test_dir)
    assert theme == "acme_corp", "Original theme should be preserved after failed switch"
    
    # Test theme detection with corrupted theme directory
    theme_dir = test_dir / "theme"
    
    # Remove all theme CSS files
    for css_file in theme_dir.glob("*_theme.css"):
        css_file.unlink()
    
    try:
        get_project_theme(test_dir)
        assert False, "Should raise error with no theme CSS files"
    except ValueError:
        pass  # Expected
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Theme error handling works correctly")


def test_theme_file_preservation():
    """Test that important files are preserved during theme switches"""
    # Setup
    test_dir = Path("user_projects/test-theme-preservation")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-preservation", theme="acme_corp")
    
    # Create a slide to ensure slide_base.css is important
    init_slide(
        project="test-theme-preservation",
        number="01",
        template="slideagent_mcp/resources/templates/slides/01_base_slide.html",
        title="Preservation Test"
    )
    
    # Add a custom file to theme directory (should be preserved)
    theme_dir = test_dir / "theme"
    custom_file = theme_dir / "custom_notes.txt"
    custom_file.write_text("This is a custom file that should be preserved")
    
    # Get initial file count and list
    initial_files = set(f.name for f in theme_dir.glob("*") if f.is_file())
    
    # Switch theme
    swap_theme("test-theme-preservation", "barney")
    
    # Check preserved files
    final_files = set(f.name for f in theme_dir.glob("*") if f.is_file())
    
    # slide_base.css should be preserved
    assert SLIDE_BASE_CSS_NAME in final_files, "slide_base.css should be preserved"
    
    # Custom file should be preserved
    assert "custom_notes.txt" in final_files, "Custom files should be preserved"
    assert custom_file.exists(), "Custom file should still exist"
    
    # Old theme files should be removed
    assert "acme_corp_theme.css" not in final_files, "Old theme CSS should be removed"
    
    # New theme files should be present
    assert "barney_theme.css" in final_files, "New theme CSS should be added"
    assert "barney_style.mplstyle" in final_files, "New theme style should be added"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Important files preserved during theme switch")


def test_theme_logo_handling():
    """Test that theme logos are properly managed"""
    themes = list_themes()
    
    # Test each available theme's logos
    for theme in themes[:2]:  # Test first 2 themes to avoid excessive testing
        theme_name = theme["name"]
        theme_path = Path(theme["path"])
        
        # Check logo files exist
        icon_logo = theme_path / f"{theme_name}_icon_logo.png"
        text_logo = theme_path / f"{theme_name}_text_logo.png"
        
        assert icon_logo.exists(), f"Icon logo missing: {icon_logo}"
        assert text_logo.exists(), f"Text logo missing: {text_logo}"
        
        # Check logos are valid PNG files (basic check)
        assert icon_logo.stat().st_size > 100, f"Icon logo too small: {icon_logo}"
        assert text_logo.stat().st_size > 100, f"Text logo too small: {text_logo}"
        
        # Check PNG headers (basic validation)
        with open(icon_logo, 'rb') as f:
            png_header = f.read(8)
            assert png_header.startswith(b'\x89PNG'), f"Icon logo not valid PNG: {icon_logo}"
        
        with open(text_logo, 'rb') as f:
            png_header = f.read(8)
            assert png_header.startswith(b'\x89PNG'), f"Text logo not valid PNG: {text_logo}"
    
    # Test logo copying during project creation and theme switching
    test_dir = Path("user_projects/test-theme-logos")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-theme-logos", theme="acme_corp")
    
    # Check logos were copied
    theme_dir = test_dir / "theme"
    assert (theme_dir / "acme_corp_icon_logo.png").exists(), "Icon logo not copied"
    assert (theme_dir / "acme_corp_text_logo.png").exists(), "Text logo not copied"
    
    # Switch theme and check logo replacement
    swap_theme("test-theme-logos", "barney")
    
    assert (theme_dir / "barney_icon_logo.png").exists(), "New icon logo not copied"
    assert (theme_dir / "barney_text_logo.png").exists(), "New text logo not copied"
    assert not (theme_dir / "acme_corp_icon_logo.png").exists(), "Old icon logo not removed"
    assert not (theme_dir / "acme_corp_text_logo.png").exists(), "Old text logo not removed"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Theme logo handling works correctly")


def run_all_tests():
    """Run all theme management tests"""
    tests = [
        test_theme_discovery_and_listing,
        test_theme_directory_resolution,
        test_theme_file_validation,
        test_theme_switching_basic,
        test_theme_switching_with_slides,
        test_theme_detection_from_files,
        test_theme_asset_consistency,
        test_theme_error_handling,
        test_theme_file_preservation,
        test_theme_logo_handling
    ]
    
    print("\nRunning Theme Management Tests")
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
        print(f"✅ All {len(tests)} theme management tests passed!")
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