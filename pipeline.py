import subprocess
import sys
import os
import time
import platform

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(" SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(" FAILED")
        print("Error:", e.stderr)
        if e.stdout:
            print("Output:", e.stdout)
        return False

def test_docker_container():
    """Test Docker container with proper cleanup"""
    container_name = "test_container_sample"
    
    print(f"\n{'='*50}")
    print("Running: Docker Container Test")
    print(f"{'='*50}")
    
    try:
        # Clean up any existing container (PowerShell compatible)
        if platform.system() == "Windows":
            subprocess.run(f"docker stop {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"docker rm {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"docker stop {container_name} 2>/dev/null", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"docker rm {container_name} 2>/dev/null", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Start container - Use port 8000 to match main.py
        print("Starting container...")
        result = subprocess.run(
            f"docker run -d -p 8000:8000 --name {container_name} fastapi_app",
            shell=True, check=True, capture_output=True, text=True
        )
        print("Container started successfully")
        
        # Wait longer for application to start
        print("Waiting for application to start...")
        time.sleep(15)  # Increased wait time
        
        # Test the health endpoint - Use port 8000
        print("Testing health endpoint...")
        
        # Try multiple times with increasing delays
        for attempt in range(3):
            try:
                if platform.system() == "Windows":
                    curl_cmd = 'curl -f -m 10 http://localhost:8000/health'
                else:
                    curl_cmd = 'curl -f -m 10 http://localhost:8000/health'
                    
                test_result = subprocess.run(
                    curl_cmd, shell=True, check=True, capture_output=True, text=True
                )
                
                print(" Container test SUCCESS")
                print("Response:", test_result.stdout)
                return True
                
            except subprocess.CalledProcessError as e:
                if attempt < 2:  # Not the last attempt
                    print(f"Attempt {attempt + 1} failed, retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print(" Container test FAILED")
                    print("Error:", e.stderr if e.stderr else "No error output")
                    if e.stdout:
                        print("Output:", e.stdout)
                    
                    # Additional debugging
                    print("Checking container logs...")
                    logs_result = subprocess.run(
                        f"docker logs {container_name}", 
                        shell=True, capture_output=True, text=True
                    )
                    if logs_result.stdout:
                        print("Container logs:", logs_result.stdout[-500:])  # Last 500 chars
                    
                    return False
        
    except subprocess.CalledProcessError as e:
        print(" Container test FAILED")
        print("Error:", e.stderr)
        if e.stdout:
            print("Output:", e.stdout)
        return False
    finally:
        # Always clean up (PowerShell compatible)
        print("Cleaning up container...")
        if platform.system() == "Windows":
            subprocess.run(f"docker stop {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"docker rm {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"docker stop {container_name} 2>/dev/null", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"docker rm {container_name} 2>/dev/null", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    """Main execution function"""
    print(" Starting Test and Build Pipeline")
    
    # Step 1: Run unit tests
    test_success = run_command("python test_main.py", "Unit Tests")
    
    if not test_success:
        print("\n Unit tests failed. Docker build will NOT be triggered.")
        sys.exit(1)
    
    print("\n All unit tests passed! Proceeding with Docker build...")
    
    # Step 2: Build Docker image (only if tests pass)
    build_success = run_command("docker build -t fastapi_app .", "Docker Build")
    
    if not build_success:
        print("\n Docker build failed.")
        sys.exit(1)
    
    # Step 3: Test Docker container
    test_container_success = test_docker_container()
    
    if test_container_success:
        print("\n All tests passed and Docker image built successfully!")
        print(" Pipeline completed successfully")
    else:
        print("\n Docker container test failed, but image was built successfully")
        print(" Core pipeline completed")
    
    print("\n Summary:")
    print(f"  Unit Tests: {' PASSED' if test_success else ' FAILED'}")
    print(f"  Docker Build: {' PASSED' if build_success else ' FAILED'}")
    print(f"  Container Test: {' PASSED' if test_container_success else '  WARNING'}")

if __name__ == "__main__":
    main()