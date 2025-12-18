# run_all.py
import subprocess
import sys
import time

SERVICES = [
    ("Auth Service",         "services/auth_service",          5001),
    ("Transactions Service", "services/transaction_service",  5002),
    ("Category Service",   "services/category_service",    5003),
    ("Analytics Service",    "services/analytics_service",     5004),
    ("Alerts Service",       "services/alerts_service",        5005),
    ("Points Service",       "services/points_service",        5006),
    ("Web App (UI)",         "web_app",                        5000),
]

def main():
    print("Starting Budget Tracker Microservices…")
    print("=" * 60)

    processes = []
    for name, path, port in SERVICES:
        print(f"Starting {name} on port {port}…")
        p = subprocess.Popen([sys.executable, "app.py"], cwd=path)
        processes.append((name, p, port))
        time.sleep(0.3)

    print("=" * 60)
    print("All services started. Press Ctrl+C to stop.")
    print("UI:           http://localhost:5000")
    print("Auth health:  http://localhost:5001/health")
    print("Transaction health:   http://localhost:5002/health")
    print("Category health:   http://localhost:5003/health")
    print("Analytics health:http://localhost:5004/health")
    print("Alerts health:http://localhost:5005/health")
    print("Points health:http://localhost:5006/health")

    try:
        while True:
            time.sleep(1)
            for name, proc, _ in processes:
                if proc.poll() is not None:
                    print(f"\n{name} exited.")
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\nStopping all services…")
        for name, proc, _ in processes:
            proc.terminate()
            print(f"Stopped {name}")
        print("All services stopped.")

if __name__ == "__main__":
    main()
