#!/usr/bin/env python3
"""
Test PlotBuddy with simplified theme folder approach
"""

import sys
import os
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from slideagent_mcp.utils.plot_buddy import PlotBuddy
from slideagent_mcp.server import create_project


def test_plotbuddy_with_theme_folder():
    """Test that PlotBuddy works with just a theme folder"""
    # Setup test project
    test_dir = Path("user_projects/test-plotbuddy")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-plotbuddy", theme="barney")
    
    # Test 1: Create PlotBuddy with explicit theme folder
    buddy = PlotBuddy(theme_folder=test_dir / "theme")
    assert buddy.theme_name == "barney"
    assert buddy.icon_logo_path is not None
    assert buddy.text_logo_path is not None
    print("✓ PlotBuddy with explicit theme_folder")
    
    # Test 2: Create PlotBuddy from project (auto-detect)
    os.chdir(test_dir / "plots")  # Simulate being in plots directory
    buddy2 = PlotBuddy()  # Should auto-detect ../theme
    assert buddy2.theme_name == "barney"
    print("✓ PlotBuddy auto-detect from plots/")
    
    # Test 3: from_project_config still works
    buddy3 = PlotBuddy.from_project_config()
    assert buddy3.theme_name == "barney"
    print("✓ from_project_config() backward compatibility")
    
    # Cleanup
    os.chdir(Path(__file__).parent.parent)
    shutil.rmtree(test_dir)
    print("✓ test_plotbuddy_with_theme_folder")


def test_plotbuddy_error_handling():
    """Test PlotBuddy error handling"""
    # Test with non-existent theme folder
    try:
        buddy = PlotBuddy(theme_folder="non-existent-folder")
        assert False, "Should raise error for non-existent folder"
    except Exception:
        print("✓ Correctly raised error for non-existent folder")
    
    # Test with empty theme folder
    test_dir = Path("user_projects/test-empty")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True)
    (test_dir / "theme").mkdir()
    
    try:
        buddy = PlotBuddy(theme_folder=test_dir / "theme")
        assert False, "Should raise error for empty theme folder"
    except ValueError as e:
        assert "No theme CSS file found" in str(e)
        print("✓ Correctly raised error for empty theme folder")
    
    # Cleanup
    shutil.rmtree(test_dir)


def test_plotbuddy_chart_methods():
    """Test that PlotBuddy chart methods work"""
    # Setup
    test_dir = Path("user_projects/test-chart-methods")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    create_project("test-chart-methods", theme="acme_corp")
    
    # Test PlotBuddy directly
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    # Create PlotBuddy with theme folder
    buddy = PlotBuddy(theme_folder=test_dir / "theme")
    assert buddy.theme_name == "acme_corp"
    
    # Test setup_figure
    fig, ax = buddy.setup_figure(figsize=(10, 6))
    assert fig is not None
    assert ax is not None
    print("✓ setup_figure works")
    
    # Test adding titles
    buddy.add_titles(ax, "Test Title", "Test Subtitle")
    print("✓ add_titles works")
    
    # Test save (creates both branded and clean)
    ax.plot([1, 2, 3], [1, 4, 9])
    os.chdir(test_dir / "plots")
    branded_path, clean_path = buddy.save("test_output.png", branded=True)
    
    assert Path(branded_path).exists()
    assert Path(clean_path).exists()
    print("✓ save creates both branded and clean versions")
    
    # Cleanup
    os.chdir(Path(__file__).parent.parent)
    plt.close('all')
    shutil.rmtree(test_dir)


def run_all_tests():
    """Run all PlotBuddy tests"""
    print("\nTesting PlotBuddy Simplified Theme Approach")
    print("=" * 40)
    
    tests = [
        test_plotbuddy_with_theme_folder,
        test_plotbuddy_error_handling,
        test_plotbuddy_chart_methods
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("=" * 40)
    print("✅ All PlotBuddy tests passed!")
    return True


if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)
    success = run_all_tests()
    sys.exit(0 if success else 1)