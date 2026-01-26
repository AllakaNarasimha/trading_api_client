#!/usr/bin/env python3
"""
Dependency analyzer and synchronizer
"""

import sys
import re
import tarfile
import subprocess
from pathlib import Path
from typing import Set, List, Tuple

# Mapping of tar.gz files to their source directories
LIBRARY_SOURCES = {
    'trading_api-1.0.0.tar.gz': r'D:\NS\trading_api',
    'nslogger-1.0.0.tar.gz': r'D:\NS\nssqllogger',
}
# Known missing dependencies for common packages
KNOWN_MISSING_DEPS = {
    'fyers-apiv3': ['protobuf>=3.20.0', 'googleapis-common-protos>=1.56.0'],
}


def extract_deps_from_tarball(tarball_path: Path) -> Tuple[str, Set[str]]:
    """Extract dependencies from tar.gz file."""
    deps = set()
    lib_name = tarball_path.stem.rsplit('-', 1)[0]
    
    try:
        with tarfile.open(tarball_path, 'r:gz') as tar:
            members = [m for m in tar.getmembers() if 'pyproject.toml' in m.name]
            
            if members:
                content = tar.extractfile(members[0]).read().decode('utf-8')
                deps = parse_dependencies_from_content(content)
                print(f"  [{lib_name}] Found {len(deps)} dependencies")
                
    except Exception as e:
        print(f"  [ERROR] Failed to extract from {tarball_path.name}: {e}")
    
    return lib_name, deps


def parse_dependencies_from_content(content: str) -> Set[str]:
    """Parse dependencies from pyproject.toml content."""
    deps = set()
    in_dependencies = False
    
    for line in content.split('\n'):
        line = line.strip()
        
        if line.startswith('dependencies') and ('=' in line or '[' in line):
            in_dependencies = True
            continue
        
        if in_dependencies:
            if line.startswith('[') or line.startswith('dev ='):
                break
            
            cleaned = line.strip(' "\'[],')
            if cleaned and not cleaned.startswith('#'):
                if ('==' in cleaned or '>=' in cleaned):
                    deps.add(cleaned)
    
    return deps


def identify_missing_deps(all_deps: Set[str]) -> Set[str]:
    """Identify missing dependencies."""
    missing = set()
    
    for dep in all_deps:
        dep_name = re.split(r'[=<>~]', dep)[0].strip().lower()
        
        if dep_name in KNOWN_MISSING_DEPS:
            missing.update(KNOWN_MISSING_DEPS[dep_name])
            print(f"  [INFO] {dep_name} requires: {', '.join(KNOWN_MISSING_DEPS[dep_name])}")
    
    return missing


def read_pyproject_toml(path: Path) -> Tuple[List[str], str]:
    """Read pyproject.toml and extract dependencies."""
    if not path.exists():
        return [], ""
    
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    deps = []
    in_deps = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('dependencies = ['):
            in_deps = True
            continue
        
        if in_deps:
            if stripped == ']':
                break
            dep = stripped.strip(' "\'[],')
            if dep and not dep.startswith('#'):
                deps.append(dep)
    
    return deps, content


def update_pyproject_dependencies(pyproject_path: Path, new_deps: Set[str]) -> bool:
    """Update pyproject.toml with new dependencies."""
    if not pyproject_path.exists():
        print(f"  [WARNING] {pyproject_path} not found")
        return False
    
    current_deps, content = read_pyproject_toml(pyproject_path)
    
    # Parse all dependencies
    dep_dict = {}
    for dep in current_deps:
        name = re.split(r'[=<>~]', dep)[0].strip().lower()
        dep_dict[name] = dep
    
    # Add new dependencies
    added_count = 0
    for dep in new_deps:
        name = re.split(r'[=<>~]', dep)[0].strip().lower()
        if name not in dep_dict:
            dep_dict[name] = dep
            added_count += 1
    
    if added_count == 0:
        print(f"  [INFO] No new dependencies to add")
        return False
    
    # Rebuild dependencies section
    merged_deps = sorted(dep_dict.values())
    
    # Find and replace dependencies section
    lines = content.split('\n')
    new_lines = []
    in_deps = False
    deps_replaced = False
    
    for line in lines:
        if line.strip().startswith('dependencies = ['):
            new_lines.append('dependencies = [')
            for dep in merged_deps:
                new_lines.append(f'    "{dep}",')
            new_lines.append(']')
            in_deps = True
            deps_replaced = True
            continue
        
        if in_deps and line.strip() == ']':
            in_deps = False
            continue
        
        if not in_deps:
            new_lines.append(line)
    
    if deps_replaced:
        # Backup original
        backup_path = pyproject_path.with_suffix('.toml.backup')
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            backup_path.write_text(content)
            print(f"  [BACKUP] Created {backup_path.name}")
        
        # Write updated content
        pyproject_path.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"  [SUCCESS] Updated {pyproject_path.name} (added {added_count} dependencies)")
        return True
    
    return False


