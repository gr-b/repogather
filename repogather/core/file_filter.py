from pathlib import Path
import fnmatch
from typing import List
from ..domain.models import GatherOptions

class FileFilter:
    """Filter for repository files based on options."""
    
    def filter_files(self, root: Path, options: GatherOptions) -> List[Path]:
        """
        Filter files in repository based on options.
        
        Args:
            root: Repository root path
            options: Options controlling which files to include
            
        Returns:
            List of paths to included files
        """
        all_files = []
        
        for path in root.rglob('*'):
            if not path.is_file():
                continue
                
            if self._should_include_file(path, options):
                all_files.append(path)
                
        return all_files
    
    def _should_include_file(self, path: Path, options: GatherOptions) -> bool:
        """Determine if a file should be included based on options."""
        # Check if file matches any exclude patterns
        rel_path = str(path.relative_to(path.parent))
        for pattern in options.exclude_patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                return False
        
        # Handle test files
        if not options.include_tests and self._is_test_file(path):
            return False
            
        # Handle config files
        if not options.include_config and self._is_config_file(path):
            return False
            
        # Handle ecosystem files
        if not options.include_ecosystem and self._is_ecosystem_file(path):
            return False
            
        # Handle gitignored files
        if not options.include_gitignored and self._is_gitignored(path):
            return False
            
        return True
    
    def _is_test_file(self, path: Path) -> bool:
        """Check if file is a test file."""
        name = path.name.lower()
        return (
            name.startswith('test_') or
            name.endswith('_test.py') or
            'tests' in path.parts
        )
    
    def _is_config_file(self, path: Path) -> bool:
        """Check if file is a config file."""
        config_names = {
            '.gitignore', '.env', 'config.json', 'settings.json',
            'pyproject.toml', 'setup.cfg', 'tox.ini'
        }
        return path.name in config_names
    
    def _is_ecosystem_file(self, path: Path) -> bool:
        """Check if file is an ecosystem file."""
        ecosystem_names = {
            'requirements.txt', 'setup.py', 'package.json',
            'package-lock.json', 'yarn.lock', 'Pipfile'
        }
        return path.name in ecosystem_names
    
    def _is_gitignored(self, path: Path) -> bool:
        """Check if file is git ignored."""
        # This is a simplified implementation
        # Would need to actually check git status
        return False 