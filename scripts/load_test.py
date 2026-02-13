
import urllib.request
import time
import concurrent.futures
import statistics

BASE_URL = "http://127.0.0.1:8001"
NUM_REQUESTS = 100
CONCURRENT_USERS = 10

def simulate_user_request(request_id):
    """Simulates a user checking context or authentication status"""
    start_time = time.time()
    try:
        # Hitting the login page (admin login)
        with urllib.request.urlopen(f"{BASE_URL}/admin/login/") as response:
            elapsed = time.time() - start_time
            return elapsed, response.getcode()
    except Exception as e:
        return None, str(e)

def run_load_test():
    print(f"\n🚀 STARTING LOAD TEST ({NUM_REQUESTS} requests, {CONCURRENT_USERS} concurrent)...")
    
    times = []
    errors = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [executor.submit(simulate_user_request, i) for i in range(NUM_REQUESTS)]
        
        for future in concurrent.futures.as_completed(futures):
            elapsed, status = future.result()
            if elapsed is not None:
                times.append(elapsed)
                if status != 200:
                    errors += 1
            else:
                # print(f"Error: {status}") 
                errors += 1
                
    if not times:
        print("❌ FAILED: No successful requests.")
        return

    avg_time = statistics.mean(times)
    max_time = max(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    
    print(f"\n📊 RESULTS:")
    print(f"  Total Requests: {NUM_REQUESTS}")
    print(f"  Concurrent:     {CONCURRENT_USERS}")
    print(f"  Errors:         {errors}")
    print(f"  Avg Time:       {avg_time*1000:.2f} ms")
    print(f"  95th % Time:    {p95_time*1000:.2f} ms")
    print(f"  Max Time:       {max_time*1000:.2f} ms")
    
    if avg_time < 0.2:
        print("\n✅ PASS: Average response time < 200ms")
    else:
        print("\n⚠️ WARN: Average response time > 200ms")

if __name__ == "__main__":
    run_load_test()