def rebuild_library(source_dir: Path, output_dir: Path) -> Path:
    """Rebuild library tar.gz from source and return the built tar.gz path."""
    if not source_dir.exists():
        print(f"  [ERROR] Source directory not found: {source_dir}")
        return None
    
    print(f"  [BUILD] Building from {source_dir.name}...")
    
    try:
        # Build in temp directory first
        temp_dist = source_dir / 'dist'
        
        result = subprocess.run(
            [sys.executable, '-m', 'build', '--outdir', str(temp_dist)],
            cwd=str(source_dir),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            tar_files = sorted(temp_dist.glob('*.tar.gz'), key=lambda x: x.stat().st_mtime, reverse=True)
            if tar_files:
                built_file = tar_files[0]
                print(f"  [SUCCESS] Built {built_file.name}")
                return built_file
        else:
            print(f"  [ERROR] Build failed: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        print(f"  [ERROR] Build exception: {e}")
        return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_and_sync_deps.py <libs_dir> <main_pyproject>")
        sys.exit(1)
    
    libs_dir = Path(sys.argv[1])
    main_pyproject = Path(sys.argv[2])
    
    print("Library Source Mapping:")
    for tar_file, source_dir in LIBRARY_SOURCES.items():
        print(f"  {tar_file} -> {source_dir}")
    print()
    
    print("[PHASE 1] Analyzing existing tar.gz dependencies...")
    print()
    
    all_deps = set()
    
    if libs_dir.exists():
        for tarball in libs_dir.glob('*.tar.gz'):
            lib_name, deps = extract_deps_from_tarball(tarball)
            all_deps.update(deps)
    
    if all_deps:
        print(f"\n[INFO] Found {len(all_deps)} total dependencies\n")
    
    print("[PHASE 2] Identifying missing dependencies...")
    print()
    
    missing_deps = identify_missing_deps(all_deps)
    
    if missing_deps:
        print(f"\n[INFO] Identified {len(missing_deps)} missing dependencies:")
        for dep in sorted(missing_deps):
            print(f"  - {dep}")
        print()
    
    print("[PHASE 3] Updating source library pyproject.toml files...")
    print()
    
    updated_libs = []
    
    # Check each library source
    for tar_file, source_path in LIBRARY_SOURCES.items():
        lib_source = Path(source_path)
        lib_name = tar_file.rsplit('-', 1)[0]  # Remove version
        lib_pyproject = lib_source / 'pyproject.toml'
        
        print(f"  Checking {lib_name}...")
        
        if not lib_pyproject.exists():
            print(f"    [WARNING] pyproject.toml not found at {lib_source}")
            continue
        
        if not missing_deps:
            print(f"    [INFO] No missing dependencies to add")
            continue
        
        current_deps, _ = read_pyproject_toml(lib_pyproject)
        
        # Only update if library uses packages that require missing deps
        # For example, if it has fyers-apiv3, it needs protobuf
        has_fyers = any('fyers' in dep.lower() for dep in current_deps)
        
        if has_fyers:
            print(f"    [INFO] {lib_name} uses fyers-apiv3, adding missing dependencies...")
            if update_pyproject_dependencies(lib_pyproject, missing_deps):
                updated_libs.append((lib_name, lib_source))
        else:
            print(f"    [INFO] {lib_name} doesn't need these dependencies")
    
    print("\n[PHASE 4] Cleaning client folder and rebuilding all libraries...")
    print()

    try:
        import build
    except ImportError:
        print("[INFO] Installing build module...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'build'], check=True)

    import shutil

    # Ensure libs directory exists
    libs_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Target directory: {libs_dir}")
    print()

    rebuilt_count = 0
    for tar_file, source_path in LIBRARY_SOURCES.items():
        lib_source = Path(source_path)
        lib_name = tar_file.rsplit('-', 1)[0]

        print(f"  Processing {lib_name}...")
        print(f"    Source: {lib_source}")

        if not lib_source.exists():
            print(f"    [WARNING] Source not found: {lib_source}")
            continue

        # Check if pyproject.toml exists
        pyproject_file = lib_source / 'pyproject.toml'
        if not pyproject_file.exists():
            print(f"    [WARNING] No pyproject.toml found in {lib_source}")
            continue

        # Rebuild the library
        built_tar = rebuild_library(lib_source, libs_dir)

        if built_tar:
            # Copy to client\libs directory with standardized name
            dest_file = libs_dir / tar_file

            # Remove old file if exists
            if dest_file.exists():
                print(f"    [CLEANUP] Removing old {dest_file.name}")
                dest_file.unlink()

            try:
                shutil.copy2(built_tar, dest_file)
                print(f"    [COPIED] {built_tar.name}")
                print(f"             -> {dest_file}")

                # Verify copy
                if dest_file.exists():
                    size_mb = dest_file.stat().st_size / (1024 * 1024)
                    print(f"             Size: {size_mb:.2f} MB")
                    rebuilt_count += 1
                else:
                    print(f"    [ERROR] Copy verification failed")
            except Exception as e:
                print(f"    [ERROR] Failed to copy: {e}")
        else:
            print(f"    [FAILED] Could not rebuild {lib_name}")

        print()

    print(f"  [INFO] Successfully rebuilt and copied {rebuilt_count}/{len(LIBRARY_SOURCES)} libraries")
    print(f"  [INFO] Libraries available in: {libs_dir.absolute()}")

    # Final verification
    print("\n[VERIFICATION] Checking copied files...")
    tar_files = list(libs_dir.glob('*.tar.gz'))
    if tar_files:
        print(f"  Found {len(tar_files)} tar.gz files:")
        for tar_file in tar_files:
            size_mb = tar_file.stat().st_size / (1024 * 1024)
            print(f"    - {tar_file.name} ({size_mb:.2f} MB)")
    else:
        print("  [WARNING] No tar.gz files found after copy operation!")
    
    print("\n[PHASE 5] Syncing to main pyproject.toml...")
    print()
    
    final_deps = all_deps | missing_deps
    
    if final_deps and main_pyproject.exists():
        update_pyproject_dependencies(main_pyproject, final_deps)
    else:
        print("  [INFO] No dependencies to sync")
    
    print("\n[COMPLETE] Done!")
    print("\nConfiguration:")
    print(f"  - Output libs directory: {libs_dir}")
    print(f"  - Main pyproject.toml: {main_pyproject}")
    print("\nLibrary Sources:")
    for tar_file, source_path in LIBRARY_SOURCES.items():
        print(f"  - {tar_file} <- {source_path}")


if __name__ == '__main__':
    main()