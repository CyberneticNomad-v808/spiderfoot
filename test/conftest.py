import contextlib
import os
import sys
import time
import pytest
import logging
import threading
import subprocess
from pathlib import Path
from _pytest.runner import runtestprotocol

# Verify required environment variables are set BEFORE any SpiderFoot imports
# These should be provided by: op run --env-file="./.env.test" -- pytest ...
required_vars = ['SPIDERFOOT_DB_TYPE', 'SPIDERFOOT_DB_HOST', 'SPIDERFOOT_DB_PORT',
                 'SPIDERFOOT_DB_NAME', 'SPIDERFOOT_DB_USER', 'SPIDERFOOT_DB_PASSWORD']
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    raise EnvironmentError(
        f"Required environment variables not set: {', '.join(missing)}\n"
        "Run tests with: op run --env-file='./.env.test' -- pytest ..."
    )

# Ensure we're in the correct directory for tests
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

# Add project root to Python path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import SpiderFootHelpers after path setup
from spiderfoot import SpiderFootHelpers  # noqa: E402

# Import our test fixtures and utilities
from test.fixtures.database_fixtures import *  # noqa: E402, F403, F401
from test.fixtures.network_fixtures import *  # noqa: E402, F403, F401
from test.fixtures.event_fixtures import *  # noqa: E402, F403, F401
from test.utils import legacy_test_helpers  # noqa: E402, F401

# Set up logging with error suppression for distributed testing


class SafeHandler(logging.StreamHandler):
    """A logging handler that suppresses BrokenPipeError and similar issues during xdist termination."""

    def emit(self, record):
        with contextlib.suppress(OSError, ValueError):
            super().emit(record)


class SafeFileHandler(logging.FileHandler):
    """A file handler that suppresses errors during xdist termination."""

    def emit(self, record):
        with contextlib.suppress(OSError, ValueError):
            super().emit(record)


# Configure logging with safe handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        SafeFileHandler("pytest-debug.log"),
        SafeHandler()
    ]
)

# Track test execution and find potential issues


@pytest.hookimpl(trylast=True)
def pytest_runtest_protocol(item, nextitem):
    start_time = time.time()

    # Use safe logging
    with contextlib.suppress(OSError, ValueError):
        logging.info(f"Starting test: {item.nodeid}")

        # Show active threads at start
        active_threads = threading.enumerate()
        logging.info(f"Active threads before test ({len(active_threads)}): {[t.name for t in active_threads]}")

    # Run the test normally
    runtestprotocol(item, nextitem=nextitem)

    # Use safe logging for completion
    with contextlib.suppress(OSError, ValueError):
        # Show threads after test completion
        active_threads = threading.enumerate()
        logging.info(f"Active threads after test ({len(active_threads)}): {[t.name for t in active_threads]}")

        # Show elapsed time
        elapsed = time.time() - start_time
        logging.info(f"Completed test: {item.nodeid} ({elapsed:.2f}s)")

    return True


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    # Only start timeout if not already configured and not in xdist worker
    if not hasattr(config, '_timeout_started') and not hasattr(config, 'workerinput'):
        config._timeout_started = True
        start_global_timeout()


def start_global_timeout():
    """Create a global timeout thread with safe error handling."""
    def timeout_thread():
        time.sleep(1800)  # 30-minute global timeout
        with contextlib.suppress(Exception):
            # Use print instead of logging to avoid closed file issues
            print("Global timeout exceeded. Terminating test run.", file=sys.stderr, flush=True)
        os._exit(1)

    # Explicitly set daemon to True to ensure it doesn't prevent shutdown
    thread = threading.Thread(target=timeout_thread, daemon=True)
    thread.start()


# Detect tests that don't clean up resources


@pytest.fixture(autouse=True)
def check_resource_leaks():
    # Record initial state
    starting_threads = set(threading.enumerate())

    # Run the test
    yield

    # Give a moment for cleanup
    time.sleep(0.1)  # Reduced sleep time

    # Check which new threads are lingering
    ending_threads = set(threading.enumerate())
    new_threads = ending_threads - starting_threads

    if new_threads:
        thread_names = [t.name for t in new_threads if t.is_alive() and not t.daemon]
        if thread_names:  # Only report non-daemon threads
            logging.warning(f"Potential thread leak detected: {thread_names}")


