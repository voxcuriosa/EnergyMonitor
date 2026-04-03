import requests
import json

def check_actions():
    url = "https://api.github.com/repos/voxcuriosa/EnergyMonitor/actions/runs"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        runs = data.get('workflow_runs', [])
        print("Latest runs:")
        for r in runs[:5]:
            print(f"- {r['name']} / {r['conclusion']} / {r['created_at']}")
            if r['conclusion'] == 'failure':
                # get jobs
                jobs_url = r['jobs_url']
                jobs_resp = requests.get(jobs_url).json()
                for j in jobs_resp.get('jobs', []):
                    if j['conclusion'] == 'failure':
                        print(f"  Job failed: {j['name']}")
                        # We can't fetch step logs without auth often, but let's try
                        for s in j.get('steps', []):
                            if s['conclusion'] == 'failure':
                                print(f"    Step failed: {s['name']}")
    else:
        print(f"Error {response.status_code}")

if __name__ == "__main__":
    check_actions()
