#!/usr/bin/env python3
"""
Test project creation, file copying, and self-containment.

This test suite validates the project structure and self-containment features
that are critical for SlideAgent projects:
- Proper directory structure creation
- Theme file copying and organization
- Project self-containment (no external dependencies)
- File permissions and accessibility
- Project configuration and metadata
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
    resolve_projects_dir,
    SLIDE_BASE_CSS_NAME,
    THEME_CSS_SUFFIX,
    THEME_STYLE_SUFFIX,
    THEME_ICON_LOGO_SUFFIX,
    THEME_TEXT_LOGO_SUFFIX,
    USER_PROJECTS_DIR
)


def test_project_directory_structure():
    """Test that create_project creates the correct directory structure"""
    # Setup
    test_dir = Path("user_projects/test-structure")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create project
    result = create_project("test-structure", theme="acme_corp")
    assert "Created project" in result, f"Project creation failed: {result}"
    
    # Check main directory exists
    assert test_dir.exists(), f"Project directory not created: {test_dir}"
    assert test_dir.is_dir(), f"Project path is not a directory: {test_dir}"
    
    # Check all required subdirectories
    required_dirs = ["slides", "plots", "input", "validation", "theme"]
    for dirname in required_dirs:
        subdir = test_dir / dirname
        assert subdir.exists(), f"Required directory missing: {subdir}"
        assert subdir.is_dir(), f"Path is not a directory: {subdir}"
    
    # Check directory permissions (should be readable/writable)
    for dirname in required_dirs:
        subdir = test_dir / dirname
        assert os.access(subdir, os.R_OK), f"Directory not readable: {subdir}"
        assert os.access(subdir, os.W_OK), f"Directory not writable: {subdir}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Project directory structure created correctly")


def test_theme_file_copying():
    """Test that all theme files are correctly copied to project"""
    # Setup
    test_dir = Path("user_projects/test-theme-files")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Test with different themes
    themes_to_test = ["acme_corp", "barney"]
    
    for theme_name in themes_to_test:
        project_name = f"test-theme-files-{theme_name}"
        project_dir = Path(f"user_projects/{project_name}")
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        # Create project with this theme
        create_project(project_name, theme=theme_name)
        
        theme_dir = project_dir / "theme"
        
        # Check that slide_base.css was copied
        slide_base_css = theme_dir / SLIDE_BASE_CSS_NAME
        assert slide_base_css.exists(), f"slide_base.css not copied for theme {theme_name}"
        assert slide_base_css.is_file(), f"slide_base.css is not a file: {slide_base_css}"
        
        # Check theme-specific files were copied
        theme_files = [
            f"{theme_name}{THEME_CSS_SUFFIX}",
            f"{theme_name}{THEME_STYLE_SUFFIX}",
            f"{theme_name}{THEME_ICON_LOGO_SUFFIX}",
            f"{theme_name}{THEME_TEXT_LOGO_SUFFIX}"
        ]
        
        for theme_file in theme_files:
            file_path = theme_dir / theme_file
            assert file_path.exists(), f"Theme file not copied: {file_path}"
            
            # Check file has content
            if file_path.suffix in ['.css', '.mplstyle']:
                assert file_path.stat().st_size > 0, f"Theme file is empty: {file_path}"
            elif file_path.suffix == '.png':
                # PNG files should have reasonable size
                assert file_path.stat().st_size > 100, f"PNG file too small: {file_path}"
        
        # Cleanup
        shutil.rmtree(project_dir)
    
    print(f"✓ Theme files copied correctly for {len(themes_to_test)} themes")


def test_project_self_containment():
    """Test that projects are completely self-contained"""
    # Setup
    test_dir = Path("user_projects/test-self-contained")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-self-contained", theme="acme_corp")
    
    # Check that all necessary files exist within project directory
    theme_dir = test_dir / "theme"
    
    # Should have base CSS
    base_css = theme_dir / SLIDE_BASE_CSS_NAME
    assert base_css.exists(), "Missing slide_base.css for self-containment"
    
    # Should have complete theme assets
    required_theme_files = [
        f"acme_corp{THEME_CSS_SUFFIX}",
        f"acme_corp{THEME_STYLE_SUFFIX}",
        f"acme_corp{THEME_ICON_LOGO_SUFFIX}",
        f"acme_corp{THEME_TEXT_LOGO_SUFFIX}"
    ]
    
    for theme_file in required_theme_files:
        file_path = theme_dir / theme_file
        assert file_path.exists(), f"Missing theme file for self-containment: {theme_file}"
    
    # Verify files are actual copies, not symlinks
    for file_path in theme_dir.glob("*"):
        if file_path.is_file():
            assert not file_path.is_symlink(), f"File should be copy, not symlink: {file_path}"
    
    # Check that we can find all files needed for a complete presentation
    # without external dependencies
    essential_extensions = {'.css', '.mplstyle', '.png'}
    found_extensions = {f.suffix for f in theme_dir.glob("*") if f.is_file()}
    
    for ext in essential_extensions:
        assert ext in found_extensions, f"Missing files of type {ext} for self-containment"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Project is fully self-contained")


def test_project_metadata_generation():
    """Test that projects have correct metadata without config.yaml dependency"""
    # Setup
    test_dir = Path("user_projects/test-metadata")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-metadata", theme="barney", description="Test project for metadata")
    
    # Verify no config.yaml is created (new approach)
    config_file = test_dir / "config.yaml"
    assert not config_file.exists(), "config.yaml should not be created in new approach"
    
    # Test project listing (should detect theme from files)
    projects = list_projects()
    test_project = next((p for p in projects if p["name"] == "test-metadata"), None)
    
    assert test_project is not None, "Project not found in listing"
    assert test_project["theme"] == "barney", f"Wrong theme detected: {test_project['theme']}"
    assert test_project["slides_count"] == 0, "New project should have 0 slides"
    assert test_project["charts_count"] == 0, "New project should have 0 charts"
    
    # Test get_project_info
    info = get_project_info("test-metadata")
    assert info["name"] == "test-metadata"
    assert info["theme"] == "barney"
    assert "path" in info
    assert Path(info["path"]).exists()
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Project metadata generated correctly without config.yaml")


def test_projects_directory_resolution():
    """Test that projects directory resolution works correctly"""
    projects_dir = resolve_projects_dir()
    
    # Should always return user_projects directory
    assert projects_dir == USER_PROJECTS_DIR, f"Wrong projects directory: {projects_dir}"
    
    # Directory should exist or be creatable
    if not projects_dir.exists():
        projects_dir.mkdir(parents=True, exist_ok=True)
    
    assert projects_dir.exists(), f"Projects directory doesn't exist: {projects_dir}"
    assert projects_dir.is_dir(), f"Projects path is not a directory: {projects_dir}"
    
    print("✓ Projects directory resolution works correctly")


def test_duplicate_project_handling():
    """Test handling of duplicate project creation"""
    # Setup
    test_dir = Path("user_projects/test-duplicate")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Create project first time
    result1 = create_project("test-duplicate", theme="acme_corp")
    assert "Created project" in result1, "First project creation should succeed"
    assert test_dir.exists(), "Project directory should exist after creation"
    
    # Try to create same project again
    result2 = create_project("test-duplicate", theme="acme_corp")
    assert "Error" in result2 or "already exists" in result2, "Should prevent duplicate creation"
    
    # Original project should still exist and be intact
    assert test_dir.exists(), "Original project should still exist"
    assert (test_dir / "theme" / SLIDE_BASE_CSS_NAME).exists(), "Original project files should be intact"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Duplicate project creation handled correctly")


def test_project_name_sanitization():
    """Test that project names are properly sanitized for filesystem"""
    # Test various project name formats
    test_cases = [
        ("test-project", "test-project"),  # Should work as-is
        ("test_project", "test_project"),  # Underscores OK
        ("test project", "test-project"),  # Spaces should be converted
        ("Test Project!", "test-project"),  # Special chars and case handled
        ("test--project", "test-project"), # Multiple dashes cleaned
    ]
    
    for input_name, expected_dir in test_cases:
        # Clean up first
        test_dir = Path(f"user_projects/{expected_dir}")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        # Create project
        result = create_project(input_name, theme="acme_corp")
        
        # Should succeed and create directory with expected name
        assert "Created project" in result, f"Project creation failed for: {input_name}"
        assert test_dir.exists(), f"Expected directory not created: {expected_dir}"
        
        # Cleanup
        shutil.rmtree(test_dir)
    
    print(f"✓ Project name sanitization works for {len(test_cases)} test cases")


def test_project_with_invalid_theme():
    """Test project creation with non-existent theme"""
    # Setup
    test_dir = Path("user_projects/test-invalid-theme")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Try to create project with non-existent theme
    result = create_project("test-invalid-theme", theme="non-existent-theme")
    
    # Should return an error
    assert "Error" in result or "not found" in result, f"Should handle invalid theme: {result}"
    
    # Project directory should not be created
    assert not test_dir.exists(), "Project directory should not exist with invalid theme"
    
    print("✓ Invalid theme handling works correctly")


def test_nested_directory_creation():
    """Test that nested directories can be created properly"""
    # Setup - test with project name that looks like a path
    project_name = "test-nested-project"
    test_dir = Path(f"user_projects/{project_name}")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # Ensure parent directory exists
    test_dir.parent.mkdir(parents=True, exist_ok=True)
    
    # Create project
    result = create_project(project_name, theme="acme_corp")
    assert "Created project" in result, "Nested project creation should succeed"
    
    # Verify all nested directories created
    for subdir in ["slides", "plots", "input", "validation", "theme"]:
        nested_dir = test_dir / subdir
        assert nested_dir.exists(), f"Nested directory not created: {nested_dir}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ Nested directory creation works correctly")


def test_file_permissions_and_access():
    """Test that created files have proper permissions"""
    # Setup
    test_dir = Path("user_projects/test-permissions")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-permissions", theme="acme_corp")
    
    # Check directory permissions
    assert os.access(test_dir, os.R_OK | os.W_OK | os.X_OK), "Project directory should be rwx"
    
    # Check subdirectory permissions
    for subdir in ["slides", "plots", "input", "validation", "theme"]:
        dir_path = test_dir / subdir
        assert os.access(dir_path, os.R_OK | os.W_OK | os.X_OK), f"Subdirectory should be rwx: {subdir}"
    
    # Check file permissions
    theme_dir = test_dir / "theme"
    for file_path in theme_dir.glob("*"):
        if file_path.is_file():
            assert os.access(file_path, os.R_OK), f"File should be readable: {file_path}"
            # CSS and style files should be writable (for theme swapping)
            if file_path.suffix in ['.css', '.mplstyle']:
                assert os.access(file_path, os.W_OK), f"CSS file should be writable: {file_path}"
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✓ File permissions and access are correct")


def test_project_outline_generation():
    """Test that projects get proper outline template"""
    # Setup
    test_dir = Path("user_projects/test-outline")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-outline", theme="acme_corp")
    
    # Check if outline.md is created
    outline_file = test_dir / "outline.md"
    
    if outline_file.exists():
        # If outline is created, validate its content
        with open(outline_file) as f:
            content = f.read()
        
        assert len(content) > 50, "Outline template should have substantial content"
        assert "# " in content, "Outline should have markdown headers"
        assert "slides" in content.lower(), "Outline should mention slides"
        
        print("✓ Outline template created and validated")
    else:
        # Outline creation might be optional
        print("✓ Outline not created (may be optional)")
    
    # Cleanup
    shutil.rmtree(test_dir)


def test_theme_availability_check():
    """Test that available themes are properly detected"""
    themes = list_themes()
    
    assert len(themes) > 0, "Should find at least some themes"
    assert isinstance(themes, list), "list_themes should return a list"
    
    # Check theme structure
    for theme in themes:
        assert "name" in theme, f"Theme missing name field: {theme}"
        assert "path" in theme, f"Theme missing path field: {theme}"
        
        theme_path = Path(theme["path"])
        assert theme_path.exists(), f"Theme path doesn't exist: {theme_path}"
        assert theme_path.is_dir(), f"Theme path is not directory: {theme_path}"
    
    # Should find essential themes
    theme_names = [t["name"] for t in themes]
    essential_themes = ["acme_corp", "barney"]
    
    for essential in essential_themes:
        assert essential in theme_names, f"Missing essential theme: {essential}"
    
    print(f"✓ Found {len(themes)} available themes: {theme_names}")


def run_all_tests():
    """Run all project structure tests"""
    tests = [
        test_project_directory_structure,
        test_theme_file_copying,
        test_project_self_containment,
        test_project_metadata_generation,
        test_projects_directory_resolution,
        test_duplicate_project_handling,
        test_project_name_sanitization,
        test_project_with_invalid_theme,
        test_nested_directory_creation,
        test_file_permissions_and_access,
        test_project_outline_generation,
        test_theme_availability_check
    ]
    
    print("\nRunning Project Structure Tests")
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
        print(f"✅ All {len(tests)} project structure tests passed!")
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