import multiprocessing
import time

# Function to check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

# Worker function to continuously test primes
def stress_worker(worker_id):
    print(f"Worker {worker_id} started")
    num = 10**7  # starting number
    
    while True:
        is_prime(num)
        num += 1  # keep increasing workload

# Main function to spawn processes
def main():
    num_cores = multiprocessing.cpu_count()
    print(f"Starting stress test on {num_cores} cores")

    processes = []

    for i in range(num_cores):
        p = multiprocessing.Process(target=stress_worker, args=(i,))
        p.start()
        processes.append(p)

    # Run indefinitely (Ctrl+C to stop)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping stress test...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()