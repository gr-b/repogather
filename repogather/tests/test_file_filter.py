from pathlib import Path
from repogather.core.file_filter import FileFilter
from repogather.domain.models import GatherOptions

def test_file_filter_excludes_tests_by_default(tmp_path):
    """Test that test files are excluded by default."""
    # Create test files
    (tmp_path / 'test_file.py').touch()
    (tmp_path / 'regular_file.py').touch()
    
    filter = FileFilter()
    options = GatherOptions()
    
    files = filter.filter_files(tmp_path, options)
    paths = [p.name for p in files]
    
    assert 'regular_file.py' in paths
    assert 'test_file.py' not in paths 