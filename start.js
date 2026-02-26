#!/usr/bin/env node

/**
 * Cross-platform startup script for FareShare
 * Starts both backend (Python/FastAPI) and frontend (Vite/React)
 */

const { spawn, spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const platform = os.platform();
const isWindows = platform === 'win32';

// Determine Python executable path based on OS
const getPythonPath = () => {
    const backendPath = path.join(__dirname, 'backend');
    if (isWindows) {
        return path.join(backendPath, 'venv', 'Scripts', 'python.exe');
    } else {
        return path.join(backendPath, 'venv', 'bin', 'python');
    }
};

// Get system Python command
const getSystemPython = () => {
    // Try common Python commands
    const pythonCommands = ['python', 'python3', 'py'];
    for (const cmd of pythonCommands) {
        try {
            const result = spawnSync(cmd, ['--version'], { shell: isWindows });
            if (result.status === 0) {
                return cmd;
            }
        } catch (e) {
            // Continue to next command
        }
    }
    return 'python'; // Default fallback
};

// Colors for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    blue: '\x1b[34m',
    yellow: '\x1b[33m',
    red: '\x1b[31m',
    cyan: '\x1b[36m',
};

const log = (color, prefix, message) => {
    console.log(`${color}${colors.bright}[${prefix}]${colors.reset} ${message}`);
};

// Check if virtual environment exists
const checkVenv = () => {
    const pythonPath = getPythonPath();
    return fs.existsSync(pythonPath);
};

// Create virtual environment
const createVenv = () => {
    return new Promise((resolve, reject) => {
        const backendPath = path.join(__dirname, 'backend');
        const systemPython = getSystemPython();

        log(colors.cyan, 'SETUP', 'Virtual environment not found. Creating...');
        log(colors.cyan, 'SETUP', `Using: ${systemPython}`);

        const venvProcess = spawn(systemPython, ['-m', 'venv', 'venv'], {
            cwd: backendPath,
            shell: isWindows,
            stdio: 'pipe',
        });

        venvProcess.stdout.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        venvProcess.stderr.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        venvProcess.on('close', (code) => {
            if (code === 0) {
                log(colors.cyan, 'SETUP', '✓ Virtual environment created successfully');
                resolve();
            } else {
                log(colors.red, 'SETUP', `✗ Failed to create virtual environment (exit code ${code})`);
                reject(new Error(`Venv creation failed with code ${code}`));
            }
        });

        venvProcess.on('error', (error) => {
            log(colors.red, 'SETUP', `Error: ${error.message}`);
            reject(error);
        });
    });
};

// Upgrade pip
const upgradePip = () => {
    return new Promise((resolve, reject) => {
        const pythonPath = getPythonPath();
        const backendPath = path.join(__dirname, 'backend');

        log(colors.cyan, 'SETUP', 'Upgrading pip...');

        const pipProcess = spawn(pythonPath, ['-m', 'pip', 'install', '--upgrade', 'pip'], {
            cwd: backendPath,
            shell: isWindows,
            stdio: 'pipe',
        });

        pipProcess.stdout.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        pipProcess.stderr.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        pipProcess.on('close', (code) => {
            if (code === 0) {
                log(colors.cyan, 'SETUP', '✓ Pip upgraded successfully');
                resolve();
            } else {
                log(colors.yellow, 'SETUP', `⚠ Pip upgrade completed with code ${code}`);
                resolve(); // Don't fail on pip upgrade issues
            }
        });

        pipProcess.on('error', (error) => {
            log(colors.yellow, 'SETUP', `Warning: ${error.message}`);
            resolve(); // Don't fail on pip upgrade issues
        });
    });
};

