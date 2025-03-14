"""Unified launcher for the application.

This script starts both the frontend and backend services
in a single console window using subprocess management.
It also ensures all required Python packages and system dependencies are installed.

Note:
    This script was generated by ChatGPT to simplify running both Flask and Vue.js application.
"""

import subprocess
import sys
import os
import signal
import logging
from typing import List, Tuple, Optional
import webbrowser
import time
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages multiple subprocesses for the application."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def find_node_executables(self) -> Tuple[Optional[str], Optional[str]]:
        """Find full paths to node and npm executables.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Paths to node and npm executables
        """
        try:
            # On Windows, try to find Node.js installation directory
            if sys.platform == 'win32':
                # Common installation paths
                program_files = [
                    os.environ.get('ProgramFiles'),
                    os.environ.get('ProgramFiles(x86)'),
                    os.environ.get('LocalAppData')
                ]
                
                node_paths = []
                for pf in program_files:
                    if pf:
                        # Check standard Node.js installation path
                        node_paths.extend([
                            os.path.join(pf, 'nodejs'),
                            os.path.join(pf, 'node')
                        ])
                        # Check standard installation paths
                        for path in os.listdir(pf):
                            if path.lower().startswith('node'):
                                node_paths.append(os.path.join(pf, path))
                
                for path in node_paths:
                    node_exe = os.path.join(path, 'node.exe')
                    npm_exe = os.path.join(path, 'npm.cmd')
                    if os.path.isfile(node_exe) and os.path.isfile(npm_exe):
                        return node_exe, npm_exe
            
            # Try to find in PATH as fallback
            if sys.platform == 'win32':
                node_cmd = "where node"
                npm_cmd = "where npm"
            else:
                node_cmd = "which node"
                npm_cmd = "which npm"
                
            node_path = subprocess.check_output(
                node_cmd, shell=True, stderr=subprocess.STDOUT
            ).decode().strip().split('\n')[0]
            
            npm_path = subprocess.check_output(
                npm_cmd, shell=True, stderr=subprocess.STDOUT
            ).decode().strip().split('\n')[0]
            
            return node_path, npm_path
            
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
            return None, None
    
    def check_node_version(self) -> bool:
        """Check if Node.js and npm are installed and have correct versions.
        
        Returns:
            bool: True if Node.js environment is properly set up
        """
        try:
            # Find Node.js executables
            node_path, npm_path = self.find_node_executables()
            if not node_path or not npm_path:
                logger.error(
                    "Node.js executables not found. Please install Node.js from https://nodejs.org/"
                    "\nMake sure to check 'Add to PATH' during installation."
                )
                return False
            
            # Store paths for later use
            self.node_path = node_path
            self.npm_path = npm_path
            
            # Check versions using full paths
            node_version = subprocess.check_output(
                [node_path, "--version"],
                stderr=subprocess.STDOUT
            ).decode().strip()
            
            npm_version = subprocess.check_output(
                [npm_path, "--version"],
                stderr=subprocess.STDOUT
            ).decode().strip()
            
            logger.info(f"Found Node.js {node_version} and npm {npm_version}")
            logger.debug(f"Node.js path: {node_path}")
            logger.debug(f"npm path: {npm_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking Node.js version: {e}")
            return False
    
    def check_requirements(self) -> bool:
        """Check and install required Python packages.
        
        Returns:
            bool: True if all requirements are met, False otherwise
        """
        requirements_file = "src/backend/requirements.txt"
        
        if not os.path.exists(requirements_file):
            logger.error(f"Requirements file not found: {requirements_file}")
            return False
            
        try:
            # Read requirements
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Check what's missing
            missing = []
            for requirement in requirements:
                try:
                    pkg_resources.require(requirement)
                except (DistributionNotFound, VersionConflict):
                    missing.append(requirement)
            
            if missing:
                logger.info(f"Installing missing packages: {', '.join(missing)}")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install",
                        "-r", requirements_file
                    ])
                    logger.info("All requirements installed successfully")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install requirements: {e}")
                    return False
            else:
                logger.info("All requirements already satisfied")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking requirements: {e}")
            return False
    
    def check_node_modules(self) -> bool:
        """Check and install Node.js dependencies.
        
        Returns:
            bool: True if all dependencies are installed, False otherwise
        """
        frontend_dir = "src/frontend"
        
        if not os.path.exists(os.path.join(frontend_dir, "package.json")):
            logger.error("Frontend package.json not found")
            return False
            
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            logger.info("Installing frontend dependencies...")
            try:
                # Use full path to npm
                subprocess.check_call(
                    [self.npm_path, "install"],
                    cwd=frontend_dir,
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                logger.info("Frontend dependencies installed successfully")
            except FileNotFoundError:
                logger.error(
                    "npm command not found. Please ensure Node.js is installed "
                    "and added to your system PATH"
                )
                return False
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install frontend dependencies: {e}")
                return False
        
        return True
    
    def start_backend(self) -> None:
        """Start the Flask backend server."""
        try:
            logger.info("Starting backend server...")
            backend_env = os.environ.copy()
            backend_env["PYTHONPATH"] = os.path.abspath("src/backend")
            
            # Change to backend directory to ensure correct relative paths
            backend_dir = os.path.abspath("src/backend")
            process = subprocess.Popen(
                [sys.executable, "server.py"],
                env=backend_env,
                cwd=backend_dir,  # Set working directory
                # Redirect output to the main console
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            self.processes.append(process)
            logger.info("Backend server started")
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            self.shutdown()
    
    def start_frontend(self) -> None:
        """Start the frontend development server."""
        try:
            logger.info("Starting frontend server...")
            process = subprocess.Popen(
                [self.npm_path, "run", "dev"],
                cwd="src/frontend",
                # Redirect output to the main console
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            self.processes.append(process)
            logger.info("Frontend server started")
        except FileNotFoundError:
            logger.error(
                "npm command not found. Please ensure Node.js is installed "
                "and added to your system PATH"
            )
            self.shutdown()
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            self.shutdown()
    
    def shutdown(self, *args) -> None:
        """Gracefully shutdown all processes."""
        logger.info("Shutting down services...")
        for process in self.processes:
            try:
                if sys.platform == 'win32':
                    # Windows requires special handling for subprocess termination
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error shutting down process: {e}")
                try:
                    process.kill()
                except:
                    pass
        
        logger.info("All services stopped")
        sys.exit(0)

def main():
    """Main entry point for the application launcher."""
    manager = ProcessManager()
    
    try:
        # Check Node.js
        if not manager.check_node_version():
            logger.error(
                "\nPlease install Node.js from https://nodejs.org/"
                "\nMake sure to check 'Add to PATH' during installation."
                "\nAfter installation, you may need to restart your computer."
            )
            return
            
        # Check requirements
        if not manager.check_requirements():
            logger.error("Failed to install Python requirements")
            return
            
        # Check frontend dependencies
        if not manager.check_node_modules():
            logger.error("Failed to install frontend dependencies")
            return
        
        # Start backend first
        manager.start_backend()
        # Wait a bit for backend to initialize
        time.sleep(2)
        
        # Start frontend
        manager.start_frontend()
        
        # Open browser after a short delay
        time.sleep(3)
        webbrowser.open('http://localhost:5173')
        
        # Keep the script running
        while True:
            # Check if any process has terminated
            for process in manager.processes:
                if process.poll() is not None:
                    logger.error("A service has terminated unexpectedly")
                    manager.shutdown()
            time.sleep(1)
            
    except KeyboardInterrupt:
        manager.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        manager.shutdown()

if __name__ == "__main__":
    main()