@pytest.fixture(autouse=True)
def default_options(request):
    # Ensure modules directory exists and is accessible
    modules_dir = PROJECT_ROOT / "modules"
    if not modules_dir.exists():
        pytest.fail(f"Modules directory not found: {modules_dir}")

    # Only set default_options if running in a class context
    if hasattr(request, 'cls') and request.cls is not None:
        # Build DSN from environment to ensure test vs prod credentials are respected
        db_user = os.environ['SPIDERFOOT_DB_USER']
        db_pass = os.environ['SPIDERFOOT_DB_PASSWORD']
        db_host = os.environ['SPIDERFOOT_DB_HOST']
        db_port = os.environ['SPIDERFOOT_DB_PORT']
        db_name = os.environ['SPIDERFOOT_DB_NAME']
        dsn = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

        request.cls.default_options = {
            '_debug': False,
            '__logging': True,
            '__outputfilter': None,
            '_useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            '_dnsserver': '',
            '_fetchtimeout': 5,
            '_internettlds': 'https://publicsuffix.org/list/effective_tld_names.dat',
            '_internettlds_cache': 72,
            '_genericusers': ",".join(SpiderFootHelpers.usernamesFromWordlists(['generic-usernames'])),
            # PostgreSQL-only: use DSN format from env
            '__database': dsn,
            '__dbtype': 'postgresql',
            '__modules__': None,
            '__correlationrules__': None,
            '_socks1type': '',
            '_socks2addr': '',
            '_socks3port': '',
            '_socks4user': '',
            '_socks5pwd': '',
            '__logstdout': False,
            '__modulesdir': str(modules_dir)
        }
        request.cls.web_default_options = {'root': '/'}
        request.cls.cli_default_options = {
            "cli.debug": False,
            "cli.silent": False,
            "cli.color": True,
            "cli.output": "pretty",
            "cli.history": True,
            "cli.history_file": "",
            "cli.spool": False,
            "cli.spool_file": "",
            "cli.ssl_verify": True,
            "cli.username": "",
            "cli.password": "",
            "cli.server_baseurl": "http://127.0.0.1:5001"
        }
    # For function-based tests, do nothing (or set module-level if needed)
    yield

# Force cleanup of lingering resources


@pytest.fixture(autouse=True, scope="session")
def recreate_test_database(request):
    """Drop and recreate the test database before running tests."""
    # Only run in master process, not in xdist workers
    if hasattr(request.config, 'workerinput'):
        yield
        return
    
    db_name = os.environ.get('SPIDERFOOT_DB_NAME', 'spiderfoot_test')
    db_owner = os.environ.get('SPIDERFOOT_DB_USER', 'spiderfoot_test')
    
    try:
        # Drop existing database
        subprocess.run(
            ['docker', 'exec', 'unified-postgres', 'psql', '-U', 'postgres', '-c', f'DROP DATABASE IF EXISTS {db_name};'],
            check=True,
            capture_output=True,
            text=True
        )
        # Create fresh database with test user as owner
        subprocess.run(
            ['docker', 'exec', 'unified-postgres', 'psql', '-U', 'postgres', '-c', f'CREATE DATABASE {db_name} OWNER {db_owner};'],
            check=True,
            capture_output=True,
            text=True
        )
        # Grant all privileges on database to test user
        subprocess.run(
            ['docker', 'exec', 'unified-postgres', 'psql', '-U', 'postgres', '-d', db_name, '-c', f'GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_owner};'],
            check=True,
            capture_output=True,
            text=True
        )
        # Change public schema owner to test user to ensure CREATE permissions
        subprocess.run(
            ['docker', 'exec', 'unified-postgres', 'psql', '-U', 'postgres', '-d', db_name, '-c', f'ALTER SCHEMA public OWNER TO {db_owner};'],
            check=True,
            capture_output=True,
            text=True
        )
        # Grant explicit permissions on public schema
        subprocess.run(
            ['docker', 'exec', 'unified-postgres', 'psql', '-U', 'postgres', '-d', db_name, '-c', f'GRANT ALL PRIVILEGES ON SCHEMA public TO {db_owner};'],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"Recreated test database: {db_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to recreate test database: {e.stderr}")
        raise
    
    yield


@pytest.fixture(autouse=True, scope="session")
def session_cleanup():
    yield
    # Force cleanup at end of session - critical to prevent xdist communication errors
    import gc
    import threading

    # Force garbage collection
    gc.collect()

    # Clean up threads safely with proper error handling
    main_thread = threading.main_thread()
    from contextlib import suppress

    for thread in threading.enumerate():
        if thread != main_thread and thread.is_alive():
            # FIXED: Don't try to set daemon on active threads - this causes RuntimeError
            # Instead, attempt to join threads safely with timeout
            with suppress(RuntimeError, OSError):
                # Only join threads that are SpiderFoot-related or our test threads
                if (hasattr(thread, '_target') and thread._target
                        and ('SpiderFoot' in str(thread._target) or 'test' in str(thread._target))):
                    thread.join(timeout=1.0)

    # CRITICAL: Shutdown logging system BEFORE xdist tries to close communication pipes
    # This prevents BrokenPipeError and "I/O operation on closed file" errors
    with contextlib.suppress(Exception):
        # First, try to log completion if logging is still available
        with contextlib.suppress(ValueError, OSError, BrokenPipeError):
            # Only log if we can safely write to handlers
            root_logger = logging.getLogger()
            if root_logger.handlers:
                for handler in root_logger.handlers[:]:  # Copy list to avoid modification during iteration
                    with contextlib.suppress(ValueError, OSError, AttributeError):
                        if hasattr(handler, 'stream') and not handler.stream.closed:
                            logging.info("Session cleanup completed")
                        break  # Only log once if we can

    # Now shutdown the logging system to clean up handlers and streams
    with contextlib.suppress(Exception):
        logging.shutdown()