// Install backend dependencies
const installBackendDeps = () => {
    return new Promise((resolve, reject) => {
        const pythonPath = getPythonPath();
        const backendPath = path.join(__dirname, 'backend');
        const requirementsPath = path.join(backendPath, 'requirements.txt');

        if (!fs.existsSync(requirementsPath)) {
            log(colors.yellow, 'SETUP', 'No requirements.txt found, skipping dependency installation');
            resolve();
            return;
        }

        log(colors.cyan, 'SETUP', 'Installing backend dependencies...');

        const installProcess = spawn(pythonPath, ['-m', 'pip', 'install', '-r', 'requirements.txt'], {
            cwd: backendPath,
            shell: isWindows,
            stdio: 'pipe',
        });

        installProcess.stdout.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        installProcess.stderr.on('data', (data) => {
            log(colors.cyan, 'SETUP', data.toString().trim());
        });

        installProcess.on('close', (code) => {
            if (code === 0) {
                log(colors.cyan, 'SETUP', '✓ Backend dependencies installed successfully');
                resolve();
            } else {
                log(colors.red, 'SETUP', `✗ Failed to install dependencies (exit code ${code})`);
                reject(new Error(`Dependency installation failed with code ${code}`));
            }
        });

        installProcess.on('error', (error) => {
            log(colors.red, 'SETUP', `Error: ${error.message}`);
            reject(error);
        });
    });
};

// Setup backend environment
const setupBackend = async () => {
    try {
        if (!checkVenv()) {
            await createVenv();
        } else {
            log(colors.cyan, 'SETUP', '✓ Virtual environment found');
        }

        await upgradePip();
        await installBackendDeps();

        log(colors.cyan, 'SETUP', '✓ Backend setup complete\n');
    } catch (error) {
        log(colors.red, 'SETUP', `Setup failed: ${error.message}`);
        process.exit(1);
    }
};

// Start backend server
const startBackend = () => {
    const pythonPath = getPythonPath();
    const backendPath = path.join(__dirname, 'backend');

    log(colors.blue, 'BACKEND', `Starting FastAPI server...`);
    log(colors.blue, 'BACKEND', `Python: ${pythonPath}`);

    const backend = spawn(
        pythonPath,
        ['-m', 'uvicorn', 'app:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
        {
            cwd: backendPath,
            shell: isWindows,
            stdio: 'pipe',
        }
    );

    backend.stdout.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => log(colors.blue, 'BACKEND', line));
    });

    backend.stderr.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => log(colors.blue, 'BACKEND', line));
    });

    backend.on('error', (error) => {
        log(colors.red, 'BACKEND', `Error: ${error.message}`);
        log(colors.yellow, 'BACKEND', 'Make sure you have activated the virtual environment and installed dependencies');
    });

    backend.on('close', (code) => {
        log(colors.red, 'BACKEND', `Process exited with code ${code}`);
    });

    return backend;
};

// Start frontend server
const startFrontend = () => {
    const frontendPath = path.join(__dirname, 'frontend');

    log(colors.green, 'FRONTEND', 'Starting Vite dev server...');

    const npm = isWindows ? 'npm.cmd' : 'npm';
    const frontend = spawn(npm, ['run', 'dev'], {
        cwd: frontendPath,
        shell: isWindows,
        stdio: 'pipe',
    });

    frontend.stdout.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => log(colors.green, 'FRONTEND', line));
    });

    frontend.stderr.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => log(colors.green, 'FRONTEND', line));
    });

    frontend.on('error', (error) => {
        log(colors.red, 'FRONTEND', `Error: ${error.message}`);
    });

    frontend.on('close', (code) => {
        log(colors.red, 'FRONTEND', `Process exited with code ${code}`);
    });

    return frontend;
};

// Main execution
const main = async () => {
    console.log('\n' + colors.bright + '🚀 Starting FareShare Application' + colors.reset);
    console.log(colors.bright + '================================\n' + colors.reset);

    // Setup backend environment first
    await setupBackend();

    // Start servers
    const backend = startBackend();
    const frontend = startFrontend();

    return { backend, frontend };
};

// Run main function
let servers = { backend: null, frontend: null };
main().then((s) => {
    servers = s;
}).catch((error) => {
    log(colors.red, 'ERROR', `Failed to start: ${error.message}`);
    process.exit(1);
});

// Graceful shutdown
const shutdown = () => {
    console.log('\n' + colors.yellow + '🛑 Shutting down servers...' + colors.reset);
    if (servers.backend) servers.backend.kill();
    if (servers.frontend) servers.frontend.kill();
    process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// Keep process alive
process.stdin.resume();
