import requests

def check_update_data_runs():
    url = "https://api.github.com/repos/voxcuriosa/EnergyMonitor/actions/workflows/update_data.yml/runs?per_page=5"
    response = requests.get(url)
    if response.status_code == 200:
        runs = response.json().get('workflow_runs', [])
        for r in runs:
            print(f"- {r['name']} / {r['conclusion']} / {r['created_at']}")
            if r['conclusion'] == 'failure':
                jobs_url = r['jobs_url']
                jobs_resp = requests.get(jobs_url).json()
                for j in jobs_resp.get('jobs', []):
                    if j['conclusion'] == 'failure':
                        print(f"  Job failed: {j['name']}")
    else:
        print(f"Error {response.status_code}")

if __name__ == "__main__":
    check_update_data_runs()
